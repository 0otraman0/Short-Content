"""
render.py - Core FFmpeg Video Rendering Engine.

Features:
- Auto-detects NVIDIA hardware acceleration (h264_nvenc) with fallback to CPU (libx264).
- Renders 1080x1920 30fps vertical video with dark placeholder background.
- Burns styled .ass subtitles directly into the video stream.
- Muxes AAC audio and outputs YouTube Shorts compliant output.mp4.
"""

import os
from pathlib import Path
import shutil
import subprocess
from typing import List, Optional, Tuple

def ensure_ffmpeg() -> bool:
    """Ensure ffmpeg is in process PATH, scanning common WinGet directories if needed."""
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

def escape_filter_path(p: Path) -> str:
    """
    Format a Windows filesystem path so it can be safely used inside an FFmpeg filter argument.
    On Windows, colons in drive letters (e.g. C:) must be escaped as C\\: and backslashes converted to /.
    """
    resolved = str(p.resolve()).replace("\\", "/")
    # Escape single quotes and colons
    escaped = resolved.replace("'", "'\\''").replace(":", "\\:")
    return escaped

def detect_video_encoder() -> Tuple[str, List[str]]:
    """
    Test if NVIDIA NVENC hardware encoder (h264_nvenc) is usable.
    Falls back to software libx264 if NVENC is absent or fails.
    """
    ensure_ffmpeg()
    try:
        # Run a quick 1-frame test using h264_nvenc
        test_cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "nullsrc=s=64x64",
            "-c:v", "h264_nvenc",
            "-frames:v", "1",
            "-f", "null", "-",
        ]
        res = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            return "h264_nvenc", ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "23"]
    except Exception:
        pass

    return "libx264", ["-c:v", "libx264", "-preset", "fast", "-crf", "22"]

def get_media_duration(media_file: Path) -> float:
    """Get the duration of a video or audio file in seconds."""
    ensure_ffmpeg()
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(media_file),
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return float(res.stdout.strip())
    except Exception:
        pass
    return 0.0

def render_video_with_placeholder(
    audio_path: Path,
    output_mp4: Path,
    ass_path: Optional[Path] = None,
    duration: Optional[float] = None,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
) -> Path:
    """
    Render a 9:16 vertical video with dark placeholder background, optional .ass subtitles, and narration audio.
    """
    ensure_ffmpeg()

    if not audio_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file âm thanh: {audio_path}")

    # Determine duration
    target_duration = duration or get_media_duration(audio_path)
    if target_duration <= 0.1:
        target_duration = 10.0 # sensible fallback

    output_mp4.parent.mkdir(parents=True, exist_ok=True)
    encoder_name, encoder_args = detect_video_encoder()

    # Build video filter graph
    # 1. Dark elegant gradient / solid background (0x12141c)
    video_source = f"color=c=0x12141c:s={width}x{height}:r={fps}:d={target_duration:.3f}"

    vf_filters = []
    if ass_path and ass_path.exists():
        escaped_ass = escape_filter_path(ass_path)
        vf_filters.append(f"ass='{escaped_ass}'")

    filter_arg = ",".join(vf_filters) if vf_filters else "null"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", video_source,
        "-i", str(audio_path),
        "-vf", filter_arg,
    ]
    cmd.extend(encoder_args)
    cmd.extend([
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{target_duration:.3f}",
        "-movflags", "+faststart",
        str(output_mp4),
    ])

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"Lỗi khi render video bằng FFmpeg (Encoder: {encoder_name}):\n{res.stderr}"
        )

    return output_mp4
