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
import re
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

    def is_available(self) -> bool:
        """Check if this provider is currently available on the system."""
        return True

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
        """Check if kokoro_onnx is importable and model files exist."""
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
                    f"and voices at '{self.voices_path}'. Place kokoro-v0_19.onnx and voices.json in assets/kokoro/."
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

        # Parse rate into speed factor (+12% -> 1.12, -15% -> 0.85)
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

# ==========================================
# 3. Audio Processing Helpers & Enhancement Chain (FFmpeg)
# ==========================================

DEFAULT_AUDIO_ENHANCEMENTS = {
    "compression": True,
    "male_eq": True,
    "deesser": True,
    "reverb": True,
    "loudnorm": True,
}

def get_audio_enhancements(config_path: Optional[Path] = None) -> Dict[str, bool]:
    """Retrieve audio enhancement toggles from config.yaml or return defaults (R2.12)."""
    cfg = get_config()
    enh = cfg.get("audio_enhancements", {})
    return {
        "compression": enh.get("compression", DEFAULT_AUDIO_ENHANCEMENTS["compression"]),
        "male_eq": enh.get("male_eq", DEFAULT_AUDIO_ENHANCEMENTS["male_eq"]),
        "deesser": enh.get("deesser", DEFAULT_AUDIO_ENHANCEMENTS["deesser"]),
        "reverb": enh.get("reverb", DEFAULT_AUDIO_ENHANCEMENTS["reverb"]),
        "loudnorm": enh.get("loudnorm", DEFAULT_AUDIO_ENHANCEMENTS["loudnorm"]),
    }

def build_audio_filter_chain(
    enhancements: Optional[Dict[str, bool]] = None,
    target_lufs: float = -16.0,
) -> str:
    """
    Construct FFmpeg audio filter string based on enabled enhancement toggles (R2.12):
    - male_eq: highpass at 80Hz + body warmth at 120Hz + presence boost at 3500Hz
    - compression: subtle vocal compressor (acompressor)
    - deesser: reduces harsh sibilance (deesser)
    - reverb: very light room acoustic reflection (aecho)
    - loudnorm: EBU R128 loudness normalization
    """
    opts = dict(DEFAULT_AUDIO_ENHANCEMENTS)
    if enhancements:
        opts.update(enhancements)

    filters: List[str] = []

    # 1. Male EQ (rumble cut + low warmth + high-mid presence)
    if opts.get("male_eq", False):
        filters.append("highpass=f=80,equalizer=f=120:width_type=o:width=1.0:g=2.0,equalizer=f=3500:width_type=o:width=1.5:g=2.5")

    # 2. Vocal compression (smooth dynamics, thicken spoken dialogue)
    if opts.get("compression", False):
        filters.append("acompressor=threshold=-18dB:ratio=3:attack=10:release=100:makeup=2dB")

    # 3. De-esser (reduce harsh 's' frequencies)
    if opts.get("deesser", False):
        filters.append("deesser=i=0.5:m=0.5:f=0.5:s=o")

    # 4. Light Reverb (subtle room acoustic ambiance)
    if opts.get("reverb", False):
        filters.append("aecho=0.8:0.88:20:0.15")

    # 5. EBU R128 Loudness Normalization
    if opts.get("loudnorm", True):
        filters.append(f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11")

    return ",".join(filters) if filters else "anull"

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
    enhancements: Optional[Dict[str, bool]] = None,
) -> Path:
    """Concatenate audio segments and apply audio post-processing chain (R2.12)."""
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

        # Step 2: Apply post-processing filter chain (R2.12)
        active_filters = build_audio_filter_chain(enhancements, target_lufs=target_lufs)
        norm_cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_concat_file),
            "-af", active_filters,
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(final_output),
        ]
        res = subprocess.run(norm_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg audio processing chain failed: {res.stderr}")

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
    allow_fallback: bool = True,
    enhancements: Optional[Dict[str, bool]] = None,
) -> Tuple[Path, float]:
    """
    Synthesize complete narration with pacing markup, real pauses, and audio post-processing chain.
    Returns (output_path, duration_seconds).
    If the active provider (e.g. EdgeTTS) fails due to a network or connection error and
    a fallback provider (Kokoro) is configured and available, it falls back seamlessly.
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
        segment_files: List[Path] = []
        seg_index = 0

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
                # Cleanup any partial files
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

        # Concatenate and apply audio post-processing chain (R2.12)
        concatenate_and_normalize(segment_files, output_path, enhancements=enhancements)
        duration = get_audio_duration(output_path)
        return output_path, duration
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
