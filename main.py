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
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = BASE_DIR / "static" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE_DIR / ".env")

import asyncio
from tts import EdgeTTSProvider, get_locked_voice, lock_voice, synthesize_narration
from captions import transcribe_to_srt

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

app = FastAPI(title="Shorts Narration Tool")

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
            return {"has_gpu": True, "details": gpu_info}
    except Exception:
        pass
    return {"has_gpu": False, "details": "CPU mode"}

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
    """Return system readiness status and diagnostic warnings."""
    ensure_ffmpeg()
    gpu = detect_gpu()
    ffmpeg_installed = check_ffmpeg()
    config = load_config()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    has_gemini_key = bool(api_key and not api_key.startswith("your_"))

    warnings = []
    if not ffmpeg_installed:
        warnings.append({
            "code": "MISSING_FFMPEG",
            "message": "Chưa cài đặt FFmpeg trên máy tính.",
            "guide": "Mở PowerShell và chạy lệnh: winget install Gyan.FFmpeg rồi khởi động lại ứng dụng."
        })
    if not has_gemini_key:
        warnings.append({
            "code": "MISSING_GEMINI_KEY",
            "message": "Chưa cấu hình GEMINI_API_KEY.",
            "guide": "Mở file .env, điền khóa API miễn phí từ https://aistudio.google.com rồi khởi động lại start.bat."
        })

    return {
        "status": "ready" if (ffmpeg_installed and has_gemini_key) else "warning",
        "gpu": gpu,
        "ffmpeg": ffmpeg_installed,
        "has_gemini_key": has_gemini_key,
        "warnings": warnings,
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
        "subtitles_file": None,
        "sources_file": None,
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
    new_data["subtitles_file"] = None
    new_data["sources_file"] = None
    
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

# ==========================================
# TTS Preview & Voice Configuration
# ==========================================

class TTSPreviewRequest(BaseModel):
    text: str
    preset: Optional[str] = "mystery"
    voice: Optional[str] = None
    enhancements: Optional[Dict[str, bool]] = None
    scope: Optional[str] = "paragraph"

class LockVoiceRequest(BaseModel):
    voice: str

class AudioEnhancementsUpdate(BaseModel):
    enhancements: Dict[str, bool]

@app.get("/api/config/audio-enhancements")
async def api_get_audio_enhancements():
    """Get active audio enhancement toggles (R2.12)."""
    from tts import get_audio_enhancements
    return {"success": True, "enhancements": get_audio_enhancements()}

@app.post("/api/config/audio-enhancements")
async def api_save_audio_enhancements(payload: AudioEnhancementsUpdate):
    """Save audio enhancement toggles to config.yaml (R2.12)."""
    cfg_file = BASE_DIR / "config.yaml"
    try:
        cfg = {}
        if cfg_file.exists():
            cfg = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        cfg["audio_enhancements"] = payload.enhancements
        cfg_file.write_text(yaml.dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return {"success": True, "enhancements": payload.enhancements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu cấu hình âm thanh: {str(e)}")

# ==========================================
# Paragraph Multi-Take Regeneration (R2.11)
# ==========================================

class ParagraphTakeRequest(BaseModel):
    project_id: str
    paragraph_index: int
    text: str
    preset: Optional[str] = "mystery"
    voice: Optional[str] = None
    enhancements: Optional[Dict[str, bool]] = None

@app.post("/api/tts/paragraph-take")
async def create_paragraph_take(payload: ParagraphTakeRequest):
    """
    R2.11: Regenerate a take for a specific paragraph, keeping up to 4 takes to pick from.
    """
    ensure_ffmpeg()
    if not check_ffmpeg():
        raise HTTPException(status_code=500, detail="Chưa cài đặt FFmpeg trên máy tính.")

    clean_text = payload.text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Đoạn văn bản đang trống.")

    folder = get_project_folder(payload.project_id)
    json_file = folder / "project.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

    project_data = json.loads(json_file.read_text(encoding="utf-8"))
    takes_store = project_data.get("takes", {})
    para_key = f"para_{payload.paragraph_index}"
    para_takes = takes_store.get(para_key, [])

    take_id = f"take_{uuid.uuid4().hex[:6]}"
    takes_dir = folder / "takes" / para_key
    takes_dir.mkdir(parents=True, exist_ok=True)
    take_file = takes_dir / f"{take_id}.mp3"

    try:
        out_path, duration = await synthesize_narration(
            script=clean_text,
            output_path=take_file,
            preset_name=payload.preset or "mystery",
            voice=payload.voice or get_locked_voice(),
            enhancements=payload.enhancements,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo bản thu đoạn văn: {str(e)}")

    take_record = {
        "id": take_id,
        "take_number": len(para_takes) + 1,
        "created_at": datetime.now().isoformat(),
        "duration": round(duration, 2),
        "text": clean_text,
        "audio_url": f"/api/projects/{payload.project_id}/takes/{para_key}/{take_id}",
        "is_selected": len(para_takes) == 0,
    }

    # Keep at most 4 takes (remove oldest if exceeds 4)
    para_takes.append(take_record)
    if len(para_takes) > 4:
        oldest = para_takes.pop(0)
        old_file = takes_dir / f"{oldest['id']}.mp3"
        try:
            old_file.unlink(missing_ok=True)
        except Exception:
            pass

    for idx, t in enumerate(para_takes, 1):
        t["take_number"] = idx

    takes_store[para_key] = para_takes
    project_data["takes"] = takes_store
    json_file.write_text(json.dumps(project_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "success": True,
        "take": take_record,
        "takes": para_takes,
        "paragraph_index": payload.paragraph_index,
    }

@app.get("/api/projects/{project_id}/paragraph-takes/{paragraph_index}")
async def get_paragraph_takes(project_id: str, paragraph_index: int):
    """Retrieve existing takes for a paragraph (R2.11)."""
    folder = get_project_folder(project_id)
    json_file = folder / "project.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    project_data = json.loads(json_file.read_text(encoding="utf-8"))
    takes = project_data.get("takes", {}).get(f"para_{paragraph_index}", [])
    return {"success": True, "takes": takes}

@app.put("/api/projects/{project_id}/paragraph-takes/{paragraph_index}/select")
async def select_paragraph_take(project_id: str, paragraph_index: int, take_id: str):
    """Select preferred take for a paragraph (R2.11)."""
    folder = get_project_folder(project_id)
    json_file = folder / "project.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    project_data = json.loads(json_file.read_text(encoding="utf-8"))
    para_key = f"para_{paragraph_index}"
    para_takes = project_data.get("takes", {}).get(para_key, [])
    found = False
    for t in para_takes:
        if t["id"] == take_id:
            t["is_selected"] = True
            found = True
        else:
            t["is_selected"] = False
    if not found:
        raise HTTPException(status_code=404, detail="Không tìm thấy Take.")
    project_data["takes"][para_key] = para_takes
    json_file.write_text(json.dumps(project_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"success": True, "takes": para_takes}

@app.get("/api/projects/{project_id}/takes/{para_key}/{take_id}")
async def get_take_audio(project_id: str, para_key: str, take_id: str):
    """Serve audio file for a paragraph take."""
    folder = get_project_folder(project_id)
    take_file = folder / "takes" / para_key / f"{take_id}.mp3"
    if not take_file.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file âm thanh của Take này.")
    return FileResponse(take_file, media_type="audio/mpeg", filename=f"{take_id}.mp3")

@app.get("/api/tts/voices")
async def get_voices():
    """List available English male voices from edge-tts and return currently locked voice."""
    provider = EdgeTTSProvider()
    try:
        voices = await provider.list_english_male_voices()
    except Exception as e:
        voices = []
    locked = get_locked_voice()
    return {"current_voice": locked, "voices": voices}

@app.post("/api/tts/lock-voice")
async def save_locked_voice(payload: LockVoiceRequest):
    """Lock chosen voice into config.yaml permanently."""
    voice_name = payload.voice.strip()
    if not voice_name:
        raise HTTPException(status_code=400, detail="Mã giọng đọc không hợp lệ.")
    success = lock_voice(voice_name)
    if not success:
        raise HTTPException(status_code=500, detail="Không thể lưu giọng đọc vào config.yaml.")
    return {"success": True, "voice": voice_name}

@app.post("/api/tts/preview")
async def preview_tts(payload: TTSPreviewRequest):
    """Synthesize selected paragraph or text with pacing markup for instant in-browser playback."""
    ensure_ffmpeg()
    if not check_ffmpeg():
        raise HTTPException(
            status_code=500,
            detail="Chưa tìm thấy FFmpeg trên hệ thống. Vui lòng mở PowerShell và chạy: winget install Gyan.FFmpeg rồi khởi động lại ứng dụng.",
        )

    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Vui lòng bôi đen hoặc nhập đoạn văn bản cần nghe thử.")

    preview_id = f"preview_{uuid.uuid4().hex[:8]}"
    output_file = CACHE_DIR / f"{preview_id}.mp3"

    try:
        from tts import get_audio_enhancements
        enhancements = payload.enhancements if payload.enhancements is not None else get_audio_enhancements()
        out_path, duration = await synthesize_narration(
            script=text,
            output_path=output_file,
            preset_name=payload.preset or "mystery",
            voice=payload.voice or get_locked_voice(),
            enhancements=enhancements,
        )
        return {
            "success": True,
            "audio_url": f"/static/cache/{preview_id}.mp3",
            "duration": round(duration, 2),
            "preview_id": preview_id,
            "scope": payload.scope or "paragraph",
        }
    except Exception as e:
        err_msg = str(e)
        if any(k in err_msg.lower() for k in ["getaddrinfo", "connection", "connecterror", "offline"]):
            detail = "Lỗi kết nối giọng đọc: Không có mạng Internet để dùng EdgeTTS và chưa cài mô hình Kokoro offline."
        else:
            detail = f"Lỗi tạo giọng đọc thử nghiệm: {err_msg}"
        raise HTTPException(status_code=500, detail=detail)

# ==========================================
# Export Pipeline (Audio + SRT + Sources)
# ==========================================

export_jobs: Dict[str, dict] = {}

async def run_export_pipeline(project_id: str, job_id: str):
    """Orchestrate export: TTS Narration → Whisper SRT Subtitles → sources.txt."""
    job = export_jobs[job_id]
    job["status"] = "processing"

    try:
        ensure_ffmpeg()
        if not check_ffmpeg():
            raise RuntimeError("Chưa tìm thấy FFmpeg trên hệ thống. Vui lòng mở PowerShell và chạy: winget install Gyan.FFmpeg rồi khởi động lại ứng dụng.")

        folder = get_project_folder(project_id)
        json_file = folder / "project.json"
        if not json_file.exists():
            raise ValueError("Không tìm thấy file project.json của dự án.")

        project_data = json.loads(json_file.read_text(encoding="utf-8"))
        script = project_data.get("script", "").strip()
        if not script:
            raise ValueError("Kịch bản đang trống. Vui lòng nhập nội dung kịch bản trước khi xuất.")

        preset = project_data.get("pacing_preset", "mystery")
        voice = get_locked_voice()

        # Create isolated job directory (R5.8)
        exports_dir = folder / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        job_dir = exports_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Step 1 (20%): TTS narration synthesis
        job["step"] = "Đang tổng hợp giọng đọc (TTS)..."
        job["progress"] = 20

        audio_file = job_dir / "narration.mp3"
        from tts import get_audio_enhancements
        enhancements = project_data.get("audio_enhancements") or get_audio_enhancements()
        out_audio, duration = await synthesize_narration(
            script=script,
            output_path=audio_file,
            preset_name=preset,
            voice=voice,
            enhancements=enhancements,
        )
        job["duration"] = round(duration, 2)
        job["progress"] = 40

        # Step 2 (60%): faster-whisper SRT subtitle generation
        job["step"] = "Đang tạo phụ đề SRT (faster-whisper)..."
        job["progress"] = 60

        srt_file = job_dir / "subtitles.srt"
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, transcribe_to_srt, audio_file, srt_file)
        job["progress"] = 80

        # Step 3 (90%): Write sources.txt from claims or placeholder formatted for YouTube description (R4.9)
        job["step"] = "Đang tạo sources.txt..."
        job["progress"] = 90

        sources_file = job_dir / "sources.txt"
        claims = project_data.get("claims", [])
        if claims:
            lines = [
                "SOURCES & REFERENCES (YouTube Shorts Description):",
                "==================================================",
            ]
            for i, claim in enumerate(claims, 1):
                label = claim.get("label", "CHƯA RÕ")
                text_c = claim.get("text", "")
                urls = claim.get("urls", [])
                evidence = claim.get("evidence", "")

                status_mark = "Verified / Đã chứng minh" if "ĐÃ" in label else "Unverified / Chưa rõ"
                lines.append(f"\n{i}. {text_c}")
                lines.append(f"   Status: [{label}] ({status_mark})")
                if evidence:
                    lines.append(f"   Summary: {evidence}")
                if urls:
                    lines.append("   References:")
                    for url in urls:
                        lines.append(f"   - {url}")
                else:
                    lines.append("   References: (No source link provided)")

            lines.append("\n==================================================")
            lines.append("Produced with Shorts Narration Tool")
            sources_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            sources_file.write_text(
                "SOURCES & REFERENCES (YouTube Shorts Description):\n"
                "==================================================\n"
                "(No claims fact-checked yet. Use the Fact Check panel in the tool to verify and list references.)\n"
                "==================================================\n",
                encoding="utf-8",
            )

        # Write job metadata.json (R5.8)
        created_at_iso = datetime.now().isoformat()
        job_meta = {
            "id": job_id,
            "created_at": created_at_iso,
            "duration": round(duration, 2),
            "script": script,
            "script_preview": script[:120] + ("..." if len(script) > 120 else ""),
            "pacing_preset": preset,
            "voice": voice,
            "audio_file": "narration.mp3",
            "subtitles_file": "subtitles.srt",
            "sources_file": "sources.txt",
        }
        (job_dir / "metadata.json").write_text(json.dumps(job_meta, ensure_ascii=False, indent=2), encoding="utf-8")

        # Copy to root folder for backward compatibility
        shutil.copy2(audio_file, folder / "narration.mp3")
        shutil.copy2(srt_file, folder / "subtitles.srt")
        shutil.copy2(sources_file, folder / "sources.txt")

        # Step 4 (100%): Finalize project.json with history entry (R5.8)
        project_data["status"] = "exported"
        project_data["audio_file"] = "narration.mp3"
        project_data["subtitles_file"] = "subtitles.srt"
        project_data["sources_file"] = "sources.txt"
        project_data["actual_duration"] = round(duration, 2)
        project_data["updated_at"] = created_at_iso

        export_entry = {
            "id": job_id,
            "created_at": created_at_iso,
            "duration": round(duration, 2),
            "script_preview": job_meta["script_preview"],
            "pacing_preset": preset,
            "voice": voice,
            "audio_url": f"/api/projects/{project_id}/exports/{job_id}/audio",
            "subtitles_url": f"/api/projects/{project_id}/exports/{job_id}/subtitles",
            "sources_url": f"/api/projects/{project_id}/exports/{job_id}/sources",
        }
        exports_history = project_data.get("exports", [])
        exports_history.insert(0, export_entry)
        project_data["exports"] = exports_history

        json_file.write_text(json.dumps(project_data, ensure_ascii=False, indent=2), encoding="utf-8")

        job["step"] = "Hoàn tất! Gói xuất đã sẵn sàng."
        job["progress"] = 100
        job["status"] = "completed"
        job["export_entry"] = export_entry

    except Exception as e:
        job["status"] = "failed"
        err_str = str(e)
        job["error"] = err_str
        job["step"] = f"Lỗi xuất: {err_str}"

@app.post("/api/projects/{project_id}/export")
async def start_export(project_id: str, background_tasks: BackgroundTasks):
    """Start export pipeline (audio + SRT + sources) in a background task."""
    folder = get_project_folder(project_id)
    json_file = folder / "project.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

    project_data = json.loads(json_file.read_text(encoding="utf-8"))
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

    background_tasks.add_task(run_export_pipeline, project_id, job_id)

    return {"job_id": job_id, "status": "started", "project_id": project_id}

@app.get("/api/projects/{project_id}/export-status/{job_id}")
async def get_export_status(project_id: str, job_id: str):
    """Poll export progress and status."""
    if job_id not in export_jobs:
        raise HTTPException(status_code=404, detail="Không tìm thấy tác vụ xuất.")
    return export_jobs[job_id]

@app.get("/api/projects/{project_id}/narration")
async def get_narration(project_id: str):
    """Download narration.mp3 for a project."""
    folder = get_project_folder(project_id)
    audio_file = folder / "narration.mp3"
    if not audio_file.exists():
        raise HTTPException(status_code=404, detail="Narration audio chưa được tạo.")
    return FileResponse(audio_file, media_type="audio/mpeg", filename=f"{project_id}_narration.mp3")

@app.get("/api/projects/{project_id}/subtitles")
async def get_subtitles(project_id: str):
    """Download subtitles.srt for a project."""
    folder = get_project_folder(project_id)
    srt_file = folder / "subtitles.srt"
    if not srt_file.exists():
        raise HTTPException(status_code=404, detail="Phụ đề SRT chưa được tạo.")
    return FileResponse(srt_file, media_type="text/plain", filename=f"{project_id}_subtitles.srt")

@app.get("/api/projects/{project_id}/sources")
async def get_sources(project_id: str):
    """Download sources.txt for a project."""
    folder = get_project_folder(project_id)
    sources_file = folder / "sources.txt"
    if not sources_file.exists():
        raise HTTPException(status_code=404, detail="Nguồn tham khảo chưa được tạo.")
    return FileResponse(sources_file, media_type="text/plain", filename=f"{project_id}_sources.txt")

# ==========================================
# Job-Isolated Export History Endpoints (R5.8, R5.9)
# ==========================================

@app.get("/api/projects/{project_id}/exports")
async def list_project_exports(project_id: str):
    """List historical exports for a project."""
    folder = get_project_folder(project_id)
    json_file = folder / "project.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    try:
        project_data = json.loads(json_file.read_text(encoding="utf-8"))
        exports = project_data.get("exports", [])
        return {"success": True, "exports": exports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc lịch sử xuất: {str(e)}")

@app.get("/api/projects/{project_id}/exports/{job_id}/audio")
async def get_job_audio(project_id: str, job_id: str):
    """Stream or download narration.mp3 of a specific export job."""
    folder = get_project_folder(project_id)
    job_audio = folder / "exports" / job_id / "narration.mp3"
    if not job_audio.exists():
        job_audio = folder / "narration.mp3"
        if not job_audio.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file audio cho tác vụ xuất này.")
    return FileResponse(job_audio, media_type="audio/mpeg", filename=f"{project_id}_{job_id}_narration.mp3")

@app.get("/api/projects/{project_id}/exports/{job_id}/subtitles")
async def get_job_subtitles(project_id: str, job_id: str):
    """Download subtitles.srt of a specific export job."""
    folder = get_project_folder(project_id)
    job_srt = folder / "exports" / job_id / "subtitles.srt"
    if not job_srt.exists():
        job_srt = folder / "subtitles.srt"
        if not job_srt.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file phụ đề cho tác vụ xuất này.")
    return FileResponse(job_srt, media_type="text/plain", filename=f"{project_id}_{job_id}_subtitles.srt")

@app.get("/api/projects/{project_id}/exports/{job_id}/sources")
async def get_job_sources(project_id: str, job_id: str):
    """Download sources.txt of a specific export job."""
    folder = get_project_folder(project_id)
    job_sources = folder / "exports" / job_id / "sources.txt"
    if not job_sources.exists():
        job_sources = folder / "sources.txt"
        if not job_sources.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file nguồn cho tác vụ xuất này.")
    return FileResponse(job_sources, media_type="text/plain", filename=f"{project_id}_{job_id}_sources.txt")

# ==========================================
# Gemini Writing Assistant Endpoints (R3)
# ==========================================

from gemini_client import (
    suggest_next_paragraphs,
    rewrite_draft,
    outline_topic,
    auto_pace,
)

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

@app.post("/api/gemini/suggest-next")
async def api_suggest_next(payload: SuggestNextRequest):
    """R3.1: Suggest 3 alternative paragraphs continuing the script."""
    script = payload.script.strip()
    if not script:
        raise HTTPException(status_code=400, detail="Kịch bản đang trống. Vui lòng nhập nội dung hiện tại để gợi ý tiếp.")
    try:
        suggestions = await suggest_next_paragraphs(script, payload.notes or "")
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI gợi ý: {str(e)}")

@app.post("/api/gemini/rewrite")
async def api_rewrite(payload: RewriteRequest):
    """R3.2: Rewrite and polish draft keeping facts and spoken rhythm."""
    script = payload.script.strip()
    if not script:
        raise HTTPException(status_code=400, detail="Kịch bản đang trống. Vui lòng nhập nội dung cần viết lại.")
    try:
        rewritten = await rewrite_draft(script, payload.notes or "", payload.target_duration)
        return {"success": True, "original": script, "rewritten": rewritten}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI viết lại: {str(e)}")

@app.post("/api/gemini/outline")
async def api_outline(payload: OutlineRequest):
    """R3.3: Generate outline and draft from a topic or fact."""
    topic = payload.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Chủ đề hoặc sự thật đang trống. Vui lòng nhập chủ đề.")
    try:
        draft = await outline_topic(topic, payload.notes or "", payload.target_duration or 90)
        return {"success": True, "draft": draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI dựng khung: {str(e)}")

class AutoPaceRequest(BaseModel):
    script: str

@app.post("/api/gemini/auto-pace")
async def api_auto_pace(payload: AutoPaceRequest):
    """R2.8: Insert pacing markup into script based on narrative structure."""
    script = payload.script.strip()
    if not script:
        raise HTTPException(status_code=400, detail="Kịch bản đang trống. Vui lòng nhập nội dung kịch bản cần thêm nhịp.")
    try:
        paced = await auto_pace(script)
        return {"success": True, "original": script, "paced": paced}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI tự thêm nhịp: {str(e)}")

# ==========================================
# Fact-Checking Endpoints (R4)
# ==========================================

from factcheck import extract_and_verify_claims, rewrite_claim_safely

class ClaimsUpdateRequest(BaseModel):
    claims: List[Dict[str, Any]]

class RewriteSentenceRequest(BaseModel):
    claim_text: str
    sentence: str
    reason: Optional[str] = ""

@app.post("/api/projects/{project_id}/factcheck")
async def api_project_factcheck(project_id: str):
    """R4.1 - R4.4: Run fact-checking on the project's script, save to project.json, and return results."""
    folder = get_project_folder(project_id)
    json_file = folder / "project.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file dự án.")

    try:
        project_data = json.loads(json_file.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc dự án: {str(e)}")

    script = project_data.get("script", "").strip()
    if not script:
        raise HTTPException(status_code=400, detail="Kịch bản đang trống. Vui lòng nhập nội dung kịch bản trước khi kiểm chứng.")

    try:
        result = await extract_and_verify_claims(script)
        claims = result.get("claims", [])
        project_data["claims"] = claims
        project_data["updated_at"] = datetime.now().isoformat()
        json_file.write_text(json.dumps(project_data, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "success": True,
            "claims": claims,
            "grounded": result.get("grounded", False),
            "notice": result.get("notice", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kiểm chứng: {str(e)}")

@app.put("/api/projects/{project_id}/claims")
async def api_update_project_claims(project_id: str, payload: ClaimsUpdateRequest):
    """R4.7: Update claims list (manual label override, edited URLs, custom sources)."""
    folder = get_project_folder(project_id)
    json_file = folder / "project.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file dự án.")

    try:
        project_data = json.loads(json_file.read_text(encoding="utf-8"))
        project_data["claims"] = payload.claims
        project_data["updated_at"] = datetime.now().isoformat()
        json_file.write_text(json.dumps(project_data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"success": True, "claims": payload.claims}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật nguồn: {str(e)}")

@app.post("/api/factcheck/rewrite-sentence")
async def api_rewrite_sentence(payload: RewriteSentenceRequest):
    """R4.6: Rewrite an unproven sentence to be safe and scientifically accurate."""
    sentence = payload.sentence.strip()
    if not sentence:
        raise HTTPException(status_code=400, detail="Câu văn cần sửa đang trống.")
    try:
        safe_sentence = await rewrite_claim_safely(payload.claim_text, sentence, payload.reason or "")
        return {"success": True, "original": sentence, "safe_sentence": safe_sentence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi sửa câu: {str(e)}")


