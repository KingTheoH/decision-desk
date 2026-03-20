import { CheckCircle, XCircle, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import type { AISkillRun, SkillRunResponse } from "../../lib/types";

const SKILL_LABELS: Record<string, string> = {
  decomposition:   "Opportunity Decomposition",
  scoring:         "Rubric Scoring",
  comparator:      "Opportunity Cost Comparator",
  assumptions:     "Assumption Surfacing",
  compression:     "Decision Compression",
  patterns:        "Pattern Recognition",
  devils_advocate: "Devil's Advocate",
  next_action:     "Next Action Generator",
  property:        "Property Underwriting",
  business:        "Business Evaluator",
  content:         "Content Evaluator",
  final_verdict:   "Final Verdict",
};

interface Props {
  run: SkillRunResponse | AISkillRun;
  defaultOpen?: boolean;
}

function parseOutput(run: Props["run"]) {
  if ("output" in run && run.output) return run.output;
  if ("output_payload" in run && run.output_payload) {
    try { return JSON.parse(run.output_payload); } catch { return null; }
  }
  return null;
}

function getRawText(run: Props["run"]) {
  if ("raw_text" in run) return run.raw_text;
  if ("output_payload" in run) return run.output_payload;
  return null;
}

export default function SkillResultCard({ run, defaultOpen = false }: Props) {
  const [open, setOpen] = useState(defaultOpen);
  const output = parseOutput(run);
  const rawText = getRawText(run);

  return (
    <div className="card overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-surface-2 transition-colors"
        onClick={() => setOpen(o => !o)}
      >
        <div className="flex items-center gap-2.5">
          {run.succeeded
            ? <CheckCircle size={13} className="text-emerald-500" />
            : <XCircle size={13} className="text-red-500" />
          }
          <span className="text-sm font-medium text-zinc-200">
            {SKILL_LABELS[run.skill_name] ?? run.skill_name}
          </span>
          <span className="text-xs text-zinc-600 font-mono">
            {run.created_at ? new Date(run.created_at).toLocaleString() : ""}
          </span>
        </div>
        {open ? <ChevronUp size={13} className="text-zinc-600" /> : <ChevronDown size={13} className="text-zinc-600" />}
      </button>

      {open && (
        <div className="border-t border-border p-4">
          {!run.succeeded && run.error_message && (
            <div className="p-3 rounded-md bg-red-900/20 border border-red-900/40 text-sm text-red-400 mb-3">
              {run.error_message}
            </div>
          )}

          {output ? (
            <div className="space-y-2">
              {Object.entries(output).map(([key, val]) => (
                <div key={key}>
                  <div className="section-title mb-1">{key.replace(/_/g, " ")}</div>
                  {Array.isArray(val) ? (
                    <ul className="space-y-1">
                      {val.map((v, i) => (
                        <li key={i} className="text-xs text-zinc-400 flex gap-2">
                          <span className="text-zinc-700 mt-0.5">·</span>
                          <span>{String(v)}</span>
                        </li>
                      ))}
                    </ul>
                  ) : typeof val === "object" && val !== null ? (
                    <pre className="text-xs text-zinc-400 bg-surface-2 p-2 rounded overflow-x-auto">
                      {JSON.stringify(val, null, 2)}
                    </pre>
                  ) : (
                    <p className="text-sm text-zinc-300">{String(val)}</p>
                  )}
                </div>
              ))}
            </div>
          ) : rawText ? (
            <pre className="text-xs text-zinc-400 whitespace-pre-wrap font-mono leading-relaxed">
              {rawText}
            </pre>
          ) : (
            <p className="text-sm text-zinc-600">No output</p>
          )}
        </div>
      )}
    </div>
  );
}
