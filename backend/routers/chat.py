import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.llm_client import chat_with_resume

logger = logging.getLogger("resume-agent.chat")
router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    resume_context: str = ""
    jd_context: str = ""


@router.post("/chat")
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    try:
        return chat_with_resume(req.message, req.resume_context, req.jd_context)
    except Exception as e:
        logger.exception("Chat failed")
        raise HTTPException(status_code=500, detail=str(e))
