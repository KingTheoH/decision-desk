"""
AI service: dispatches skill runs to Ollama.
Gracefully handles Ollama being offline — the rest of the app works fine.
"""
import json
import re
from pathlib import Path
from typing import Optional, Any, Dict

import httpx

from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

SKILL_NAMES = [
    "decomposition", "scoring", "comparator", "assumptions",
    "compression", "patterns", "devils_advocate", "next_action",
    "property", "business", "content", "final_verdict",
]


def load_prompt(skill_name: str) -> str:
    path = PROMPTS_DIR / f"{skill_name}.txt"
    if path.exists():
        return path.read_text()
    return f"You are the {skill_name.replace('_', ' ').title()} engine in a decision command center."


def build_user_message(skill_name: str, decision_data: dict, extra_context: Optional[str]) -> str:
    """Combine decision data + extra context into a clean input message."""
    parts = []
    if decision_data:
        parts.append("DECISION DATA:\n" + json.dumps(decision_data, indent=2, default=str))
    if extra_context:
        parts.append("ADDITIONAL CONTEXT:\n" + extra_context)
    if not parts:
        parts.append("(No input data provided — demonstrate your output format with a placeholder.)")
    return "\n\n".join(parts)


def try_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """Try to extract JSON from LLM output. Models often wrap JSON in markdown fences
    and append evaluation notes after the closing brace — raw_decode handles this cleanly."""
    # Strip markdown fences (opening and closing)
    clean = re.sub(r"```(?:json)?", "", text).strip().strip("`").strip()

    # Try direct parse first (cleanest case)
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    # Use raw_decode: finds the first { and stops exactly at end of valid JSON,
    # ignoring any trailing text like "**Evaluation Notes:**..."
    start = clean.find("{")
    if start != -1:
        decoder = json.JSONDecoder()
        try:
            obj, _ = decoder.raw_decode(clean[start:])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass

    # Last resort: regex to find {...} block
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


async def run_skill(
    skill_name: str,
    decision_data: dict,
    extra_context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call Ollama with the skill prompt + decision data.
    Returns a dict with: succeeded, output (parsed), raw_text, error_message
    """
    if skill_name not in SKILL_NAMES:
        return {
            "succeeded": False,
            "error_message": f"Unknown skill: {skill_name}",
            "output": None,
            "raw_text": None,
        }

    system_prompt = load_prompt(skill_name)
    user_message = build_user_message(skill_name, decision_data, extra_context)

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        "stream": False,
        "options": {"temperature": 0.3},
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data.get("message", {}).get("content", "")
            parsed = try_parse_json(raw_text)
            return {
                "succeeded": True,
                "output": parsed,
                "raw_text": raw_text,
                "error_message": None,
            }
    except httpx.ConnectError:
        return {
            "succeeded": False,
            "error_message": "Ollama is offline. Install Ollama and run: ollama pull llama3.2",
            "output": None,
            "raw_text": None,
        }
    except Exception as e:
        return {
            "succeeded": False,
            "error_message": str(e),
            "output": None,
            "raw_text": None,
        }


async def check_ollama_status() -> Dict[str, Any]:
    """Return Ollama availability and loaded models."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            return {"available": True, "models": models, "current_model": OLLAMA_MODEL}
    except Exception:
        return {"available": False, "models": [], "current_model": OLLAMA_MODEL}
