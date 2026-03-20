import { useEffect, useState } from "react";
import { Plus, Trash2, ChevronDown, ChevronUp } from "lucide-react";
import { rubrics as rubricsApi } from "../lib/api";
import type { Rubric } from "../lib/types";

export default function Rubrics() {
  const [items, setItems] = useState<Rubric[]>([]);
  const [open, setOpen] = useState<string | null>(null);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");

  useEffect(() => { rubricsApi.list().then(setItems); }, []);

  async function create() {
    if (!newName.trim()) return;
    const r = await rubricsApi.create({ name: newName, description: newDesc });
    setItems(p => [r, ...p]);
    setNewName(""); setNewDesc("");
  }

  async function del(id: string) {
    if (!confirm("Delete rubric?")) return;
    await rubricsApi.delete(id);
    setItems(p => p.filter(r => r.id !== id));
  }

  const totalWeight = (r: Rubric) => r.factors.reduce((s, f) => s + f.weight, 0);

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-5">
      <h1 className="text-lg font-semibold text-zinc-100">Rubrics</h1>

      {/* Create */}
      <div className="card p-4 space-y-3">
        <div className="section-title">New Rubric</div>
        <input className="input" placeholder="Rubric name" value={newName} onChange={e => setNewName(e.target.value)} />
        <textarea className="textarea" rows={2} placeholder="Description" value={newDesc} onChange={e => setNewDesc(e.target.value)} />
        <button className="btn btn-primary text-xs" onClick={create} disabled={!newName.trim()}>
          <Plus size={11} /> Create Rubric
        </button>
      </div>

      {/* List */}
      {items.map(r => (
        <div key={r.id} className="card overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-surface-2"
            onClick={() => setOpen(o => o === r.id ? null : r.id)}>
            <div>
              <div className="text-sm font-medium text-zinc-200 flex items-center gap-2">
                {r.name}
                {r.is_default && <span className="text-[10px] text-violet-400 border border-violet-800 px-1.5 rounded">default</span>}
              </div>
              <div className="text-xs text-zinc-600 mt-0.5">
                {r.factors.length} factors · {totalWeight(r).toFixed(0)}% total weight
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button className="btn btn-danger p-1" onClick={e => { e.stopPropagation(); del(r.id); }}>
                <Trash2 size={11} />
              </button>
              {open === r.id ? <ChevronUp size={13} className="text-zinc-600" /> : <ChevronDown size={13} className="text-zinc-600" />}
            </div>
          </div>

          {open === r.id && (
            <div className="border-t border-border p-4 space-y-2">
              {r.description && <p className="text-xs text-zinc-500 mb-3">{r.description}</p>}
              {r.factors.map(f => (
                <div key={f.id} className="flex items-center gap-3">
                  <div className="flex-1 text-xs text-zinc-400">{f.name}</div>
                  <div className="text-xs font-mono text-violet-400 w-12 text-right">{f.weight}%</div>
                  <div className="w-24 h-1 bg-surface-3 rounded-full overflow-hidden">
                    <div className="h-full bg-violet-500/50 rounded-full" style={{ width: `${f.weight}%` }} />
                  </div>
                  {f.description && <div className="text-[10px] text-zinc-600 w-40 truncate">{f.description}</div>}
                </div>
              ))}
              {totalWeight(r) !== 100 && (
                <p className="text-xs text-amber-500 mt-2">⚠ Weights sum to {totalWeight(r).toFixed(0)}% (should be 100%)</p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
