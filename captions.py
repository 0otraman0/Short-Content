"""
captions.py - Thin facade. All logic lives in infrastructure/whisper_adapter.py.
Tests import from this module directly; it re-exports everything they need.
"""

from infrastructure.whisper_adapter import (
    WordTiming,
    CaptionChunk,
    format_srt_time,
    chunk_words_for_srt,
    build_srt_content,
    get_word_timings,
    group_into_chunks,
    chunks_to_srt,
    transcribe_to_srt,
    format_ass_time,
    get_ass_header,
    chunk_words,
    build_ass_events,
    transcribe_and_build_ass,
)

__all__ = [
    "WordTiming",
    "CaptionChunk",
    "format_srt_time",
    "chunk_words_for_srt",
    "build_srt_content",
    "get_word_timings",
    "group_into_chunks",
    "chunks_to_srt",
    "transcribe_to_srt",
    "format_ass_time",
    "get_ass_header",
    "chunk_words",
    "build_ass_events",
    "transcribe_and_build_ass",
]
