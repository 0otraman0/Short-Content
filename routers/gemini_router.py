"""
gemini_router.py - Presentation router for Gemini AI Writing Assistant endpoints.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.gemini_service import GeminiService

router = APIRouter(prefix="/api/gemini", tags=["gemini"])


class SuggestNextRequest(BaseModel):
    script: str
    notes: Optional[str] = ""


class RewriteRequest(BaseModel):
    script: str
    notes: Optional[str] = ""
    target_duration: Optional[int] = None


class OutlineRequest(BaseModel):
    topic: str
    notes: Optional[str] = ""
    target_duration: Optional[int] = 90


class AutoPaceRequest(BaseModel):
    script: str


@router.post("/suggest-next")
async def api_suggest_next(payload: SuggestNextRequest):
    """R3.1: Suggest 3 alternative paragraphs continuing the script."""
    script = payload.script.strip()
    if not script:
        raise HTTPException(status_code=400, detail="Kịch bản đang trống. Vui lòng nhập nội dung hiện tại để gợi ý tiếp.")
    try:
        suggestions = await GeminiService.suggest_next(script, payload.notes or "")
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI gợi ý: {str(e)}")


@router.post("/rewrite")
async def api_rewrite(payload: RewriteRequest):
    """R3.2: Rewrite and polish draft keeping facts and spoken rhythm."""
    script = payload.script.strip()
    if not script:
        raise HTTPException(status_code=400, detail="Kịch bản đang trống. Vui lòng nhập nội dung cần viết lại.")
    try:
        rewritten = await GeminiService.rewrite(script, payload.notes or "", payload.target_duration)
        return {"success": True, "original": script, "rewritten": rewritten}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI viết lại: {str(e)}")


@router.post("/outline")
async def api_outline(payload: OutlineRequest):
    """R3.3: Generate outline and draft from a topic or fact."""
    topic = payload.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Chủ đề hoặc sự thật đang trống. Vui lòng nhập chủ đề.")
    try:
        draft = await GeminiService.outline(topic, payload.notes or "", payload.target_duration or 90)
        return {"success": True, "draft": draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI dựng khung: {str(e)}")


@router.post("/auto-pace")
async def api_auto_pace(payload: AutoPaceRequest):
    """R2.8: Insert pacing markup into script based on narrative structure."""
    script = payload.script.strip()
    if not script:
        raise HTTPException(status_code=400, detail="Kịch bản đang trống. Vui lòng nhập nội dung kịch bản cần thêm nhịp.")
    try:
        paced = await GeminiService.auto_pace(script)
        return {"success": True, "original": script, "paced": paced}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI tự thêm nhịp: {str(e)}")
