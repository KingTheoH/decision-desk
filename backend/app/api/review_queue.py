from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.review_service import get_review_queue

router = APIRouter(prefix="/review-queue", tags=["review"])


@router.get("")
def review_queue(db: Session = Depends(get_db)):
    queue = get_review_queue(db)
    return [
        {
            "id": entry["item"].id,
            "title": entry["item"].title,
            "type": entry["item"].type,
            "status": entry["item"].status,
            "priority": entry["item"].priority,
            "next_action": entry["item"].next_action,
            "reasons": entry["reasons"],
        }
        for entry in queue
    ]
