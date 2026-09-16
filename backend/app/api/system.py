from fastapi import APIRouter
from backend.app.platform.windows import windows_platform
from backend.app.core.emergency import emergency_manager

router = APIRouter(prefix="/api/system", tags=["System"])

@router.get("/metrics")
async def get_metrics():
    return windows_platform.get_system_metrics()

@router.get("/processes")
async def get_processes():
    return windows_platform.get_running_processes()

@router.post("/emergency-stop")
async def emergency_stop():
    cancelled = emergency_manager.trigger_stop()
    return {
        "status": "STOPPED",
        "message": f"Emergency Stop activated. Cancelled {cancelled} running task(s).",
        "emergency_stop_active": True
    }

@router.post("/emergency-reset")
async def emergency_reset():
    emergency_manager.reset()
    return {
        "status": "OPERATIONAL",
        "message": "Emergency Stop reset. System is ready.",
        "emergency_stop_active": False
    }

@router.get("/emergency-status")
async def emergency_status():
    return {
        "emergency_stop_active": emergency_manager.is_stopped
    }
