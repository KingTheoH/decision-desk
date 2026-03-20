import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { decisions } from "../lib/api";
import type { DecisionSummary } from "../lib/types";
import DecisionCard from "../components/decisions/DecisionCard";
import DecisionModal from "../components/decisions/DecisionModal";

export default function BusinessIdeas() {
  const [items, setItems] = useState<DecisionSummary[]>([]);
  const [showNew, setShowNew] = useState(false);
  const load = () => decisions.list({ type: "BusinessIdea" }).then(setItems);
  useEffect(() => { load(); }, []);
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">Business Ideas</h1>
        <button className="btn btn-primary" onClick={() => setShowNew(true)}><Plus size={13} /> New</button>
      </div>
      {items.length === 0 ? (
        <div className="card p-8 text-center text-zinc-600 text-sm">No business ideas yet.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {items.map(i => <DecisionCard key={i.id} item={i} />)}
        </div>
      )}
      {showNew && <DecisionModal onClose={() => setShowNew(false)} onSaved={() => { setShowNew(false); load(); }} />}
    </div>
  );
}
