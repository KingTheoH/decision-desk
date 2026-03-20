"""Review queue heuristics — surfaces items that need attention."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import DecisionItem


def get_review_queue(db: Session):
    now = datetime.utcnow()
    reasons = {}

    all_items = db.query(DecisionItem).filter(
        DecisionItem.archived_at == None,
        DecisionItem.status != "Rejected",
        DecisionItem.status != "Archived",
    ).all()

    for item in all_items:
        item_reasons = []

        # High priority not reviewed in 7 days
        if item.priority in ("High", "TopQueue"):
            if item.last_reviewed_at is None or (now - item.last_reviewed_at).days > 7:
                item_reasons.append("High priority — not reviewed recently")

        # Stuck in Researching for 14+ days
        if item.status == "Researching":
            age = (now - item.created_at).days
            if age > 14:
                item_reasons.append(f"Researching for {age} days")

        # Missing next action
        if not item.next_action and item.status not in ("Inbox", "Rejected"):
            item_reasons.append("No next action defined")

        # Deferred items (check updated_at as proxy)
        if item.status == "Deferred":
            days_deferred = (now - item.updated_at).days
            if days_deferred > 14:
                item_reasons.append(f"Deferred {days_deferred} days ago — due for re-check")

        # High confidence score but never progressed
        if item.confidence_score and item.confidence_score >= 7 and item.status in ("Inbox", "New"):
            item_reasons.append("High confidence score but still in Inbox/New")

        if item_reasons:
            reasons[item.id] = {"item": item, "reasons": item_reasons}

    # Sort: TopQueue first, then High, then rest
    priority_order = {"TopQueue": 0, "High": 1, "Medium": 2, "Low": 3}
    sorted_items = sorted(
        reasons.values(),
        key=lambda x: priority_order.get(x["item"].priority, 9)
    )
    return sorted_items
