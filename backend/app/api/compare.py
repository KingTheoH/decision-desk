from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import DecisionItem

router = APIRouter(prefix="/compare", tags=["compare"])


@router.get("")
def compare_decisions(
    ids: List[str] = Query(...),
    db: Session = Depends(get_db),
):
    """Return structured comparison data for 2–4 decisions."""
    if len(ids) < 2 or len(ids) > 4:
        raise HTTPException(400, "Provide 2–4 decision IDs")

    items = db.query(DecisionItem).filter(DecisionItem.id.in_(ids)).all()
    if len(items) != len(ids):
        raise HTTPException(404, "One or more decisions not found")

    def score_for(item):
        if item.scores:
            latest = sorted(item.scores, key=lambda s: s.created_at, reverse=True)[0]
            return latest.total_score
        return None

    results = []
    for item in items:
        results.append({
            "id": item.id,
            "title": item.title,
            "type": item.type,
            "status": item.status,
            "priority": item.priority,
            "capital_required": item.capital_required,
            "expected_return": item.expected_return,
            "time_to_cashflow": item.time_to_cashflow,
            "ongoing_time_req": item.ongoing_time_req,
            "downside_risk": item.downside_risk,
            "liquidity_exit_ease": item.liquidity_exit_ease,
            "operational_complexity": item.operational_complexity,
            "next_action": item.next_action,
            "score": score_for(item),
            "tags": item.tags,
        })

    # Highlight best/worst for numeric fields
    numeric_fields = ["capital_required", "expected_return", "score"]
    highlights = {}
    for field in numeric_fields:
        values = [(r["id"], r[field]) for r in results if r[field] is not None]
        if values:
            best_id = max(values, key=lambda x: x[1])[0] if field != "capital_required" else min(values, key=lambda x: x[1])[0]
            worst_id = min(values, key=lambda x: x[1])[0] if field != "capital_required" else max(values, key=lambda x: x[1])[0]
            highlights[field] = {"best": best_id, "worst": worst_id}

    return {"decisions": results, "highlights": highlights}
