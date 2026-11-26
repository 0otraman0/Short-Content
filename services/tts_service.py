"""
tts_service.py - Business Logic for TTS Narration Synthesis.
Orchestrates pacing parsing, TTS provider calls, silence generation, and audio normalization.
"""

import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from infrastructure.ffmpeg_processor import (
    generate_silence,
    concatenate_and_normalize,
    get_audio_duration,
    get_audio_enhancements,
    ensure_ffmpeg,
)
from infrastructure.tts_providers import (
    TTSProvider,
    EdgeTTSProvider,
    KokoroTTSProvider,
    get_tts_provider,
    get_locked_voice,
    get_config,
)
from services.pacing_service import PauseSegment, SpeechSegment, parse_script


class TTSService:
    @staticmethod
    def get_enhancements(config_path: Optional[Path] = None) -> Dict[str, bool]:
        return get_audio_enhancements(config_path)


async def synthesize_narration(
    script: str,
    output_path: Path,
    preset_name: str = "mystery",
    voice: Optional[str] = None,
    provider: Optional[TTSProvider] = None,
    allow_fallback: bool = True,
    enhancements: Optional[Dict[str, bool]] = None,
) -> Tuple[Path, float]:
    """
    Synthesize complete narration with pacing markup, real pauses, and audio post-processing.
    Returns (output_path, duration_seconds).
    Falls back to Kokoro offline TTS on network failure when available.
    """
    ensure_ffmpeg()
    output_path = Path(output_path)
    cfg = get_config()
    chosen_voice = voice or get_locked_voice()
    active_provider = provider or get_tts_provider()
    fallback_provider_name = cfg.get("tts", {}).get("fallback_provider", "kokoro")

    segments = parse_script(script, preset_name=preset_name)
    if not segments:
        raise ValueError("Script contains no readable text.")

    temp_dir = Path(tempfile.mkdtemp(prefix="shorts_tts_"))
    try:
        async def _synthesize_with_provider(p: TTSProvider, v: str) -> List[Path]:
            files: List[Path] = []
            idx = 0
            for seg in segments:
                if isinstance(seg, SpeechSegment):
                    clean_text = seg.text.strip()
                    if not re.search(r"\w", clean_text):
                        continue
                    part_file = temp_dir / f"speech_{idx:04d}.mp3"
                    await p.synthesize_segment(
                        text=clean_text,
                        output_file=part_file,
                        voice=v,
                        rate=seg.rate,
                        pitch=seg.pitch,
                        volume=seg.volume,
                    )
                    files.append(part_file)
                    idx += 1
                elif isinstance(seg, PauseSegment):
                    if seg.duration > 0.05:
                        silence_file = temp_dir / f"silence_{idx:04d}.mp3"
                        generate_silence(duration=seg.duration, output_file=silence_file)
                        files.append(silence_file)
                        idx += 1
            return files

        segment_files: List[Path] = []
        try:
            segment_files = await _synthesize_with_provider(active_provider, chosen_voice)
        except Exception as primary_err:
            kokoro_fallback = KokoroTTSProvider()
            if (
                allow_fallback
                and str(fallback_provider_name).lower() == "kokoro"
                and kokoro_fallback.is_available()
            ):
                print(f"[TTS Fallback] Primary TTS provider failed ({primary_err}). Falling back to offline Kokoro TTS...")
                for f in segment_files:
                    try:
                        f.unlink(missing_ok=True)
                    except Exception:
                        pass
                segment_files.clear()
                kokoro_voice = cfg.get("tts", {}).get("kokoro", {}).get("voice", "am_adam")
                segment_files = await _synthesize_with_provider(kokoro_fallback, kokoro_voice)
            else:
                raise primary_err

        concatenate_and_normalize(segment_files, output_path, enhancements=enhancements)
        duration = get_audio_duration(output_path)
        return output_path, duration
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# Convenience re-export used by export_service
def get_audio_enhancements_svc(config_path: Optional[Path] = None) -> Dict[str, bool]:
    return get_audio_enhancements(config_path)
