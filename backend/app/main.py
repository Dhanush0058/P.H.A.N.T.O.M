import asyncio
import json
from contextlib import asynccontextmanager
from typing import Set, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.events import WebSocketEvent, WebSocketEventType
from backend.app.database.database import init_db
from backend.app.platform.windows import windows_platform
from backend.app.agent.agent import jarvis_agent
from backend.app.security.permissions import permission_manager
from backend.app.core.emergency import emergency_manager

# API Routers
from backend.app.api.chat import router as chat_router
from backend.app.api.voice import router as voice_router
from backend.app.api.tools import router as tools_router
from backend.app.api.memory import router as memory_router
from backend.app.api.tasks import router as tasks_router
from backend.app.api.system import router as system_router
from backend.app.api.settings import router as settings_router

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        payload = json.dumps({"event": event_type, "data": data})
        for conn in list(self.active_connections):
            try:
                await conn.send_text(payload)
            except Exception as e:
                logger.error(f"Error sending message to websocket: {e}")
                self.active_connections.discard(conn)

manager = ConnectionManager()

async def system_telemetry_loop():
    """Periodically broadcast live CPU/RAM/Disk stats to connected clients."""
    while True:
        try:
            if manager.active_connections:
                metrics = windows_platform.get_system_metrics()
                await manager.broadcast("assistant.system_stats", metrics)
        except Exception as e:
            logger.debug(f"Telemetry loop error: {e}")
        await asyncio.sleep(2.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing JARVIS Core Server...")
    await init_db()
    telemetry_task = asyncio.create_task(system_telemetry_loop())
    yield
    telemetry_task.cancel()
    logger.info("JARVIS Server shutdown complete.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount API routes
app.include_router(chat_router)
app.include_router(voice_router)
app.include_router(tools_router)
app.include_router(memory_router)
app.include_router(tasks_router)
app.include_router(system_router)
app.include_router(settings_router)

@app.get("/")
async def root():
    return {
        "status": "ONLINE",
        "system": settings.APP_NAME,
        "version": settings.VERSION,
        "emergency_stop_active": emergency_manager.is_stopped
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial status & pending permissions
        await websocket.send_text(json.dumps({
            "event": "assistant.state_change",
            "data": {"state": "IDLE"}
        }))

        active_agent_task: Optional[asyncio.Task] = None

        while True:
            raw_data = await websocket.receive_text()
            try:
                msg = json.loads(raw_data)
                action = msg.get("action")

                if action == "interrupt":
                    if active_agent_task and not active_agent_task.done():
                        logger.info("Interrupt received: Cancelling active agent task.")
                        active_agent_task.cancel()
                    await manager.broadcast("assistant.state_change", {"state": "IDLE"})

                elif action == "chat":
                    text = msg.get("text", "")
                    cid = msg.get("conversation_id")
                    
                    # If an existing agent query is running, cancel it to prioritize the new user input immediately
                    if active_agent_task and not active_agent_task.done():
                        logger.info("New message arrived: Cancelling previous agent task for barge-in responsiveness.")
                        active_agent_task.cancel()

                    # Run agent processing in tracked task
                    active_agent_task = asyncio.create_task(
                        jarvis_agent.process_user_request(
                            user_text=text,
                            conversation_id=cid,
                            broadcast_callback=manager.broadcast
                        )
                    )

                elif action == "resolve_permission":
                    req_id = msg.get("request_id")
                    approved = msg.get("approved", False)
                    permission_manager.resolve_request(req_id, approved)

                elif action == "emergency_stop":
                    if active_agent_task and not active_agent_task.done():
                        active_agent_task.cancel()
                    emergency_manager.trigger_stop()
                    await manager.broadcast("assistant.emergency_stop", {"stopped": True})

                elif action == "emergency_reset":
                    emergency_manager.reset()
                    await manager.broadcast("assistant.emergency_stop", {"stopped": False})

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received on websocket: {raw_data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket unhandled error: {str(e)}")
        manager.disconnect(websocket)
