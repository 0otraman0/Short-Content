"""
gemini_service.py - Business Logic for Gemini AI Writing Assistant.
Thin wrapper over gemini_client functions to enforce service-layer boundary.
"""

from typing import List, Optional

# Import all helpers from the existing gemini_client (unchanged root module)
from gemini_client import (
    generate_text,
    format_gemini_error,
    suggest_next_paragraphs,
    rewrite_draft,
    outline_topic,
    auto_pace,
)


class GeminiService:
    """Stateless service facade for all Gemini AI operations."""

    @staticmethod
    async def suggest_next(script: str, notes: str = "", count: int = 3) -> List[str]:
        return await suggest_next_paragraphs(script, notes)

    @staticmethod
    async def rewrite(script: str, notes: str = "", target_duration: Optional[int] = None) -> str:
        return await rewrite_draft(script, notes, target_duration)

    @staticmethod
    async def outline(topic: str, notes: str = "", target_duration: int = 90) -> str:
        return await outline_topic(topic, notes, target_duration)

    @staticmethod
    async def auto_pace(script: str) -> str:
        return await auto_pace(script)
