import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, AlertCircle } from "lucide-react";
import { decisions, reviewQueue, health } from "../lib/api";
import type { DecisionSummary, ReviewQueueItem } from "../lib/types";
import StatCard from "../components/ui/StatCard";
import DecisionCard from "../components/decisions/DecisionCard";
import TypeBadge from "../components/ui/TypeBadge";
import StatusBadge from "../components/ui/StatusBadge";
import DecisionModal from "../components/decisions/DecisionModal";

export default function Dashboard() {
  const nav = useNavigate();
  const [items, setItems] = useState<DecisionSummary[]>([]);
  const [queue, setQueue] = useState<ReviewQueueItem[]>([]);
  const [ollamaOk, setOllamaOk] = useState<boolean | null>(null);
  const [showNew, setShowNew] = useState(false);

  useEffect(() => {
    decisions.list({ sort_by: "updated_at" }).then(setItems);
    reviewQueue.get().then(setQueue);
    health.check().then(d => setOllamaOk(d?.ollama?.available ?? false)).catch(() => setOllamaOk(false));
  }, []);

  const byStatus = (s: string) => items.filter(i => i.status === s).length;
  const topQueue  = items.filter(i => i.priority === "TopQueue");
  const recent    = items.slice(0, 6);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-zinc-100">Dashboard</h1>
          <p className="text-xs text-zinc-600 mt-0.5">{items.length} decisions tracked</p>
        </div>
        <div className="flex items-center gap-2">
          {ollamaOk === false && (
            <div className="flex items-center gap-1.5 text-xs text-amber-600 border border-amber-900/50 bg-amber-900/20 rounded-md px-2.5 py-1">
              <AlertCircle size={11} />
              AI offline
            </div>
          )}
          {ollamaOk === true && (
            <div className="flex items-center gap-1.5 text-xs text-emerald-600 border border-emerald-900/50 bg-emerald-900/20 rounded-md px-2.5 py-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              AI online
            </div>
          )}
          <button className="btn btn-primary" onClick={() => setShowNew(true)}>
            <Plus size={13} /> New Decision
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total" value={items.length} />
        <StatCard label="Researching" value={byStatus("Researching")} />
        <StatCard label="Ready" value={byStatus("Ready")} accent />
        <StatCard label="Review Queue" value={queue.length} sub="need attention" accent={queue.length > 0} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Queue */}
        <div className="lg:col-span-2 space-y-3">
          <div className="section-title">Top Queue</div>
          {topQueue.length === 0 ? (
            <p className="text-sm text-zinc-700">No top-priority items</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {topQueue.map(i => <DecisionCard key={i.id} item={i} />)}
            </div>
          )}

          <div className="section-title pt-3">Recent</div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {recent.map(i => <DecisionCard key={i.id} item={i} />)}
          </div>
        </div>

        {/* Review Queue sidebar */}
        <div className="space-y-2">
          <div className="section-title">Needs Attention</div>
          {queue.length === 0 ? (
            <p className="text-sm text-zinc-700">Queue is clear</p>
          ) : (
            queue.slice(0, 8).map(q => (
              <div
                key={q.id}
                className="card p-3 cursor-pointer hover:border-zinc-700 transition-colors"
                onClick={() => nav(`/decisions/${q.id}`)}
              >
                <div className="flex items-start gap-2">
                  <AlertCircle size={12} className="text-amber-500 mt-0.5 shrink-0" />
                  <div className="min-w-0">
                    <div className="text-xs font-medium text-zinc-200 truncate">{q.title}</div>
                    <div className="flex gap-1 mt-1 flex-wrap">
                      <TypeBadge type={q.type} />
                      <StatusBadge status={q.status} />
                    </div>
                    {q.reasons.slice(0, 1).map((r, i) => (
                      <p key={i} className="text-[11px] text-zinc-600 mt-1">{r}</p>
                    ))}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showNew && (
        <DecisionModal
          onClose={() => setShowNew(false)}
          onSaved={item => { setShowNew(false); nav(`/decisions/${item.id}`); }}
        />
      )}
    </div>
  );
}
