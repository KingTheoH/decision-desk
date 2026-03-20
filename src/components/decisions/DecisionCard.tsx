import { useNavigate } from "react-router-dom";
import { ArrowRight, DollarSign, Zap } from "lucide-react";
import TypeBadge from "../ui/TypeBadge";
import StatusBadge from "../ui/StatusBadge";
import PriorityBadge from "../ui/PriorityBadge";
import type { DecisionSummary } from "../../lib/types";

export default function DecisionCard({ item }: { item: DecisionSummary }) {
  const nav = useNavigate();
  const tags: string[] = (() => { try { return JSON.parse(item.tags || "[]"); } catch { return []; } })();

  return (
    <div
      className="card p-4 hover:border-zinc-700 transition-colors cursor-pointer group"
      onClick={() => nav(`/decisions/${item.id}`)}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <TypeBadge type={item.type} />
            <StatusBadge status={item.status} />
          </div>
          <h3 className="text-sm font-medium text-zinc-100 group-hover:text-white truncate">
            {item.title}
          </h3>
          {item.summary && (
            <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{item.summary}</p>
          )}
        </div>
        <ArrowRight size={14} className="text-zinc-700 group-hover:text-zinc-500 mt-1 shrink-0 transition-colors" />
      </div>

      <div className="mt-3 flex items-center justify-between">
        <PriorityBadge priority={item.priority} />
        <div className="flex items-center gap-3 text-xs text-zinc-600">
          {item.capital_required != null && (
            <span className="flex items-center gap-1">
              <DollarSign size={10} />
              {item.capital_required.toLocaleString()}
            </span>
          )}
          {item.expected_return != null && (
            <span className="flex items-center gap-1 text-emerald-600">
              <Zap size={10} />
              {item.expected_return}%
            </span>
          )}
        </div>
      </div>

      {tags.length > 0 && (
        <div className="mt-2 flex gap-1 flex-wrap">
          {tags.slice(0, 4).map(tag => (
            <span key={tag} className="px-1.5 py-0.5 bg-surface-2 text-zinc-600 rounded text-[10px]">
              {tag}
            </span>
          ))}
        </div>
      )}

      {item.next_action && (
        <div className="mt-2 pt-2 border-t border-border">
          <p className="text-[11px] text-zinc-600">
            <span className="text-zinc-500">Next: </span>{item.next_action}
          </p>
        </div>
      )}
    </div>
  );
}
