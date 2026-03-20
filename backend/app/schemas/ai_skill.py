from typing import Optional, Any, Dict
from pydantic import BaseModel


class SkillRunRequest(BaseModel):
    decision_item_id: Optional[str] = None
    skill_name: str
    extra_context: Optional[str] = None


class SkillRunResponse(BaseModel):
    id: str
    skill_name: str
    succeeded: bool
    error_message: Optional[str] = None
    output: Optional[Dict[str, Any]] = None   # parsed JSON from model
    raw_text: Optional[str] = None            # fallback raw output
