"""
ffmpeg_processor.py - FFmpeg silence generation, audio filter chain, and loudness normalization.
Extracted from tts.py as part of 3-Layer Architecture (Phase 12).
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Dict, List, Optional
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


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


def check_ffmpeg() -> bool:
    """Check if ffmpeg executable exists in PATH."""
    return shutil.which("ffmpeg") is not None


ensure_ffmpeg()


def get_config_path() -> Path:
    return BASE_DIR / "config.yaml"


def get_config() -> dict:
    cfg_file = get_config_path()
    if cfg_file.exists():
        try:
            return yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        except Exception:
            pass
    return {}


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

    if opts.get("male_eq", False):
        filters.append("highpass=f=80,equalizer=f=120:width_type=o:width=1.0:g=2.0,equalizer=f=3500:width_type=o:width=1.5:g=2.5")
    if opts.get("compression", False):
        filters.append("acompressor=threshold=-18dB:ratio=3:attack=10:release=100:makeup=2dB")
    if opts.get("deesser", False):
        filters.append("deesser=i=0.5:m=0.5:f=0.5:s=o")
    if opts.get("reverb", False):
        filters.append("aecho=0.8:0.88:20:0.15")
    if opts.get("loudnorm", True):
        filters.append(f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11")

    return ",".join(filters) if filters else "anull"


def generate_silence(duration: float, output_file: Path, sample_rate: int = 24000) -> Path:
    """Generate a precise silent audio file of specified duration using FFmpeg."""
    output_file = Path(output_file)
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

    final_output = Path(final_output)
    final_output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        concat_list_file = tmp_path / "concat_list.txt"

        lines = []
        for f in audio_files:
            clean_path = str(Path(f).resolve()).replace("\\", "/")
            lines.append(f"file '{clean_path}'")
        concat_list_file.write_text("\n".join(lines), encoding="utf-8")

        raw_concat_file = tmp_path / "raw_concat.wav"

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
    """Return the real duration in seconds of an audio file via ffprobe."""
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
