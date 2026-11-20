from fastapi import APIRouter
from backend.schemas.ai_schema import AIChatSchema
from backend.services.ai_service import ask_ai_hybrid

router = APIRouter(prefix="/api/ai", tags=["Trợ lý AI Hybrid Online/Offline"])

@router.post("/chat")
def ai_chat(payload: AIChatSchema):
    return ask_ai_hybrid(payload.question, payload.code, payload.error_message, payload.api_key)
