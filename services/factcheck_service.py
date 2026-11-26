"""
factcheck_service.py - Business Logic for Fact Checking.
Thin wrapper over factcheck module functions.
"""

from typing import Any, Dict

from factcheck import extract_and_verify_claims, rewrite_claim_safely, clean_pacing_tags


class FactCheckService:
    """Stateless service facade for all fact-checking operations."""

    @staticmethod
    def clean_tags(text: str) -> str:
        return clean_pacing_tags(text)

    @staticmethod
    async def extract_and_verify(script: str) -> Dict[str, Any]:
        return await extract_and_verify_claims(script)

    @staticmethod
    async def rewrite_safely(claim_text: str, sentence: str, reason: str = "") -> str:
        return await rewrite_claim_safely(claim_text, sentence, reason)
