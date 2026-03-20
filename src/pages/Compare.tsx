import { useEffect, useState } from "react";
import { decisions as decisionsApi, compare as compareApi } from "../lib/api";
import type { DecisionSummary, CompareResult } from "../lib/types";
import TypeBadge from "../components/ui/TypeBadge";
import StatusBadge from "../components/ui/StatusBadge";
import { clsx } from "clsx";

export default function Compare() {
  const [all, setAll] = useState<DecisionSummary[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [result, setResult] = useState<CompareResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    decisionsApi.list().then(data => {
      setAll(data);
      const validIds = new Set(data.map(d => d.id));
      setSelected(prev => prev.filter(id => validIds.has(id)));
    });
  }, []);

  function toggle(id: string) {
    setSelected(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : prev.length < 4 ? [...prev, id] : prev
    );
  }

  async function runCompare() {
    if (selected.length < 2) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await compareApi.get(selected);
      setResult(r);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? "Compare failed — please try again");
    } finally {
      setLoading(false);
    }
  }

  const fields = [
    { key: "capital_required",      label: "Capital Required",       fmt: (v: number) => v != null ? `$${v.toLocaleString()}` : "—" },
    { key: "expected_return",        label: "Expected Return",        fmt: (v: number) => v != null ? `${v}%` : "—" },
    { key: "time_to_cashflow",       label: "Time to Cash Flow",      fmt: (v: string) => v || "—" },
    { key: "operational_complexity", label: "Complexity",             fmt: (v: string) => v || "—" },
    { key: "downside_risk",          label: "Downside Risk",          fmt: (v: string) => v || "—" },
    { key: "liquidity_exit_ease",    label: "Liquidity / Exit",       fmt: (v: string) => v || "—" },
    { key: "score",                  label: "Rubric Score",           fmt: (v: number) => v != null ? v.toFixed(0) : "—" },
    { key: "next_action",            label: "Next Action",            fmt: (v: string) => v || "—" },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <h1 className="text-lg font-semibold text-zinc-100">Compare Decisions</h1>

      {/* Selection */}
      <div>
        <div className="section-title mb-2">Select 2–4 decisions to compare</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {all.map(item => (
            <div
              key={item.id}
              className={clsx(
                "card p-3 cursor-pointer transition-colors",
                selected.includes(item.id) ? "border-violet-500 bg-violet-900/10" : "hover:border-zinc-700"
              )}
              onClick={() => toggle(item.id)}
            >
              <div className="flex items-start gap-2">
                <input type="checkbox" checked={selected.includes(item.id)}
                  onChange={() => {}} className="mt-0.5 accent-violet-500" readOnly />
                <div className="min-w-0">
                  <div className="text-sm font-medium text-zinc-200 truncate">{item.title}</div>
                  <div className="flex gap-1 mt-1"><TypeBadge type={item.type} /><StatusBadge status={item.status} /></div>
                </div>
              </div>
            </div>
          ))}
        </div>
        <button
          className="btn btn-primary mt-3"
          onClick={runCompare}
          disabled={selected.length < 2 || loading}
        >
          {loading ? "Comparing…" : `Compare ${selected.length} Decision${selected.length !== 1 ? "s" : ""}`}
        </button>
        {selected.length < 2 && selected.length > 0 && (
          <p className="text-xs text-zinc-600 mt-2">Select at least 2 to compare</p>
        )}
        {error && (
          <div className="mt-3 p-3 rounded-md bg-red-900/20 border border-red-900/40 text-red-400 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left text-xs text-zinc-600 font-medium p-3 w-36">Field</th>
                {result.decisions.map(d => (
                  <th key={d.id} className="text-left p-3">
                    <div className="font-medium text-zinc-200 text-sm">{d.title}</div>
                    <div className="flex gap-1 mt-1"><TypeBadge type={d.type} /><StatusBadge status={d.status} /></div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {fields.map(({ key, label, fmt }) => (
                <tr key={key} className="border-b border-border/50">
                  <td className="p-3 text-xs text-zinc-600 font-medium">{label}</td>
                  {result.decisions.map(d => {
                    const val = (d as any)[key];
                    const isBest = result.highlights[key]?.best === d.id;
                    const isWorst = result.highlights[key]?.worst === d.id;
                    return (
                      <td key={d.id} className={clsx(
                        "p-3 text-sm",
                        isBest ? "text-emerald-400" : isWorst ? "text-red-400" : "text-zinc-400"
                      )}>
                        {(fmt as (v: any) => string)(val)}
                        {isBest && <span className="ml-1 text-[10px] text-emerald-600">▲ best</span>}
                        {isWorst && <span className="ml-1 text-[10px] text-red-600">▼ worst</span>}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
