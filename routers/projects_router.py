"""
projects_router.py - Presentation router for Project CRUD and Duplication.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.project_service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["projects"])
_svc = ProjectService()


class ProjectCreate(BaseModel):
    title: Optional[str] = "Dự án chưa đặt tên"
    script: Optional[str] = ""


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    script: Optional[str] = None
    target_duration: Optional[int] = None
    pacing_preset: Optional[str] = None
    status: Optional[str] = None
    claims: Optional[List[Dict[str, Any]]] = None


@router.get("")
async def list_projects():
    """List all saved projects sorted by updated_at descending."""
    return _svc.list_projects()


@router.post("")
async def create_project(payload: ProjectCreate):
    """Create a new project folder and project.json."""
    return _svc.create_project(title=payload.title or "Dự án chưa đặt tên", script=payload.script or "")


@router.get("/{project_id}")
async def get_project(project_id: str):
    """Retrieve full project data including script and claims."""
    project = _svc.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    return project


@router.put("/{project_id}")
async def update_project(project_id: str, payload: ProjectUpdate):
    """Update project details (script, title, duration, preset, claims)."""
    try:
        updates = payload.model_dump(exclude_unset=True)
        return _svc.update_project(project_id, updates)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật dự án: {str(e)}")


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete an entire project folder."""
    try:
        _svc.delete_project(project_id)
        return {"success": True, "message": "Đã xóa dự án thành công."}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")


@router.post("/{project_id}/duplicate")
async def duplicate_project(project_id: str):
    """Duplicate an existing project to a new ID."""
    try:
        return _svc.duplicate_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi nhân đôi dự án: {str(e)}")
