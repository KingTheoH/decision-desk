from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import DecisionItem, Rubric, DecisionScore, DecisionScoreFactor
from app.schemas.rubric import ScoreEntryCreate
from app.schemas.decision import ScoreOut
from app.services.scoring_service import calculate_weighted_score

router = APIRouter(prefix="/scores", tags=["scoring"])


@router.post("", response_model=ScoreOut, status_code=201)
def create_score(data: ScoreEntryCreate, db: Session = Depends(get_db)):
    item = db.query(DecisionItem).filter(DecisionItem.id == data.decision_item_id).first()
    if not item:
        raise HTTPException(404, "Decision not found")
    rubric = db.query(Rubric).filter(Rubric.id == data.rubric_id).first()
    if not rubric:
        raise HTTPException(404, "Rubric not found")

    total = calculate_weighted_score(data.factors)

    score = DecisionScore(
        decision_item_id=data.decision_item_id,
        rubric_id=data.rubric_id,
        total_score=total,
        confidence_level=data.confidence_level,
        scoring_notes=data.scoring_notes,
    )
    db.add(score)
    db.flush()

    for f in data.factors:
        db.add(DecisionScoreFactor(
            decision_score_id=score.id,
            factor_name=f.factor_name,
            factor_weight=f.factor_weight,
            factor_score=f.factor_score,
            justification=f.justification,
        ))

    # Update decision's confidence_score to latest total
    item.confidence_score = total
    db.commit()
    db.refresh(score)
    return score


@router.get("/decision/{decision_id}", response_model=List[ScoreOut])
def get_scores_for_decision(decision_id: str, db: Session = Depends(get_db)):
    return db.query(DecisionScore).filter(
        DecisionScore.decision_item_id == decision_id
    ).order_by(DecisionScore.created_at.desc()).all()


@router.delete("/{score_id}", status_code=204)
def delete_score(score_id: str, db: Session = Depends(get_db)):
    s = db.query(DecisionScore).filter(DecisionScore.id == score_id).first()
    if not s:
        raise HTTPException(404)
    db.delete(s)
    db.commit()
