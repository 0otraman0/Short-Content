"""
main.py - Presentation Layer Bootstrap for Shorts Narration Tool.

3-Layer Architecture:
  Presentation  : main.py + routers/ (HTTP API, static UI)
  Business Logic: services/ (project, tts, gemini, factcheck, export)
  Data Access   : repositories/ (project I/O) + infrastructure/ (TTS, FFmpeg, Whisper)
"""

import os
import subprocess
from pathlib import Path

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from infrastructure.ffmpeg_processor import ensure_ffmpeg, check_ffmpeg
from routers import (
    projects_router,
    tts_router,
    gemini_router,
    factcheck_router,
    export_router,
    topics_router,
)

# ---------------------------------------------------------------------------
# Base directories
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = BASE_DIR / "static" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")
ensure_ffmpeg()

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(title="Shorts Narration Tool")

static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount domain routers
app.include_router(projects_router)
app.include_router(tts_router)
app.include_router(gemini_router)
app.include_router(factcheck_router)
app.include_router(export_router)
app.include_router(topics_router)


# ---------------------------------------------------------------------------
# Bootstrap helpers
# ---------------------------------------------------------------------------

def _detect_gpu() -> dict:
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=3,
        )
        if res.returncode == 0 and res.stdout.strip():
            return {"has_gpu": True, "details": res.stdout.strip().split("\n")[0]}
    except Exception:
        pass
    return {"has_gpu": False, "details": "CPU mode"}


def _load_config() -> dict:
    cfg_file = BASE_DIR / "config.yaml"
    if cfg_file.exists():
        try:
            return yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        except Exception:
            pass
    return {}


# ---------------------------------------------------------------------------
# Core routes (kept in main.py – not domain-specific)
# ---------------------------------------------------------------------------

@app.get("/")
async def index():
    """Serve the main single-page UI."""
    index_file = static_dir / "index.html"
    if not index_file.exists():
        return JSONResponse(status_code=404, content={"error": "Giao diện static/index.html chưa được khởi tạo."})
    return FileResponse(index_file)


@app.get("/api/status")
async def system_status():
    """Return system readiness status and diagnostic warnings."""
    ensure_ffmpeg()
    gpu = _detect_gpu()
    ffmpeg_ok = check_ffmpeg()
    config = _load_config()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    has_gemini_key = bool(api_key and not api_key.startswith("your_"))

    warnings = []
    if not ffmpeg_ok:
        warnings.append({
            "code": "MISSING_FFMPEG",
            "message": "Chưa cài đặt FFmpeg trên máy tính.",
            "guide": "Mở PowerShell và chạy lệnh: winget install Gyan.FFmpeg rồi khởi động lại ứng dụng.",
        })
    if not has_gemini_key:
        warnings.append({
            "code": "MISSING_GEMINI_KEY",
            "message": "Chưa cấu hình GEMINI_API_KEY.",
            "guide": "Mở file .env, điền khóa API miễn phí từ https://aistudio.google.com rồi khởi động lại start.bat.",
        })

    return {
        "status": "ready" if (ffmpeg_ok and has_gemini_key) else "warning",
        "gpu": gpu,
        "ffmpeg": ffmpeg_ok,
        "has_gemini_key": has_gemini_key,
        "warnings": warnings,
        "config": {
            "voice": config.get("tts", {}).get("voice", "Chưa chọn"),
            "model": config.get("gemini", {}).get("model", "Chưa đặt"),
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
