import { useState, useEffect } from "react";
import { health } from "../lib/api";

export default function Settings() {
  const [ollamaStatus, setOllamaStatus] = useState<any>(null);
  const [ollamaUrl, setOllamaUrl] = useState("http://localhost:11434");
  const [model, setModel] = useState("llama3.2");

  useEffect(() => {
    health.check().then(d => setOllamaStatus(d?.ollama)).catch(() => setOllamaStatus({ available: false }));
  }, []);

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <h1 className="text-lg font-semibold text-zinc-100">Settings</h1>

      {/* AI / Ollama */}
      <div className="card p-5 space-y-4">
        <div className="section-title">AI — Ollama</div>

        <div className={`flex items-center gap-2 p-3 rounded-md text-sm ${
          ollamaStatus?.available
            ? "bg-emerald-900/20 border border-emerald-900/40 text-emerald-400"
            : "bg-red-900/20 border border-red-900/40 text-red-400"
        }`}>
          <span className={`w-2 h-2 rounded-full ${ollamaStatus?.available ? "bg-emerald-500" : "bg-red-500"}`} />
          {ollamaStatus?.available ? "Ollama is running" : "Ollama is offline"}
          {ollamaStatus?.models?.length > 0 && (
            <span className="ml-auto text-xs opacity-70">
              Models: {ollamaStatus.models.join(", ")}
            </span>
          )}
        </div>

        {!ollamaStatus?.available && (
          <div className="text-xs text-zinc-500 space-y-1.5 bg-surface-2 p-3 rounded-md font-mono">
            <div className="text-zinc-400 font-sans font-medium mb-2">Setup Instructions:</div>
            <div>1. Download Ollama: <a href="https://ollama.com/download" className="text-violet-400 underline" target="_blank">ollama.com/download</a></div>
            <div>2. Install and run Ollama</div>
            <div>3. Pull a model: <code className="text-amber-400">ollama pull llama3.2</code></div>
            <div>4. Ollama will auto-connect on next app restart</div>
          </div>
        )}

        <div>
          <label className="label">Ollama Endpoint</label>
          <input className="input font-mono text-xs" value={ollamaUrl} onChange={e => setOllamaUrl(e.target.value)} />
          <p className="text-[11px] text-zinc-600 mt-1">Default: http://localhost:11434 — set OLLAMA_BASE_URL env var to override</p>
        </div>

        <div>
          <label className="label">Model</label>
          <input className="input font-mono text-xs" value={model} onChange={e => setModel(e.target.value)} placeholder="e.g. llama3.2, mistral, qwen2.5" />
          <p className="text-[11px] text-zinc-600 mt-1">Set OLLAMA_MODEL env var to make permanent</p>
        </div>
      </div>

      {/* App info */}
      <div className="card p-5 space-y-3">
        <div className="section-title">About</div>
        <div className="text-sm text-zinc-500 space-y-1">
          <div>Decision Desk v1.0.0</div>
          <div className="text-zinc-600">Local-first personal decision command center</div>
          <div className="text-zinc-700 text-xs font-mono">FastAPI backend · React/Vite frontend · Tauri shell · SQLite</div>
        </div>
        <div className="text-xs text-zinc-600 pt-1">
          Data stored at: <code className="text-zinc-500 font-mono">decision-desk/data/decision_desk.db</code>
        </div>
      </div>

      {/* Keyboard shortcuts */}
      <div className="card p-5 space-y-3">
        <div className="section-title">Keyboard Shortcuts</div>
        <div className="space-y-1.5 text-xs text-zinc-500">
          {[
            ["N", "New decision"],
            ["⌘K", "Command palette (coming soon)"],
            ["⌘,", "Settings"],
          ].map(([k, v]) => (
            <div key={k} className="flex items-center gap-3">
              <kbd className="px-1.5 py-0.5 rounded bg-surface-3 border border-border font-mono text-zinc-400">{k}</kbd>
              <span>{v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
