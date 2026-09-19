import React from 'react';
import type { AssistantState } from '../types';

interface CoreOrbProps {
  state: AssistantState;
  isAudioActive?: boolean;
}

export const CoreOrb: React.FC<CoreOrbProps> = ({ state }) => {
  const getStateColors = () => {
    switch (state) {
      case 'LISTENING':
        return {
          glow: 'rgba(16, 185, 129, 0.4)',
          border: 'border-emerald-400',
          ring: 'border-emerald-500/50',
          core: 'from-emerald-400 via-teal-500 to-cyan-600',
          text: 'text-emerald-400',
          pulse: 'animate-ping-slow'
        };
      case 'THINKING':
        return {
          glow: 'rgba(245, 158, 11, 0.4)',
          border: 'border-amber-400',
          ring: 'border-amber-500/50',
          core: 'from-amber-400 via-orange-500 to-yellow-600',
          text: 'text-amber-400',
          pulse: 'animate-pulse'
        };
      case 'EXECUTING':
        return {
          glow: 'rgba(168, 85, 247, 0.4)',
          border: 'border-purple-400',
          ring: 'border-purple-500/50',
          core: 'from-purple-400 via-indigo-500 to-cyan-500',
          text: 'text-purple-400',
          pulse: 'animate-spin-slow'
        };
      case 'SPEAKING':
        return {
          glow: 'rgba(0, 240, 255, 0.5)',
          border: 'border-cyan-400',
          ring: 'border-cyan-500/60',
          core: 'from-cyan-300 via-blue-500 to-indigo-600',
          text: 'text-cyan-400',
          pulse: 'animate-pulse-glow'
        };
      case 'ERROR':
        return {
          glow: 'rgba(239, 68, 68, 0.5)',
          border: 'border-red-500',
          ring: 'border-red-500/50',
          core: 'from-red-500 via-rose-600 to-red-800',
          text: 'text-red-400',
          pulse: 'animate-pulse'
        };
      case 'IDLE':
      default:
        return {
          glow: 'rgba(0, 240, 255, 0.25)',
          border: 'border-cyan-500/60',
          ring: 'border-cyan-500/30',
          core: 'from-cyan-500 via-blue-600 to-slate-900',
          text: 'text-cyan-400',
          pulse: 'animate-pulse-glow'
        };
    }
  };

  const style = getStateColors();

  return (
    <div className="relative flex items-center justify-center w-48 h-48 my-2 select-none">
      {/* Outer Holographic Radar Ring */}
      <div
        className={`absolute inset-0 rounded-full border border-dashed ${style.ring} animate-spin-slow opacity-60`}
      />

      {/* Counter Rotating Ring */}
      <div
        className={`absolute inset-2 rounded-full border ${style.border} border-t-transparent border-b-transparent animate-spin-reverse opacity-70`}
      />

      {/* State Pulse Ring */}
      <div
        className={`absolute inset-6 rounded-full border ${style.ring} ${style.pulse}`}
        style={{ boxShadow: `0 0 30px ${style.glow}` }}
      />

      {/* Center Spherical Glowing Core */}
      <div
        className={`relative flex flex-col items-center justify-center w-28 h-28 rounded-full bg-gradient-to-tr ${style.core} shadow-2xl transition-all duration-700 backdrop-blur-md`}
        style={{
          boxShadow: `0 0 40px ${style.glow}, inset 0 0 20px rgba(255,255,255,0.4)`
        }}
      >
        {/* Core HUD Branding */}
        <span className="text-[10px] font-mono tracking-[0.25em] font-black text-white/90 drop-shadow-md">
          PHANTOM
        </span>
        <span className={`text-[8px] font-mono font-semibold tracking-widest ${style.text} opacity-90`}>
          CORE
        </span>
      </div>
    </div>
  );
};
