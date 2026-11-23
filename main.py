from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional
import uuid
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE_DIR / ".env")

def ensure_ffmpeg() -> bool:
    """Ensure ffmpeg is in PATH, checking common WinGet install directories if needed."""
    if shutil.which("ffmpeg"):
        return True
    
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        winget_pkg = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_pkg.exists():
            for p in winget_pkg.glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe"):
                bin_dir = str(p.parent)
                os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
                return True
    return False

# Ensure FFmpeg is found and added to process PATH
ensure_ffmpeg()

app = FastAPI(title="Shorts Video Generator")

# Mount static files
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

def detect_gpu() -> dict:
    """Detect NVIDIA GPU availability using nvidia-smi."""
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0 and res.stdout.strip():
            gpu_info = res.stdout.strip().split("\n")[0]
            return {"has_gpu": True, "details": gpu_info, "encoder": "h264_nvenc"}
    except Exception:
        pass
    return {"has_gpu": False, "details": "CPU mode (libx264)", "encoder": "libx264"}

def check_ffmpeg() -> bool:
    """Check if ffmpeg executable exists in PATH."""
    return shutil.which("ffmpeg") is not None

def load_config() -> dict:
    cfg_file = BASE_DIR / "config.yaml"
    if cfg_file.exists():
        try:
            return yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        except Exception:
            return {}
    return {}

@app.get("/")
async def index():
    """Serve the main single-page UI."""
    index_file = static_dir / "index.html"
    if not index_file.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "Giao diện static/index.html chưa được khởi tạo."},
        )
    return FileResponse(index_file)

@app.get("/api/status")
async def system_status():
    """Return system readiness status."""
    gpu = detect_gpu()
    ffmpeg_installed = check_ffmpeg()
    config = load_config()
    
    # Check assets folders
    minecraft_dir = BASE_DIR / "assets" / "minecraft"
    music_dir = BASE_DIR / "assets" / "music"
    has_clips = minecraft_dir.exists() and any(minecraft_dir.glob("*.mp4"))
    has_music = music_dir.exists() and any(music_dir.glob("*.mp3"))

    return {
        "status": "ready",
        "gpu": gpu,
        "ffmpeg": ffmpeg_installed,
        "has_minecraft_clips": has_clips,
        "has_background_music": has_music,
        "config": {
            "voice": config.get("tts", {}).get("voice", "Chưa chọn"),
            "model": config.get("gemini", {}).get("model", "Chưa đặt"),
        },
    }

# ==========================================
# Projects Management (CRUD)
# ==========================================

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

def sanitize_project_id(project_id: str) -> str:
    """Validate project ID to prevent path traversal."""
    if not re.match(r"^[a-zA-Z0-9_-]+$", project_id):
        raise HTTPException(status_code=400, detail="Mã dự án không hợp lệ.")
    return project_id

def get_project_folder(project_id: str) -> Path:
    clean_id = sanitize_project_id(project_id)
    folder = PROJECTS_DIR / clean_id
    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    return folder

@app.get("/api/projects")
async def list_projects():
    """List all saved projects sorted by updated_at descending."""
    projects = []
    for item in PROJECTS_DIR.iterdir():
        if item.is_dir():
            json_file = item / "project.json"
            if json_file.exists():
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    projects.append({
                        "id": data.get("id", item.name),
                        "title": data.get("title", item.name),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at"),
                        "status": data.get("status", "draft"),
                        "target_duration": data.get("target_duration", 90),
                        "word_count": len(data.get("script", "").split()) if data.get("script") else 0,
                    })
                except Exception:
                    continue
    
    # Sort projects: newest updated first
    projects.sort(key=lambda p: p.get("updated_at") or "", reverse=True)
    return projects

@app.post("/api/projects")
async def create_project(payload: Optional[ProjectCreate] = None):
    """Create a new project folder and project.json."""
    if payload is None:
        payload = ProjectCreate()
    
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    folder = PROJECTS_DIR / project_id
    folder.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now().isoformat()
    project_data = {
        "id": project_id,
        "title": payload.title or "Dự án chưa đặt tên",
        "script": payload.script or "",
        "target_duration": 90,
        "pacing_preset": "mystery",
        "status": "draft",
        "created_at": now,
        "updated_at": now,
        "claims": [],
        "audio_file": None,
        "video_file": None,
    }
    
    json_file = folder / "project.json"
    json_file.write_text(json.dumps(project_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return project_data

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Retrieve full data for a single project."""
    folder = get_project_folder(project_id)
    json_file = folder / "project.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="File project.json không tồn tại.")
    try:
        return json.loads(json_file.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc dữ liệu dự án: {str(e)}")

@app.put("/api/projects/{project_id}")
async def update_project(project_id: str, payload: ProjectUpdate):
    """Update project fields and autosave script/settings."""
    folder = get_project_folder(project_id)
    json_file = folder / "project.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="File project.json không tồn tại.")
    
    try:
        data = json.loads(json_file.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc dữ liệu dự án: {str(e)}")
    
    # Update only provided fields
    updates = payload.model_dump(exclude_unset=True)
    data.update(updates)
    data["updated_at"] = datetime.now().isoformat()
    
    json_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

@app.post("/api/projects/{project_id}/duplicate")
async def duplicate_project(project_id: str):
    """Duplicate an existing project into a new project."""
    source_folder = get_project_folder(project_id)
    source_json = source_folder / "project.json"
    if not source_json.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file nguồn của dự án.")
    
    try:
        source_data = json.loads(source_json.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc dữ liệu dự án gốc: {str(e)}")
    
    new_id = f"proj_{uuid.uuid4().hex[:8]}"
    new_folder = PROJECTS_DIR / new_id
    new_folder.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now().isoformat()
    new_data = dict(source_data)
    new_data["id"] = new_id
    new_data["title"] = f"{source_data.get('title', 'Dự án')} (Bản sao)"
    new_data["created_at"] = now
    new_data["updated_at"] = now
    new_data["status"] = "draft"
    new_data["audio_file"] = None
    new_data["video_file"] = None
    
    new_json = new_folder / "project.json"
    new_json.write_text(json.dumps(new_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return new_data

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project and all associated files."""
    folder = get_project_folder(project_id)
    try:
        shutil.rmtree(folder)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể xóa thư mục dự án: {str(e)}")
    return {"success": True, "message": "Đã xóa dự án thành công.", "id": project_id}

