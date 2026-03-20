import { useState } from "react";
import { Zap, WifiOff, Loader } from "lucide-react";
import { ai } from "../../lib/api";
import SkillResultCard from "./SkillResultCard";
import type { SkillRunResponse } from "../../lib/types";

const SKILLS = [
  { key: "decomposition",   label: "Decompose" },
  { key: "scoring",         label: "Score" },
  { key: "comparator",      label: "Compare vs Baseline" },
  { key: "assumptions",     label: "Surface Assumptions" },
  { key: "devils_advocate", label: "Devil's Advocate" },
  { key: "compression",     label: "Compress to Decision" },
  { key: "next_action",     label: "Next Action" },
  { key: "property",        label: "Property Underwrite" },
  { key: "business",        label: "Business Evaluate" },
  { key: "content",         label: "Content Evaluate" },
  { key: "patterns",        label: "Pattern Recognition" },
  { key: "final_verdict",   label: "Final Verdict" },
];

interface Props {
  decisionId: string;
  existingRuns?: SkillRunResponse[];
}

export default function SkillRunner({ decisionId, existingRuns = [] }: Props) {
  const [running, setRunning] = useState<string | null>(null);
  const [results, setResults] = useState<SkillRunResponse[]>(existingRuns);
  const [offline, setOffline] = useState(false);

  async function run(skillKey: string) {
    setRunning(skillKey);
    setOffline(false);
    try {
      const res = await ai.run(skillKey, decisionId);
      if (!res.succeeded && res.error_message?.includes("offline")) {
        setOffline(true);
      }
      setResults(prev => [res, ...prev.filter(r => r.skill_name !== skillKey)]);
    } catch {
      setOffline(true);
    } finally {
      setRunning(null);
    }
  }

  return (
    <div className="space-y-4">
      {offline && (
        <div className="flex items-center gap-2 p-3 rounded-md bg-amber-900/20 border border-amber-900/40 text-sm text-amber-400">
          <WifiOff size={13} />
          <span>Ollama is offline. Install Ollama and run: <code className="font-mono text-xs">ollama pull llama3.2</code></span>
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {SKILLS.map(s => (
          <button
            key={s.key}
            className="btn btn-secondary text-xs py-1 px-2.5"
            onClick={() => run(s.key)}
            disabled={running !== null}
          >
            {running === s.key ? (
              <Loader size={11} className="animate-spin" />
            ) : (
              <Zap size={11} className="text-violet-500" />
            )}
            {s.label}
          </button>
        ))}
      </div>

      {results.length > 0 && (
        <div className="space-y-2">
          {results.map(r => (
            <SkillResultCard key={r.id} run={r} defaultOpen={results.indexOf(r) === 0} />
          ))}
        </div>
      )}
    </div>
  );
}
