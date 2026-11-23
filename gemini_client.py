import asyncio
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Try to import official google-genai SDK
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
    "4. Use short, punchy, speakable sentences designed for audio narration (~150 words per minute).\n"
    "5. Hook the listener in the very first sentence.\n"
    "6. Do NOT use clickbait lies or deceptive statements."
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

def get_gemini_client() -> Any:
    """Initialize and return google-genai Client using API key from .env."""
    if genai is None:
        raise RuntimeError("Thư viện 'google-genai' chưa được cài đặt. Vui lòng chạy pip install google-genai.")
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Chưa thiết lập GEMINI_API_KEY trong file .env. Vui lòng thêm khóa API vào .env.")
    
    # Crucial: Use v1beta where current models (gemini-3.5-flash-lite, etc.) are active
    return genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})

async def generate_text(
    prompt: str,
    system_instruction: Optional[str] = SYSTEM_INSTRUCTION_WRITING,
    model: Optional[str] = None,
    max_retries: int = 3,
) -> str:
    """
    Generate text using Gemini with automatic retry on rate limits or service unavailability.
    Falls back to backup models if a model is unavailable.
    """
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
                # If unavailable (503), timed out, or rate-limited (429), back off before retry
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2.5
                    await asyncio.sleep(wait_time)
                    continue
                break

    raise RuntimeError(f"Lỗi gọi Gemini API sau khi thử các model ({', '.join(models_to_try)}): {str(last_error)}")

# ==========================================
# Specialized Assistant Helpers
# ==========================================

async def suggest_next_paragraphs(script_so_far: str, notes: str = "") -> List[str]:
    """
    R3.1: Suggest 3 alternative next paragraphs continuing the story.
    Returns a list of 3 strings.
    """
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

    # Fallback cleanup
    cleaned = [opt for opt in options if opt]
    if len(cleaned) < 3:
        # If delimiter parsing failed, split by blank lines or paragraphs
        paras = [p.strip() for p in raw_output.split("\n\n") if p.strip()]
        return paras[:3] if len(paras) >= 3 else [raw_output]
    return cleaned[:3]

async def rewrite_draft(script: str, notes: str = "", target_duration: Optional[int] = None) -> str:
    """
    R3.2: Rewrite and polish draft keeping facts, short speakable sentences, strong hook.
    """
    duration_guide = ""
    if target_duration:
        min_words = int(target_duration * 2.2)
        max_words = int(target_duration * 2.8)
        duration_guide = f"Target duration: ~{target_duration} seconds ({min_words}-{max_words} words)."

    prompt = (
        f"Rewrite and polish this YouTube Shorts script draft for spoken narration.\n"
        f"Guidelines:\n"
        f"- Short, speakable sentences.\n"
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
    """
    R3.3: Generate an outline and initial draft for a topic or single fact.
    """
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
    """
    R2.8: Insert pacing markup into raw script based on narrative structure.
    Markup allowed:
    - [pause X] (e.g. [pause 0.5] or [pause 1.0])
    - [slow]...[/slow]
    - [fast]...[/fast]
    - *emphasis*
    - [whisper]...[/whisper]
    """
    prompt = (
        "You are an audio pacing director. Analyze this YouTube Shorts script and insert pacing markup to maximize engagement.\n\n"
        "MARKUP RULES:\n"
        "- [fast]text[/fast]: for high-energy hooks or rapid lists (+12% rate).\n"
        "- [slow]text[/slow]: for serious, solemn, or suspenseful buildup (-15% rate).\n"
        "- [pause 0.5] to [pause 1.0]: before a big reveal or after a shocking statement.\n"
        "- *word*: for single punchy emphasis words.\n"
        "- [whisper]text[/whisper]: for quiet secrets or mysterious details.\n\n"
        "ORIGINAL SCRIPT:\n\"\"\"" + script.strip() + "\"\"\"\n\n"
        "TASK: Return the exact script with pacing markup added naturally. Do not change words or facts, only add tags. "
        "Return ONLY the marked-up script."
    )
    return await generate_text(prompt)
