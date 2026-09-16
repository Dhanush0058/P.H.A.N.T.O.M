import React from 'react';
import { AlertOctagon, RotateCcw } from 'lucide-react';

interface EmergencyStopProps {
  isStopped: boolean;
  onTriggerStop: () => void;
  onResetStop: () => void;
}

export const EmergencyStop: React.FC<EmergencyStopProps> = ({ isStopped, onTriggerStop, onResetStop }) => {
  if (isStopped) {
    return (
      <div className="flex items-center gap-2 p-2 rounded-xl bg-red-950/80 border border-red-500 animate-pulse">
        <AlertOctagon className="w-5 h-5 text-red-400" />
        <span className="text-xs font-mono font-bold text-red-300">EMERGENCY STOP ACTIVE</span>
        <button
          onClick={onResetStop}
          className="ml-auto flex items-center gap-1 px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-semibold shadow transition"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>RESET</span>
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={onTriggerStop}
      title="Immediately abort active tool executions and freeze operations"
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-red-950/40 hover:bg-red-900/60 border border-red-700/60 text-red-400 hover:text-red-300 text-xs font-mono font-semibold transition shadow-sm active:scale-95"
    >
      <AlertOctagon className="w-4 h-4 text-red-500" />
      <span>EMERGENCY STOP</span>
    </button>
  );
};
