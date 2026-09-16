import React from 'react';
import type { AssistantState } from '../types';

interface StateIndicatorProps {
  state: AssistantState;
  subText?: string;
}

export const StateIndicator: React.FC<StateIndicatorProps> = ({ state, subText }) => {
  const getBadge = () => {
    switch (state) {
      case 'LISTENING':
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
          dot: 'bg-emerald-400 animate-ping'
        };
      case 'THINKING':
        return {
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
          dot: 'bg-amber-400 animate-pulse'
        };
      case 'EXECUTING':
        return {
          bg: 'bg-purple-500/10 border-purple-500/30 text-purple-400',
          dot: 'bg-purple-400 animate-ping'
        };
      case 'SPEAKING':
        return {
          bg: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400',
          dot: 'bg-cyan-400 animate-pulse'
        };
      case 'ERROR':
        return {
          bg: 'bg-red-500/10 border-red-500/30 text-red-400',
          dot: 'bg-red-500'
        };
      case 'IDLE':
      default:
        return {
          bg: 'bg-slate-800/40 border-slate-700/50 text-slate-400',
          dot: 'bg-cyan-500'
        };
    }
  };

  const badge = getBadge();

  return (
    <div className="flex flex-col items-center gap-1.5 select-none">
      <div className={`flex items-center gap-2 px-3.5 py-1 rounded-full border text-xs font-mono tracking-widest uppercase font-semibold ${badge.bg}`}>
        <span className={`w-2 h-2 rounded-full ${badge.dot}`} />
        <span>{state}</span>
      </div>
      {subText && (
        <span className="text-[11px] font-mono text-slate-400 animate-pulse tracking-wide">
          {subText}
        </span>
      )}
    </div>
  );
};
