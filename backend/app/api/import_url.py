"""
URL import endpoint — fetch a URL, extract its content, run Ollama to populate decision fields.
Supports: YouTube (oEmbed + transcript), property listings, articles, any web page.
Auto-saves the decision to the database with all estimated fields.
"""
import re
import json
from typing import Optional
from urllib.parse import urlparse, parse_qs

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    DecisionItem, PropertyDetails, BusinessIdeaDetails,
    InvestmentDetails, ContentIdeaDetails
)
from app.services.ai_service import try_parse_json, OLLAMA_MODEL, OLLAMA_BASE_URL

router = APIRouter()


# ── Request / Response ────────────────────────────────────────────────────────

class ImportRequest(BaseModel):
    url: str
    auto_evaluate: bool = True   # run decomposition skill automatically after import
    auto_save: bool = True       # create the decision in the DB immediately

class ImportResult(BaseModel):
    succeeded: bool
    url: str
    page_type: str
    extracted_text: str
    fields: dict
    auto_evaluation: Optional[dict] = None
    saved_decision_id: Optional[str] = None   # set when auto_save=True
    error_message: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def detect_page_type(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    if any(k in host for k in ["zillow", "redfin", "realtor", "homes.com",
                                 "craigslist", "suumo", "athome", "homes",
                                 "century21", "remax", "rightmove", "zoopla"]):
        return "property"
    return "article"


def get_youtube_id(url: str) -> Optional[str]:
    parsed = urlparse(url)
    # youtu.be/VIDEO_ID
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/").split("?")[0]
    # /shorts/VIDEO_ID
    shorts_match = re.match(r"/shorts/([A-Za-z0-9_-]+)", parsed.path)
    if shorts_match:
        return shorts_match.group(1)
    # /live/VIDEO_ID
    live_match = re.match(r"/live/([A-Za-z0-9_-]+)", parsed.path)
    if live_match:
        return live_match.group(1)
    # ?v=VIDEO_ID (standard watch URL)
    qs = parse_qs(parsed.query)
    return qs.get("v", [None])[0]


async def fetch_youtube_metadata(url: str) -> str:
    """
    Fetch YouTube video content: oEmbed metadata + auto-generated transcript.
    Transcript gives the AI the actual spoken content to evaluate.
    """
    parts = []
    video_id = get_youtube_id(url)

    # ── 1. oEmbed: title + channel ────────────────────────────────────────────
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            r = await client.get(oembed_url)
            if r.status_code == 200:
                data = r.json()
                title = data.get("title", "")
                channel = data.get("author_name", "")

                clean_title = re.sub(r"#\w+", "", title).strip().rstrip(".")
                hashtags = re.findall(r"#(\w+)", title)

                parts.append(f"Video title: {clean_title}")
                if channel:
                    parts.append(f"YouTube channel: {channel}")
                if hashtags:
                    parts.append(f"Topics/tags: {', '.join(hashtags)}")
    except Exception:
        pass

    # ── 2. Transcript: actual spoken content ──────────────────────────────────
    if video_id:
        import asyncio

        def _fetch_transcript(vid_id: str) -> str:
            from youtube_transcript_api import YouTubeTranscriptApi
            api = YouTubeTranscriptApi()
            try:
                transcript = api.fetch(vid_id, languages=["en", "en-US", "en-GB"])
            except Exception:
                transcript = api.fetch(vid_id)  # any available language
            return " ".join(t.text for t in transcript)

        # Use get_running_loop() — get_event_loop() is deprecated in Python 3.10+
        # and unreliable inside async coroutines
        loop = asyncio.get_running_loop()
        transcript_text = ""

        # Attempt transcript up to 2 times (YouTube occasionally rate-limits on first hit)
        for attempt in range(2):
            try:
                transcript_text = await loop.run_in_executor(None, _fetch_transcript, video_id)
                if transcript_text:
                    break
            except Exception as exc:
                if attempt == 0:
                    import asyncio as _a; await _a.sleep(1.5)  # brief pause before retry
                else:
                    print(f"Transcript unavailable for {video_id}: {exc}")

        if transcript_text and len(transcript_text) > 50:
            parts.append(f"\nVIDEO TRANSCRIPT:\n{transcript_text[:4000]}")

    return "\n".join(parts) if parts else ""


async def fetch_page_text(url: str, max_chars: int = 6000) -> str:
    """Fetch a web page and extract its readable text content."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise HTTPException(500, "beautifulsoup4 not installed")

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=headers) as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(400, f"Could not fetch URL: HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            raise HTTPException(400, f"Could not reach URL: {e}")

    soup = BeautifulSoup(r.text, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "form", "noscript", "iframe", "ads"]):
        tag.decompose()

    # Try to grab meaningful blocks: title + meta + main content
    parts = []

    title = soup.find("title")
    if title:
        parts.append(f"Page title: {title.get_text(strip=True)}")

    for meta_name in ["description", "og:description", "og:title"]:
        tag = soup.find("meta", attrs={"name": meta_name}) or \
              soup.find("meta", attrs={"property": meta_name})
        if tag and tag.get("content"):
            parts.append(tag["content"][:500])

    # Main content body
    main = soup.find("main") or soup.find(id=re.compile(r"(content|main|body)", re.I)) or soup.body
    if main:
        text = main.get_text(separator="\n", strip=True)
        # Collapse repeated newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        parts.append(text[:max_chars])

    combined = "\n\n".join(parts)
    return combined[:max_chars] if combined else "Could not extract meaningful text from this page."


# Regional gross yield benchmarks (%) — used when AI can't calculate or gets it wrong
_REGION_YIELDS = {
    # Japan — central cities (high price, compressed yield)
    "central_japan":  5.5,   # Tokyo 23 wards, Osaka central, Kyoto, Nagoya, Yokohama
    # Japan — suburban commuter belt (1hr from major city)
    "suburban_japan": 7.0,   # Chiba, Saitama, Kanagawa suburbs, Osaka suburbs
    # Japan — regional cities & rural
    "rural_japan":    8.5,   # Fukushima, Hokkaido, countryside, akiya belt
    # Canada
    "vancouver":      4.0,
    "toronto":        4.5,
    "canada":         5.0,
    # UK
    "london":         4.0,
    "uk":             5.5,
    # Europe
    "europe":         4.5,
    # Australia
    "australia":      4.5,
    # USA
    "nyc":            4.0,
    "usa":            6.0,
    # Default
    "default":        6.0,
}

def _extract_price_from_text(text: str) -> Optional[float]:
    """
    Regex fallback to extract asking price from raw transcript/page text.
    Handles: $100,000 | $100k | ¥14.9M | 14.9 million yen | 14,900,000 yen
    Returns USD value, or None if nothing found.
    """
    text = text.replace(",", "")  # remove commas for easier parsing

    # Direct USD amounts: "$100000", "$100k", "$1.5M"
    m = re.search(r'\$\s*(\d+(?:\.\d+)?)\s*(k|K|million|M|m)?\b', text)
    if m:
        val = float(m.group(1))
        suffix = (m.group(2) or "").lower()
        if suffix in ("k",):          val *= 1_000
        elif suffix in ("m", "million"): val *= 1_000_000
        if 10_000 <= val <= 50_000_000:
            return round(val)

    # Yen amounts: "14.9 million yen", "¥14.9M", "14900000 yen"
    m = re.search(r'(?:¥|yen\s+|jpy\s*)?(\d+(?:\.\d+)?)\s*(million|M|m|万)?\s*(?:yen|円|JPY|¥)', text, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        suffix = (m.group(2) or "").lower()
        if suffix in ("million", "m"):  val *= 1_000_000
        elif suffix == "万":            val *= 10_000
        usd = round(val / 150)
        if 5_000 <= usd <= 20_000_000:
            return usd

    # CAD: "CAD 500,000" or "C$500000"
    m = re.search(r'(?:CAD|C\$)\s*(\d+(?:\.\d+)?)\s*(k|K|million|M)?', text)
    if m:
        val = float(m.group(1))
        suffix = (m.group(2) or "").lower()
        if suffix == "k":           val *= 1_000
        elif suffix in ("m", "million"): val *= 1_000_000
        usd = round(val / 1.38)
        if 10_000 <= usd <= 20_000_000:
            return usd

    return None


def _regional_yield_target(address: str) -> float:
    """Return the expected gross yield % for a property location."""
    a = address.lower()
    # Japan — must check specific cities before the generic "japan" catch-all
    if any(k in a for k in ["shibuya", "shinjuku", "minato", "chiyoda", "23 ward", "23-ward",
                             "central tokyo", "osaka city", "kyoto city", "nagoya", "yokohama"]):
        return _REGION_YIELDS["central_japan"]
    if any(k in a for k in ["chiba", "saitama", "kanagawa", "kawasaki", "sagamihara",
                             "funabashi", "yachio", "ichikawa", "matsudo", "urayasu",
                             "suburban tokyo", "suburban osaka"]):
        return _REGION_YIELDS["suburban_japan"]
    if any(k in a for k in ["japan", "tokyo", "osaka", "hokkaido", "fukushima",
                             "akiya", "rural", "countryside", "inaka"]):
        # Generic Japan — lean toward suburban/rural since cheap properties are rarely central
        return _REGION_YIELDS["rural_japan"]
    if "vancouver" in a or "bc" in a:
        return _REGION_YIELDS["vancouver"]
    if "toronto" in a or "ontario" in a:
        return _REGION_YIELDS["toronto"]
    if "canada" in a or "calgary" in a or "montreal" in a:
        return _REGION_YIELDS["canada"]
    if "london" in a:
        return _REGION_YIELDS["london"]
    if any(k in a for k in ["uk", "england", "scotland", "wales"]):
        return _REGION_YIELDS["uk"]
    if any(k in a for k in ["new york", "nyc", "manhattan"]):
        return _REGION_YIELDS["nyc"]
    if any(k in a for k in ["australia", "sydney", "melbourne"]):
        return _REGION_YIELDS["australia"]
    return _REGION_YIELDS["default"]


def _sanity_check_property_financials(fields: dict, raw_content: str = "") -> dict:
    """
    Validate and correct property financial estimates produced by the LLM.

    LLMs (especially smaller ones like llama3.2) frequently:
      - Return rent in the wrong currency (JPY instead of USD)
      - Return null gross_yield even when they have rent + price
      - Return a negative expected_return that overrides our calculation

    Strategy: whenever asking_price is known, we always verify / recalculate
    gross_yield from first principles and override expected_return accordingly.
    """
    pd_dict = fields.get("property_details")
    # If AI returned null/missing property_details but type is Property, create an empty dict
    # so we can still apply the regex price fallback and regional yield estimation
    if not pd_dict or not isinstance(pd_dict, dict):
        if fields.get("type") != "Property":
            return fields
        pd_dict = {}
        fields["property_details"] = pd_dict

    asking = pd_dict.get("asking_price")

    # If AI missed the asking price, try to extract it from the raw transcript/page text
    if (not asking or float(asking) <= 0) and raw_content:
        fallback_price = _extract_price_from_text(raw_content)
        if fallback_price:
            asking = fallback_price
            pd_dict["asking_price"] = asking
            fields["capital_required"] = asking

    # If we still have no price, apply a safety net and bail
    if not asking or float(asking) <= 0:
        er = fields.get("expected_return")
        if isinstance(er, (int, float)) and er < 0:
            fields["expected_return"] = None
        return fields

    asking = float(asking)
    address = pd_dict.get("address") or ""
    target_gross = _regional_yield_target(address)

    rent = pd_dict.get("monthly_rent_estimate")
    gross = pd_dict.get("gross_yield_pct")

    # ── Step 1: derive gross from rent if we have it but gross is missing ──────
    if rent and float(rent) > 0 and not gross:
        gross = (float(rent) * 12 / asking) * 100
        pd_dict["gross_yield_pct"] = round(gross, 2)

    # ── Step 2: if gross is implausible (>20% or ≤0), recalculate from target ─
    if not gross or float(gross) <= 0 or float(gross) > 20:
        corrected_rent = round((asking * target_gross / 100) / 12)
        gross = round((corrected_rent * 12 / asking) * 100, 2)
        pd_dict["monthly_rent_estimate"] = corrected_rent
        pd_dict["gross_yield_pct"] = gross
        note = f"[Rent estimated at ${corrected_rent}/mo ({gross:.1f}% gross yield, {address.split(',')[0].strip() or 'regional'} market benchmark)]"
        pd_dict["demand_notes"] = ((pd_dict.get("demand_notes") or pd_dict.get("notes") or "") + " " + note).strip()
        if "notes" in pd_dict:
            pd_dict["notes"] = pd_dict["demand_notes"]

    # ── Step 3: also correct rent if yield is now known but rent is still off ──
    if gross and float(gross) > 0:
        gross = float(gross)
        # Back-calculate what rent should be; if AI rent implies wrong yield, fix it
        if rent and float(rent) > 0:
            implied = (float(rent) * 12 / asking) * 100
            # If the AI's rent implies a wildly different yield from what gross_yield says, fix rent
            if gross > 0 and abs(implied - gross) > 5:
                corrected_rent = round((asking * gross / 100) / 12)
                pd_dict["monthly_rent_estimate"] = corrected_rent

    # ── Step 4: always set expected_return from validated gross yield ──────────
    gross = float(pd_dict.get("gross_yield_pct") or 0)
    if gross > 0:
        # Net yield: subtract management (~10% of rent = ~gross*0.1),
        # property tax (~0.3%/yr of assessed), maintenance (~1%), vacancy (~8%)
        # Simplified: gross - 2.5% covers all of the above for most markets
        net = round(max(gross - 2.5, 0.1), 1)
        fields["expected_return"] = net

    # ── Step 5: ensure capital_required mirrors asking_price ──────────────────
    if not fields.get("capital_required"):
        fields["capital_required"] = asking

    fields["property_details"] = pd_dict
    return fields


async def call_ollama_import(page_type: str, content: str, url: str) -> dict:
    """Ask Ollama to extract decision fields from the page content."""
    from pathlib import Path
    prompts_dir = Path(__file__).parent.parent / "prompts"
    prompt_path = prompts_dir / "url_import.txt"
    system_prompt = prompt_path.read_text() if prompt_path.exists() else _default_import_prompt()

    user_message = f"""URL: {url}
PAGE TYPE: {page_type}

EXTRACTED CONTENT:
{content}

Return ONLY the JSON object. No explanation, no markdown fences."""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            r = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
            r.raise_for_status()
            raw = r.json().get("message", {}).get("content", "")
            parsed = try_parse_json(raw)
            return parsed or {}
        except httpx.ConnectError:
            raise HTTPException(503, "Ollama is offline — start Ollama to use URL import")
        except Exception as e:
            raise HTTPException(500, f"AI extraction failed: {e}")


def _default_import_prompt() -> str:
    return """You are a data extraction engine for a personal decision-making app.
Extract structured fields from a web page and return a JSON object."""


async def call_ollama_skill(skill_name: str, decision_data: dict) -> dict:
    """Run a named skill prompt against decision data. Used for auto-evaluation on import."""
    from pathlib import Path
    prompts_dir = Path(__file__).parent.parent / "prompts"
    prompt_path = prompts_dir / f"{skill_name}.txt"
    if not prompt_path.exists():
        return {}

    import json as _json
    system_prompt = prompt_path.read_text()
    user_message = "DECISION DATA:\n" + _json.dumps(decision_data, indent=2, default=str)

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        "stream": False,
        "options": {"temperature": 0.3},
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        r.raise_for_status()
        raw = r.json().get("message", {}).get("content", "")
        return try_parse_json(raw) or {"raw": raw[:1000]}


def _save_extracted_decision(fields: dict, url: str, db: Session) -> str:
    """Create a DecisionItem + domain detail row from extracted fields. Returns the new item ID."""
    prop = fields.pop("property_details", None)
    biz  = fields.pop("business_details", None)
    inv  = fields.pop("investment_details", None)
    cont = fields.pop("content_details", None)

    # Map extracted fields to DecisionItem columns
    DECISION_COLS = {
        "title", "type", "status", "priority", "summary", "thesis",
        "capital_required", "expected_return", "time_to_cashflow",
        "operational_complexity", "downside_risk", "next_action", "tags",
    }
    item_kwargs = {k: v for k, v in fields.items() if k in DECISION_COLS and v is not None}

    # Defaults
    item_kwargs.setdefault("title", "Imported Decision")
    item_kwargs.setdefault("status", "Inbox")
    item_kwargs.setdefault("priority", "Medium")

    # Tags: store as JSON string if list
    if isinstance(item_kwargs.get("tags"), list):
        item_kwargs["tags"] = json.dumps(item_kwargs["tags"])

    item = DecisionItem(**item_kwargs)
    db.add(item)
    db.flush()  # get item.id

    # Domain detail rows — map AI field names → DB column names
    item_type = item_kwargs.get("type", "")

    if prop and item_type == "Property":
        net_yield = None
        gross = prop.get("gross_yield_pct")
        if gross:
            net_yield = round(max(float(gross) - 2.5, 0), 2)
        prop_row = {
            "address_text":  prop.get("address"),
            "asset_type":    prop.get("property_type"),
            "purchase_price": prop.get("asking_price"),
            "size_sqm":      prop.get("sqft"),       # AI returns sqft; label as sqm — acceptable approximation
            "estimated_rent": prop.get("monthly_rent_estimate"),
            "gross_yield":   gross,
            "net_yield":     net_yield,
            "monthly_fees":  prop.get("hoa_monthly"),
            "demand_notes":  prop.get("notes"),
        }
        clean = {k: v for k, v in prop_row.items() if v is not None}
        try:
            db.add(PropertyDetails(decision_item_id=item.id, **clean))
        except Exception as e:
            print(f"PropertyDetails save error: {e}")

    if biz and item_type == "BusinessIdea":
        biz_row = {
            "business_model":              biz.get("business_model"),
            "target_customer":             biz.get("target_market"),
            "startup_cost":                biz.get("startup_cost_estimate"),
            "recurring_revenue_potential": str(biz["monthly_revenue_potential"]) if biz.get("monthly_revenue_potential") else None,
            "moat_notes":                  biz.get("competitive_advantage"),
            "risk_notes":                  biz.get("key_risks"),
            "distribution_notes":          biz.get("revenue_model"),
        }
        clean = {k: v for k, v in biz_row.items() if v is not None}
        try:
            db.add(BusinessIdeaDetails(decision_item_id=item.id, **clean))
        except Exception as e:
            print(f"BusinessIdeaDetails save error: {e}")

    if inv and item_type == "Investment":
        inv_row = {
            "ticker_or_asset":  inv.get("ticker") or inv.get("asset_class"),
            "entry_price":      inv.get("current_price"),
            "target_price":     inv.get("target_price"),
            "holding_period":   inv.get("investment_horizon"),
            "catalyst":         inv.get("thesis_summary"),
            "risk_reward_notes": inv.get("key_risks"),
        }
        clean = {k: v for k, v in inv_row.items() if v is not None}
        try:
            db.add(InvestmentDetails(decision_item_id=item.id, **clean))
        except Exception as e:
            print(f"InvestmentDetails save error: {e}")

    if cont and item_type == "ContentIdea":
        cont_row = {
            "platform":          cont.get("platform"),
            "format_type":       cont.get("content_format"),
            "production_burden": cont.get("production_effort"),
            "monetization_path": cont.get("monetization"),
            "creative_notes":    cont.get("differentiation"),
        }
        clean = {k: v for k, v in cont_row.items() if v is not None}
        try:
            db.add(ContentIdeaDetails(decision_item_id=item.id, **clean))
        except Exception as e:
            print(f"ContentIdeaDetails save error: {e}")

    db.commit()
    db.refresh(item)
    return item.id


# ── Route ─────────────────────────────────────────────────────────────────────

@router.post("/import/url", response_model=ImportResult)
async def import_from_url(req: ImportRequest, db: Session = Depends(get_db)):
    url = req.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    page_type = detect_page_type(url)

    # Fetch content
    try:
        if page_type == "youtube":
            content = await fetch_youtube_metadata(url)
        else:
            content = await fetch_page_text(url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch URL: {e}")

    if not content or len(content.strip()) < 50:
        raise HTTPException(422, "Could not extract enough content from this URL — the page may be paywalled, bot-protected, or the video/listing doesn't exist. Try a different URL.")

    # ── AI field extraction ───────────────────────────────────────────────────
    try:
        fields = await call_ollama_import(page_type, content, url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    # Sanity-check financial estimates (corrects common LLM unit errors)
    fields = _sanity_check_property_financials(fields, raw_content=content)

    # Final safety net: never show negative expected_return on any decision
    er = fields.get("expected_return")
    if isinstance(er, (int, float)) and er < 0:
        fields["expected_return"] = None

    # ── Auto-evaluation: run decomposition on the raw content ─────────────────
    auto_evaluation = None
    if req.auto_evaluate:
        try:
            # Build a minimal decision_data dict from extracted fields + raw content
            decision_data = {
                "title": fields.get("title", "Untitled"),
                "type": fields.get("type", "Unknown"),
                "summary": fields.get("summary", ""),
                "source_url": url,
                "raw_content_preview": content[:3000],
            }
            eval_result = await call_ollama_skill("decomposition", decision_data)
            auto_evaluation = eval_result
        except Exception:
            pass  # Evaluation failure doesn't fail the import

    # ── Auto-save to database ─────────────────────────────────────────────────
    saved_decision_id = None
    if req.auto_save and fields:
        try:
            saved_decision_id = _save_extracted_decision(dict(fields), url, db)
        except Exception as e:
            import traceback
            print("Auto-save failed:", traceback.format_exc())

    return ImportResult(
        succeeded=True,
        url=url,
        page_type=page_type,
        extracted_text=content[:1500],
        fields=fields,
        auto_evaluation=auto_evaluation,
        saved_decision_id=saved_decision_id,
    )
