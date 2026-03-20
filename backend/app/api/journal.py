from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import DecisionJournalEntry
from app.schemas.decision import JournalEntryOut

router = APIRouter(prefix="/journal", tags=["journal"])


@router.get("/{decision_id}", response_model=List[JournalEntryOut])
def get_journal(decision_id: str, db: Session = Depends(get_db)):
    return db.query(DecisionJournalEntry).filter(
        DecisionJournalEntry.decision_item_id == decision_id
    ).order_by(DecisionJournalEntry.created_at.desc()).all()


@router.get("")
def get_all_journal(db: Session = Depends(get_db), limit: int = 50):
    entries = db.query(DecisionJournalEntry).order_by(
        DecisionJournalEntry.created_at.desc()
    ).limit(limit).all()
    return entries
