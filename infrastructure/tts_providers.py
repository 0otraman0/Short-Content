"""
tts_providers.py - TTS Provider interface + EdgeTTS + Kokoro implementations.
Extracted from tts.py as part of 3-Layer Architecture (Phase 12).
"""

import asyncio
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def get_config_path() -> Path:
    return BASE_DIR / "config.yaml"


def get_config() -> dict:
    """Read configuration dictionary from config.yaml."""
    cfg_file = get_config_path()
    if cfg_file.exists():
        try:
            return yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        except Exception:
            pass
    return {}


def get_locked_voice(config_path: Optional[Path] = None) -> str:
    """Retrieve the locked English male voice from config.yaml, or a sensible default."""
    cfg = get_config() if config_path is None else {}
    if config_path and config_path.exists():
        try:
            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except Exception:
            pass
    voice = cfg.get("tts", {}).get("voice")
    if voice and isinstance(voice, str) and voice.strip():
        return voice.strip()
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

    def is_available(self) -> bool:
        return True


class EdgeTTSProvider(TTSProvider):
    async def list_english_male_voices(self) -> List[Dict[str, str]]:
        """Fetch available English male voices from edge-tts."""
        import edge_tts
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
        import edge_tts
        output_file = Path(output_file)
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


class KokoroTTSProvider(TTSProvider):
    """
    Offline TTS Provider powered by Kokoro ONNX.
    Operates without internet connection using local model weights.
    """
    MALE_VOICES = [
        {"id": "am_adam", "name": "Kokoro - Adam (US Male)", "locale": "en-US", "gender": "Male"},
        {"id": "am_echo", "name": "Kokoro - Echo (US Male)", "locale": "en-US", "gender": "Male"},
        {"id": "am_eric", "name": "Kokoro - Eric (US Male)", "locale": "en-US", "gender": "Male"},
        {"id": "am_fenrir", "name": "Kokoro - Fenrir (US Male)", "locale": "en-US", "gender": "Male"},
        {"id": "am_liam", "name": "Kokoro - Liam (US Male)", "locale": "en-US", "gender": "Male"},
        {"id": "am_michael", "name": "Kokoro - Michael (US Male)", "locale": "en-US", "gender": "Male"},
        {"id": "am_onyx", "name": "Kokoro - Onyx (US Male)", "locale": "en-US", "gender": "Male"},
        {"id": "am_puck", "name": "Kokoro - Puck (US Male)", "locale": "en-US", "gender": "Male"},
        {"id": "bm_daniel", "name": "Kokoro - Daniel (UK Male)", "locale": "en-GB", "gender": "Male"},
        {"id": "bm_george", "name": "Kokoro - George (UK Male)", "locale": "en-GB", "gender": "Male"},
        {"id": "bm_lewis", "name": "Kokoro - Lewis (UK Male)", "locale": "en-GB", "gender": "Male"},
    ]

    def __init__(
        self,
        model_path: Optional[Path] = None,
        voices_path: Optional[Path] = None,
        default_voice: str = "am_adam",
    ):
        cfg = get_config()
        tts_cfg = cfg.get("tts", {}).get("kokoro", {})
        self.model_path = model_path or (BASE_DIR / tts_cfg.get("model_path", "assets/kokoro/kokoro-v0_19.onnx"))
        self.voices_path = voices_path or (BASE_DIR / tts_cfg.get("voices_path", "assets/kokoro/voices.json"))
        self.default_voice = tts_cfg.get("voice", default_voice)
        self._kokoro = None

    def is_available(self) -> bool:
        try:
            import kokoro_onnx  # noqa: F401
            return self.model_path.exists() and self.voices_path.exists()
        except ImportError:
            return False

    async def list_english_male_voices(self) -> List[Dict[str, str]]:
        return list(self.MALE_VOICES)

    def _get_kokoro_instance(self):
        if self._kokoro is None:
            if not self.model_path.exists() or not self.voices_path.exists():
                raise FileNotFoundError(
                    f"Kokoro model files not found. Expected model at '{self.model_path}' "
                    f"and voices at '{self.voices_path}'."
                )
            from kokoro_onnx import Kokoro
            self._kokoro = Kokoro(str(self.model_path), str(self.voices_path))
        return self._kokoro

    async def synthesize_segment(
        self,
        text: str,
        output_file: Path,
        voice: str = "am_adam",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> Path:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        kokoro = self._get_kokoro_instance()

        speed = 1.0
        match = re.search(r"([+-]?\d+(?:\.\d+)?)%", rate)
        if match:
            speed = max(0.5, min(2.0, 1.0 + float(match.group(1)) / 100.0))

        kokoro_voice = voice
        valid_ids = {v["id"] for v in self.MALE_VOICES}
        if kokoro_voice not in valid_ids:
            kokoro_voice = self.default_voice

        lang = "en-gb" if kokoro_voice.startswith("bm_") else "en-us"

        loop = asyncio.get_running_loop()
        samples, sample_rate = await loop.run_in_executor(
            None,
            lambda: kokoro.create(text=text, voice=kokoro_voice, speed=speed, lang=lang),
        )

        import numpy as np
        import wave

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            tmp_wav_path = Path(tmp_wav.name)

        try:
            int_samples = np.clip(samples * 32767, -32768, 32767).astype(np.int16)
            with wave.open(str(tmp_wav_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(int_samples.tobytes())

            cmd = [
                "ffmpeg", "-y",
                "-i", str(tmp_wav_path),
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                str(output_file),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg conversion for Kokoro audio failed: {res.stderr}")
            return output_file
        finally:
            if tmp_wav_path.exists():
                tmp_wav_path.unlink(missing_ok=True)


def get_tts_provider(provider_name: Optional[str] = None) -> TTSProvider:
    """Factory to retrieve requested or configured TTS provider."""
    if not provider_name:
        cfg = get_config()
        provider_name = cfg.get("tts", {}).get("provider", "edge-tts")
    if str(provider_name).lower() == "kokoro":
        return KokoroTTSProvider()
    return EdgeTTSProvider()
