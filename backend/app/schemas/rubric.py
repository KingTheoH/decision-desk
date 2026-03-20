from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class RubricFactorCreate(BaseModel):
    name: str
    weight: float
    description: Optional[str] = None
    sort_order: Optional[int] = 0


class RubricFactorOut(BaseModel):
    id: str
    name: str
    weight: float
    description: Optional[str] = None
    sort_order: int
    class Config: from_attributes = True


class RubricCreate(BaseModel):
    name: str
    decision_type: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = False
    factors: Optional[List[RubricFactorCreate]] = []


class RubricUpdate(BaseModel):
    name: Optional[str] = None
    decision_type: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None


class RubricOut(BaseModel):
    id: str
    name: str
    decision_type: Optional[str] = None
    description: Optional[str] = None
    is_default: bool
    created_at: datetime
    updated_at: datetime
    factors: List[RubricFactorOut] = []
    class Config: from_attributes = True


class ScoreEntryFactor(BaseModel):
    factor_name: str
    factor_weight: float
    factor_score: float   # 1–10
    justification: Optional[str] = None


class ScoreEntryCreate(BaseModel):
    decision_item_id: str
    rubric_id: str
    factors: List[ScoreEntryFactor]
    confidence_level: Optional[str] = "Medium"   # High | Medium | Low
    scoring_notes: Optional[str] = None
