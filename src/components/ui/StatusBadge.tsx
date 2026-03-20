import { clsx } from "clsx";
import type { DecisionStatus } from "../../lib/types";

const styles: Record<DecisionStatus, string> = {
  Inbox:      "bg-zinc-800 text-zinc-400",
  New:        "bg-blue-900/40 text-blue-400",
  Researching:"bg-amber-900/40 text-amber-400",
  Waiting:    "bg-orange-900/40 text-orange-400",
  Ready:      "bg-emerald-900/40 text-emerald-400",
  Approved:   "bg-emerald-700/50 text-emerald-300",
  Rejected:   "bg-red-900/40 text-red-400",
  Deferred:   "bg-zinc-700/50 text-zinc-400",
  Archived:   "bg-zinc-900 text-zinc-600",
};

export default function StatusBadge({ status }: { status: string }) {
  const cls = styles[status as DecisionStatus] ?? "bg-zinc-800 text-zinc-400";
  return (
    <span className={clsx("px-2 py-0.5 rounded text-xs font-medium", cls)}>
      {status}
    </span>
  );
}
