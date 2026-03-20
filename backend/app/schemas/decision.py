from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class PropertyDetailsBase(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    address_text: Optional[str] = None
    asset_type: Optional[str] = None
    purchase_price: Optional[float] = None
    size_sqm: Optional[float] = None
    building_age: Optional[int] = None
    monthly_fees: Optional[float] = None
    annual_taxes: Optional[float] = None
    estimated_rent: Optional[float] = None
    gross_yield: Optional[float] = None
    net_yield: Optional[float] = None
    renovation_budget: Optional[float] = None
    demand_notes: Optional[str] = None
    exit_notes: Optional[str] = None
    red_flags: Optional[str] = None

class PropertyDetailsOut(PropertyDetailsBase):
    id: str
    decision_item_id: str
    class Config: from_attributes = True


class BusinessDetailsBase(BaseModel):
    business_model: Optional[str] = None
    target_customer: Optional[str] = None
    startup_cost: Optional[float] = None
    recurring_revenue_potential: Optional[str] = None
    time_to_launch: Optional[str] = None
    regulatory_burden: Optional[str] = None
    competitive_intensity: Optional[str] = None
    scalability: Optional[str] = None
    distribution_notes: Optional[str] = None
    moat_notes: Optional[str] = None
    risk_notes: Optional[str] = None

class BusinessDetailsOut(BusinessDetailsBase):
    id: str
    decision_item_id: str
    class Config: from_attributes = True


class InvestmentDetailsBase(BaseModel):
    ticker_or_asset: Optional[str] = None
    entry_price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    holding_period: Optional[str] = None
    catalyst: Optional[str] = None
    invalidation: Optional[str] = None
    risk_reward_notes: Optional[str] = None
    liquidity_notes: Optional[str] = None

class InvestmentDetailsOut(InvestmentDetailsBase):
    id: str
    decision_item_id: str
    class Config: from_attributes = True


class ContentDetailsBase(BaseModel):
    platform: Optional[str] = None
    format_type: Optional[str] = None
    hook: Optional[str] = None
    production_burden: Optional[str] = None
    virality_potential: Optional[str] = None
    repeatability: Optional[str] = None
    monetization_path: Optional[str] = None
    creative_notes: Optional[str] = None

class ContentDetailsOut(ContentDetailsBase):
    id: str
    decision_item_id: str
    class Config: from_attributes = True


class ScoreFactorOut(BaseModel):
    id: str
    factor_name: str
    factor_weight: float
    factor_score: float
    justification: Optional[str] = None
    class Config: from_attributes = True


class ScoreOut(BaseModel):
    id: str
    rubric_id: str
    total_score: Optional[float] = None
    confidence_level: Optional[str] = None
    scoring_notes: Optional[str] = None
    created_at: datetime
    factor_scores: List[ScoreFactorOut] = []
    class Config: from_attributes = True


class NoteOut(BaseModel):
    id: str
    body: str
    note_type: str
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True


class JournalEntryOut(BaseModel):
    id: str
    prior_status: Optional[str] = None
    new_status: Optional[str] = None
    rationale: Optional[str] = None
    created_at: datetime
    class Config: from_attributes = True


class AISkillRunOut(BaseModel):
    id: str
    skill_name: str
    output_payload: Optional[str] = None
    succeeded: bool
    error_message: Optional[str] = None
    created_at: datetime
    class Config: from_attributes = True


class DecisionItemCreate(BaseModel):
    title: str
    type: str
    status: Optional[str] = "Inbox"
    priority: Optional[str] = "Medium"
    summary: Optional[str] = None
    thesis: Optional[str] = None
    why_it_matters: Optional[str] = None
    capital_required: Optional[float] = None
    expected_return: Optional[float] = None
    time_to_cashflow: Optional[str] = None
    ongoing_time_req: Optional[str] = None
    operational_complexity: Optional[str] = None
    downside_risk: Optional[str] = None
    confidence_score: Optional[float] = None
    urgency_score: Optional[float] = None
    reversibility: Optional[str] = None
    liquidity_exit_ease: Optional[str] = None
    next_action: Optional[str] = None
    owner: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    tags: Optional[str] = "[]"
    # domain detail sub-objects
    property_details: Optional[PropertyDetailsBase] = None
    business_details: Optional[BusinessDetailsBase] = None
    investment_details: Optional[InvestmentDetailsBase] = None
    content_details: Optional[ContentDetailsBase] = None


class DecisionItemUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    summary: Optional[str] = None
    thesis: Optional[str] = None
    why_it_matters: Optional[str] = None
    capital_required: Optional[float] = None
    expected_return: Optional[float] = None
    time_to_cashflow: Optional[str] = None
    ongoing_time_req: Optional[str] = None
    operational_complexity: Optional[str] = None
    downside_risk: Optional[str] = None
    confidence_score: Optional[float] = None
    urgency_score: Optional[float] = None
    reversibility: Optional[str] = None
    liquidity_exit_ease: Optional[str] = None
    next_action: Optional[str] = None
    owner: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    tags: Optional[str] = None
    property_details: Optional[PropertyDetailsBase] = None
    business_details: Optional[BusinessDetailsBase] = None
    investment_details: Optional[InvestmentDetailsBase] = None
    content_details: Optional[ContentDetailsBase] = None


class DecisionItemOut(BaseModel):
    id: str
    title: str
    type: str
    status: str
    priority: str
    summary: Optional[str] = None
    thesis: Optional[str] = None
    why_it_matters: Optional[str] = None
    capital_required: Optional[float] = None
    expected_return: Optional[float] = None
    time_to_cashflow: Optional[str] = None
    ongoing_time_req: Optional[str] = None
    operational_complexity: Optional[str] = None
    downside_risk: Optional[str] = None
    confidence_score: Optional[float] = None
    urgency_score: Optional[float] = None
    reversibility: Optional[str] = None
    liquidity_exit_ease: Optional[str] = None
    next_action: Optional[str] = None
    owner: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    tags: Optional[str] = "[]"
    created_at: datetime
    updated_at: datetime
    last_reviewed_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    # nested
    scores: List[ScoreOut] = []
    notes: List[NoteOut] = []
    journal_entries: List[JournalEntryOut] = []
    ai_runs: List[AISkillRunOut] = []
    property_details: Optional[PropertyDetailsOut] = None
    business_details: Optional[BusinessDetailsOut] = None
    investment_details: Optional[InvestmentDetailsOut] = None
    content_details: Optional[ContentDetailsOut] = None
    class Config: from_attributes = True


class DecisionItemSummary(BaseModel):
    """Lightweight list view — no nested relations"""
    id: str
    title: str
    type: str
    status: str
    priority: str
    summary: Optional[str] = None
    capital_required: Optional[float] = None
    expected_return: Optional[float] = None
    next_action: Optional[str] = None
    tags: Optional[str] = "[]"
    created_at: datetime
    updated_at: datetime
    last_reviewed_at: Optional[datetime] = None
    class Config: from_attributes = True


class NoteCreate(BaseModel):
    body: str
    note_type: Optional[str] = "General"


class StatusUpdate(BaseModel):
    status: str
    rationale: Optional[str] = None
