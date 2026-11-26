"""
factcheck_service.py - Business Logic for Fact Checking.
Contains ALL fact-checking logic (moved from factcheck.py as part of 3-layer cleanup).
"""

import json
import re
from typing import Any, Dict
from urllib.parse import urlparse

from services.gemini_service import generate_text


def _is_valid_url(url: str) -> bool:
    """P0-2: a source URL is only usable if it is http/https with a host."""
    try:
        parsed = urlparse(str(url).strip())
    except Exception:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc) and " " not in str(url).strip()


def _clean_urls(urls) -> list:
    """Drop invalid/duplicate URLs; keep the first valid occurrence."""
    seen = set()
    out = []
    for u in urls or []:
        u = str(u).strip()
        if u and _is_valid_url(u) and u not in seen:
            seen.add(u)
            out.append(u)
    return out


def clean_pacing_tags(text: str) -> str:
    """Remove pacing markup tags for fact-checking while keeping natural text.

    P0-2: strip all 10 tags (not just the first 4) plus their closing tags.
    """
    if not text:
        return ""
    cleaned = re.sub(r"\[/?(pause(\s+[0-9.]+)?|slow|fast|whisper|deep|shock|urgent|solemn|loud)\]", " ", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


SYSTEM_INSTRUCTION_FACTCHECK = (
    "You are a rigorous, scientific fact-checker for educational content.\n"
    "Your job is to identify every factual claim in a script and verify it with reputable sources.\n"
    "You must categorize every claim into EXACTLY ONE of two labels:\n"
    "1. 'ĐÃ CHỨNG MINH': Confirmed by scientific consensus, peer-reviewed studies, government/academic institutions, or reputable historical records. Must include credible source URLs and a concise 1-sentence evidence summary.\n"
    "2. 'CHƯA RÕ': Unproven, widely disputed, anecdotal, unverified popular myth, exaggerated statistic, or lacking authoritative documentation. State clearly in 1 sentence why it is unclear or unproven.\n\n"
    "Output must be strictly valid JSON array format."
)


async def extract_and_verify_claims(script: str) -> Dict[str, Any]:
    """
    R4.1 - R4.4: Extract checkable atomic claims from script and verify them.
    Assigns each claim to 'ĐÃ CHỨNG MINH' or 'CHƯA RÕ'.
    """
    clean_text = clean_pacing_tags(script)
    if not clean_text:
        return {"success": True, "claims": [], "grounded": False, "notice": "Kịch bản trống."}

    prompt = (
        f"Analyze this script and extract all factual statements as atomic claims.\n\n"
        f"SCRIPT:\n\"\"\"{clean_text}\"\"\"\n\n"
        f"For each factual statement, produce a JSON object with:\n"
        f"- \"id\": string (e.g. \"claim_1\", \"claim_2\")\n"
        f"- \"text\": string (atomic fact statement in English)\n"
        f"- \"sentence\": string (exact sentence from the script where this statement appears)\n"
        f"- \"label\": exactly either \"ĐÃ CHỨNG MINH\" or \"CHƯA RÕ\"\n"
        f"- \"urls\": list of strings (real, credible reference URLs like Wikipedia, nature.com, science.org, noaa.gov, etc.)\n"
        f"- \"evidence\": string (1 concise sentence explaining the scientific proof or why it is unclear)\n\n"
        f"Return ONLY the JSON array starting with [ and ending with ]."
    )

    try:
        raw_res = await generate_text(prompt, system_instruction=SYSTEM_INSTRUCTION_FACTCHECK)
        # Parse JSON from response — handle markdown fences or raw string
        match = re.search(r"\[\s*\{.*\}\s*\]", raw_res, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            json_str = raw_res.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]

        parsed = json.loads(json_str.strip())
        claims = []
        for i, item in enumerate(parsed):
            cid = item.get("id") or f"claim_{i+1}"
            # P0-2: exact label match only; any other string is CHƯA RÕ.
            # The old loose "contains ĐÃ" check promoted long sentences.
            raw_label = str(item.get("label", "")).strip()
            label = "ĐÃ CHỨNG MINH" if raw_label == "ĐÃ CHỨNG MINH" else "CHƯA RÕ"

            urls = item.get("urls") or []
            if isinstance(urls, str):
                urls = [urls]

            claims.append({
                "id": cid,
                "text": str(item.get("text", "")).strip(),
                "sentence": str(item.get("sentence", "")).strip(),
                "label": label,
                # P0-2: drop URLs Gemini invented / malformed ones.
                "urls": _clean_urls(urls),
                "evidence": str(item.get("evidence", "")).strip(),
            })

        return {
            "success": True,
            "grounded": False,
            "notice": "Kết quả kiểm chứng được phân tích bởi Gemini. Vui lòng mở các liên kết nguồn để kiểm tra trực tiếp.",
            "claims": claims,
        }

    except Exception as e:
        raise RuntimeError(f"Lỗi phân tích kiểm chứng: {str(e)}")


async def rewrite_claim_safely(claim_text: str, sentence: str, reason: str = "") -> str:
    """
    R4.6: Rewrite a 'CHƯA RÕ' sentence to be cautious, safe, and accurate.
    """
    prompt = (
        f"You are editing a science YouTube Shorts script to make an unproven or disputed claim safe and scientifically accurate.\n\n"
        f"ORIGINAL SENTENCE: \"{sentence.strip()}\"\n"
        f"UNPROVEN CLAIM: \"{claim_text.strip()}\"\n"
    )
    if reason:
        prompt += f"REASON UNCLEAR: \"{reason.strip()}\"\n"

    prompt += (
        "\nTASK: Rewrite this single sentence in English to soften certainty and ensure scientific accuracy.\n"
        "Use phrases like 'estimates suggest', 'according to researchers', 'some studies indicate', or rephrase carefully.\n"
        "Keep it punchy for narration.\n"
        "Return ONLY the rewritten sentence in plain text, with no quotes or preamble."
    )

    return await generate_text(prompt)


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
