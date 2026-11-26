"""
gemini_client.py - Thin facade. All logic lives in services/gemini_service.py.
Tests import from this module directly; it re-exports everything they need.
"""
from services.gemini_service import (
    generate_text,
    format_gemini_error,
    get_gemini_client,
    get_configured_model,
    load_config,
    SYSTEM_INSTRUCTION_WRITING,
    FALLBACK_MODELS,
    suggest_next_paragraphs,
    rewrite_draft,
    outline_topic,
    auto_pace,
    GeminiService,
)

__all__ = [
    "generate_text",
    "format_gemini_error",
    "get_gemini_client",
    "get_configured_model",
    "load_config",
    "SYSTEM_INSTRUCTION_WRITING",
    "FALLBACK_MODELS",
    "suggest_next_paragraphs",
    "rewrite_draft",
    "outline_topic",
    "auto_pace",
    "GeminiService",
]
