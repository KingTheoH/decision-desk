import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { journal } from "../lib/api";

export default function Journal() {
  const nav = useNavigate();
  const [entries, setEntries] = useState<any[]>([]);

  useEffect(() => { journal.all(100).then(setEntries); }, []);

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4">
      <h1 className="text-lg font-semibold text-zinc-100">Decision Journal</h1>
      <p className="text-xs text-zinc-600">Timeline of all status changes across decisions.</p>

      {entries.length === 0 ? (
        <div className="card p-8 text-center text-zinc-600 text-sm">No journal entries yet.</div>
      ) : (
        <div className="relative pl-4">
          <div className="absolute left-0 top-2 bottom-2 w-px bg-border" />
          <div className="space-y-4">
            {entries.map(e => (
              <div key={e.id} className="relative pl-5">
                <div className="absolute left-0 top-1.5 w-2 h-2 rounded-full bg-violet-600 -translate-x-[4.5px]" />
                <div className="text-[11px] text-zinc-600 font-mono mb-0.5">
                  {new Date(e.created_at).toLocaleString()}
                </div>
                <div className="card p-3 text-sm">
                  <div className="text-zinc-500">
                    {e.prior_status || "—"} → <span className="text-zinc-200">{e.new_status}</span>
                  </div>
                  {e.rationale && (
                    <p className="text-xs text-zinc-600 mt-1 italic">{e.rationale}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
