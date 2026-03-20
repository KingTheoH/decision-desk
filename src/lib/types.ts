// ── Enums ────────────────────────────────────────────────────────────────────

export type DecisionType = "Property" | "BusinessIdea" | "Investment" | "ContentIdea" | "Other";

export type DecisionStatus =
  | "Inbox" | "New" | "Researching" | "Waiting"
  | "Ready" | "Approved" | "Rejected" | "Deferred" | "Archived";

export type Priority = "Low" | "Medium" | "High" | "TopQueue";

export type ConfidenceLevel = "High" | "Medium" | "Low";

// ── Domain details ────────────────────────────────────────────────────────────

export interface PropertyDetails {
  id: string;
  decision_item_id: string;
  country?: string;
  city?: string;
  neighborhood?: string;
  address_text?: string;
  asset_type?: string;
  purchase_price?: number;
  size_sqm?: number;
  building_age?: number;
  monthly_fees?: number;
  annual_taxes?: number;
  estimated_rent?: number;
  gross_yield?: number;
  net_yield?: number;
  renovation_budget?: number;
  demand_notes?: string;
  exit_notes?: string;
  red_flags?: string;
}

export interface BusinessDetails {
  id: string;
  decision_item_id: string;
  business_model?: string;
  target_customer?: string;
  startup_cost?: number;
  recurring_revenue_potential?: string;
  time_to_launch?: string;
  regulatory_burden?: string;
  competitive_intensity?: string;
  scalability?: string;
  distribution_notes?: string;
  moat_notes?: string;
  risk_notes?: string;
}

export interface InvestmentDetails {
  id: string;
  decision_item_id: string;
  ticker_or_asset?: string;
  entry_price?: number;
  target_price?: number;
  stop_loss?: number;
  holding_period?: string;
  catalyst?: string;
  invalidation?: string;
  risk_reward_notes?: string;
  liquidity_notes?: string;
}

export interface ContentDetails {
  id: string;
  decision_item_id: string;
  platform?: string;
  format_type?: string;
  hook?: string;
  production_burden?: string;
  virality_potential?: string;
  repeatability?: string;
  monetization_path?: string;
  creative_notes?: string;
}

// ── Scoring ──────────────────────────────────────────────────────────────────

export interface ScoreFactor {
  id: string;
  factor_name: string;
  factor_weight: number;
  factor_score: number;
  justification?: string;
}

export interface DecisionScore {
  id: string;
  rubric_id: string;
  total_score?: number;
  confidence_level?: string;
  scoring_notes?: string;
  created_at: string;
  factor_scores: ScoreFactor[];
}

// ── Notes / Journal ───────────────────────────────────────────────────────────

export interface DecisionNote {
  id: string;
  body: string;
  note_type: string;
  created_at: string;
  updated_at: string;
}

export interface JournalEntry {
  id: string;
  prior_status?: string;
  new_status?: string;
  rationale?: string;
  created_at: string;
}

export interface AISkillRun {
  id: string;
  skill_name: string;
  output_payload?: string;
  succeeded: boolean;
  error_message?: string;
  created_at: string;
}

// ── Core DecisionItem ─────────────────────────────────────────────────────────

export interface DecisionItem {
  id: string;
  title: string;
  type: DecisionType;
  status: DecisionStatus;
  priority: Priority;
  summary?: string;
  thesis?: string;
  why_it_matters?: string;
  capital_required?: number;
  expected_return?: number;
  time_to_cashflow?: string;
  ongoing_time_req?: string;
  operational_complexity?: string;
  downside_risk?: string;
  confidence_score?: number;
  urgency_score?: number;
  reversibility?: string;
  liquidity_exit_ease?: string;
  next_action?: string;
  owner?: string;
  source_type?: string;
  source_reference?: string;
  tags?: string;
  created_at: string;
  updated_at: string;
  last_reviewed_at?: string;
  archived_at?: string;
  // nested
  scores: DecisionScore[];
  notes: DecisionNote[];
  journal_entries: JournalEntry[];
  ai_runs: AISkillRun[];
  property_details?: PropertyDetails;
  business_details?: BusinessDetails;
  investment_details?: InvestmentDetails;
  content_details?: ContentDetails;
}

export interface DecisionSummary {
  id: string;
  title: string;
  type: DecisionType;
  status: DecisionStatus;
  priority: Priority;
  summary?: string;
  capital_required?: number;
  expected_return?: number;
  next_action?: string;
  tags?: string;
  created_at: string;
  updated_at: string;
  last_reviewed_at?: string;
}

// ── Rubric ────────────────────────────────────────────────────────────────────

export interface RubricFactor {
  id: string;
  name: string;
  weight: number;
  description?: string;
  sort_order: number;
}

export interface Rubric {
  id: string;
  name: string;
  decision_type?: string;
  description?: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
  factors: RubricFactor[];
}

// ── AI ────────────────────────────────────────────────────────────────────────

export interface SkillRunResponse {
  id: string;
  skill_name: string;
  succeeded: boolean;
  error_message?: string;
  output?: Record<string, unknown>;
  raw_text?: string;
  created_at?: string;
}

// ── Compare ───────────────────────────────────────────────────────────────────

export interface CompareResult {
  decisions: {
    id: string;
    title: string;
    type: string;
    status: string;
    priority: string;
    capital_required?: number;
    expected_return?: number;
    time_to_cashflow?: string;
    ongoing_time_req?: string;
    downside_risk?: string;
    liquidity_exit_ease?: string;
    operational_complexity?: string;
    next_action?: string;
    score?: number;
    tags?: string;
  }[];
  highlights: Record<string, { best: string; worst: string }>;
}

// ── Review Queue ──────────────────────────────────────────────────────────────

export interface ReviewQueueItem {
  id: string;
  title: string;
  type: string;
  status: string;
  priority: string;
  next_action?: string;
  reasons: string[];
}
