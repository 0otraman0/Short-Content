"""
factcheck.py - Thin facade. All logic lives in services/factcheck_service.py.
Tests import from this module directly; it re-exports everything they need.
"""
from services.factcheck_service import (
    clean_pacing_tags,
    SYSTEM_INSTRUCTION_FACTCHECK,
    extract_and_verify_claims,
    rewrite_claim_safely,
    FactCheckService,
)

__all__ = [
    "clean_pacing_tags",
    "SYSTEM_INSTRUCTION_FACTCHECK",
    "extract_and_verify_claims",
    "rewrite_claim_safely",
    "FactCheckService",
]
