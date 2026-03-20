import { clsx } from "clsx";

const styles: Record<string, string> = {
  Low:      "text-zinc-500",
  Medium:   "text-blue-400",
  High:     "text-amber-400",
  TopQueue: "text-violet-400 font-semibold",
};

const dots: Record<string, string> = {
  Low:      "bg-zinc-600",
  Medium:   "bg-blue-500",
  High:     "bg-amber-500",
  TopQueue: "bg-violet-500",
};

export default function PriorityBadge({ priority }: { priority: string }) {
  return (
    <span className={clsx("inline-flex items-center gap-1.5 text-xs", styles[priority] ?? "text-zinc-500")}>
      <span className={clsx("w-1.5 h-1.5 rounded-full", dots[priority] ?? "bg-zinc-600")} />
      {priority}
    </span>
  );
}
