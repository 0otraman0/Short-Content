"""
topic_service.py - Business Logic for the Topic Suggestion bank.

No internet, no API key, no AI call: topics live in data/topics.json
(hook + fact + source, already fact-checked). The service only
lists them, picks an unused one at random, and remembers which
ones have been used, so the same topic is never suggested twice.

Follows the repo's 3-layer style: plain functions + a small
stateless TopicService facade, stdlib only.
"""

import json
import random
import re
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TOPICS_PATH = BASE_DIR / "data" / "topics.json"

REQUIRED_FIELDS = ("id", "hook", "fact", "source", "status")


def load_topics(path: Optional[Path] = None) -> List[Dict]:
    """Load and validate the topic bank. Raises FileNotFoundError / ValueError."""
    topics_path = Path(path) if path else DEFAULT_TOPICS_PATH
    if not topics_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy ngân hàng chủ đề: {topics_path}. "
            "Hãy copy data/topics.json vào thư mục data/ của repo."
        )
    with open(topics_path, encoding="utf-8") as f:
        topics = json.load(f)
    if not isinstance(topics, list) or not topics:
        raise ValueError("Ngân hàng chủ đề trống hoặc sai định dạng (cần 1 list JSON).")
    seen = set()
    for t in topics:
        for field in REQUIRED_FIELDS:
            if field not in t or t[field] in (None, ""):
                raise ValueError(f"Chủ đề thiếu trường bắt buộc: {field} (id={t.get('id')})")
        if t["status"] not in ("unused", "used"):
            raise ValueError(f"Chủ đề {t['id']} có status sai: {t['status']} (chỉ unused/used)")
        if t["id"] in seen:
            raise ValueError(f"Trùng id chủ đề: {t['id']}")
        seen.add(t["id"])
    return topics


def _save_topics(topics: List[Dict], path: Optional[Path] = None) -> None:
    topics_path = Path(path) if path else DEFAULT_TOPICS_PATH
    topics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(topics_path, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)
        f.write("\n")


def list_topics(only_unused: bool = False, path: Optional[Path] = None) -> List[Dict]:
    """Return all topics, or only unused ones when only_unused=True."""
    topics = load_topics(path)
    if only_unused:
        return [t for t in topics if t["status"] == "unused"]
    return topics


def get_topic(topic_id: str, path: Optional[Path] = None) -> Dict:
    """Return one topic by id. Raises KeyError when the id does not exist."""
    for t in load_topics(path):
        if str(t["id"]) == str(topic_id):
            return t
    raise KeyError(f"Không có chủ đề id={topic_id}")


def suggest_topic(path: Optional[Path] = None, seed: Optional[int] = None) -> Optional[Dict]:
    """Pick one random unused topic, or None when every topic is used."""
    unused = list_topics(only_unused=True, path=path)
    if not unused:
        return None
    rng = random.Random(seed) if seed is not None else random
    return rng.choice(unused)


def suggest_topics(count: int = 3, path: Optional[Path] = None) -> List[Dict]:
    """Pick up to `count` random unused topics (fewer when the bank runs low)."""
    unused = list_topics(only_unused=True, path=path)
    if not unused:
        return []
    return random.sample(unused, min(count, len(unused)))


def parse_generated_topic(text: str) -> Dict:
    """Parse Gemini's JSON reply into a topic dict. Raises ValueError on bad output."""
    if not text or not str(text).strip():
        raise ValueError("AI không trả về nội dung.")
    match = re.search(r"\{.*\}", str(text), re.DOTALL)
    if not match:
        raise ValueError("AI không trả về JSON.")
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        raise ValueError("AI trả về JSON sai định dạng.")
    hook = str(data.get("hook") or "").strip()
    fact = str(data.get("fact") or "").strip()
    source = str(data.get("source") or "").strip()
    if not hook or not fact:
        raise ValueError("AI trả về chủ đề thiếu hook hoặc fact.")
    return {"hook": hook, "fact": fact, "source": source or "AI gợi ý — chưa kiểm chứng nguồn."}


async def generate_topic(path: Optional[Path] = None, attempts: int = 3, _generate_text=None) -> Dict:
    """Ask Gemini for one NEW topic not already in the bank.

    Returns {hook, fact, source, ai_generated: True}. The topic is NOT saved
    to the bank — the caller decides whether to save it. Raises RuntimeError
    when Gemini fails or only suggests duplicates after `attempts` tries.
    The lazy import keeps this module stdlib-only at import time; the
    `_generate_text` parameter exists only so tests can inject a stub.
    """
    if _generate_text is None:
        from services.gemini_service import generate_text as _generate_text

    existing = {t["hook"].strip().lower() for t in load_topics(path)}
    avoid = "; ".join(sorted(existing)) if existing else "none"
    prompt = (
        "You are a fact-checker for a YouTube Shorts channel about surprising science facts.\n"
        "Suggest ONE surprising, verified science fact suitable for a 60-second Short.\n"
        f"It must NOT be any of these already-used hooks: {avoid}.\n"
        "Reply with JSON ONLY, no other text:\n"
        '{"hook": "One short surprising sentence, under 15 words.", '
        '"fact": "One or two sentences explaining the fact with the key number or date.", '
        '"source": "Name of a trustworthy source, e.g. NASA, Nature, Smithsonian Magazine."}\n'
        "Rules: only facts you are confident about; if unsure, pick a different fact. "
        "Write in English. Never invent numbers, dates, or names."
    )
    last_error = None
    for _ in range(attempts):
        try:
            raw = await _generate_text(
                prompt,
                system_instruction="Reply with JSON only. Never invent statistics, dates, names, or sources.",
            )
            topic = parse_generated_topic(raw)
        except Exception as e:
            last_error = e
            continue
        if topic["hook"].strip().lower() in existing:
            last_error = ValueError("Gemini gợi ý trùng chủ đề đã có.")
            continue
        topic["ai_generated"] = True
        return topic
    raise RuntimeError(f"Không tạo được chủ đề mới: {last_error}")


def create_topic(hook: str, fact: str, source: str = "", path: Optional[Path] = None) -> Dict:
    """Append a new topic to the bank with the next id. Persists to data/topics.json."""
    hook = (hook or "").strip()
    fact = (fact or "").strip()
    source = (source or "").strip() or "Tự thêm — chưa kiểm chứng nguồn."
    if not hook or not fact:
        raise ValueError("Chủ đề mới cần có hook và fact.")
    topics = load_topics(path)
    next_id = max((int(t["id"]) for t in topics), default=0) + 1
    topic = {"id": f"{next_id:02d}", "hook": hook, "fact": fact, "source": source, "status": "unused"}
    topics.append(topic)
    _save_topics(topics, path)
    return topic


def mark_used(topic_id: str, used: bool = True, path: Optional[Path] = None) -> Dict:
    """Mark a topic used (or unused again). Persists to data/topics.json."""
    topics = load_topics(path)
    for t in topics:
        if str(t["id"]) == str(topic_id):
            t["status"] = "used" if used else "unused"
            _save_topics(topics, path)
            return t
    raise KeyError(f"Không có chủ đề id={topic_id}")


def counts(path: Optional[Path] = None) -> Dict[str, int]:
    """Return {"total": N, "unused": n, "used": m} for the UI header."""
    topics = load_topics(path)
    unused = sum(1 for t in topics if t["status"] == "unused")
    return {"total": len(topics), "unused": unused, "used": len(topics) - unused}


class TopicService:
    """Stateless service facade, same shape as GeminiService in this repo."""

    @staticmethod
    def list_topics(only_unused: bool = False) -> List[Dict]:
        return list_topics(only_unused=only_unused)

    @staticmethod
    def get_topic(topic_id: str) -> Dict:
        return get_topic(topic_id)

    @staticmethod
    def suggest_topic() -> Optional[Dict]:
        return suggest_topic()

    @staticmethod
    def suggest_topics(count: int = 3) -> List[Dict]:
        return suggest_topics(count)

    @staticmethod
    def create_topic(hook: str, fact: str, source: str = "") -> Dict:
        return create_topic(hook, fact, source)

    @staticmethod
    async def generate_topic() -> Dict:
        return await generate_topic()

    @staticmethod
    def mark_used(topic_id: str, used: bool = True) -> Dict:
        return mark_used(topic_id, used=used)

    @staticmethod
    def counts() -> Dict[str, int]:
        return counts()
