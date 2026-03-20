"""
All SQLAlchemy ORM models for Decision Desk.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Text, DateTime, Boolean, Integer, ForeignKey
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def new_id():
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────────────────────────
# Core decision item
# ─────────────────────────────────────────────────────────────────────────────

class DecisionItem(Base):
    __tablename__ = "decision_items"

    id                     = Column(String, primary_key=True, default=new_id)
    title                  = Column(String, nullable=False)
    type                   = Column(String, nullable=False)          # Property | BusinessIdea | Investment | ContentIdea | Other
    status                 = Column(String, default="Inbox")         # Inbox | New | Researching | Waiting | Ready | Approved | Rejected | Deferred | Archived
    priority               = Column(String, default="Medium")        # Low | Medium | High | TopQueue
    summary                = Column(Text)
    thesis                 = Column(Text)
    why_it_matters         = Column(Text)
    capital_required       = Column(Float)
    expected_return        = Column(Float)
    time_to_cashflow       = Column(String)
    ongoing_time_req       = Column(String)
    operational_complexity = Column(String)
    downside_risk          = Column(String)
    confidence_score       = Column(Float)
    urgency_score          = Column(Float)
    reversibility          = Column(String)
    liquidity_exit_ease    = Column(String)
    next_action            = Column(Text)
    owner                  = Column(String)
    source_type            = Column(String)
    source_reference       = Column(Text)
    tags                   = Column(String, default="[]")            # JSON array string
    created_at             = Column(DateTime, default=datetime.utcnow)
    updated_at             = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_reviewed_at       = Column(DateTime)
    archived_at            = Column(DateTime)

    # Relationships
    scores           = relationship("DecisionScore",        back_populates="decision", cascade="all, delete-orphan")
    notes            = relationship("DecisionNote",         back_populates="decision", cascade="all, delete-orphan")
    journal_entries  = relationship("DecisionJournalEntry", back_populates="decision", cascade="all, delete-orphan")
    ai_runs          = relationship("AISkillRun",           back_populates="decision", cascade="all, delete-orphan")
    property_details = relationship("PropertyDetails",      back_populates="decision", uselist=False, cascade="all, delete-orphan")
    business_details = relationship("BusinessIdeaDetails",  back_populates="decision", uselist=False, cascade="all, delete-orphan")
    investment_details = relationship("InvestmentDetails",  back_populates="decision", uselist=False, cascade="all, delete-orphan")
    content_details  = relationship("ContentIdeaDetails",   back_populates="decision", uselist=False, cascade="all, delete-orphan")
    attachments      = relationship("AttachmentMeta",       back_populates="decision", cascade="all, delete-orphan")


# ─────────────────────────────────────────────────────────────────────────────
# Domain detail tables
# ─────────────────────────────────────────────────────────────────────────────

class PropertyDetails(Base):
    __tablename__ = "property_details"

    id                  = Column(String, primary_key=True, default=new_id)
    decision_item_id    = Column(String, ForeignKey("decision_items.id"), unique=True)
    country             = Column(String)
    city                = Column(String)
    neighborhood        = Column(String)
    address_text        = Column(Text)
    asset_type          = Column(String)        # Apartment | House | Commercial | Land
    purchase_price      = Column(Float)
    size_sqm            = Column(Float)
    building_age        = Column(Integer)
    monthly_fees        = Column(Float)
    annual_taxes        = Column(Float)
    estimated_rent      = Column(Float)
    gross_yield         = Column(Float)
    net_yield           = Column(Float)
    renovation_budget   = Column(Float)
    demand_notes        = Column(Text)
    exit_notes          = Column(Text)
    red_flags           = Column(Text)

    decision = relationship("DecisionItem", back_populates="property_details")


class BusinessIdeaDetails(Base):
    __tablename__ = "business_idea_details"

    id                          = Column(String, primary_key=True, default=new_id)
    decision_item_id            = Column(String, ForeignKey("decision_items.id"), unique=True)
    business_model              = Column(String)
    target_customer             = Column(Text)
    startup_cost                = Column(Float)
    recurring_revenue_potential = Column(String)
    time_to_launch              = Column(String)
    regulatory_burden           = Column(String)
    competitive_intensity       = Column(String)
    scalability                 = Column(String)
    distribution_notes          = Column(Text)
    moat_notes                  = Column(Text)
    risk_notes                  = Column(Text)

    decision = relationship("DecisionItem", back_populates="business_details")


class InvestmentDetails(Base):
    __tablename__ = "investment_details"

    id                  = Column(String, primary_key=True, default=new_id)
    decision_item_id    = Column(String, ForeignKey("decision_items.id"), unique=True)
    ticker_or_asset     = Column(String)
    entry_price         = Column(Float)
    target_price        = Column(Float)
    stop_loss           = Column(Float)
    holding_period      = Column(String)
    catalyst            = Column(Text)
    invalidation        = Column(Text)
    risk_reward_notes   = Column(Text)
    liquidity_notes     = Column(Text)

    decision = relationship("DecisionItem", back_populates="investment_details")


class ContentIdeaDetails(Base):
    __tablename__ = "content_idea_details"

    id                  = Column(String, primary_key=True, default=new_id)
    decision_item_id    = Column(String, ForeignKey("decision_items.id"), unique=True)
    platform            = Column(String)        # YouTube | TikTok | Instagram | Twitter
    format_type         = Column(String)        # Short | Long | Series | Meme
    hook                = Column(Text)
    production_burden   = Column(String)        # Low | Medium | High
    virality_potential  = Column(String)
    repeatability       = Column(String)
    monetization_path   = Column(Text)
    creative_notes      = Column(Text)

    decision = relationship("DecisionItem", back_populates="content_details")


# ─────────────────────────────────────────────────────────────────────────────
# Rubric system
# ─────────────────────────────────────────────────────────────────────────────

class Rubric(Base):
    __tablename__ = "rubrics"

    id            = Column(String, primary_key=True, default=new_id)
    name          = Column(String, nullable=False)
    decision_type = Column(String)   # null = applies to all types
    description   = Column(Text)
    is_default    = Column(Boolean, default=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    factors = relationship("RubricFactor", back_populates="rubric", cascade="all, delete-orphan", order_by="RubricFactor.sort_order")
    scores  = relationship("DecisionScore", back_populates="rubric")


class RubricFactor(Base):
    __tablename__ = "rubric_factors"

    id          = Column(String, primary_key=True, default=new_id)
    rubric_id   = Column(String, ForeignKey("rubrics.id"))
    name        = Column(String, nullable=False)
    weight      = Column(Float, nullable=False)   # 0–100; all weights in rubric should sum to 100
    description = Column(Text)
    sort_order  = Column(Integer, default=0)

    rubric = relationship("Rubric", back_populates="factors")


# ─────────────────────────────────────────────────────────────────────────────
# Scoring
# ─────────────────────────────────────────────────────────────────────────────

class DecisionScore(Base):
    __tablename__ = "decision_scores"

    id               = Column(String, primary_key=True, default=new_id)
    decision_item_id = Column(String, ForeignKey("decision_items.id"))
    rubric_id        = Column(String, ForeignKey("rubrics.id"))
    total_score      = Column(Float)    # 0–100
    confidence_level = Column(String)   # High | Medium | Low
    scoring_notes    = Column(Text)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    decision        = relationship("DecisionItem", back_populates="scores")
    rubric          = relationship("Rubric", back_populates="scores")
    factor_scores   = relationship("DecisionScoreFactor", back_populates="score", cascade="all, delete-orphan")


class DecisionScoreFactor(Base):
    __tablename__ = "decision_score_factors"

    id               = Column(String, primary_key=True, default=new_id)
    decision_score_id = Column(String, ForeignKey("decision_scores.id"))
    factor_name      = Column(String)
    factor_weight    = Column(Float)
    factor_score     = Column(Float)   # 1–10
    justification    = Column(Text)

    score = relationship("DecisionScore", back_populates="factor_scores")


# ─────────────────────────────────────────────────────────────────────────────
# Notes, attachments, journal
# ─────────────────────────────────────────────────────────────────────────────

class DecisionNote(Base):
    __tablename__ = "decision_notes"

    id               = Column(String, primary_key=True, default=new_id)
    decision_item_id = Column(String, ForeignKey("decision_items.id"))
    body             = Column(Text, nullable=False)
    note_type        = Column(String, default="General")   # General | Risk | Assumption | Update
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    decision = relationship("DecisionItem", back_populates="notes")


class AttachmentMeta(Base):
    __tablename__ = "attachment_meta"

    id               = Column(String, primary_key=True, default=new_id)
    decision_item_id = Column(String, ForeignKey("decision_items.id"))
    filename         = Column(String)
    file_path        = Column(String)
    mime_type        = Column(String)
    created_at       = Column(DateTime, default=datetime.utcnow)

    decision = relationship("DecisionItem", back_populates="attachments")


class DecisionJournalEntry(Base):
    __tablename__ = "decision_journal"

    id               = Column(String, primary_key=True, default=new_id)
    decision_item_id = Column(String, ForeignKey("decision_items.id"))
    prior_status     = Column(String)
    new_status       = Column(String)
    rationale        = Column(Text)
    created_at       = Column(DateTime, default=datetime.utcnow)

    decision = relationship("DecisionItem", back_populates="journal_entries")


# ─────────────────────────────────────────────────────────────────────────────
# AI skill runs
# ─────────────────────────────────────────────────────────────────────────────

class AISkillRun(Base):
    __tablename__ = "ai_skill_runs"

    id               = Column(String, primary_key=True, default=new_id)
    decision_item_id = Column(String, ForeignKey("decision_items.id"), nullable=True)
    skill_name       = Column(String, nullable=False)
    input_payload    = Column(Text)   # JSON string
    output_payload   = Column(Text)   # JSON string
    succeeded        = Column(Boolean, default=True)
    error_message    = Column(Text)
    created_at       = Column(DateTime, default=datetime.utcnow)

    decision = relationship("DecisionItem", back_populates="ai_runs")
