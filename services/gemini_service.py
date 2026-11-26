"""
gemini_service.py - Business Logic for Gemini AI Writing Assistant.
Contains ALL Gemini logic (moved from gemini_client.py as part of 3-layer cleanup).
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError, ClientError, ServerError
except ImportError:
    genai = None
    types = None
    APIError = Exception
    ClientError = Exception
    ServerError = Exception

# R3.4: Mandatory writing rules for YouTube Shorts script narration
SYSTEM_INSTRUCTION_WRITING = (
    "You are an expert scriptwriter for YouTube Shorts specializing in fascinating, verified science and real-world facts. "
    "You write for English-speaking viewers abroad. Follow these mandatory rules:\n"
    "1. Write exclusively in English.\n"
    "2. NEVER invent or fabricate statistics, dates, names, or sources.\n"
    "3. If any number, date, or fact is uncertain or unverified, write the sentence cautiously without false certainty and flag it with '[VERIFY]'.\n"
    "4. Hook the listener in the very first sentence.\n"
    "5. Do NOT use clickbait lies or deceptive statements.\n\n"
    "SPEAKABILITY & NARRATION RULES (R3.4):\n"
    "- Alternate short, punchy sentences with longer flowing ones to create a dynamic, musical rhythm.\n"
    "- Use commas, em-dashes (—), and ellipses (...) strategically for natural spoken pauses and breathing room.\n"
    "- Place the punchline, key fact, or shocking number at the very end of the sentence for maximum suspense and auditory impact.\n"
    "- Write numbers as spoken words whenever ambiguous (e.g. 'twenty-five hundred' instead of '2,500'; 'four hundred years' instead of '400 yrs') to guarantee accurate neural TTS pronunciation."
)

FALLBACK_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
]


def load_config() -> dict:
    cfg_file = BASE_DIR / "config.yaml"
    if cfg_file.exists():
        try:
            return yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        except Exception:
            return {}
    return {}


def get_configured_model() -> str:
    """Read configured model from config.yaml with default fallback."""
    cfg = load_config()
    return cfg.get("gemini", {}).get("model", "gemini-flash-lite-latest")


def format_gemini_error(err: Exception) -> str:
    """Translate raw Gemini / network errors into clear, friendly, actionable Vietnamese (R5.7)."""
    err_str = str(err)
    err_lower = err_str.lower()

    if "429" in err_str or "resource_exhausted" in err_lower or "quota" in err_lower or "rate limit" in err_lower:
        return (
            "Đã vượt quá giới hạn lượt gọi Gemini API (Rate limit 429 / Quota exhausted). "
            "Hệ thống đã tự động thử lại nhưng máy chủ vẫn bận. Vui lòng chờ 30-60 giây rồi thử lại."
        )
    if "api_key" in err_lower or "401" in err_str or "403" in err_str or "permission_denied" in err_lower:
        return (
            "Khóa GEMINI_API_KEY trong file .env không hợp lệ hoặc chưa được cấp quyền. "
            "Vui lòng kiểm tra lại khóa API tại https://aistudio.google.com và cập nhật vào file .env."
        )
    if "503" in err_str or "unavailable" in err_lower or "high demand" in err_lower:
        return (
            "Máy chủ Google Gemini đang quá tải tạm thời (503 High Demand / Service Unavailable). "
            "Hệ thống đã tự động thử các model dự phòng nhưng chưa phản hồi. Vui lòng thử lại sau giây lát."
        )
    if any(k in err_lower for k in ["getaddrinfo failed", "connection", "timeout", "timed out", "handshake", "offline", "network"]):
        return (
            "Không thể kết nối đến máy chủ Google Gemini do sự cố mạng. "
            "Vui lòng kiểm tra kết nối Internet của bạn."
        )
    return f"Lỗi từ dịch vụ Gemini AI: {err_str}"


def get_gemini_client() -> Any:
    """Initialize and return google-genai Client using API key from .env."""
    if genai is None:
        raise RuntimeError("Thư viện 'google-genai' chưa được cài đặt. Vui lòng chạy lệnh: pip install google-genai.")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key.startswith("your_"):
        raise ValueError(
            "Chưa cấu hình GEMINI_API_KEY trong file .env. "
            "Vui lòng mở file .env, nhập khóa API miễn phí từ Google AI Studio (https://aistudio.google.com) và khởi động lại ứng dụng."
        )
    return genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})


async def generate_text(
    prompt: str,
    system_instruction: Optional[str] = SYSTEM_INSTRUCTION_WRITING,
    model: Optional[str] = None,
    max_retries: int = 3,
) -> str:
    """Generate text using Gemini with automatic retry on rate limits or service unavailability."""
    client = get_gemini_client()
    target_model = model or get_configured_model()

    models_to_try = [target_model]
    for fb in FALLBACK_MODELS:
        if fb != target_model and fb not in models_to_try:
            models_to_try.append(fb)

    last_error = None

    for m in models_to_try:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        ) if system_instruction else types.GenerateContentConfig(temperature=0.7)

        for attempt in range(max_retries):
            try:
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model=m,
                        contents=prompt,
                        config=config,
                    ),
                )
                if response and response.text:
                    return response.text.strip()
                raise ValueError("Gemini API trả về nội dung rỗng.")

            except Exception as e:
                err_str = str(e)
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2.5
                    print(f"[Gemini Retry] Model {m} (lần {attempt + 1}/{max_retries}): {err_str[:60]}... Đợi {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                break

    raise RuntimeError(format_gemini_error(last_error))


# ------------------------------------------------------------------
# Specialized Assistant Helpers
# ------------------------------------------------------------------

async def suggest_next_paragraphs(script_so_far: str, notes: str = "") -> List[str]:
    """R3.1: Suggest 3 alternative next paragraphs continuing the story."""
    prompt = (
        f"The user is writing a YouTube Shorts script about science/curious facts.\n\n"
        f"CURRENT SCRIPT SO FAR:\n\"\"\"{script_so_far.strip()}\"\"\"\n\n"
    )
    if notes.strip():
        prompt += f"USER NOTES / DIRECTION:\n{notes.strip()}\n\n"

    prompt += (
        "TASK: Provide EXACTLY 3 alternative options for the next paragraph (each 2-4 sentences, punchy narration style).\n"
        "Format your output strictly as:\n"
        "=== OPTION 1 ===\n[Text of option 1]\n"
        "=== OPTION 2 ===\n[Text of option 2]\n"
        "=== OPTION 3 ===\n[Text of option 3]"
    )

    raw_output = await generate_text(prompt)
    options: List[str] = []
    current_text = []

    for line in raw_output.split("\n"):
        if "=== OPTION" in line:
            if current_text:
                options.append("\n".join(current_text).strip())
                current_text = []
        else:
            current_text.append(line)

    if current_text:
        options.append("\n".join(current_text).strip())

    cleaned = [opt for opt in options if opt]
    if len(cleaned) < 3:
        paras = [p.strip() for p in raw_output.split("\n\n") if p.strip()]
        return paras[:3] if len(paras) >= 3 else [raw_output]
    return cleaned[:3]


async def rewrite_draft(script: str, notes: str = "", target_duration: Optional[int] = None) -> str:
    """R3.2: Rewrite and polish draft keeping facts, short speakable sentences, strong hook."""
    duration_guide = ""
    if target_duration:
        min_words = int(target_duration * 2.2)
        max_words = int(target_duration * 2.8)
        duration_guide = f"Target duration: ~{target_duration} seconds ({min_words}-{max_words} words)."

    prompt = (
        f"Rewrite and polish this YouTube Shorts script draft for spoken narration.\n"
        f"Guidelines:\n"
        f"- Short, speakable sentences; alternate short punchy sentences with longer flowing ones for musical rhythm.\n"
        f"- Use commas, em-dashes (—), and ellipses (...) for natural spoken breath pauses.\n"
        f"- Place the punchline, key fact, or number at the very end of the sentence.\n"
        f"- Write ambiguous numbers as spoken words (e.g. 'twenty-five hundred', 'four hundred years').\n"
        f"- Strong curiosity hook in the first 1-2 sentences.\n"
        f"- Keep the user's authentic facts; do not invent fake details.\n"
        f"- Satisfying, memorable conclusion.\n"
        f"{duration_guide}\n\n"
        f"DRAFT TO REWRITE:\n\"\"\"{script.strip()}\"\"\"\n\n"
    )
    if notes.strip():
        prompt += f"USER NOTES:\n{notes.strip()}\n\n"

    prompt += "Return ONLY the rewritten script in plain text, with no preamble or commentary."
    return await generate_text(prompt)


async def outline_topic(topic: str, notes: str = "", target_duration: int = 90) -> str:
    """R3.3: Generate an outline and initial draft for a topic or single fact."""
    min_words = int(target_duration * 2.2)
    max_words = int(target_duration * 2.8)

    prompt = (
        f"Create a YouTube Shorts script outline and first draft for this topic or fact:\n"
        f"TOPIC/FACT: \"{topic.strip()}\"\n"
        f"TARGET LENGTH: {target_duration} seconds (~{min_words}-{max_words} words).\n\n"
    )
    if notes.strip():
        prompt += f"USER NOTES:\n{notes.strip()}\n\n"

    prompt += (
        "Structure required:\n"
        "1. Hook (0-5s): immediate intrigue\n"
        "2. Core mystery/context (5-30s)\n"
        "3. The unexpected twist or mechanism (30-60s)\n"
        "4. Climax / Mind-blowing conclusion\n\n"
        "Provide the complete, ready-to-narrate English script draft."
    )
    return await generate_text(prompt)


async def auto_pace(script: str) -> str:
    """R2.8: Insert pacing markup into raw script based on narrative structure."""
    prompt = (
        "You are an expert audio pacing director for viral YouTube Shorts fact narrations.\n"
        "Analyze this YouTube Shorts script and strategically insert pacing markup to maximize viewer retention and emotional impact.\n\n"
        "AVAILABLE PACING TAGS:\n"
        "- [fast]text[/fast]: Quick, punchy hooks or rapid item lists (+12% speed).\n"
        "- [slow]text[/slow]: Suspenseful, slow buildup before facts (-15% speed).\n"
        "- [pause 0.5] to [pause 1.0]: Dramatic silence before a big reveal or after a mind-blowing statement.\n"
        "- *word*: Emphasis on 1-2 punchy keywords (slightly louder, higher pitch).\n"
        "- [whisper]text[/whisper]: Whispered secrets, mysterious or hidden details.\n"
        "- [deep]text[/deep]: Deep, low-pitch eerie voice for cosmic scale, dark ocean depths, or chilling facts.\n"
        "- [shock]text[/shock]: High-pitch dramatic revelation, disbelief, or shocking discovery.\n"
        "- [urgent]text[/urgent]: Rapid, intense pacing for ticking clock or survival stakes (+22% speed).\n"
        "- [solemn]text[/solemn]: Slow, thoughtful closing takeaway, ancient history, or philosophical reflection (-20% speed).\n"
        "- [loud]text[/loud]: Command attention, loud wake-up warning (+30% volume).\n\n"
        "RULES:\n"
        "1. Blend different tags across sentences to create dynamic, musical narration variety.\n"
        "2. Do NOT change, rephrase, or remove any words from the original script.\n"
        "3. Only add the pacing markup tags.\n"
        "4. Return ONLY the marked-up script.\n\n"
        "ORIGINAL SCRIPT:\n\"\"\"" + script.strip() + "\"\"\"\n\n"
        "MARKED-UP SCRIPT:"
    )
    return await generate_text(prompt)


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
