"""
factcheck_router.py - Presentation router for Fact-Checking endpoints (R4).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from repositories.project_repository import ProjectRepository
from services.factcheck_service import FactCheckService

router = APIRouter(tags=["factcheck"])
_repo = ProjectRepository()


class ClaimsUpdateRequest(BaseModel):
    claims: List[Dict[str, Any]]


class RewriteSentenceRequest(BaseModel):
    claim_text: str
    sentence: str
    reason: Optional[str] = ""


@router.post("/api/projects/{project_id}/factcheck")
async def api_project_factcheck(project_id: str):
    """R4.1-R4.4: Run fact-checking on project script, save to project.json, return results."""
    project_data = _repo.get_project(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Không tìm thấy file dự án.")

    script = project_data.get("script", "").strip()
    if not script:
        raise HTTPException(status_code=400, detail="Kịch bản đang trống. Vui lòng nhập nội dung kịch bản trước khi kiểm chứng.")

    try:
        result = await FactCheckService.extract_and_verify(script)
        claims = result.get("claims", [])
        project_data["claims"] = claims
        project_data["updated_at"] = datetime.now().isoformat()
        _repo.save_project(project_data)
        return {
            "success": True,
            "claims": claims,
            "grounded": result.get("grounded", False),
            "notice": result.get("notice", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kiểm chứng: {str(e)}")


@router.put("/api/projects/{project_id}/claims")
async def api_update_project_claims(project_id: str, payload: ClaimsUpdateRequest):
    """R4.7: Update claims list (manual label override, edited URLs, custom sources)."""
    project_data = _repo.get_project(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Không tìm thấy file dự án.")

    try:
        project_data["claims"] = payload.claims
        project_data["updated_at"] = datetime.now().isoformat()
        _repo.save_project(project_data)
        return {"success": True, "claims": payload.claims}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật nguồn: {str(e)}")


@router.post("/api/factcheck/rewrite-sentence")
async def api_rewrite_sentence(payload: RewriteSentenceRequest):
    """R4.6: Rewrite an unproven sentence to be safe and scientifically accurate."""
    sentence = payload.sentence.strip()
    if not sentence:
        raise HTTPException(status_code=400, detail="Câu văn cần sửa đang trống.")
    try:
        safe_sentence = await FactCheckService.rewrite_safely(payload.claim_text, sentence, payload.reason or "")
        return {"success": True, "original": sentence, "safe_sentence": safe_sentence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi sửa câu: {str(e)}")
