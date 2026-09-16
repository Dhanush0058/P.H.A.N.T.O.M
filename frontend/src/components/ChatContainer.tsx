import React, { useRef, useEffect } from 'react';
import type { ChatMessage } from '../types';
import { Terminal, Shield, Bot, User, Wrench, ChevronDown, ChevronUp } from 'lucide-react';

interface ChatContainerProps {
  messages: ChatMessage[];
  streamingThought?: string;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({ messages, streamingThought }) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [expandedTools, setExpandedTools] = React.useState<Record<string, boolean>>({});

  const toggleToolExpand = (id: string) => {
    setExpandedTools(prev => ({ ...prev, [id]: !prev[id] }));
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingThought]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 font-sans">
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-48 text-center text-slate-500 font-mono text-sm">
          <div className="w-10 h-10 mb-3 rounded-full border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Bot className="w-5 h-5" />
          </div>
          <p className="text-slate-400 font-medium">JARVIS Core Operational</p>
          <p className="text-xs text-slate-600 mt-1 max-w-sm">
            Say &ldquo;Hey Jarvis&rdquo; or type a command below. Try &ldquo;Open VS Code&rdquo;, &ldquo;System status&rdquo;, or &ldquo;Search for AI news&rdquo;.
          </p>
        </div>
      )}

      {messages.map((msg) => {
        if (msg.role === 'user') {
          return (
            <div key={msg.id} className="flex justify-end">
              <div className="max-w-xl bg-gradient-to-r from-cyan-600 to-blue-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm shadow-lg text-sm leading-relaxed">
                <div className="flex items-center gap-1.5 mb-1 opacity-75 text-[10px] font-mono uppercase tracking-wider">
                  <User className="w-3 h-3" />
                  <span>User</span>
                  <span className="ml-auto">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          );
        }

        if (msg.role === 'assistant') {
          return (
            <div key={msg.id} className="flex justify-start">
              <div className="max-w-2xl bg-slate-900/90 border border-slate-800 text-slate-100 px-4 py-3 rounded-2xl rounded-tl-sm shadow-xl text-sm leading-relaxed backdrop-blur-md">
                <div className="flex items-center gap-2 mb-2 pb-1.5 border-b border-slate-800 text-[11px] font-mono text-cyan-400">
                  <div className="w-4 h-4 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                  </div>
                  <span className="font-semibold tracking-wider">JARVIS</span>
                  <span className="text-slate-500 ml-auto">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>

                {/* Tool Invocation Badges */}
                {msg.tools_invoked && msg.tools_invoked.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    {msg.tools_invoked.map((t, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-purple-950/60 border border-purple-800/40 text-[10px] font-mono text-purple-300"
                      >
                        <Wrench className="w-2.5 h-2.5" />
                        {t}
                      </span>
                    ))}
                  </div>
                )}

                <div className="prose prose-invert prose-sm max-w-none whitespace-pre-wrap">
                  {msg.content}
                </div>
              </div>
            </div>
          );
        }

        if (msg.role === 'tool') {
          const isExp = expandedTools[msg.id];
          return (
            <div key={msg.id} className="flex justify-start pl-4">
              <div className="w-full max-w-xl bg-slate-950/80 border border-slate-800/80 rounded-lg p-2.5 text-xs font-mono text-slate-300">
                <div
                  className="flex items-center justify-between cursor-pointer text-slate-400 hover:text-cyan-400"
                  onClick={() => toggleToolExpand(msg.id)}
                >
                  <div className="flex items-center gap-2">
                    <Terminal className="w-3.5 h-3.5 text-purple-400" />
                    <span className="font-semibold text-purple-300">Tool Result</span>
                  </div>
                  {isExp ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </div>
                {isExp && (
                  <div className="mt-2 pt-2 border-t border-slate-800/60 bg-black/40 p-2 rounded text-[11px] max-h-40 overflow-y-auto whitespace-pre-wrap text-emerald-300">
                    {msg.content}
                  </div>
                )}
              </div>
            </div>
          );
        }

        if (msg.role === 'system') {
          return (
            <div key={msg.id} className="flex justify-center">
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-400">
                <Shield className="w-3 h-3 text-cyan-400" />
                <span>{msg.content}</span>
              </div>
            </div>
          );
        }

        return null;
      })}

      {streamingThought && (
        <div className="flex justify-start">
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-amber-950/20 border border-amber-500/20 text-xs font-mono text-amber-400 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
            <span>{streamingThought}</span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};
