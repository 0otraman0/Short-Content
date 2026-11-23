"""
captions.py - Word-level Subtitle Generation and 9:16 ASS Styling using faster-whisper.

Features:
- Transcribes narration audio locally with faster-whisper (word-level timestamps).
- Groups words into short, punchy 2-4 word chunks.
- Formats 1080x1920 vertical video ASS subtitles with safe-area positioning.
- Highlights active word dynamically (karaoke style with yellow/gold accent).
"""

from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import List, Optional

# Disable Windows symlink warning for huggingface hub cache
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

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

def format_ass_time(seconds: float) -> str:
    """Format float seconds to ASS timestamp format H:MM:SS.cc."""
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
    """
    Generate Advanced SubStation Alpha (.ass) header for 9:16 vertical video.
    MarginV 860 places subtitles centered within the vertical safe area.
    """
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
    """
    Group words into 2-4 word display chunks.
    Breaks on sentence-ending punctuation or significant audio pauses.
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

        if len(current_chunk) >= max_words or ends_sentence or has_big_gap or i == len(words) - 1:
            c_start = current_chunk[0].start
            c_end = current_chunk[-1].end
            chunks.append(CaptionChunk(words=list(current_chunk), start=c_start, end=c_end))
            current_chunk = []

    return chunks

def build_ass_events(
    chunks: List[CaptionChunk],
    highlight_color: str = "&H0000FFFF&", # Yellow/Gold highlight
    default_color: str = "&H00FFFFFF&"   # Crisp White
) -> str:
    """
    Build ASS dialogue event lines.
    For each word in the chunk, renders the line highlighting that active word.
    """
    lines = []

    for chunk in chunks:
        words = chunk.words
        num_words = len(words)

        for active_idx in range(num_words):
            curr_w = words[active_idx]
            w_start = curr_w.start
            # If last word in chunk, end at chunk.end; otherwise end at next word start
            w_end = words[active_idx + 1].start if active_idx < num_words - 1 else curr_w.end
            if w_end <= w_start:
                w_end = w_start + 0.1

            # Format words text with active word highlighted
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

            line = f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{dialogue_text}"
            lines.append(line)

    return "\n".join(lines)

def transcribe_and_build_ass(
    audio_path: Path,
    output_ass_path: Path,
    model_size: str = "base.en",
    device: Optional[str] = None
) -> Path:
    """
    Transcribe audio with faster-whisper and write styled .ass subtitle file.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Determine execution device (auto-detect CUDA vs CPU)
    if device is None:
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            device = "cpu"

    compute_type = "float16" if device == "cuda" else "int8"

    try:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
    except Exception:
        # Fallback to CPU int8 if CUDA fails
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

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
    full_ass_content = header + "\n" + events + "\n"
    output_ass_path.write_text(full_ass_content, encoding="utf-8")

    return output_ass_path
