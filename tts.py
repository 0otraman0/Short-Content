"""
tts.py - Text-to-Speech Engine with Pacing, Silence Insertion, and Loudness Normalization.

Features:
- Abstract TTSProvider interface.
- EdgeTTSProvider using Microsoft Edge TTS (free, natural voices).
- Voice selection & locking to config.yaml.
- Synthesis of segmented pacing markup.
- FFmpeg-based silence generation, concatenation, and EBU R128 loudness normalization.
"""

from abc import ABC, abstractmethod
import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple
import edge_tts
import yaml

from pacing import PauseSegment, Segment, SpeechSegment, parse_script

BASE_DIR = Path(__file__).resolve().parent

def ensure_ffmpeg() -> bool:
    """Ensure ffmpeg is in PATH, scanning WinGet packages if needed."""
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

ensure_ffmpeg()

# ==========================================
# 1. Voice Locking & Config Management
# ==========================================

def get_config_path() -> Path:
    return BASE_DIR / "config.yaml"

def get_locked_voice(config_path: Optional[Path] = None) -> str:
    """Retrieve the locked English male voice from config.yaml, or a sensible default."""
    cfg_file = config_path or get_config_path()
    if cfg_file.exists():
        try:
            cfg = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
            voice = cfg.get("tts", {}).get("voice")
            if voice and isinstance(voice, str) and voice.strip():
                return voice.strip()
        except Exception:
            pass
    return "en-US-ChristopherNeural"

def lock_voice(voice_id: str, config_path: Optional[Path] = None) -> bool:
    """Lock a chosen English male voice into config.yaml permanently."""
    cfg_file = config_path or get_config_path()
    try:
        cfg = {}
        if cfg_file.exists():
            cfg = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        if "tts" not in cfg:
            cfg["tts"] = {}
        cfg["tts"]["voice"] = voice_id
        cfg_file.write_text(yaml.dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error locking voice in config: {e}")
        return False

# ==========================================
# 2. TTS Provider Interface & Implementation
# ==========================================

class TTSProvider(ABC):
    @abstractmethod
    async def synthesize_segment(
        self,
        text: str,
        output_file: Path,
        voice: str,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> Path:
        """Synthesize a single speech segment to an audio file."""
        pass

    @abstractmethod
    async def list_english_male_voices(self) -> List[Dict[str, str]]:
        """List available English male voices."""
        pass

class EdgeTTSProvider(TTSProvider):
    async def list_english_male_voices(self) -> List[Dict[str, str]]:
        """Fetch available English male voices from edge-tts."""
        voices = await edge_tts.list_voices()
        male_en_voices = []
        for v in voices:
            locale = v.get("Locale", "")
            gender = v.get("Gender", "")
            short_name = v.get("ShortName", "")
            if locale.startswith("en-") and gender.lower() == "male":
                male_en_voices.append({
                    "id": short_name,
                    "name": v.get("FriendlyName", short_name),
                    "locale": locale,
                    "gender": "Male",
                })
        # Sort so en-US voices come first
        male_en_voices.sort(key=lambda x: (not x["locale"].startswith("en-US"), x["name"]))
        return male_en_voices

    async def synthesize_segment(
        self,
        text: str,
        output_file: Path,
        voice: str,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> Path:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )
        await communicate.save(str(output_file))
        return output_file

# ==========================================
# 3. Audio Processing Helpers (FFmpeg)
# ==========================================

def generate_silence(duration: float, output_file: Path, sample_rate: int = 24000) -> Path:
    """Generate a precise silent audio file of specified duration using FFmpeg."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=r={sample_rate}:cl=mono",
        "-t", f"{duration:.3f}",
        "-c:a", "libmp3lame",
        "-q:a", "2",
        str(output_file),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg silence generation failed: {res.stderr}")
    return output_file

def concatenate_and_normalize(
    audio_files: List[Path],
    final_output: Path,
    target_lufs: float = -16.0,
) -> Path:
    """Concatenate audio segments and apply EBU R128 loudness normalization."""
    if not audio_files:
        raise ValueError("No audio files provided for concatenation.")

    final_output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        concat_list_file = tmp_path / "concat_list.txt"

        # Concat demuxer expects forward slashes and escaped single quotes
        lines = []
        for f in audio_files:
            clean_path = str(f.resolve()).replace("\\", "/")
            lines.append(f"file '{clean_path}'")
        concat_list_file.write_text("\n".join(lines), encoding="utf-8")

        raw_concat_file = tmp_path / "raw_concat.wav"

        # Step 1: Concatenate raw segments to WAV
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-c:a", "pcm_s16le",
            str(raw_concat_file),
        ]
        res = subprocess.run(concat_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg concat failed: {res.stderr}")

        # Step 2: Normalize loudness with loudnorm filter
        norm_cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_concat_file),
            "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(final_output),
        ]
        res = subprocess.run(norm_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg loudnorm failed: {res.stderr}")

    return final_output

def get_audio_duration(audio_file: Path) -> float:
    """Return the real duration in seconds of an audio file via ffprobe or ffmpeg."""
    ensure_ffmpeg()
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file),
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return float(res.stdout.strip())
    except Exception:
        pass
    return 0.0

# ==========================================
# 4. High-Level Narration Pipeline
# ==========================================

async def synthesize_narration(
    script: str,
    output_path: Path,
    preset_name: str = "mystery",
    voice: Optional[str] = None,
    provider: Optional[TTSProvider] = None,
) -> Tuple[Path, float]:
    """
    Synthesize complete narration with pacing markup, real pauses, and loudness normalization.
    Returns (output_path, duration_seconds).
    """
    ensure_ffmpeg()
    chosen_voice = voice or get_locked_voice()
    active_provider = provider or EdgeTTSProvider()

    segments = parse_script(script, preset_name=preset_name)
    if not segments:
        raise ValueError("Script contains no readable text.")

    temp_dir = Path(tempfile.mkdtemp(prefix="shorts_tts_"))
    try:
        segment_files: List[Path] = []
        seg_index = 0

        for seg in segments:
            if isinstance(seg, SpeechSegment):
                part_file = temp_dir / f"speech_{seg_index:04d}.mp3"
                await active_provider.synthesize_segment(
                    text=seg.text,
                    output_file=part_file,
                    voice=chosen_voice,
                    rate=seg.rate,
                    pitch=seg.pitch,
                    volume=seg.volume,
                )
                segment_files.append(part_file)
                seg_index += 1
            elif isinstance(seg, PauseSegment):
                if seg.duration > 0.05:
                    silence_file = temp_dir / f"silence_{seg_index:04d}.mp3"
                    generate_silence(duration=seg.duration, output_file=silence_file)
                    segment_files.append(silence_file)
                    seg_index += 1

        # Concatenate and normalize
        concatenate_and_normalize(segment_files, output_path)
        duration = get_audio_duration(output_path)
        return output_path, duration
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
