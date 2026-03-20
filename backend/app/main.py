"""Decision Desk — FastAPI backend"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.api import health, decisions, rubrics, scoring, ai_skills, compare, review_queue, journal

app = FastAPI(title="Decision Desk API", version="1.0.0")

# Allow Vite dev server + Tauri
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:1420", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
app.include_router(health.router)
app.include_router(decisions.router, prefix="/api")
app.include_router(rubrics.router,   prefix="/api")
app.include_router(scoring.router,   prefix="/api")
app.include_router(ai_skills.router, prefix="/api")
app.include_router(compare.router,   prefix="/api")
app.include_router(review_queue.router, prefix="/api")
app.include_router(journal.router,   prefix="/api")


@app.on_event("startup")
def startup():
    init_db()
    _seed_data()


def _seed_data():
    """Insert demo data on first run if DB is empty."""
    from app.core.database import SessionLocal
    from app.models.models import DecisionItem, PropertyDetails, BusinessIdeaDetails, InvestmentDetails, ContentIdeaDetails
    import uuid

    db = SessionLocal()
    try:
        if db.query(DecisionItem).count() > 0:
            return  # Already seeded

        items = [
            {
                "item": DecisionItem(
                    id=str(uuid.uuid4()),
                    title="Osaka 1K Apartment — Namba area",
                    type="Property",
                    status="Researching",
                    priority="High",
                    summary="1K apartment near Namba, ¥9M asking price. Estimated rent ¥65k/mo. High tourist demand area.",
                    thesis="Osaka STR market remains strong. 1K near Namba consistently achieves 70%+ occupancy. Net yield after fees ~5.8%.",
                    capital_required=70000,
                    expected_return=5.8,
                    time_to_cashflow="3 months",
                    operational_complexity="Medium",
                    downside_risk="STR regulation risk in Osaka; vacancy if regulations tighten",
                    next_action="Get property inspection quote and confirm building management fees",
                    tags='["Japan", "STR", "Osaka"]',
                ),
                "property": PropertyDetails(
                    country="Japan", city="Osaka", neighborhood="Namba",
                    asset_type="Apartment", purchase_price=67000,
                    size_sqm=28, building_age=12,
                    monthly_fees=150, annual_taxes=400,
                    estimated_rent=590, gross_yield=10.6, net_yield=5.8,
                    renovation_budget=5000,
                    demand_notes="High tourist and business traveler demand. Namba station 5-min walk.",
                    red_flags="Building age 12 years — check for elevator maintenance history",
                ),
            },
            {
                "item": DecisionItem(
                    id=str(uuid.uuid4()),
                    title="Mobile Car Detailing — Vancouver Suburbs",
                    type="BusinessIdea",
                    status="New",
                    priority="Medium",
                    summary="Mobile detailing service targeting suburban homeowners in Burnaby/Coquitlam. Low startup cost, recurring clientele.",
                    thesis="High disposable income suburbs. No dominant mobile detailing brand. $150–300/car. 3 cars/day = $450–900 revenue.",
                    capital_required=8000,
                    expected_return=35,
                    time_to_cashflow="1 month",
                    operational_complexity="Low",
                    downside_risk="Weather dependency, physical labour, hard to scale beyond 1 van",
                    next_action="Call 10 potential customers to validate willingness to pay $200+ for mobile detail",
                    tags='["Vancouver", "Service", "B2C"]',
                ),
                "business": BusinessIdeaDetails(
                    business_model="Mobile service / B2C recurring",
                    target_customer="Suburban homeowners aged 35–55 with $80k+ income",
                    startup_cost=8000,
                    recurring_revenue_potential="High — customers book monthly or quarterly",
                    time_to_launch="2 weeks",
                    regulatory_burden="Low — basic business license",
                    competitive_intensity="Medium — fragmented local market",
                    scalability="Low single-van; Medium with 2+ vans",
                    moat_notes="Recurring relationships and referrals are the moat",
                    risk_notes="Rain season April–Nov. Must have indoor facility or accept downtime",
                ),
            },
            {
                "item": DecisionItem(
                    id=str(uuid.uuid4()),
                    title="NVDA — Pullback Entry at $850",
                    type="Investment",
                    status="Waiting",
                    priority="TopQueue",
                    summary="NVDA trading at $950. Thesis: pullback to $850 support from Nov 2024 consolidation offers 3:1 R/R to $1050.",
                    thesis="AI capex cycle intact. NVDA dominates H100/H200 allocation. $850 is strong structure. Catalyst: next earnings in 6 weeks.",
                    capital_required=15000,
                    expected_return=23,
                    time_to_cashflow="6 weeks",
                    operational_complexity="Low",
                    downside_risk="Hard stop $790. Full position loss if export controls tighten",
                    next_action="Set limit buy alert at $855. Re-evaluate if support breaks below $840",
                    tags='["Equities", "Tech", "AI"]',
                ),
                "investment": InvestmentDetails(
                    ticker_or_asset="NVDA",
                    entry_price=850,
                    target_price=1050,
                    stop_loss=790,
                    holding_period="6–8 weeks",
                    catalyst="Q4 earnings beat + forward guidance on Blackwell demand",
                    invalidation="Close below $840 on volume; or new export control announcement",
                    risk_reward_notes="3:1 R/R at entry. Max loss $60/share = $900 on 15 shares",
                    liquidity_notes="Extremely liquid — no slippage concern",
                ),
            },
            {
                "item": DecisionItem(
                    id=str(uuid.uuid4()),
                    title="Japan Property Investor Vlog Series",
                    type="ContentIdea",
                    status="Inbox",
                    priority="Low",
                    summary="Weekly YouTube series documenting the process of buying and managing rental property in Japan as a foreigner.",
                    thesis="High search demand for Japan property content. Low competition in English. Natural authority from Japan RE App project.",
                    next_action="Record a 3-minute test video on 'Can foreigners buy property in Japan' and post to YouTube Shorts",
                    tags='["YouTube", "Japan", "RE"]',
                ),
                "content": ContentIdeaDetails(
                    platform="YouTube",
                    format_type="Series",
                    hook="A Canadian buys an Osaka apartment for $65,000 — here's everything that happened",
                    production_burden="Medium",
                    virality_potential="Moderate — strong niche, limited breakout potential",
                    repeatability="High — ongoing deal flow provides content indefinitely",
                    monetization_path="AdSense + affiliate (real estate tools) + consulting leads",
                    creative_notes="Documentary style. Show real numbers, real friction, real mistakes.",
                ),
            },
        ]

        for entry in items:
            item = entry["item"]
            db.add(item)
            db.flush()
            if "property" in entry:
                entry["property"].decision_item_id = item.id
                db.add(entry["property"])
            if "business" in entry:
                entry["business"].decision_item_id = item.id
                db.add(entry["business"])
            if "investment" in entry:
                entry["investment"].decision_item_id = item.id
                db.add(entry["investment"])
            if "content" in entry:
                entry["content"].decision_item_id = item.id
                db.add(entry["content"])

        # Seed default rubric
        from app.models.models import Rubric, RubricFactor
        rubric = Rubric(
            id=str(uuid.uuid4()),
            name="General Opportunity Rubric",
            is_default=True,
            description="Balanced rubric for evaluating any opportunity type",
        )
        db.add(rubric)
        db.flush()
        factors = [
            ("Yield / Payoff Potential", 20, "Expected financial return relative to risk"),
            ("Capital Efficiency",        15, "Return per dollar deployed"),
            ("Execution Realism",         20, "Realistic probability of execution given skills/time/resources"),
            ("Time to Cash Flow",         15, "How quickly does this generate returns"),
            ("Opportunity Cost",          15, "Does this beat the baseline alternatives"),
            ("Operational Burden",        10, "Ongoing time and complexity required to run"),
            ("Downside Protection",        5, "How contained is the worst-case loss"),
        ]
        for i, (name, weight, desc) in enumerate(factors):
            db.add(RubricFactor(rubric_id=rubric.id, name=name, weight=weight, description=desc, sort_order=i))

        db.commit()
        print("✅ Seed data inserted")
    except Exception as e:
        db.rollback()
        print(f"Seed data error (non-fatal): {e}")
    finally:
        db.close()
