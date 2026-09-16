import React from 'react';
import type { ToolDefinition } from '../types';
import { Terminal, Wrench } from 'lucide-react';

interface DebugPanelProps {
  tools: ToolDefinition[];
  eventsLog: Array<{ time: string; event: string; data: any }>;
}

export const DebugPanel: React.FC<DebugPanelProps> = ({ tools, eventsLog }) => {
  return (
    <div className="flex flex-col h-full space-y-4 font-mono text-xs">
      <div>
        <div className="flex items-center gap-2 text-slate-300 font-sans font-semibold mb-2">
          <Wrench className="w-4 h-4 text-cyan-400" />
          <span>Registered Capabilities ({tools.length})</span>
        </div>
        <div className="grid grid-cols-1 gap-1.5 max-h-48 overflow-y-auto pr-1">
          {tools.map((t) => (
            <div
              key={t.name}
              className="p-2 rounded-lg bg-slate-950/70 border border-slate-800/80 flex items-center justify-between"
            >
              <div>
                <span className="font-bold text-cyan-300">{t.name}</span>
                <span className="text-[10px] text-slate-500 block truncate max-w-[180px]">
                  {t.description}
                </span>
              </div>
              <span
                className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                  t.permission_level === 'SAFE'
                    ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60'
                    : t.permission_level === 'CONFIRM'
                    ? 'bg-amber-950/80 text-amber-400 border border-amber-800/60'
                    : 'bg-red-950/80 text-red-400 border border-red-800/60'
                }`}
              >
                {t.permission_level}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col min-h-0">
        <div className="flex items-center gap-2 text-slate-300 font-sans font-semibold mb-2">
          <Terminal className="w-4 h-4 text-purple-400" />
          <span>Real-Time Event Stream</span>
        </div>
        <div className="flex-1 bg-black/60 rounded-xl border border-slate-800/80 p-2.5 overflow-y-auto space-y-1.5 text-[11px]">
          {eventsLog.length === 0 ? (
            <span className="text-slate-600 italic">No events recorded yet...</span>
          ) : (
            eventsLog.map((ev, i) => (
              <div key={i} className="text-slate-400 leading-tight">
                <span className="text-slate-600 mr-1.5">[{ev.time}]</span>
                <span className="text-cyan-400 font-semibold">{ev.event}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
