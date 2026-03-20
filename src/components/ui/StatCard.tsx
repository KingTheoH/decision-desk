interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  accent?: boolean;
}

export default function StatCard({ label, value, sub, accent }: StatCardProps) {
  return (
    <div className="card p-4 flex flex-col gap-1">
      <div className="section-title">{label}</div>
      <div className={`text-2xl font-semibold ${accent ? "text-violet-400" : "text-zinc-100"}`}>
        {value}
      </div>
      {sub && <div className="text-xs text-zinc-600">{sub}</div>}
    </div>
  );
}
