import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertCircle, ArrowRight } from "lucide-react";
import { reviewQueue } from "../lib/api";
import type { ReviewQueueItem } from "../lib/types";
import TypeBadge from "../components/ui/TypeBadge";
import StatusBadge from "../components/ui/StatusBadge";
import PriorityBadge from "../components/ui/PriorityBadge";

export default function ReviewQueue() {
  const nav = useNavigate();
  const [items, setItems] = useState<ReviewQueueItem[]>([]);

  useEffect(() => { reviewQueue.get().then(setItems); }, []);

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-zinc-100">Review Queue</h1>
        <p className="text-xs text-zinc-600 mt-0.5">{items.length} items need attention</p>
      </div>

      {items.length === 0 ? (
        <div className="card p-8 text-center text-zinc-600 text-sm">Queue is clear — no items need attention.</div>
      ) : (
        <div className="space-y-2">
          {items.map(item => (
            <div key={item.id} className="card p-4 hover:border-zinc-700 transition-colors cursor-pointer group"
              onClick={() => nav(`/decisions/${item.id}`)}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 min-w-0">
                  <AlertCircle size={14} className="text-amber-500 mt-0.5 shrink-0" />
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-zinc-200 truncate">{item.title}</div>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <TypeBadge type={item.type} />
                      <StatusBadge status={item.status} />
                      <PriorityBadge priority={item.priority} />
                    </div>
                    <div className="mt-2 space-y-1">
                      {item.reasons.map((r, i) => (
                        <div key={i} className="text-xs text-zinc-600 flex gap-1.5">
                          <span className="text-amber-700">·</span> {r}
                        </div>
                      ))}
                    </div>
                    {item.next_action && (
                      <div className="mt-2 text-xs text-emerald-600">
                        Next: {item.next_action}
                      </div>
                    )}
                  </div>
                </div>
                <ArrowRight size={13} className="text-zinc-700 group-hover:text-zinc-500 mt-1 shrink-0" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
