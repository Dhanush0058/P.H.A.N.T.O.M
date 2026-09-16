import React, { useState, useEffect } from 'react';
import type { MemoryItem } from '../types';
import { getMemories, createMemory, deleteMemory } from '../services/api';
import { Database, Plus, Trash2, Search } from 'lucide-react';

export const MemoryViewer: React.FC = () => {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [query, setQuery] = useState('');
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [newType, setNewType] = useState('preference');
  const [isAdding, setIsAdding] = useState(false);

  const fetchMemories = async () => {
    try {
      const data = await getMemories(query);
      setMemories(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, [query]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKey || !newValue) return;
    await createMemory(newKey, newValue, newType);
    setNewKey('');
    setNewValue('');
    setIsAdding(false);
    fetchMemories();
  };

  const handleDelete = async (key: string) => {
    await deleteMemory(key);
    fetchMemories();
  };

  return (
    <div className="flex flex-col h-full space-y-3 font-sans">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
          <Database className="w-4 h-4 text-cyan-400" />
          <span>Long-Term Memory</span>
        </div>
        <button
          onClick={() => setIsAdding(!isAdding)}
          className="p-1 rounded-lg bg-cyan-950/60 border border-cyan-800 text-cyan-400 hover:bg-cyan-900/60 text-xs flex items-center gap-1 px-2"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add</span>
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-500" />
        <input
          type="text"
          placeholder="Search memories..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
        />
      </div>

      {/* Add New Memory Form */}
      {isAdding && (
        <form onSubmit={handleAdd} className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 space-y-2 text-xs">
          <input
            type="text"
            placeholder="Key (e.g. main_project)"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
            className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-slate-200"
          />
          <input
            type="text"
            placeholder="Value (e.g. SnapClass)"
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
            className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-slate-200"
          />
          <select
            value={newType}
            onChange={(e) => setNewType(e.target.value)}
            className="w-full px-2 py-1 rounded bg-slate-900 border border-slate-700 text-slate-300"
          >
            <option value="preference">Preference</option>
            <option value="fact">Fact</option>
            <option value="goal">Goal</option>
          </select>
          <div className="flex justify-end gap-2 pt-1">
            <button
              type="button"
              onClick={() => setIsAdding(false)}
              className="px-2.5 py-1 rounded bg-slate-800 text-slate-400"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-3 py-1 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-semibold"
            >
              Save
            </button>
          </div>
        </form>
      )}

      {/* Memory List */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {memories.length === 0 ? (
          <p className="text-xs text-slate-500 font-mono text-center py-6">No long-term memories found.</p>
        ) : (
          memories.map((m) => (
            <div
              key={m.id || m.key}
              className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 flex items-start justify-between gap-2 group text-xs"
            >
              <div>
                <div className="flex items-center gap-1.5 font-mono">
                  <span className="font-bold text-cyan-300">{m.key}</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 uppercase">
                    {m.type}
                  </span>
                </div>
                <p className="text-slate-300 mt-1">{m.value}</p>
              </div>
              <button
                onClick={() => handleDelete(m.key)}
                className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition p-1"
                title="Forget this memory"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
