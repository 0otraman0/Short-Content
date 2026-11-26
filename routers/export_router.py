"""
export_router.py - Presentation router for Export Pipeline & History Endpoints.
"""

from pathlib import Path
from typing import Dict, Optional
import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from repositories.project_repository import ProjectRepository
from services.export_service import ExportService

router = APIRouter(tags=["export"])
_repo = ProjectRepository()
_svc = ExportService(repository=_repo)

# In-memory job registry (process lifetime)
export_jobs: Dict[str, dict] = {}


async def _run_export_pipeline(project_id: str, job_id: str):
    """Run export pipeline in background and update job state."""
    job = export_jobs[job_id]
    job["status"] = "processing"

    def _progress(progress: int, step: str, duration: Optional[float] = None):
        job["progress"] = progress
        job["step"] = step
        if duration is not None:
            job["duration"] = duration

    try:
        job_meta = await _svc.execute_export(project_id, job_id, progress_callback=_progress)
        job["status"] = "completed"
        job["export_entry"] = job_meta.get("export_entry")
    except Exception as e:
        job["status"] = "failed"
        err_str = str(e)
        job["error"] = err_str
        job["step"] = f"Lỗi xuất: {err_str}"


@router.post("/api/projects/{project_id}/export")
async def start_export(project_id: str, background_tasks: BackgroundTasks):
    """Start export pipeline (audio + SRT + sources) in a background task."""
    project_data = _repo.get_project(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

    script = project_data.get("script", "").strip()
    if not script:
        raise HTTPException(status_code=400, detail="Kịch bản đang trống. Vui lòng nhập nội dung kịch bản trước khi xuất.")

    job_id = f"job_{uuid.uuid4().hex[:8]}"
    export_jobs[job_id] = {
        "job_id": job_id,
        "project_id": project_id,
        "status": "pending",
        "progress": 5,
        "step": "Đang chuẩn bị tiến trình xuất...",
        "duration": None,
        "error": None,
    }

    background_tasks.add_task(_run_export_pipeline, project_id, job_id)
    return {"job_id": job_id, "status": "started", "project_id": project_id}


@router.get("/api/projects/{project_id}/export-status/{job_id}")
async def get_export_status(project_id: str, job_id: str):
    """Poll export progress and status."""
    if job_id not in export_jobs:
        raise HTTPException(status_code=404, detail="Không tìm thấy tác vụ xuất.")
    return export_jobs[job_id]


@router.get("/api/projects/{project_id}/narration")
async def get_narration(project_id: str):
    """Download narration.mp3 for a project."""
    audio_file = _repo.get_folder(project_id) / "narration.mp3"
    if not audio_file.exists():
        raise HTTPException(status_code=404, detail="Narration audio chưa được tạo.")
    return FileResponse(audio_file, media_type="audio/mpeg", filename=f"{project_id}_narration.mp3")


@router.get("/api/projects/{project_id}/subtitles")
async def get_subtitles(project_id: str):
    """Download subtitles.srt for a project."""
    srt_file = _repo.get_folder(project_id) / "subtitles.srt"
    if not srt_file.exists():
        raise HTTPException(status_code=404, detail="Phụ đề SRT chưa được tạo.")
    return FileResponse(srt_file, media_type="text/plain", filename=f"{project_id}_subtitles.srt")


@router.get("/api/projects/{project_id}/sources")
async def get_sources(project_id: str):
    """Download sources.txt for a project."""
    sources_file = _repo.get_folder(project_id) / "sources.txt"
    if not sources_file.exists():
        raise HTTPException(status_code=404, detail="Nguồn tham khảo chưa được tạo.")
    return FileResponse(sources_file, media_type="text/plain", filename=f"{project_id}_sources.txt")


@router.get("/api/projects/{project_id}/exports")
async def list_project_exports(project_id: str):
    """List historical exports for a project."""
    project_data = _repo.get_project(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    return {"success": True, "exports": project_data.get("exports", [])}


@router.get("/api/projects/{project_id}/exports/{job_id}/audio")
async def get_job_audio(project_id: str, job_id: str):
    """Stream or download narration.mp3 of a specific export job."""
    folder = _repo.get_folder(project_id)
    job_audio = folder / "exports" / job_id / "narration.mp3"
    if not job_audio.exists():
        job_audio = folder / "narration.mp3"
        if not job_audio.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file audio cho tác vụ xuất này.")
    return FileResponse(job_audio, media_type="audio/mpeg", filename=f"{project_id}_{job_id}_narration.mp3")


@router.get("/api/projects/{project_id}/exports/{job_id}/subtitles")
async def get_job_subtitles(project_id: str, job_id: str):
    """Download subtitles.srt of a specific export job."""
    folder = _repo.get_folder(project_id)
    job_srt = folder / "exports" / job_id / "subtitles.srt"
    if not job_srt.exists():
        job_srt = folder / "subtitles.srt"
        if not job_srt.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file phụ đề cho tác vụ xuất này.")
    return FileResponse(job_srt, media_type="text/plain", filename=f"{project_id}_{job_id}_subtitles.srt")


@router.get("/api/projects/{project_id}/exports/{job_id}/sources")
async def get_job_sources(project_id: str, job_id: str):
    """Download sources.txt of a specific export job."""
    folder = _repo.get_folder(project_id)
    job_sources = folder / "exports" / job_id / "sources.txt"
    if not job_sources.exists():
        job_sources = folder / "sources.txt"
        if not job_sources.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file nguồn cho tác vụ xuất này.")
    return FileResponse(job_sources, media_type="text/plain", filename=f"{project_id}_{job_id}_sources.txt")
