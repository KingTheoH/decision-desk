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

function stripFences(text: string): string {
  return text.replace(/```(?:json)?/g, "").replace(/`{1,3}/g, "").trim();
}

function tryParseJson(text: string): Record<string, unknown> | null {
  const clean = stripFences(text);
  // Direct parse
  try { return JSON.parse(clean); } catch { /* fall through */ }
  // Find first { and raw-decode up to matching }
  const start = clean.indexOf("{");
  if (start !== -1) {
    // Walk chars to find balanced closing brace
    let depth = 0;
    for (let i = start; i < clean.length; i++) {
      if (clean[i] === "{") depth++;
      else if (clean[i] === "}") { depth--; if (depth === 0) {
        try { return JSON.parse(clean.slice(start, i + 1)); } catch { break; }
      }}
    }
  }
  return null;
}

function splitTrailingNotes(text: string): { jsonBlock: string; notes: string } {
  // Split off any text after the closing fence or after the JSON object
  const fenceEnd = text.lastIndexOf("```");
  if (fenceEnd !== -1) {
    return { jsonBlock: text.slice(0, fenceEnd + 3), notes: text.slice(fenceEnd + 3).trim() };
  }
  return { jsonBlock: text, notes: "" };
}

function parseOutput(run: Props["run"]) {
  if ("output" in run && run.output) return run.output;
  // Frontend fallback: try to parse raw_text if backend didn't
  const raw = "raw_text" in run ? run.raw_text : ("output_payload" in run ? run.output_payload : null);
  if (raw) {
    const parsed = tryParseJson(raw);
    if (parsed) return parsed;
  }
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

function getTrailingNotes(run: Props["run"]): string {
  const raw = getRawText(run);
  if (!raw) return "";
  const { notes } = splitTrailingNotes(raw);
  // Strip markdown bold markers for clean display
  return notes.replace(/\*\*/g, "").trim();
}

export default function SkillResultCard({ run, defaultOpen = false }: Props) {
  const [open, setOpen] = useState(defaultOpen);
  const output = parseOutput(run);
  const rawText = getRawText(run);
  const trailingNotes = getTrailingNotes(run);

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
            <div className="space-y-3">
              {Object.entries(output as Record<string, unknown>).map(([key, val]) => (
                <div key={key} className="space-y-1">
                  <div className="section-title">{key.replace(/_/g, " ")}</div>
                  {Array.isArray(val) ? (
                    val.length === 0 ? (
                      <p className="text-xs text-zinc-600 italic">none</p>
                    ) : (
                      <ul className="space-y-1 pl-1">
                        {val.map((v, i) => (
                          <li key={i} className="text-xs text-zinc-300 flex gap-2">
                            <span className="text-violet-500 mt-0.5 shrink-0">·</span>
                            <span>{typeof v === "object" ? JSON.stringify(v) : String(v)}</span>
                          </li>
                        ))}
                      </ul>
                    )
                  ) : typeof val === "object" && val !== null ? (
                    <div className="space-y-1 pl-2 border-l border-border">
                      {Object.entries(val as Record<string, unknown>).map(([k, v]) => (
                        <div key={k} className="flex gap-2 text-xs">
                          <span className="text-zinc-500 shrink-0 capitalize">{k.replace(/_/g, " ")}:</span>
                          <span className="text-zinc-300">{v === null ? "—" : String(v)}</span>
                        </div>
                      ))}
                    </div>
                  ) : val === null || val === "" ? (
                    <p className="text-xs text-zinc-600 italic">—</p>
                  ) : (
                    <p className="text-sm text-zinc-300 leading-relaxed">{String(val)}</p>
                  )}
                </div>
              ))}
              {/* Show any trailing notes the model appended after the JSON */}
              {trailingNotes && (
                <div className="pt-3 border-t border-border">
                  <div className="section-title mb-1">Notes</div>
                  <p className="text-xs text-zinc-400 leading-relaxed whitespace-pre-line">{trailingNotes}</p>
                </div>
              )}
            </div>
          ) : rawText ? (
            // Fallback: raw text that couldn't be parsed — strip fences, display cleanly
            <pre className="text-xs text-zinc-400 whitespace-pre-wrap leading-relaxed font-sans">
              {stripFences(rawText)}
            </pre>
          ) : (
            <p className="text-sm text-zinc-600">No output</p>
          )}
        </div>
      )}
    </div>
  );
}
