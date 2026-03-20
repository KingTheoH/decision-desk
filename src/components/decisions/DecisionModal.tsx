import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { decisions } from "../../lib/api";
import type { DecisionItem, DecisionType } from "../../lib/types";

interface Props {
  onClose: () => void;
  onSaved: (item: DecisionItem) => void;
  existing?: DecisionItem;
}

const TYPES: DecisionType[] = ["Property", "BusinessIdea", "Investment", "ContentIdea", "Other"];
const STATUSES = ["Inbox", "New", "Researching", "Waiting", "Ready", "Approved", "Rejected", "Deferred"];
const PRIORITIES = ["Low", "Medium", "High", "TopQueue"];

export default function DecisionModal({ onClose, onSaved, existing }: Props) {
  const [form, setForm] = useState({
    title: existing?.title || "",
    type: existing?.type || "Property" as DecisionType,
    status: existing?.status || "Inbox",
    priority: existing?.priority || "Medium",
    summary: existing?.summary || "",
    thesis: existing?.thesis || "",
    capital_required: existing?.capital_required?.toString() || "",
    expected_return: existing?.expected_return?.toString() || "",
    time_to_cashflow: existing?.time_to_cashflow || "",
    operational_complexity: existing?.operational_complexity || "",
    downside_risk: existing?.downside_risk || "",
    next_action: existing?.next_action || "",
    tags: (() => { try { return JSON.parse(existing?.tags || "[]").join(", "); } catch { return ""; } })(),
  });
  const [saving, setSaving] = useState(false);

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  async function save() {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      const payload = {
        ...form,
        capital_required: form.capital_required ? parseFloat(form.capital_required) : undefined,
        expected_return: form.expected_return ? parseFloat(form.expected_return) : undefined,
        tags: JSON.stringify(form.tags.split(",").map((t: string) => t.trim()).filter((t: string) => t.trim().length > 0)),
      };
      const item = existing
        ? await decisions.update(existing.id, payload)
        : await decisions.create(payload as any);
      onSaved(item);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-surface-1 border border-border rounded-xl w-full max-w-xl shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <h2 className="text-sm font-semibold text-zinc-100">
            {existing ? "Edit Decision" : "New Decision"}
          </h2>
          <button onClick={onClose} className="btn btn-ghost p-1">
            <X size={15} />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* Title */}
          <div>
            <label className="label">Title *</label>
            <input className="input" value={form.title} onChange={e => set("title", e.target.value)}
              placeholder="e.g. Osaka 1K Apartment — Namba Area" autoFocus />
          </div>

          {/* Type + Status + Priority */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="label">Type</label>
              <select className="input" value={form.type} onChange={e => set("type", e.target.value)}>
                {TYPES.map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Status</label>
              <select className="input" value={form.status} onChange={e => set("status", e.target.value)}>
                {STATUSES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Priority</label>
              <select className="input" value={form.priority} onChange={e => set("priority", e.target.value)}>
                {PRIORITIES.map(p => <option key={p}>{p}</option>)}
              </select>
            </div>
          </div>

          {/* Summary */}
          <div>
            <label className="label">Summary</label>
            <textarea className="textarea" rows={2} value={form.summary}
              onChange={e => set("summary", e.target.value)}
              placeholder="One paragraph overview" />
          </div>

          {/* Thesis */}
          <div>
            <label className="label">Thesis</label>
            <textarea className="textarea" rows={2} value={form.thesis}
              onChange={e => set("thesis", e.target.value)}
              placeholder="Why this opportunity is worth pursuing" />
          </div>

          {/* Economics */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Capital Required ($)</label>
              <input className="input" type="number" value={form.capital_required}
                onChange={e => set("capital_required", e.target.value)} placeholder="e.g. 75000" />
            </div>
            <div>
              <label className="label">Expected Return (%)</label>
              <input className="input" type="number" value={form.expected_return}
                onChange={e => set("expected_return", e.target.value)} placeholder="e.g. 6.5" />
            </div>
            <div>
              <label className="label">Time to Cash Flow</label>
              <input className="input" value={form.time_to_cashflow}
                onChange={e => set("time_to_cashflow", e.target.value)} placeholder="e.g. 3 months" />
            </div>
            <div>
              <label className="label">Operational Complexity</label>
              <select className="input" value={form.operational_complexity}
                onChange={e => set("operational_complexity", e.target.value)}>
                <option value="">—</option>
                <option>Low</option><option>Medium</option><option>High</option>
              </select>
            </div>
          </div>

          {/* Downside + Next Action */}
          <div>
            <label className="label">Downside Risk</label>
            <input className="input" value={form.downside_risk}
              onChange={e => set("downside_risk", e.target.value)}
              placeholder="Worst case scenario" />
          </div>
          <div>
            <label className="label">Next Action</label>
            <input className="input" value={form.next_action}
              onChange={e => set("next_action", e.target.value)}
              placeholder="One concrete next step" />
          </div>

          {/* Tags */}
          <div>
            <label className="label">Tags (comma-separated)</label>
            <input className="input" value={form.tags}
              onChange={e => set("tags", e.target.value)}
              placeholder="e.g. Japan, STR, Osaka" />
          </div>
        </div>

        <div className="flex justify-end gap-2 px-5 py-4 border-t border-border">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={save} disabled={saving || !form.title.trim()}>
            {saving ? "Saving…" : (existing ? "Save Changes" : "Create Decision")}
          </button>
        </div>
      </div>
    </div>
  );
}
