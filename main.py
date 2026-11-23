from pathlib import Path
import shutil
import subprocess
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

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
