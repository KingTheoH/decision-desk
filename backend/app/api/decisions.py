from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    DecisionItem, PropertyDetails, BusinessIdeaDetails,
    InvestmentDetails, ContentIdeaDetails, DecisionNote, DecisionJournalEntry
)
from app.schemas.decision import (
    DecisionItemCreate, DecisionItemUpdate, DecisionItemOut,
    DecisionItemSummary, NoteCreate, StatusUpdate
)

router = APIRouter(prefix="/decisions", tags=["decisions"])


def _apply_domain_details(db, item, data):
    """Upsert domain detail tables from create/update payload."""
    if data.property_details:
        if item.property_details:
            for k, v in data.property_details.model_dump(exclude_unset=True).items():
                setattr(item.property_details, k, v)
        else:
            db.add(PropertyDetails(decision_item_id=item.id, **data.property_details.model_dump()))

    if data.business_details:
        if item.business_details:
            for k, v in data.business_details.model_dump(exclude_unset=True).items():
                setattr(item.business_details, k, v)
        else:
            db.add(BusinessIdeaDetails(decision_item_id=item.id, **data.business_details.model_dump()))

    if data.investment_details:
        if item.investment_details:
            for k, v in data.investment_details.model_dump(exclude_unset=True).items():
                setattr(item.investment_details, k, v)
        else:
            db.add(InvestmentDetails(decision_item_id=item.id, **data.investment_details.model_dump()))

    if data.content_details:
        if item.content_details:
            for k, v in data.content_details.model_dump(exclude_unset=True).items():
                setattr(item.content_details, k, v)
        else:
            db.add(ContentIdeaDetails(decision_item_id=item.id, **data.content_details.model_dump()))


@router.get("", response_model=List[DecisionItemSummary])
def list_decisions(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("updated_at"),
    db: Session = Depends(get_db),
):
    q = db.query(DecisionItem).filter(DecisionItem.archived_at == None)
    if type:
        q = q.filter(DecisionItem.type == type)
    if status:
        q = q.filter(DecisionItem.status == status)
    if priority:
        q = q.filter(DecisionItem.priority == priority)
    if search:
        like = f"%{search}%"
        q = q.filter(
            DecisionItem.title.ilike(like) |
            DecisionItem.summary.ilike(like) |
            DecisionItem.thesis.ilike(like) |
            DecisionItem.tags.ilike(like)
        )
    sort_col = {
        "updated_at": DecisionItem.updated_at,
        "created_at": DecisionItem.created_at,
        "priority": DecisionItem.priority,
        "capital_required": DecisionItem.capital_required,
    }.get(sort_by, DecisionItem.updated_at)
    q = q.order_by(sort_col.desc())
    return q.all()


@router.post("", response_model=DecisionItemOut, status_code=201)
def create_decision(data: DecisionItemCreate, db: Session = Depends(get_db)):
    item = DecisionItem(**data.model_dump(
        exclude={"property_details", "business_details", "investment_details", "content_details"}
    ))
    db.add(item)
    db.flush()
    _apply_domain_details(db, item, data)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{id}", response_model=DecisionItemOut)
def get_decision(id: str, db: Session = Depends(get_db)):
    item = db.query(DecisionItem).filter(DecisionItem.id == id).first()
    if not item:
        raise HTTPException(404, "Decision not found")
    # Update last_reviewed_at
    item.last_reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{id}", response_model=DecisionItemOut)
def update_decision(id: str, data: DecisionItemUpdate, db: Session = Depends(get_db)):
    item = db.query(DecisionItem).filter(DecisionItem.id == id).first()
    if not item:
        raise HTTPException(404, "Decision not found")
    update_fields = data.model_dump(
        exclude_unset=True,
        exclude={"property_details", "business_details", "investment_details", "content_details"}
    )
    for k, v in update_fields.items():
        setattr(item, k, v)
    item.updated_at = datetime.utcnow()
    _apply_domain_details(db, item, data)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{id}", status_code=204)
def delete_decision(id: str, db: Session = Depends(get_db)):
    item = db.query(DecisionItem).filter(DecisionItem.id == id).first()
    if not item:
        raise HTTPException(404, "Decision not found")
    db.delete(item)
    db.commit()


@router.post("/{id}/status")
def update_status(id: str, data: StatusUpdate, db: Session = Depends(get_db)):
    """Change status and auto-create a journal entry."""
    item = db.query(DecisionItem).filter(DecisionItem.id == id).first()
    if not item:
        raise HTTPException(404, "Decision not found")
    prior = item.status
    item.status = data.status
    item.updated_at = datetime.utcnow()
    entry = DecisionJournalEntry(
        decision_item_id=id,
        prior_status=prior,
        new_status=data.status,
        rationale=data.rationale,
    )
    db.add(entry)
    db.commit()
    db.refresh(item)
    return item


@router.post("/{id}/notes")
def add_note(id: str, data: NoteCreate, db: Session = Depends(get_db)):
    item = db.query(DecisionItem).filter(DecisionItem.id == id).first()
    if not item:
        raise HTTPException(404, "Decision not found")
    note = DecisionNote(decision_item_id=id, **data.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{id}/notes/{note_id}", status_code=204)
def delete_note(id: str, note_id: str, db: Session = Depends(get_db)):
    note = db.query(DecisionNote).filter(
        DecisionNote.id == note_id,
        DecisionNote.decision_item_id == id
    ).first()
    if not note:
        raise HTTPException(404)
    db.delete(note)
    db.commit()
