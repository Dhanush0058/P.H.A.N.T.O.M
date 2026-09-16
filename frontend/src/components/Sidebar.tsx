import React, { useState } from 'react';
import { MemoryViewer } from './MemoryViewer';
import { DebugPanel } from './DebugPanel';
import type { ToolDefinition } from '../types';
import { MessageSquare, Database, Wrench, Settings as SettingsIcon, X } from 'lucide-react';

interface SidebarProps {
  conversations: Array<{ id: string; title: string; created_at: string }>;
  onSelectConversation: (id: string) => void;
  tools: ToolDefinition[];
  eventsLog: Array<{ time: string; event: string; data: any }>;
  onOpenSettings: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  onSelectConversation,
  tools,
  eventsLog,
  onOpenSettings,
  isOpen,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'history' | 'memory' | 'tools'>('history');

  if (!isOpen) return null;

  return (
    <aside className="w-80 h-full bg-slate-950/95 border-r border-slate-800/80 flex flex-col z-30 backdrop-blur-xl">
      {/* Tabs */}
      <div className="flex items-center justify-between p-3 border-b border-slate-800">
        <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('history')}
            className={`p-1.5 rounded-lg text-xs font-mono transition ${
              activeTab === 'history' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Chat History"
          >
            <MessageSquare className="w-4 h-4" />
          </button>
          <button
            onClick={() => setActiveTab('memory')}
            className={`p-1.5 rounded-lg text-xs font-mono transition ${
              activeTab === 'memory' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Memory Manager"
          >
            <Database className="w-4 h-4" />
          </button>
          <button
            onClick={() => setActiveTab('tools')}
            className={`p-1.5 rounded-lg text-xs font-mono transition ${
              activeTab === 'tools' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Registered Tools & Debug"
          >
            <Wrench className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={onOpenSettings}
            className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-cyan-400 transition"
            title="Settings"
          >
            <SettingsIcon className="w-4 h-4" />
          </button>
          <button onClick={onClose} className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 md:hidden">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'history' && (
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono mb-3">
              Past Conversations
            </h3>
            {conversations.length === 0 ? (
              <p className="text-xs text-slate-500 font-mono text-center py-6">No previous conversations.</p>
            ) : (
              conversations.map((c) => (
                <button
                  key={c.id}
                  onClick={() => onSelectConversation(c.id)}
                  className="w-full text-left p-2.5 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800/80 hover:border-cyan-500/40 transition group"
                >
                  <p className="text-xs font-medium text-slate-200 group-hover:text-cyan-300 truncate">
                    {c.title}
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono mt-0.5 block">
                    {new Date(c.created_at).toLocaleDateString()}
                  </span>
                </button>
              ))
            )}
          </div>
        )}

        {activeTab === 'memory' && <MemoryViewer />}

        {activeTab === 'tools' && <DebugPanel tools={tools} eventsLog={eventsLog} />}
      </div>
    </aside>
  );
};
