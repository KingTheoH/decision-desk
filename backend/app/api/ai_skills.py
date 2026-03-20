import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import DecisionItem, AISkillRun
from app.schemas.ai_skill import SkillRunRequest, SkillRunResponse
from app.services.ai_service import run_skill, SKILL_NAMES

router = APIRouter(prefix="/ai", tags=["ai"])


def _decision_to_dict(item: DecisionItem) -> dict:
    """Flatten a DecisionItem + domain details into a dict for prompt injection."""
    d = {
        "title": item.title,
        "type": item.type,
        "status": item.status,
        "priority": item.priority,
        "summary": item.summary,
        "thesis": item.thesis,
        "why_it_matters": item.why_it_matters,
        "capital_required": item.capital_required,
        "expected_return": item.expected_return,
        "time_to_cashflow": item.time_to_cashflow,
        "operational_complexity": item.operational_complexity,
        "downside_risk": item.downside_risk,
        "next_action": item.next_action,
        "tags": item.tags,
    }
    if item.property_details:
        pd = item.property_details
        d["property"] = {
            "location": f"{pd.city}, {pd.country}",
            "purchase_price": pd.purchase_price,
            "estimated_rent": pd.estimated_rent,
            "gross_yield": pd.gross_yield,
            "net_yield": pd.net_yield,
            "renovation_budget": pd.renovation_budget,
            "red_flags": pd.red_flags,
        }
    if item.business_details:
        bd = item.business_details
        d["business"] = {
            "model": bd.business_model,
            "target_customer": bd.target_customer,
            "startup_cost": bd.startup_cost,
            "scalability": bd.scalability,
            "risk_notes": bd.risk_notes,
        }
    if item.investment_details:
        inv = item.investment_details
        d["investment"] = {
            "asset": inv.ticker_or_asset,
            "entry_price": inv.entry_price,
            "target_price": inv.target_price,
            "catalyst": inv.catalyst,
            "invalidation": inv.invalidation,
        }
    if item.content_details:
        cd = item.content_details
        d["content"] = {
            "platform": cd.platform,
            "format": cd.format_type,
            "hook": cd.hook,
            "production_burden": cd.production_burden,
        }
    return d


@router.get("/skills")
def list_skills():
    return {"skills": SKILL_NAMES}


@router.post("/run", response_model=SkillRunResponse)
async def run_ai_skill(data: SkillRunRequest, db: Session = Depends(get_db)):
    decision_data = {}
    item = None

    if data.decision_item_id:
        item = db.query(DecisionItem).filter(DecisionItem.id == data.decision_item_id).first()
        if not item:
            raise HTTPException(404, "Decision not found")
        decision_data = _decision_to_dict(item)

    result = await run_skill(
        skill_name=data.skill_name,
        decision_data=decision_data,
        extra_context=data.extra_context,
    )

    # Log the run
    run_log = AISkillRun(
        decision_item_id=data.decision_item_id,
        skill_name=data.skill_name,
        input_payload=json.dumps(decision_data, default=str),
        output_payload=json.dumps(result.get("output") or {}) if result.get("output") else result.get("raw_text", ""),
        succeeded=result["succeeded"],
        error_message=result.get("error_message"),
    )
    db.add(run_log)
    db.commit()
    db.refresh(run_log)

    return SkillRunResponse(
        id=run_log.id,
        skill_name=data.skill_name,
        succeeded=result["succeeded"],
        error_message=result.get("error_message"),
        output=result.get("output"),
        raw_text=result.get("raw_text"),
    )


@router.get("/history/{decision_id}")
def skill_history(decision_id: str, db: Session = Depends(get_db)):
    runs = db.query(AISkillRun).filter(
        AISkillRun.decision_item_id == decision_id
    ).order_by(AISkillRun.created_at.desc()).all()
    return runs
