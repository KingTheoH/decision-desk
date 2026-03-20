import { clsx } from "clsx";

const config: Record<string, { label: string; cls: string }> = {
  Property:     { label: "Property",     cls: "bg-blue-900/40 text-blue-400 border-blue-900/60" },
  BusinessIdea: { label: "Business",     cls: "bg-amber-900/40 text-amber-400 border-amber-900/60" },
  Investment:   { label: "Investment",   cls: "bg-emerald-900/40 text-emerald-400 border-emerald-900/60" },
  ContentIdea:  { label: "Content",      cls: "bg-pink-900/40 text-pink-400 border-pink-900/60" },
  Other:        { label: "Other",        cls: "bg-zinc-800 text-zinc-400 border-zinc-700" },
};

export default function TypeBadge({ type }: { type: string }) {
  const { label, cls } = config[type] ?? config.Other;
  return (
    <span className={clsx("px-1.5 py-0.5 rounded text-[11px] font-medium border", cls)}>
      {label}
    </span>
  );
}
