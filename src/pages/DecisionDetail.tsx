import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Edit, Trash2, Plus } from "lucide-react";
import { decisions, scoring, rubrics } from "../lib/api";
import type { DecisionItem, Rubric } from "../lib/types";
import TypeBadge from "../components/ui/TypeBadge";
import StatusBadge from "../components/ui/StatusBadge";
import PriorityBadge from "../components/ui/PriorityBadge";
import ScoreBreakdown from "../components/scoring/ScoreBreakdown";
import SkillRunner from "../components/ai/SkillRunner";
import SkillResultCard from "../components/ai/SkillResultCard";
import DecisionModal from "../components/decisions/DecisionModal";

const STATUSES = ["Inbox", "New", "Researching", "Waiting", "Ready", "Approved", "Rejected", "Deferred", "Archived"];

export default function DecisionDetail() {
  const { id } = useParams<{ id: string }>();
  const nav = useNavigate();
  const [item, setItem] = useState<DecisionItem | null>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [rationale, setRationale] = useState("");
  const [newStatus, setNewStatus] = useState("");

  useEffect(() => {
    if (id) decisions.get(id).then(setItem);
  }, [id]);

  if (!item) return <div className="p-8 text-zinc-600">Loading…</div>;

  async function changeStatus() {
    if (!newStatus || !id) return;
    const updated = await decisions.updateStatus(id, newStatus, rationale || undefined);
    setItem(updated);
    setNewStatus("");
    setRationale("");
  }

  async function addNote() {
    if (!noteText.trim() || !id) return;
    await decisions.addNote(id, noteText);
    const updated = await decisions.get(id);
    setItem(updated);
    setNoteText("");
  }

  async function deleteItem() {
    if (!id) return;
    if (!confirm("Delete this decision?")) return;
    await decisions.delete(id);
    nav("/decisions");
  }

  const tags: string[] = (() => { try { return JSON.parse(item.tags || "[]"); } catch { return []; } })();
  const latestScore = item.scores.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <button className="btn btn-ghost p-1.5 mt-0.5" onClick={() => nav(-1)}>
            <ArrowLeft size={14} />
          </button>
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <TypeBadge type={item.type} />
              <StatusBadge status={item.status} />
              <PriorityBadge priority={item.priority} />
            </div>
            <h1 className="text-xl font-semibold text-zinc-100">{item.title}</h1>
            {item.summary && <p className="text-sm text-zinc-500 mt-1 max-w-2xl">{item.summary}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button className="btn btn-secondary" onClick={() => setEditOpen(true)}><Edit size={13} /> Edit</button>
          <button className="btn btn-danger" onClick={deleteItem}><Trash2 size={13} /></button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: main data */}
        <div className="lg:col-span-2 space-y-5">
          {/* Core fields */}
          <div className="card p-4 grid grid-cols-2 gap-4 text-sm">
            {[
              ["Capital Required", item.capital_required != null ? `$${item.capital_required.toLocaleString()}` : "—"],
              ["Expected Return", item.expected_return != null ? `${item.expected_return}%` : "—"],
              ["Time to Cash Flow", item.time_to_cashflow || "—"],
              ["Operational Complexity", item.operational_complexity || "—"],
              ["Downside Risk", item.downside_risk || "—"],
              ["Liquidity / Exit", item.liquidity_exit_ease || "—"],
            ].map(([k, v]) => (
              <div key={k}>
                <div className="section-title mb-0.5">{k}</div>
                <div className="text-zinc-300">{v}</div>
              </div>
            ))}
          </div>

          {/* Thesis */}
          {item.thesis && (
            <div className="card p-4">
              <div className="section-title mb-2">Thesis</div>
              <p className="text-sm text-zinc-300 leading-relaxed">{item.thesis}</p>
            </div>
          )}

          {/* Domain-specific */}
          {item.property_details && (
            <div className="card p-4">
              <div className="section-title mb-3">Property Details</div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                {[
                  ["Location", [item.property_details.neighborhood, item.property_details.city, item.property_details.country].filter(Boolean).join(", ")],
                  ["Asset Type", item.property_details.asset_type],
                  ["Purchase Price", item.property_details.purchase_price ? `$${item.property_details.purchase_price.toLocaleString()}` : null],
                  ["Monthly Rent", item.property_details.estimated_rent ? `$${item.property_details.estimated_rent.toLocaleString()}` : null],
                  ["Gross Yield", item.property_details.gross_yield ? `${item.property_details.gross_yield}%` : null],
                  ["Net Yield", item.property_details.net_yield ? `${item.property_details.net_yield}%` : null],
                  ["Reno Budget", item.property_details.renovation_budget ? `$${item.property_details.renovation_budget.toLocaleString()}` : null],
                  ["Size", item.property_details.size_sqm ? `${item.property_details.size_sqm} sqm` : null],
                ].filter(([, v]) => v).map(([k, v]) => (
                  <div key={k as string}>
                    <div className="section-title mb-0.5">{k}</div>
                    <div className="text-zinc-300">{v}</div>
                  </div>
                ))}
              </div>
              {item.property_details.red_flags && (
                <div className="mt-3 p-2.5 rounded bg-red-900/20 border border-red-900/40 text-xs text-red-400">
                  ⚠ {item.property_details.red_flags}
                </div>
              )}
            </div>
          )}

          {item.investment_details && (
            <div className="card p-4">
              <div className="section-title mb-3">Investment Details</div>
              <div className="grid grid-cols-3 gap-3 text-sm">
                {[
                  ["Asset", item.investment_details.ticker_or_asset],
                  ["Entry", item.investment_details.entry_price ? `$${item.investment_details.entry_price}` : null],
                  ["Target", item.investment_details.target_price ? `$${item.investment_details.target_price}` : null],
                  ["Stop", item.investment_details.stop_loss ? `$${item.investment_details.stop_loss}` : null],
                  ["Hold Period", item.investment_details.holding_period],
                ].filter(([, v]) => v).map(([k, v]) => (
                  <div key={k as string}>
                    <div className="section-title mb-0.5">{k}</div>
                    <div className="text-zinc-300 font-mono">{v}</div>
                  </div>
                ))}
              </div>
              {item.investment_details.catalyst && (
                <div className="mt-2 text-xs text-zinc-500">
                  <span className="text-zinc-600">Catalyst: </span>{item.investment_details.catalyst}
                </div>
              )}
              {item.investment_details.invalidation && (
                <div className="mt-1 text-xs text-red-500">
                  <span className="text-zinc-600">Invalidation: </span>{item.investment_details.invalidation}
                </div>
              )}
            </div>
          )}

          {/* Next action */}
          {item.next_action && (
            <div className="card p-4">
              <div className="section-title mb-1">Next Action</div>
              <p className="text-sm text-emerald-400">{item.next_action}</p>
            </div>
          )}

          {/* AI Skills */}
          <div>
            <div className="section-title mb-3">AI Skills</div>
            <SkillRunner decisionId={item.id} />
          </div>

          {/* Notes */}
          <div>
            <div className="section-title mb-2">Notes</div>
            <div className="space-y-2 mb-2">
              {item.notes.map(n => (
                <div key={n.id} className="card p-3 text-sm text-zinc-400">
                  <div className="flex justify-between mb-1">
                    <span className="text-xs text-zinc-600">{n.note_type} · {new Date(n.created_at).toLocaleDateString()}</span>
                    <button className="text-zinc-700 hover:text-red-500 text-xs"
                      onClick={async () => {
                        await decisions.deleteNote(item.id, n.id);
                        const upd = await decisions.get(item.id);
                        setItem(upd);
                      }}>×</button>
                  </div>
                  {n.body}
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input className="input flex-1 text-xs" placeholder="Add a note…"
                value={noteText} onChange={e => setNoteText(e.target.value)}
                onKeyDown={e => e.key === "Enter" && addNote()} />
              <button className="btn btn-secondary text-xs" onClick={addNote}>
                <Plus size={11} /> Add
              </button>
            </div>
          </div>
        </div>

        {/* Right: score + status + journal */}
        <div className="space-y-5">
          {/* Score */}
          {latestScore && (
            <div className="card p-4">
              <div className="section-title mb-3">Latest Score</div>
              <ScoreBreakdown score={latestScore} />
            </div>
          )}

          {/* Change Status */}
          <div className="card p-4">
            <div className="section-title mb-3">Change Status</div>
            <select className="input mb-2" value={newStatus} onChange={e => setNewStatus(e.target.value)}>
              <option value="">Select status…</option>
              {STATUSES.map(s => <option key={s}>{s}</option>)}
            </select>
            <textarea className="textarea text-xs mb-2" rows={2} placeholder="Rationale (optional)"
              value={rationale} onChange={e => setRationale(e.target.value)} />
            <button className="btn btn-secondary w-full text-xs" onClick={changeStatus} disabled={!newStatus}>
              Update Status
            </button>
          </div>

          {/* Journal */}
          {item.journal_entries.length > 0 && (
            <div className="card p-4">
              <div className="section-title mb-3">History</div>
              <div className="space-y-2">
                {item.journal_entries.map(j => (
                  <div key={j.id} className="text-xs border-l-2 border-border pl-2">
                    <div className="text-zinc-600 mb-0.5">
                      {new Date(j.created_at).toLocaleDateString()}
                    </div>
                    <div className="text-zinc-500">
                      {j.prior_status} → <span className="text-zinc-300">{j.new_status}</span>
                    </div>
                    {j.rationale && <div className="text-zinc-600 mt-0.5 italic">{j.rationale}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tags */}
          {tags.length > 0 && (
            <div className="card p-4">
              <div className="section-title mb-2">Tags</div>
              <div className="flex flex-wrap gap-1">
                {tags.map(t => (
                  <span key={t} className="px-2 py-0.5 bg-surface-2 text-zinc-500 rounded text-xs">{t}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {editOpen && (
        <DecisionModal
          existing={item}
          onClose={() => setEditOpen(false)}
          onSaved={updated => { setItem(updated); setEditOpen(false); }}
        />
      )}
    </div>
  );
}
