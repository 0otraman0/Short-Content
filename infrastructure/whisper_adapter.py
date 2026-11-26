"""
whisper_adapter.py - faster-whisper model loading, PyAV compatibility patch, and SRT/ASS transcription.
Part of 3-Layer Architecture (Infrastructure Layer).
"""

from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import List, Optional

# Disable Windows symlink warning for huggingface hub cache
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Monkey-patch PyAV av.open to maintain compatibility with faster-whisper across all av versions (av >= 14 removed metadata_errors)
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

_whisper_model: Optional[WhisperModel] = None
_whisper_model_size: Optional[str] = None

# P0-5: one model size everywhere. "base" and "base.en" are different
# models; the export path used base.en while the cache defaulted to base.
DEFAULT_WHISPER_MODEL = "base.en"


def get_whisper_model(model_size: str = DEFAULT_WHISPER_MODEL, device: Optional[str] = None) -> WhisperModel:
    global _whisper_model, _whisper_model_size
    if _whisper_model is None or _whisper_model_size != model_size:
        if device is None:
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except Exception:
                device = "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        try:
            _whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception:
            _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        _whisper_model_size = model_size
    return _whisper_model

# ==========================================
# 1. Standard SRT Subtitles (5-8 words/line)
# ==========================================

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

def chunk_words_for_srt(
    words: List[WordTiming],
    min_words: int = 5,
    max_words: int = 8,
    max_gap: float = 0.55
) -> List[CaptionChunk]:
    """
    Group words into full, natural spoken phrases of about 5-8 words per line.
    Breaks on sentence-ending punctuation or natural pauses.
    """
    if not words:
        return []

    chunks: List[CaptionChunk] = []
    current_chunk: List[WordTiming] = []

    for i, w in enumerate(words):
        current_chunk.append(w)

        clean_word = w.word.strip()
        ends_sentence = bool(re.search(r"[.!?]+$", clean_word))
        has_big_gap = False
        if i < len(words) - 1:
            next_start = words[i + 1].start
            if next_start - w.end > max_gap:
                has_big_gap = True

        should_break = (
            len(current_chunk) >= max_words
            or (ends_sentence and len(current_chunk) >= 3)
            or (has_big_gap and len(current_chunk) >= min_words)
            or i == len(words) - 1
        )

        if should_break:
            c_start = current_chunk[0].start
            c_end = current_chunk[-1].end
            chunks.append(CaptionChunk(words=list(current_chunk), start=c_start, end=c_end))
            current_chunk = []

    return chunks

def build_srt_content(chunks: List[CaptionChunk]) -> str:
    """
    Build standard SRT subtitle content with index, timestamps, and phrase text.
    """
    blocks = []
    for idx, chunk in enumerate(chunks, start=1):
        start_str = format_srt_time(chunk.start)
        end_str = format_srt_time(chunk.end)
        phrase_text = " ".join(w.word.strip() for w in chunk.words)

        block = f"{idx}\n{start_str} --> {end_str}\n{phrase_text}\n"
        blocks.append(block)

    return "\n".join(blocks)

def get_word_timings(audio_file: Path) -> List[WordTiming]:
    """Transcribe audio and return word-level timestamps via faster-whisper."""
    model = get_whisper_model()
    segments, _ = model.transcribe(str(audio_file), word_timestamps=True, language="en")
    words = []
    for seg in segments:
        if seg.words:
            for w in seg.words:
                cleaned = w.word.strip()
                if cleaned:
                    words.append(WordTiming(word=cleaned, start=w.start, end=w.end))
    return words

def group_into_chunks(words: List[WordTiming], words_per_line: int = 7) -> List[CaptionChunk]:
    return chunk_words_for_srt(words, min_words=min(5, words_per_line), max_words=max(8, words_per_line))

def chunks_to_srt(chunks: List[CaptionChunk]) -> str:
    return build_srt_content(chunks)

def transcribe_to_srt(
    audio_path: Path,
    output_srt_path: Path,
    model_size: str = DEFAULT_WHISPER_MODEL,
    device: Optional[str] = None
) -> Path:
    """
    Transcribe audio with faster-whisper and export clean .srt subtitle file
    with natural phrases of about 5-8 words per line.
    P0-5: reuse the cached model from get_whisper_model() instead of
    loading a second model for every export.
    """
    audio_path = Path(audio_path)
    output_srt_path = Path(output_srt_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file âm thanh: {audio_path}")

    model = get_whisper_model(model_size, device=device)

    segments_gen, info = model.transcribe(
        str(audio_path),
        word_timestamps=True,
        language="en"
    )

    words: List[WordTiming] = []
    for segment in segments_gen:
        if segment.words:
            for w in segment.words:
                cleaned = w.word.strip()
                if cleaned:
                    words.append(WordTiming(word=cleaned, start=w.start, end=w.end))

    chunks = chunk_words_for_srt(words, min_words=5, max_words=8)
    srt_content = build_srt_content(chunks)

    output_srt_path.parent.mkdir(parents=True, exist_ok=True)
    output_srt_path.write_text(srt_content, encoding="utf-8")

    return output_srt_path

# ==========================================
# 2. Backwards-compatible ASS Subtitles
# ==========================================

def format_ass_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"

def get_ass_header(
    width: int = 1080,
    height: int = 1920,
    font_name: str = "Arial Black",
    font_size: int = 72,
    margin_v: int = 860
) -> str:
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def chunk_words(
    words: List[WordTiming],
    min_words: int = 2,
    max_words: int = 4,
    max_gap: float = 0.4
) -> List[CaptionChunk]:
    if not words:
        return []

    chunks: List[CaptionChunk] = []
    current_chunk: List[WordTiming] = []

    for i, w in enumerate(words):
        current_chunk.append(w)
        clean_word = w.word.strip()
        ends_sentence = bool(re.search(r"[.!?]+$", clean_word))
        has_big_gap = False
        if i < len(words) - 1:
            next_start = words[i + 1].start
            if next_start - w.end > max_gap:
                has_big_gap = True

        if len(current_chunk) >= max_words or ends_sentence or has_big_gap or i == len(words) - 1:
            c_start = current_chunk[0].start
            c_end = current_chunk[-1].end
            chunks.append(CaptionChunk(words=list(current_chunk), start=c_start, end=c_end))
            current_chunk = []

    return chunks

def build_ass_events(
    chunks: List[CaptionChunk],
    highlight_color: str = "&H0000FFFF&",
    default_color: str = "&H00FFFFFF&"
) -> str:
    lines = []
    for chunk in chunks:
        words = chunk.words
        num_words = len(words)

        for active_idx in range(num_words):
            curr_w = words[active_idx]
            w_start = curr_w.start
            w_end = words[active_idx + 1].start if active_idx < num_words - 1 else curr_w.end
            if w_end <= w_start:
                w_end = w_start + 0.1

            formatted_words = []
            for j, w in enumerate(words):
                upper_word = w.word.strip().upper()
                if not upper_word:
                    continue
                if j == active_idx:
                    formatted_words.append(f"{{\\c{highlight_color}}}{upper_word}{{\\c{default_color}}}")
                else:
                    formatted_words.append(upper_word)

            dialogue_text = " ".join(formatted_words)
            start_str = format_ass_time(w_start)
            end_str = format_ass_time(w_end)
            lines.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{dialogue_text}")

    return "\n".join(lines)

def transcribe_and_build_ass(
    audio_path: Path,
    output_ass_path: Path,
    model_size: str = DEFAULT_WHISPER_MODEL,
    device: Optional[str] = None
) -> Path:
    audio_path = Path(audio_path)
    output_ass_path = Path(output_ass_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # P0-5: reuse the cached model here too.
    model = get_whisper_model(model_size, device=device)

    segments_gen, info = model.transcribe(
        str(audio_path),
        word_timestamps=True,
        language="en"
    )

    words: List[WordTiming] = []
    for segment in segments_gen:
        if segment.words:
            for w in segment.words:
                cleaned = w.word.strip()
                if cleaned:
                    words.append(WordTiming(word=cleaned, start=w.start, end=w.end))

    chunks = chunk_words(words)
    header = get_ass_header()
    events = build_ass_events(chunks)

    output_ass_path.parent.mkdir(parents=True, exist_ok=True)
    output_ass_path.write_text(header + "\n" + events + "\n", encoding="utf-8")
    return output_ass_path
