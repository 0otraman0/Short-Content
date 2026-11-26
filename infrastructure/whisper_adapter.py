"""
whisper_adapter.py - faster-whisper model loading, PyAV compatibility patch, and SRT transcription.
Extracted from captions.py as part of 3-Layer Architecture (Phase 12).
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Monkey-patch PyAV av.open to maintain compatibility with faster-whisper across all av versions
# (av >= 14 removed metadata_errors parameter)
try:
    import av
    _orig_av_open = av.open

    def _safe_av_open(*args, **kwargs):
        kwargs.pop("metadata_errors", None)
        return _orig_av_open(*args, **kwargs)

    av.open = _safe_av_open
except Exception:
    pass

from faster_whisper import WhisperModel


@dataclass
class WordTiming:
    word: str
    start: float
    end: float


@dataclass
class CaptionChunk:
    words: List[WordTiming]
    start: float
    end: float


_whisper_model: "WhisperModel | None" = None


def _get_whisper_model() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model


def format_srt_time(seconds: float) -> str:
    """Format float seconds to SRT timestamp format HH:MM:SS,mmm."""
    if seconds < 0:
        seconds = 0.0
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def get_word_timings(audio_file: Path) -> List[WordTiming]:
    """Transcribe audio and return word-level timestamps via faster-whisper."""
    model = _get_whisper_model()
    segments, _ = model.transcribe(str(audio_file), word_timestamps=True)
    words = []
    for seg in segments:
        if seg.words:
            for w in seg.words:
                words.append(WordTiming(word=w.word, start=w.start, end=w.end))
    return words


def group_into_chunks(words: List[WordTiming], words_per_line: int = 7) -> List[CaptionChunk]:
    """Group word timings into natural phrase chunks for subtitles."""
    if not words:
        return []
    chunks = []
    for i in range(0, len(words), words_per_line):
        group = words[i: i + words_per_line]
        chunks.append(CaptionChunk(
            words=group,
            start=group[0].start,
            end=group[-1].end,
        ))
    return chunks


def chunks_to_srt(chunks: List[CaptionChunk]) -> str:
    """Format caption chunks as an SRT subtitle string."""
    lines = []
    for idx, chunk in enumerate(chunks, 1):
        text = " ".join(w.word.strip() for w in chunk.words).strip()
        if not text:
            continue
        lines.append(str(idx))
        lines.append(f"{format_srt_time(chunk.start)} --> {format_srt_time(chunk.end)}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def transcribe_to_srt(audio_file: Path, output_srt: Path) -> Path:
    """Transcribe audio file and write SRT subtitle file."""
    audio_file = Path(audio_file)
    output_srt = Path(output_srt)
    output_srt.parent.mkdir(parents=True, exist_ok=True)
    words = get_word_timings(audio_file)
    chunks = group_into_chunks(words)
    srt_content = chunks_to_srt(chunks)
    output_srt.write_text(srt_content, encoding="utf-8")
    return output_srt
