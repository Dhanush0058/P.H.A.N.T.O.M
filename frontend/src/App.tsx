import React, { useState, useEffect, useRef } from 'react';
import { CoreOrb } from './components/CoreOrb';
import { StateIndicator } from './components/StateIndicator';
import { Waveform } from './components/Waveform';
import { ChatContainer } from './components/ChatContainer';
import { PermissionModal } from './components/PermissionModal';
import { SystemHUD } from './components/SystemHUD';
import { EmergencyStop } from './components/EmergencyStop';
import { Sidebar } from './components/Sidebar';
import { SettingsModal } from './components/SettingsModal';
import type {
  AssistantState,
  ChatMessage,
  PermissionRequestEvent,
  SystemMetrics,
  ToolDefinition
} from './types';
import {
  sendChatMessage,
  getConversations,
  getTools,
  triggerEmergencyStop,
  triggerEmergencyReset,
  resolvePermission,
  synthesizeTTS
} from './services/api';
import {
  Mic,
  MicOff,
  Send,
  Volume2,
  VolumeX,
  Layers,
  Sparkles
} from 'lucide-react';

export const App: React.FC = () => {
  const [state, setState] = useState<AssistantState>('IDLE');
  const [statusText, setStatusText] = useState<string>('ONLINE');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isAudioMuted, setIsAudioMuted] = useState(false);
  const [permissionRequest, setPermissionRequest] = useState<PermissionRequestEvent | null>(null);
  const [isEmergencyStopped, setIsEmergencyStopped] = useState(false);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [tools, setTools] = useState<ToolDefinition[]>([]);
  const [conversations, setConversations] = useState<any[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>();
  const [eventsLog, setEventsLog] = useState<Array<{ time: string; event: string; data: any }>>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [streamingThought, setStreamingThought] = useState<string | undefined>();

  const socketRef = useRef<WebSocket | null>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize Web Speech Recognition
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        const transcript = event.results[event.results.length - 1][0].transcript.trim();
        if (transcript) {
          handleUserSubmit(transcript);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        setIsListening(false);
        setState('IDLE');
      };

      recognitionRef.current = recognition;
    }
  }, []);

  // Initialize WebSocket & data
  useEffect(() => {
    getTools().then(setTools).catch(console.error);
    getConversations().then(setConversations).catch(console.error);

    const connectWs = () => {
      const ws = new WebSocket('ws://127.0.0.1:8000/ws');
      socketRef.current = ws;

      ws.onopen = () => {
        setStatusText('CONNECTED');
        logEvent('system.connected', {});
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const { event: evType, data } = payload;
          logEvent(evType, data);

          switch (evType) {
            case 'assistant.state_change':
              setState(data.state);
              if (data.state === 'IDLE') setStreamingThought(undefined);
              break;

            case 'assistant.thinking':
              setState('THINKING');
              setStreamingThought(data.status || 'Reasoning...');
              break;

            case 'assistant.tool_call':
              setState('EXECUTING');
              setStreamingThought(`Executing tool: ${data.name}`);
              break;

            case 'assistant.tool_result':
              setMessages((prev) => [
                ...prev,
                {
                  id: String(Date.now()),
                  role: 'tool',
                  content: data.message || JSON.stringify(data.data || data.error),
                  timestamp: new Date().toISOString()
                }
              ]);
              break;

            case 'assistant.permission_required':
              setPermissionRequest(data);
              break;

            case 'assistant.permission_resolved':
              setPermissionRequest(null);
              break;

            case 'assistant.chat_message':
              setState('SPEAKING');
              setStreamingThought(undefined);
              setMessages((prev) => [
                ...prev,
                {
                  id: String(Date.now()),
                  role: 'assistant',
                  content: data.content,
                  tools_invoked: data.tools_invoked,
                  timestamp: new Date().toISOString()
                }
              ]);
              if (!isAudioMuted && data.content) {
                playVoiceResponse(data.content);
              } else {
                setTimeout(() => setState('IDLE'), 1200);
              }
              break;

            case 'assistant.system_stats':
              setSystemMetrics(data);
              break;

            case 'assistant.emergency_stop':
              setIsEmergencyStopped(data.stopped);
              if (data.stopped) setState('ERROR');
              else setState('IDLE');
              break;
          }
        } catch (e) {
          console.error('Error handling WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        setStatusText('DISCONNECTED');
        setTimeout(connectWs, 3000);
      };
    };

    connectWs();

    return () => {
      socketRef.current?.close();
    };
  }, [isAudioMuted]);

  const logEvent = (event: string, data: any) => {
    setEventsLog((prev) => [
      { time: new Date().toLocaleTimeString(), event, data },
      ...prev.slice(0, 40)
    ]);
  };

  const playVoiceResponse = async (text: string) => {
    try {
      const audioBlob = await synthesizeTTS(text);
      if (audioBlob.size > 0) {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.onended = () => setState('IDLE');
        audio.onerror = () => setState('IDLE');
        await audio.play();
      } else {
        setState('IDLE');
      }
    } catch (e) {
      console.warn('TTS playback error:', e);
      setState('IDLE');
    }
  };

  const handleUserSubmit = async (textToSend?: string) => {
    const query = textToSend || inputText;
    if (!query.trim()) return;

    setInputText('');
    setStreamingThought('Processing user request...');
    setState('THINKING');

    const newMsg: ChatMessage = {
      id: String(Date.now()),
      role: 'user',
      content: query,
      timestamp: new Date().toISOString()
    };
    setMessages((prev) => [...prev, newMsg]);

    try {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(
          JSON.stringify({
            action: 'chat',
            text: query,
            conversation_id: currentConversationId
          })
        );
      } else {
        const res = await sendChatMessage(query, currentConversationId);
        if (res.conversation_id && !currentConversationId) {
          setCurrentConversationId(res.conversation_id);
        }
      }
    } catch (e) {
      console.error(e);
      setState('ERROR');
    }
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser. Use Chrome or Edge.');
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      setState('IDLE');
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        setState('LISTENING');
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleResolvePermission = async (reqId: string, approved: boolean) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          action: 'resolve_permission',
          request_id: reqId,
          approved
        })
      );
    } else {
      await resolvePermission(reqId, approved);
    }
    setPermissionRequest(null);
  };

  const handleTriggerEmergencyStop = async () => {
    await triggerEmergencyStop();
    setIsEmergencyStopped(true);
    setState('ERROR');
  };

  const handleResetEmergencyStop = async () => {
    await triggerEmergencyReset();
    setIsEmergencyStopped(false);
    setState('IDLE');
  };

  return (
    <div className="flex h-screen w-screen bg-[#05070e] text-slate-100 font-sans overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        conversations={conversations}
        onSelectConversation={(cid) => {
          setCurrentConversationId(cid);
        }}
        tools={tools}
        eventsLog={eventsLog}
        onOpenSettings={() => setIsSettingsOpen(true)}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Main Operating HUD Interface */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Top Holographic Navigation Bar */}
        <header className="flex items-center justify-between px-5 py-3 border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-xl z-20">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-500/50 text-slate-300 hover:text-cyan-400 transition"
              title="Toggle Sidebar"
            >
              <Layers className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-2 font-mono">
              <span className="font-extrabold tracking-widest text-cyan-400 text-sm flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
                JARVIS
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400">
                v1.0.0
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <EmergencyStop
              isStopped={isEmergencyStopped}
              onTriggerStop={handleTriggerEmergencyStop}
              onResetStop={handleResetEmergencyStop}
            />
            <button
              onClick={() => setIsAudioMuted(!isAudioMuted)}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-cyan-400 transition"
              title={isAudioMuted ? 'Unmute Audio' : 'Mute Audio'}
            >
              {isAudioMuted ? <VolumeX className="w-4 h-4 text-red-400" /> : <Volume2 className="w-4 h-4 text-cyan-400" />}
            </button>
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-[11px] font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-slate-300">{statusText}</span>
            </div>
          </div>
        </header>

        {/* Center Stage: Core Orb + State Machine + Live Telemetry */}
        <div className="flex flex-col items-center justify-center pt-2 pb-2 px-4 border-b border-slate-900/80 bg-gradient-to-b from-slate-950/40 via-transparent to-slate-950/20">
          <CoreOrb state={state} isAudioActive={isListening || state === 'SPEAKING'} />
          <StateIndicator state={state} subText={streamingThought} />
          <Waveform state={state} isActive={isListening || state === 'SPEAKING'} />
        </div>

        {/* System Telemetry Bar */}
        <div className="px-5 py-2">
          <SystemHUD metrics={systemMetrics} />
        </div>

        {/* Chat Stream Area */}
        <ChatContainer messages={messages} streamingThought={streamingThought} />

        {/* Bottom Command & Voice Control Bar */}
        <footer className="p-4 border-t border-slate-800/80 bg-slate-950/80 backdrop-blur-xl z-20">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleUserSubmit();
            }}
            className="flex items-center gap-2 max-w-4xl mx-auto"
          >
            {/* Voice Input Button */}
            <button
              type="button"
              onClick={toggleListening}
              className={`p-3 rounded-2xl border transition-all duration-300 flex items-center justify-center ${
                isListening
                  ? 'bg-emerald-500/20 border-emerald-400 text-emerald-300 shadow-lg shadow-emerald-500/30 scale-105 animate-pulse'
                  : 'bg-slate-900 border-slate-800 hover:border-cyan-500/50 text-slate-400 hover:text-cyan-400'
              }`}
              title={isListening ? 'Stop Listening' : 'Start Voice Input ("Hey Phantom")'}
            >
              {isListening ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
            </button>

            {/* Natural Language Prompt Input */}
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Give PHANTOM a command (e.g., 'Shut down my laptop', 'What's the system status?', 'Open Chrome')..."
                className="w-full px-4 py-3 rounded-2xl bg-slate-900/90 border border-slate-800 focus:border-cyan-500/70 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500 font-sans shadow-inner transition"
              />
            </div>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!inputText.trim()}
              className="p-3 rounded-2xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white shadow-lg shadow-cyan-600/30 transition active:scale-95 flex items-center justify-center"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </footer>

        {/* Interactive Permission Escalation Modal */}
        <PermissionModal request={permissionRequest} onResolve={handleResolvePermission} />

        {/* Settings Modal */}
        <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      </main>
    </div>
  );
};

export default App;
