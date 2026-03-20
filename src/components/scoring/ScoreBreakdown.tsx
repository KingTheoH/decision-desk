import type { DecisionScore } from "../../lib/types";

interface Props {
  score: DecisionScore;
}

const confidenceColor = { High: "text-emerald-400", Medium: "text-amber-400", Low: "text-red-400" };

export default function ScoreBreakdown({ score }: Props) {
  const pct = score.total_score ?? 0;
  const color = pct >= 70 ? "text-emerald-400" : pct >= 45 ? "text-amber-400" : "text-red-400";

  return (
    <div className="space-y-3">
      <div className="flex items-baseline gap-3">
        <span className={`text-3xl font-bold font-mono ${color}`}>{pct.toFixed(0)}</span>
        <span className="text-zinc-600 text-sm">/ 100</span>
        {score.confidence_level && (
          <span className={`text-xs ml-auto ${confidenceColor[score.confidence_level as keyof typeof confidenceColor] ?? "text-zinc-400"}`}>
            {score.confidence_level} confidence
          </span>
        )}
      </div>

      {/* Score bar */}
      <div className="h-1.5 bg-surface-3 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${pct >= 70 ? "bg-emerald-500" : pct >= 45 ? "bg-amber-500" : "bg-red-500"}`}
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Factor breakdown */}
      {score.factor_scores.length > 0 && (
        <div className="space-y-2 pt-1">
          {score.factor_scores.map(f => (
            <div key={f.id} className="flex items-center gap-2">
              <div className="text-xs text-zinc-500 w-40 truncate">{f.factor_name}</div>
              <div className="flex-1 h-1 bg-surface-3 rounded-full overflow-hidden">
                <div
                  className="h-full bg-violet-500/60 rounded-full"
                  style={{ width: `${(f.factor_score / 10) * 100}%` }}
                />
              </div>
              <div className="text-xs font-mono text-zinc-400 w-8 text-right">{f.factor_score}/10</div>
            </div>
          ))}
        </div>
      )}

      {score.scoring_notes && (
        <p className="text-xs text-zinc-600 italic">{score.scoring_notes}</p>
      )}
    </div>
  );
}
