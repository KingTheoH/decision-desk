import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Plus, Search, LayoutGrid, List } from "lucide-react";
import { decisions } from "../lib/api";
import type { DecisionSummary, DecisionItem } from "../lib/types";
import DecisionCard from "../components/decisions/DecisionCard";
import DecisionTable from "../components/decisions/DecisionTable";
import DecisionModal from "../components/decisions/DecisionModal";
import TypeBadge from "../components/ui/TypeBadge";

const TYPES = ["", "Property", "BusinessIdea", "Investment", "ContentIdea", "Other"];
const STATUSES = ["", "Inbox", "New", "Researching", "Waiting", "Ready", "Approved", "Rejected", "Deferred"];
const PRIORITIES = ["", "TopQueue", "High", "Medium", "Low"];

export default function AllDecisions() {
  const [params, setParams] = useSearchParams();
  const [items, setItems] = useState<DecisionSummary[]>([]);
  const [search, setSearch] = useState(params.get("search") || "");
  const [type, setType] = useState(params.get("type") || "");
  const [status, setStatus] = useState(params.get("status") || "");
  const [priority, setPriority] = useState(params.get("priority") || "");
  const [view, setView] = useState<"card" | "table">("table");
  const [showNew, setShowNew] = useState(false);

  async function load() {
    const data = await decisions.list({
      search: search || undefined,
      type: type || undefined,
      status: status || undefined,
      priority: priority || undefined,
    });
    setItems(data);
  }

  useEffect(() => { load(); }, [search, type, status, priority]);

  return (
    <div className="p-6 space-y-4 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">All Decisions</h1>
        <button className="btn btn-primary" onClick={() => setShowNew(true)}>
          <Plus size={13} /> New
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap items-center">
        <div className="relative flex-1 min-w-48">
          <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-600" />
          <input className="input pl-7" placeholder="Search…"
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="input w-36" value={type} onChange={e => setType(e.target.value)}>
          <option value="">All Types</option>
          {TYPES.filter(Boolean).map(t => <option key={t}>{t}</option>)}
        </select>
        <select className="input w-36" value={status} onChange={e => setStatus(e.target.value)}>
          <option value="">All Statuses</option>
          {STATUSES.filter(Boolean).map(s => <option key={s}>{s}</option>)}
        </select>
        <select className="input w-36" value={priority} onChange={e => setPriority(e.target.value)}>
          <option value="">All Priorities</option>
          {PRIORITIES.filter(Boolean).map(p => <option key={p}>{p}</option>)}
        </select>
        <div className="flex border border-border rounded-md overflow-hidden">
          <button className={`p-2 ${view === "table" ? "bg-surface-3 text-zinc-200" : "text-zinc-600 hover:bg-surface-2"}`}
            onClick={() => setView("table")}><List size={13} /></button>
          <button className={`p-2 ${view === "card" ? "bg-surface-3 text-zinc-200" : "text-zinc-600 hover:bg-surface-2"}`}
            onClick={() => setView("card")}><LayoutGrid size={13} /></button>
        </div>
      </div>

      <div className="text-xs text-zinc-600">{items.length} results</div>

      {view === "table"
        ? <div className="card p-4"><DecisionTable items={items} /></div>
        : <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {items.map(i => <DecisionCard key={i.id} item={i} />)}
          </div>
      }

      {showNew && (
        <DecisionModal
          onClose={() => setShowNew(false)}
          onSaved={() => { setShowNew(false); load(); }}
        />
      )}
    </div>
  );
}
