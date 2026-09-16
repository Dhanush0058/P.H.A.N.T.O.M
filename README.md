# JARVIS — Personal AI Operating Assistant

[![System Status: Online](https://img.shields.io/badge/JARVIS-OPERATIONAL-00f0ff?style=for-the-badge&logo=shield)](https://github.com)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-TypeScript-61dafb?style=for-the-badge&logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-Bundler-646cff?style=for-the-badge&logo=vite)](https://vitejs.dev)

JARVIS is a modular personal AI operating assistant capable of multi-step autonomous reasoning, executing tools, computer automation on Windows, long-term memory management, speech recognition, neural voice synthesis, screen vision analysis, and safety-enforced interactive permission controls.

---

## 🌟 Architecture Overview

```
                       ┌──────────────┐
                       │    JARVIS    │
                       │ AI Operating │
                       │   Assistant  │
                       └──────┬───────┘
                              │
       ┌──────────────┬───────┼────────┬──────────────┐
       ↓              ↓       ↓        ↓              ↓
     VOICE          BRAIN   MEMORY   VISION         TOOLS
       │              │       │        │              │
    STT/TTS        Pluggable  SQLite  Screenshots   Windows Apps
   (EdgeTTS /      Providers (History,              Filesystem
   WebSpeech)     (Gemini,   Working,               Terminal
                  OpenAI,    Prefs)                 DuckDuckGo
                  Anthropic,                        Git / GitHub
                  Custom)                           System Metrics
```

---

## 🚀 Key Features

1. **Modular Pluggable AI Brain (`AIProvider`)**
   - **Ollama Local LLMs**: 100% Free, infinite tokens, offline inference with zero rate limits (`qwen2.5-coder:1.5b`, `llama3.2:3b`, etc.).
   - **OmniRoute Gateway**: Auto-routing pool accessing ~1.51B tokens/month across 352 AI providers.
   - **Google Gemini**: Native function-calling and vision reasoning.
   - **OpenAI / Anthropic Claude**: Cloud foundation models.
   - **Custom Multi-Model Adapter**: Connect to custom routing endpoints.
   - **Deterministic Mock Provider**: 100% offline testing with zero API keys required.

2. **Standardized Tool Registry & Windows Automation**
   - **Computer Tools**: Native Windows application launcher with URI scheme integration (`vscode`, `chrome`, `terminal`, `notepad`, `calc`, `explorer`, `spotify`, `whatsapp`).
   - **WhatsApp Automation**: Direct messaging (`send_whatsapp_message`) with automatic phone number recall from long-term memory.
   - **Filesystem Tools**: Path-sandboxed listing, reading, writing, moving, and safe deleting.
   - **Terminal Tools**: Shell command execution with strict regex classification and timeout controls.
   - **Web Research Tools**: DuckDuckGo search + web page text extraction.
   - **Git & GitHub Tools**: Local repository branch, commit, and diff inspection + authenticated issue creation.
   - **System Telemetry Tools**: Live CPU, RAM, Disk, Network, and process tree diagnostics.

3. **4-Tier Permission & Cybersecurity Engine**
   - `SAFE`: Non-destructive queries executed instantly (e.g. system status, file read, web search).
   - `CONFIRM`: Environment modifying actions require interactive user authorization (e.g. package installation, file modification, terminal execution).
   - `DANGEROUS`: Destructive actions require explicit dual confirmation (e.g. file deletion, process termination, system restart).
   - `BLOCKED`: Malicious commands, credential-dumping, and fork bombs are strictly rejected by `CommandValidator`.
   - **Emergency Stop**: Instant global cancellation switch halting all active tasks.

4. **Multi-Tier Memory Subsystem**
   - **Short-Term Memory**: Active conversation history & turn context.
   - **Working Memory**: Step-by-step decomposition & intermediate observations.
   - **Long-Term Memory**: Persistent SQLite database storing user facts, project preferences, and goals.

5. **Futuristic Cyberpunk HUD (React + TypeScript + Vite + Tailwind CSS)**
   - Dynamic Holographic **Core Orb** reflecting live state transitions: `IDLE`, `LISTENING`, `THINKING`, `EXECUTING`, `SPEAKING`, `ERROR`.
   - Audio Waveform frequency visualizer.
   - Live hardware telemetry gauges (CPU / RAM / Disk / Network).
   - Interactive Permission Approval modal dialogs.
   - Sidebar with Conversation History, Long-Term Memory editor, Tool Catalog, and Configuration Settings.

---

## 🛠️ Quick Start Guide (Windows 10/11)

### 1. Prerequisites
- Python 3.12+ (tested with 3.13.7)
- Node.js v20+ / npm v10+

### 2. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run backend unit tests
python -m pytest backend/tests -v

# Start FastAPI backend server (port 8000)
python run.py
```

### 3. Frontend Setup

```powershell
# In a separate PowerShell terminal, navigate to frontend
cd frontend

# Install dependencies (if not already installed)
npm install

# Start Vite development server
npm run dev
```

Open your browser at: **`http://localhost:5173`**

---

## ⚙️ Configuration (`.env`)

Copy `.env.example` to `.env`:

```env
AI_PROVIDER=gemini
AI_MODEL=gemini-2.0-flash
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_key_here

# For custom multi-model repository
CUSTOM_LLM_API_URL=http://localhost:8080/v1
CUSTOM_LLM_API_KEY=your_custom_secret

# Voice Settings
DEFAULT_TTS_VOICE=en-US-ChristopherNeural
WAKE_WORD="hey jarvis"
```

---

## 🔒 Security Architecture

| Permission Tier | Behavior | Example Operations |
|---|---|---|
| `SAFE` | Automatic Execution | `get_system_status`, `list_files`, `search_web`, `open_application` |
| `CONFIRM` | Interactive UI Prompt | `write_file`, `run_command`, `git push`, `pip install` |
| `DANGEROUS` | Explicit Warning & Confirmation | `delete_file`, `close_application`, `rm -rf`, `shutdown` |
| `BLOCKED` | Strictly Prohibited | `mimikatz`, `format C:`, Fork bombs, credential dumping |

---

## 🧪 Running Tests

```powershell
# Run the complete test suite
python -m pytest backend/tests -v
```

---

## 📂 Project Structure

```
c:\Users\dhanu\OneDrive\Desktop\MyProjects\Jarivs/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI server & WebSocket manager
│   │   ├── api/                     # Chat, Voice, Tools, Memory, Tasks, System, Settings
│   │   ├── agent/                   # Agent loop, Planner, Executor, Context
│   │   ├── ai/                      # Gemini, OpenAI, Anthropic, CustomRepo, Mock
│   │   ├── voice/                   # STT, Edge-TTS, WakeWord detector
│   │   ├── tools/                   # Computer, Filesystem, Terminal, Web, Git, GitHub
│   │   ├── memory/                  # ShortTerm, Working, LongTerm SQLite manager
│   │   ├── security/                # Permissions, CommandValidator, PathSandbox
│   │   ├── database/                # SQLAlchemy async models & SQLite engine
│   │   ├── platform/                # Windows-specific automation & app launcher
│   │   └── core/                    # Config, Logging, Events, EmergencyStop
│   ├── tests/                       # Unit test suite
│   ├── requirements.txt
│   └── run.py                       # Backend server launcher
├── frontend/
│   ├── src/
│   │   ├── components/              # CoreOrb, StateIndicator, Waveform, Chat, HUD, Modals
│   │   ├── services/                # REST & WebSocket API clients
│   │   ├── types/                   # TypeScript interfaces
│   │   ├── App.tsx                  # Main HUD Application
│   │   └── index.css                # Futuristic Cyberpunk theme & animations
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── data/                            # Local SQLite DB & screenshots
├── logs/                            # Scrubbed application logs
├── .env.example
├── .gitignore
└── README.md
```
