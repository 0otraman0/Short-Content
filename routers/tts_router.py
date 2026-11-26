"""
tts_router.py - Presentation router for TTS voices, audio preview, paragraph takes, and audio FX config.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from infrastructure.ffmpeg_processor import ensure_ffmpeg, check_ffmpeg, get_config_path, get_audio_enhancements
from infrastructure.tts_providers import EdgeTTSProvider, get_locked_voice, lock_voice
from repositories.project_repository import ProjectRepository
from services.tts_service import synthesize_narration, TTSService

router = APIRouter(tags=["tts"])
_repo = ProjectRepository()

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "static" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class AudioEnhancementsUpdate(BaseModel):
    enhancements: Dict[str, bool]


class LockVoiceRequest(BaseModel):
    voice: str


class TTSPreviewRequest(BaseModel):
    text: str
    preset: Optional[str] = "mystery"
    voice: Optional[str] = None
    scope: Optional[str] = "paragraph"
    enhancements: Optional[Dict[str, bool]] = None


class ParagraphTakeRequest(BaseModel):
    project_id: str
    paragraph_index: int
    text: str
    preset: Optional[str] = "mystery"
    voice: Optional[str] = None
    enhancements: Optional[Dict[str, bool]] = None


# ------------------------------------------------------------------
# Audio Enhancement Config
# ------------------------------------------------------------------

@router.get("/api/config/audio-enhancements")
async def api_get_audio_enhancements():
    """Get active audio enhancement toggles (R2.12)."""
    return {"success": True, "enhancements": TTSService.get_enhancements()}


@router.post("/api/config/audio-enhancements")
async def api_save_audio_enhancements(payload: AudioEnhancementsUpdate):
    """Save audio enhancement toggles to config.yaml (R2.12)."""
    cfg_file = get_config_path()
    try:
        cfg = {}
        if cfg_file.exists():
            cfg = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        cfg["audio_enhancements"] = payload.enhancements
        cfg_file.write_text(yaml.dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return {"success": True, "enhancements": payload.enhancements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu cấu hình âm thanh: {str(e)}")


# ------------------------------------------------------------------
# Voice Management
# ------------------------------------------------------------------

@router.get("/api/tts/voices")
async def get_voices():
    """List available English male voices from edge-tts and return currently locked voice."""
    provider = EdgeTTSProvider()
    try:
        voices = await provider.list_english_male_voices()
    except Exception:
        voices = []
    locked = get_locked_voice()
    return {"current_voice": locked, "voices": voices}


@router.post("/api/tts/lock-voice")
async def save_locked_voice(payload: LockVoiceRequest):
    """Lock chosen voice into config.yaml permanently."""
    voice_name = payload.voice.strip()
    if not voice_name:
        raise HTTPException(status_code=400, detail="Mã giọng đọc không hợp lệ.")
    success = lock_voice(voice_name)
    if not success:
        raise HTTPException(status_code=500, detail="Không thể lưu giọng đọc vào config.yaml.")
    return {"success": True, "voice": voice_name}


# ------------------------------------------------------------------
# TTS Preview
# ------------------------------------------------------------------

@router.post("/api/tts/preview")
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
        enhancements = payload.enhancements if payload.enhancements is not None else get_audio_enhancements()
        _, duration = await synthesize_narration(
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


# ------------------------------------------------------------------
# Paragraph Multi-Take Regeneration (R2.11)
# ------------------------------------------------------------------

@router.post("/api/tts/paragraph-take")
async def create_paragraph_take(payload: ParagraphTakeRequest):
    """R2.11: Regenerate a take for a specific paragraph, keeping up to 4 takes."""
    ensure_ffmpeg()
    if not check_ffmpeg():
        raise HTTPException(status_code=500, detail="Chưa cài đặt FFmpeg trên máy tính.")

    clean_text = payload.text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Đoạn văn bản đang trống.")

    project_data = _repo.get_project(payload.project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

    folder = _repo.get_folder(payload.project_id)
    takes_store = project_data.get("takes", {})
    para_key = f"para_{payload.paragraph_index}"
    para_takes: List[Any] = takes_store.get(para_key, [])

    take_id = f"take_{uuid.uuid4().hex[:6]}"
    takes_dir = folder / "takes" / para_key
    takes_dir.mkdir(parents=True, exist_ok=True)
    take_file = takes_dir / f"{take_id}.mp3"

    try:
        _, duration = await synthesize_narration(
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
    _repo.save_project(project_data)

    return {
        "success": True,
        "take": take_record,
        "takes": para_takes,
        "paragraph_index": payload.paragraph_index,
    }


@router.get("/api/projects/{project_id}/paragraph-takes/{paragraph_index}")
async def get_paragraph_takes(project_id: str, paragraph_index: int):
    """Retrieve existing takes for a paragraph (R2.11)."""
    project_data = _repo.get_project(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    takes = project_data.get("takes", {}).get(f"para_{paragraph_index}", [])
    return {"success": True, "takes": takes}


@router.put("/api/projects/{project_id}/paragraph-takes/{paragraph_index}/select")
async def select_paragraph_take(project_id: str, paragraph_index: int, take_id: str):
    """Select preferred take for a paragraph (R2.11)."""
    project_data = _repo.get_project(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
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
    _repo.save_project(project_data)
    return {"success": True, "takes": para_takes}


@router.get("/api/projects/{project_id}/takes/{para_key}/{take_id}")
async def get_take_audio(project_id: str, para_key: str, take_id: str):
    """Serve audio file for a paragraph take."""
    # P0-3: get_take_file() sanitizes para_key/take_id (400 on traversal).
    try:
        take_file = _repo.get_take_file(project_id, para_key, take_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Mã đoạn/take không hợp lệ.")
    if not take_file.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file âm thanh của Take này.")
    return FileResponse(take_file, media_type="audio/mpeg", filename=f"{take_id}.mp3")
