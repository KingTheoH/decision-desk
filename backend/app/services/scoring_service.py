"""Weighted rubric scoring math."""
from typing import List
from app.schemas.rubric import ScoreEntryFactor


def calculate_weighted_score(factors: List[ScoreEntryFactor]) -> float:
    """
    Weighted average: sum(score_i * weight_i) / sum(weight_i)
    Scores are 1–10, weights are percentages (sum to 100).
    Returns a 0–100 result.
    """
    total_weight = sum(f.factor_weight for f in factors)
    if total_weight == 0:
        return 0.0
    weighted_sum = sum(f.factor_score * f.factor_weight for f in factors)
    # Normalize to 0–100 range (score 1–10 → 0–100)
    raw = weighted_sum / total_weight      # 1–10
    normalized = (raw - 1) / 9 * 100      # 0–100
    return round(normalized, 1)
