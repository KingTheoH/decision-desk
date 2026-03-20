"""
URL import endpoint — fetch a URL, extract its content, run Ollama to populate decision fields.
Supports: YouTube (oEmbed + description), property listings, articles, any web page.
"""
import re
import json
from typing import Optional
from urllib.parse import urlparse, parse_qs

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai_service import try_parse_json, OLLAMA_MODEL, OLLAMA_BASE_URL

router = APIRouter()


# ── Request / Response ────────────────────────────────────────────────────────

class ImportRequest(BaseModel):
    url: str

class ImportResult(BaseModel):
    succeeded: bool
    url: str
    page_type: str          # "youtube" | "property" | "article" | "unknown"
    extracted_text: str     # raw content we fed to the AI
    fields: dict            # suggested field values to pre-fill
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
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")
    qs = parse_qs(parsed.query)
    return qs.get("v", [None])[0]


async def fetch_youtube_metadata(url: str) -> str:
    """Use YouTube oEmbed to get title + channel. Extract hashtags from title for richer context."""
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    parts = []

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            r = await client.get(oembed_url)
            if r.status_code == 200:
                data = r.json()
                title = data.get("title", "")
                channel = data.get("author_name", "")
                channel_url = data.get("author_url", "")

                # Strip hashtags from title for a clean title, keep them separately
                clean_title = re.sub(r"#\w+", "", title).strip().rstrip(".")
                hashtags = re.findall(r"#(\w+)", title)

                parts.append(f"Video title: {clean_title}")
                if channel:
                    parts.append(f"YouTube channel: {channel}")
                if channel_url:
                    parts.append(f"Channel URL: {channel_url}")
                if hashtags:
                    parts.append(f"Hashtags/topics: {', '.join(hashtags)}")
                parts.append(f"Full title with tags: {title}")
    except Exception:
        pass

    # Try to get more from the page (won't always work — YouTube bot-protects most content)
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True,
                                      headers={"User-Agent": "Mozilla/5.0"}) as client:
            r = await client.get(url)
            if r.status_code == 200:
                for pattern in [
                    r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
                    r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']',
                ]:
                    m = re.search(pattern, r.text, re.DOTALL)
                    if m and len(m.group(1)) > 50:
                        parts.append(f"Description: {m.group(1)[:1500]}")
                        break
    except Exception:
        pass

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


# ── Route ─────────────────────────────────────────────────────────────────────

@router.post("/import/url", response_model=ImportResult)
async def import_from_url(req: ImportRequest):
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

    # AI extraction
    try:
        fields = await call_ollama_import(page_type, content, url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    return ImportResult(
        succeeded=True,
        url=url,
        page_type=page_type,
        extracted_text=content[:1000],  # Return a preview for debugging
        fields=fields,
    )
