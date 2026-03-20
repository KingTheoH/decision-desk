from fastapi import APIRouter
from app.services.ai_service import check_ollama_status

router = APIRouter()


@router.get("/health")
async def health():
    ollama = await check_ollama_status()
    return {"status": "ok", "ollama": ollama}
