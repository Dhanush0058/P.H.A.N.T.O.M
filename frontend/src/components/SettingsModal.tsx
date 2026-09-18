import React, { useState, useEffect } from 'react';
import { getSettings, updateSettings } from '../services/api';
import { Settings, Save, X, Cpu, Key, Volume2, Shield, Network } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [provider, setProvider] = useState('mistral');
  const [mistralKey, setMistralKey] = useState('');
  const [mistralModel, setMistralModel] = useState('mistral-small-latest');
  const [omniUrl, setOmniUrl] = useState('http://localhost:20128/v1');
  const [omniModel, setOmniModel] = useState('auto');
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [ollamaModel, setOllamaModel] = useState('qwen2.5-coder:7b');
  const [model, setModel] = useState('gemini-2.0-flash');
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [anthropicKey, setAnthropicKey] = useState('');
  const [customUrl, setCustomUrl] = useState('');
  const [ttsVoice, setTtsVoice] = useState('en-US-ChristopherNeural');
  const [wakeWord, setWakeWord] = useState('hey jarvis');
  const [savedMsg, setSavedMsg] = useState('');

  useEffect(() => {
    if (isOpen) {
      getSettings().then((s) => {
        if (s.ai_provider) setProvider(s.ai_provider);
        if (s.ai_model) setModel(s.ai_model);
        if (s.mistral_model) setMistralModel(s.mistral_model);
        if (s.omniroute_base_url) setOmniUrl(s.omniroute_base_url);
        if (s.omniroute_model) setOmniModel(s.omniroute_model);
        if (s.ollama_base_url) setOllamaUrl(s.ollama_base_url);
        if (s.ollama_model) setOllamaModel(s.ollama_model);
        if (s.custom_llm_api_url) setCustomUrl(s.custom_llm_api_url);
        if (s.tts_voice) setTtsVoice(s.tts_voice);
        if (s.wake_word) setWakeWord(s.wake_word);
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, any> = {
      ai_provider: provider,
      ai_model: provider === 'mistral' ? mistralModel : model,
      mistral_model: mistralModel,
      omniroute_base_url: omniUrl,
      omniroute_model: omniModel,
      ollama_base_url: ollamaUrl,
      ollama_model: ollamaModel,
      tts_voice: ttsVoice,
      wake_word: wakeWord,
    };
    if (mistralKey) payload.mistral_api_key = mistralKey;
    if (geminiKey) payload.gemini_api_key = geminiKey;
    if (openaiKey) payload.openai_api_key = openaiKey;
    if (anthropicKey) payload.anthropic_api_key = anthropicKey;
    if (customUrl) payload.custom_llm_api_url = customUrl;

    await updateSettings(payload);
    setSavedMsg('Settings saved and applied!');
    setTimeout(() => setSavedMsg(''), 3000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 font-sans">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <Settings className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold text-slate-100">JARVIS Configuration</h2>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-4 py-4 max-h-[70vh] overflow-y-auto pr-2 text-xs">
          {savedMsg && (
            <div className="p-2.5 rounded-xl bg-emerald-950/60 border border-emerald-500 text-emerald-300 font-mono">
              ✓ {savedMsg}
            </div>
          )}

          {/* AI Provider */}
          <div className="space-y-1.5">
            <label className="flex items-center gap-1.5 text-slate-300 font-semibold">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" /> Primary AI Provider
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 font-mono focus:border-cyan-500"
            >
              <option value="mistral">🌪️ Mistral AI Cloud (Zero Local RAM • Ultra-Fast • SOTA Reasoning)</option>
              <option value="ollama">💻 Ollama (Local Infinite Tokens • Offline • Zero Rate Limits)</option>
              <option value="omniroute">🚀 OmniRoute (~1.51B Free Tokens Pool / 352 Providers Gateway)</option>
              <option value="gemini">Google Gemini (Gemini 2.0 Flash / Pro)</option>
              <option value="openai">OpenAI (GPT-4o / o3-mini)</option>
              <option value="anthropic">Anthropic Claude (Claude 3.5 Sonnet)</option>
              <option value="custom">Custom Multi-Model Repo</option>
              <option value="mock">Mock Offline Provider (Zero Keys)</option>
            </select>
          </div>

          {/* Mistral AI Cloud Controls */}
          {provider === 'mistral' && (
            <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-800/40 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-amber-300 flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-amber-400" /> Mistral Cloud Configuration
                </span>
                <a
                  href="https://console.mistral.ai"
                  target="_blank"
                  rel="noreferrer"
                  className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-mono hover:bg-amber-500/30 underline"
                >
                  Get Free Key at console.mistral.ai ↗
                </a>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-400 flex items-center gap-1">
                    <Key className="w-3 h-3 text-amber-400" /> Mistral API Key
                  </label>
                  <input
                    type="password"
                    placeholder="Enter your Mistral API Key..."
                    value={mistralKey}
                    onChange={(e) => setMistralKey(e.target.value)}
                    className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono focus:border-amber-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-slate-400 block mb-1">Mistral Model</label>
                  <input
                    type="text"
                    value={mistralModel}
                    onChange={(e) => setMistralModel(e.target.value)}
                    className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono focus:border-amber-500"
                    placeholder="mistral-small-latest"
                  />
                </div>
              </div>
              <div className="flex flex-wrap gap-1.5 pt-1">
                <span className="text-slate-500 text-[10px] py-1">Recommended Models:</span>
                {['mistral-small-latest', 'codestral-latest', 'mistral-large-latest', 'ministral-8b-latest', 'open-mistral-nemo'].map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setMistralModel(m)}
                    className={`px-2 py-0.5 rounded-md font-mono text-[10px] border transition-colors ${
                      mistralModel === m
                        ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                        : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Ollama Local LLM Controls */}
          {provider === 'ollama' && (
            <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-800/40 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-emerald-300 flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-emerald-400" /> Ollama Local LLM Configuration
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono">
                  100% Free • Infinite Tokens • Offline
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Ollama Server Endpoint</label>
                  <input
                    type="text"
                    value={ollamaUrl}
                    onChange={(e) => setOllamaUrl(e.target.value)}
                    className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono"
                    placeholder="http://localhost:11434"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Local Model Name</label>
                  <input
                    type="text"
                    value={ollamaModel}
                    onChange={(e) => setOllamaModel(e.target.value)}
                    className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono"
                    placeholder="qwen2.5-coder:7b"
                  />
                </div>
              </div>
              <div className="flex flex-wrap gap-1.5 pt-1">
                <span className="text-slate-500 text-[10px] py-1">Quick Select:</span>
                {['qwen2.5-coder:7b', 'llama3.2:3b', 'mistral:latest', 'deepseek-r1:8b'].map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setOllamaModel(m)}
                    className={`px-2 py-0.5 rounded-md font-mono text-[10px] border transition-colors ${
                      ollamaModel === m
                        ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300'
                        : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* OmniRoute Specific Controls */}
          {provider === 'omniroute' && (
            <div className="p-3.5 rounded-xl bg-cyan-950/20 border border-cyan-800/40 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-cyan-300 flex items-center gap-1.5">
                  <Network className="w-4 h-4 text-cyan-400" /> OmniRoute Gateway Configuration
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono">
                  ~1.51B Tokens / Mo
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">OmniRoute Gateway URL</label>
                  <input
                    type="text"
                    value={omniUrl}
                    onChange={(e) => setOmniUrl(e.target.value)}
                    className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono"
                    placeholder="http://localhost:20128/v1"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Routing Combo Model</label>
                  <select
                    value={omniModel}
                    onChange={(e) => setOmniModel(e.target.value)}
                    className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono"
                  >
                    <option value="auto">auto (Balanced Auto-Combo)</option>
                    <option value="auto/coding">auto/coding (Code Quality First)</option>
                    <option value="auto/fast">auto/fast (Lowest Latency First)</option>
                    <option value="auto/cheap">auto/cheap (Cheapest / Free First)</option>
                    <option value="auto/smart">auto/smart (Quality + 10% Exploration)</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* API Keys */}
          {provider !== 'omniroute' && provider !== 'ollama' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-slate-400 flex items-center gap-1">
                  <Key className="w-3 h-3 text-yellow-400" /> Gemini API Key
                </label>
                <input
                  type="password"
                  placeholder="AIzaSy..."
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  className="w-full p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="text-slate-400 flex items-center gap-1">
                  <Key className="w-3 h-3 text-yellow-400" /> OpenAI / Ollama Key
                </label>
                <input
                  type="password"
                  placeholder="sk-..."
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  className="w-full p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 font-mono"
                />
              </div>
            </div>
          )}

          {provider === 'anthropic' && (
            <div className="space-y-1">
              <label className="text-slate-400 flex items-center gap-1">
                <Key className="w-3 h-3 text-yellow-400" /> Anthropic API Key
              </label>
              <input
                type="password"
                placeholder="sk-ant-..."
                value={anthropicKey}
                onChange={(e) => setAnthropicKey(e.target.value)}
                className="w-full p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 font-mono"
              />
            </div>
          )}

          {provider === 'custom' && (
            <div className="space-y-1">
              <label className="text-slate-400 flex items-center gap-1">
                <Cpu className="w-3 h-3 text-purple-400" /> Custom LLM Repository API URL
              </label>
              <input
                type="text"
                placeholder="http://localhost:8080/v1"
                value={customUrl}
                onChange={(e) => setCustomUrl(e.target.value)}
                className="w-full p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 font-mono"
              />
            </div>
          )}

          {/* Voice & Wake word */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 border-t border-slate-800/80">
            <div className="space-y-1">
              <label className="text-slate-400 flex items-center gap-1">
                <Volume2 className="w-3 h-3 text-cyan-400" /> Neural TTS Voice
              </label>
              <select
                value={ttsVoice}
                onChange={(e) => setTtsVoice(e.target.value)}
                className="w-full p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 font-mono"
              >
                <option value="en-US-ChristopherNeural">Christopher (Natural English Male)</option>
                <option value="en-US-GuyNeural">Guy (Professional Male)</option>
                <option value="en-US-JennyNeural">Jenny (Natural Female)</option>
                <option value="en-GB-RyanNeural">Ryan (British Male - Jarvis Style)</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-slate-400 flex items-center gap-1">
                <Shield className="w-3 h-3 text-cyan-400" /> Wake Word Trigger
              </label>
              <input
                type="text"
                value={wakeWord}
                onChange={(e) => setWakeWord(e.target.value)}
                className="w-full p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 font-mono"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700"
            >
              Close
            </button>
            <button
              type="submit"
              className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold shadow-lg shadow-cyan-600/30"
            >
              <Save className="w-4 h-4" />
              <span>Save Changes</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
