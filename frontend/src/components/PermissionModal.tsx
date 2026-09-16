import React from 'react';
import type { PermissionRequestEvent } from '../types';
import { ShieldAlert, AlertTriangle, Check, X, Terminal } from 'lucide-react';

interface PermissionModalProps {
  request: PermissionRequestEvent | null;
  onResolve: (requestId: string, approved: boolean) => void;
}

export const PermissionModal: React.FC<PermissionModalProps> = ({ request, onResolve }) => {
  if (!request) return null;

  const isDangerous = request.permission_level === 'DANGEROUS';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div
        className={`w-full max-w-lg rounded-2xl p-6 shadow-2xl border ${
          isDangerous
            ? 'bg-slate-950 border-red-500/70 shadow-red-500/20'
            : 'bg-slate-900 border-amber-500/50 shadow-amber-500/10'
        }`}
      >
        {/* Header */}
        <div className="flex items-center gap-3 mb-4 pb-3 border-b border-slate-800">
          <div
            className={`p-2.5 rounded-xl ${
              isDangerous ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
            }`}
          >
            {isDangerous ? <ShieldAlert className="w-6 h-6 animate-pulse" /> : <AlertTriangle className="w-6 h-6" />}
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <span>{isDangerous ? 'HIGH RISK ACTION REQUIRED' : 'PERMISSION CONFIRMATION'}</span>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold ${
                  isDangerous ? 'bg-red-500/30 text-red-300' : 'bg-amber-500/30 text-amber-300'
                }`}
              >
                {request.permission_level}
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              JARVIS is requesting authorization to execute an environment action.
            </p>
          </div>
        </div>

        {/* Action Details */}
        <div className="space-y-3 mb-6">
          <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80 font-mono text-xs">
            <div className="flex items-center gap-2 text-slate-400 mb-1.5 font-sans font-semibold">
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span>Target Tool: <strong className="text-cyan-300">{request.tool_name}</strong></span>
            </div>
            <p className="text-slate-300 mb-2 font-sans">{request.action_summary}</p>
            <div className="bg-black/50 p-2.5 rounded-lg border border-slate-800/60 overflow-x-auto text-[11px] text-emerald-400">
              <pre>{JSON.stringify(request.parameters, null, 2)}</pre>
            </div>
          </div>

          {isDangerous && (
            <p className="text-xs text-red-400 bg-red-950/30 border border-red-800/40 p-2.5 rounded-lg font-mono">
              ⚠️ Warning: This action is potentially destructive or modifies critical system state. Ensure you want to proceed.
            </p>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3">
          <button
            onClick={() => onResolve(request.request_id, false)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono text-xs font-semibold transition"
          >
            <X className="w-4 h-4" />
            <span>DENY</span>
          </button>
          <button
            onClick={() => onResolve(request.request_id, true)}
            className={`flex items-center gap-1.5 px-5 py-2 rounded-xl font-mono text-xs font-semibold text-white shadow-lg transition ${
              isDangerous
                ? 'bg-red-600 hover:bg-red-500 shadow-red-600/30'
                : 'bg-cyan-600 hover:bg-cyan-500 shadow-cyan-600/30'
            }`}
          >
            <Check className="w-4 h-4" />
            <span>{isDangerous ? 'CONFIRM EXECUTE' : 'ALLOW ACTION'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
