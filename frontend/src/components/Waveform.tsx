import React from 'react';
import type { AssistantState } from '../types';

interface WaveformProps {
  state: AssistantState;
  isActive: boolean;
}

export const Waveform: React.FC<WaveformProps> = ({ state, isActive }) => {
  const bars = Array.from({ length: 24 });

  const getBarHeight = (index: number) => {
    if (!isActive && state === 'IDLE') {
      return '4px';
    }
    // Dynamic organic heights
    const seed = (index % 5) + 1;
    if (state === 'LISTENING') return `${seed * 7 + 6}px`;
    if (state === 'SPEAKING') return `${seed * 9 + 8}px`;
    if (state === 'THINKING') return `${seed * 5 + 4}px`;
    if (state === 'EXECUTING') return `${seed * 6 + 5}px`;
    return '6px';
  };

  const getBarColor = () => {
    switch (state) {
      case 'LISTENING': return 'bg-emerald-400 shadow-emerald-500/50';
      case 'THINKING': return 'bg-amber-400 shadow-amber-500/50';
      case 'EXECUTING': return 'bg-purple-400 shadow-purple-500/50';
      case 'SPEAKING': return 'bg-cyan-400 shadow-cyan-500/50';
      case 'ERROR': return 'bg-red-400 shadow-red-500/50';
      default: return 'bg-slate-700 shadow-none';
    }
  };

  return (
    <div className="flex items-center justify-center gap-[3px] h-10 px-4 py-1">
      {bars.map((_, i) => (
        <div
          key={i}
          className={`w-[3px] rounded-full transition-all duration-200 shadow-sm ${getBarColor()}`}
          style={{
            height: getBarHeight(i),
            opacity: isActive || state !== 'IDLE' ? (0.6 + ((i % 4) * 0.1)) : 0.3
          }}
        />
      ))}
    </div>
  );
};
