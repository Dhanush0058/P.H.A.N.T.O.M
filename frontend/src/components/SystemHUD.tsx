import React from 'react';
import type { SystemMetrics } from '../types';
import { Cpu, HardDrive, Activity, Wifi } from 'lucide-react';

interface SystemHUDProps {
  metrics: SystemMetrics | null;
}

export const SystemHUD: React.FC<SystemHUDProps> = ({ metrics }) => {
  if (!metrics) {
    return (
      <div className="flex items-center justify-between p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl text-xs font-mono text-slate-500">
        <span>CONNECTING TELEMETRY...</span>
      </div>
    );
  }

  const getGaugeColor = (pct: number) => {
    if (pct > 85) return 'text-red-400 bg-red-500';
    if (pct > 65) return 'text-amber-400 bg-amber-500';
    return 'text-cyan-400 bg-cyan-500';
  };

  const cpuColor = getGaugeColor(metrics.cpu.usage_percent);
  const memColor = getGaugeColor(metrics.memory.percent);
  const diskColor = getGaugeColor(metrics.disk.percent);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
      {/* CPU Metric */}
      <div className="bg-slate-900/60 border border-slate-800/80 p-2.5 rounded-xl backdrop-blur-sm">
        <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
          <span className="flex items-center gap-1.5 font-semibold">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" /> CPU
          </span>
          <span className={cpuColor.split(' ')[0]}>{metrics.cpu.usage_percent}%</span>
        </div>
        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${cpuColor.split(' ')[1]}`}
            style={{ width: `${Math.min(100, metrics.cpu.usage_percent)}%` }}
          />
        </div>
        <span className="text-[10px] font-mono text-slate-500 mt-1 block">
          {metrics.cpu.cores} Cores @ {metrics.cpu.freq_mhz} MHz
        </span>
      </div>

      {/* RAM Metric */}
      <div className="bg-slate-900/60 border border-slate-800/80 p-2.5 rounded-xl backdrop-blur-sm">
        <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
          <span className="flex items-center gap-1.5 font-semibold">
            <Activity className="w-3.5 h-3.5 text-purple-400" /> RAM
          </span>
          <span className={memColor.split(' ')[0]}>{metrics.memory.percent}%</span>
        </div>
        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${memColor.split(' ')[1]}`}
            style={{ width: `${Math.min(100, metrics.memory.percent)}%` }}
          />
        </div>
        <span className="text-[10px] font-mono text-slate-500 mt-1 block">
          {metrics.memory.used_gb} / {metrics.memory.total_gb} GB
        </span>
      </div>

      {/* Disk Metric */}
      <div className="bg-slate-900/60 border border-slate-800/80 p-2.5 rounded-xl backdrop-blur-sm">
        <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
          <span className="flex items-center gap-1.5 font-semibold">
            <HardDrive className="w-3.5 h-3.5 text-emerald-400" /> DISK (C:)
          </span>
          <span className={diskColor.split(' ')[0]}>{metrics.disk.percent}%</span>
        </div>
        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${diskColor.split(' ')[1]}`}
            style={{ width: `${Math.min(100, metrics.disk.percent)}%` }}
          />
        </div>
        <span className="text-[10px] font-mono text-slate-500 mt-1 block">
          {metrics.disk.used_gb} / {metrics.disk.total_gb} GB
        </span>
      </div>

      {/* Network / Battery Metric */}
      <div className="bg-slate-900/60 border border-slate-800/80 p-2.5 rounded-xl backdrop-blur-sm">
        <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
          <span className="flex items-center gap-1.5 font-semibold">
            <Wifi className="w-3.5 h-3.5 text-blue-400" /> NET
          </span>
          <span className="text-blue-400">ONLINE</span>
        </div>
        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mt-2">
          <span>↑ {metrics.network.bytes_sent_mb} MB</span>
          <span>↓ {metrics.network.bytes_recv_mb} MB</span>
        </div>
      </div>
    </div>
  );
};
