import { useNavigate } from "react-router-dom";
import TypeBadge from "../ui/TypeBadge";
import StatusBadge from "../ui/StatusBadge";
import PriorityBadge from "../ui/PriorityBadge";
import type { DecisionSummary } from "../../lib/types";

export default function DecisionTable({ items }: { items: DecisionSummary[] }) {
  const nav = useNavigate();

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            {["Title", "Type", "Status", "Priority", "Capital", "Return", "Updated"].map(h => (
              <th key={h} className="text-left text-xs text-zinc-600 font-medium px-3 py-2 first:pl-0">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <tr
              key={item.id}
              className="border-b border-border/50 hover:bg-surface-2 cursor-pointer transition-colors"
              onClick={() => nav(`/decisions/${item.id}`)}
            >
              <td className="px-3 py-2.5 first:pl-0 max-w-xs">
                <div className="truncate text-zinc-200 font-medium">{item.title}</div>
                {item.summary && (
                  <div className="text-[11px] text-zinc-600 truncate mt-0.5">{item.summary}</div>
                )}
              </td>
              <td className="px-3 py-2.5"><TypeBadge type={item.type} /></td>
              <td className="px-3 py-2.5"><StatusBadge status={item.status} /></td>
              <td className="px-3 py-2.5"><PriorityBadge priority={item.priority} /></td>
              <td className="px-3 py-2.5 text-zinc-500 font-mono text-xs">
                {item.capital_required != null ? `$${item.capital_required.toLocaleString()}` : "—"}
              </td>
              <td className="px-3 py-2.5 text-emerald-600 font-mono text-xs">
                {item.expected_return != null ? `${item.expected_return}%` : "—"}
              </td>
              <td className="px-3 py-2.5 text-zinc-600 text-xs font-mono whitespace-nowrap">
                {new Date(item.updated_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
