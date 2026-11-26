"""
tts.py - Thin facade. All logic lives in infrastructure/ and services/.
Tests import from this module directly; it re-exports everything they need.
"""
from infrastructure.tts_providers import (
    TTSProvider,
    EdgeTTSProvider,
    KokoroTTSProvider,
    get_tts_provider,
    get_locked_voice,
    lock_voice,
    get_config,
    get_config_path,
)
from infrastructure.ffmpeg_processor import (
    ensure_ffmpeg,
    get_audio_enhancements,
    build_audio_filter_chain,
    generate_silence,
    concatenate_and_normalize,
    get_audio_duration,
    DEFAULT_AUDIO_ENHANCEMENTS,
)
from services.tts_service import synthesize_narration, TTSService
from pacing import PauseSegment, SpeechSegment

__all__ = [
    # Providers
    "TTSProvider",
    "EdgeTTSProvider",
    "KokoroTTSProvider",
    "get_tts_provider",
    "get_locked_voice",
    "lock_voice",
    "get_config",
    "get_config_path",
    # FFmpeg / audio helpers
    "ensure_ffmpeg",
    "get_audio_enhancements",
    "build_audio_filter_chain",
    "generate_silence",
    "concatenate_and_normalize",
    "get_audio_duration",
    "DEFAULT_AUDIO_ENHANCEMENTS",
    # High-level synthesis
    "synthesize_narration",
    "TTSService",
    # Pacing segments (kept in pacing.py)
    "PauseSegment",
    "SpeechSegment",
]
