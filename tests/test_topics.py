"""Tests for the Topic Suggestion bank (no network, no API key, no Gemini).

Run from the repo root, same as the other tests:
    python -m unittest discover -s tests -p "test_topics.py" -v
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.topic_service import (
    create_topic,
    generate_topic,
    load_topics,
    list_topics,
    get_topic,
    parse_generated_topic,
    suggest_topic,
    suggest_topics,
    mark_used,
    counts,
)


def _bank_copy(tmpdir):
    """Copy the real bank into a temp file so tests never touch data/topics.json."""
    src = Path(__file__).resolve().parent.parent / "data" / "topics.json"
    dst = Path(tmpdir) / "topics.json"
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return dst


class TestTopicBank(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = _bank_copy(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_bank_has_10_verified_topics(self):
        topics = load_topics(self.path)
        self.assertEqual(len(topics), 10)
        ids = [t["id"] for t in topics]
        self.assertEqual(ids, ["07", "08", "09", "10", "11", "12", "13", "14", "15", "16"])
        for t in topics:
            self.assertTrue(t["hook"].strip())
            self.assertTrue(t["fact"].strip())
            self.assertTrue(t["source"].strip())
            self.assertEqual(t["status"], "unused")

    def test_get_topic_by_id(self):
        t = get_topic("07", self.path)
        self.assertEqual(t["hook"], "Oxford University is older than the Aztec Empire.")
        with self.assertRaises(KeyError):
            get_topic("99", self.path)

    def test_suggest_returns_unused_only(self):
        t = suggest_topic(self.path)
        self.assertIsNotNone(t)
        self.assertEqual(t["status"], "unused")

    def test_suggest_three_are_distinct(self):
        topics = suggest_topics(3, self.path)
        self.assertEqual(len(topics), 3)
        self.assertEqual(len({t["id"] for t in topics}), 3)

    def test_mark_used_persists_and_hides_from_unused(self):
        mark_used("07", used=True, path=self.path)
        self.assertEqual(get_topic("07", self.path)["status"], "used")
        self.assertNotIn("07", [t["id"] for t in list_topics(only_unused=True, path=self.path)])
        self.assertEqual(counts(self.path), {"total": 10, "unused": 9, "used": 1})
        # Undo works
        mark_used("07", used=False, path=self.path)
        self.assertEqual(get_topic("07", self.path)["status"], "unused")

    def test_create_topic_appends_with_next_id(self):
        t = create_topic("Test hook.", "Test fact.", "Test source.", path=self.path)
        self.assertEqual(t["id"], "17")
        self.assertEqual(t["status"], "unused")
        self.assertEqual(len(load_topics(self.path)), 11)
        self.assertEqual(get_topic("17", self.path)["hook"], "Test hook.")
        with self.assertRaises(ValueError):
            create_topic("", "Test fact.", path=self.path)
        with self.assertRaises(ValueError):
            create_topic("Test hook.", "", path=self.path)

    def test_suggest_none_when_all_used(self):
        for t in load_topics(self.path):
            mark_used(t["id"], used=True, path=self.path)
        self.assertIsNone(suggest_topic(self.path))
        self.assertEqual(suggest_topics(3, self.path), [])


class TestGenerateTopicParsing(unittest.TestCase):
    def test_parse_valid_json(self):
        t = parse_generated_topic('{"hook": "A new hook.", "fact": "A new fact.", "source": "NASA"}')
        self.assertEqual(t["hook"], "A new hook.")
        self.assertEqual(t["source"], "NASA")

    def test_parse_extracts_json_from_extra_text(self):
        t = parse_generated_topic('Here it is:\n{"hook": "H.", "fact": "F.", "source": ""}\nDone.')
        self.assertEqual(t["hook"], "H.")
        self.assertIn("chưa kiểm chứng", t["source"])

    def test_parse_rejects_missing_hook_or_fact(self):
        with self.assertRaises(ValueError):
            parse_generated_topic('{"hook": "", "fact": "F."}')
        with self.assertRaises(ValueError):
            parse_generated_topic('not json at all')


class TestGenerateTopicAI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = _bank_copy(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    async def test_generate_skips_duplicate_hook(self):
        duplicate = json.dumps({"hook": "Oxford University is older than the Aztec Empire.",
                                "fact": "Old fact.", "source": "Oxford"})
        fresh = json.dumps({"hook": "A brand new hook.", "fact": "A brand new fact.", "source": "NASA"})
        stub = AsyncMock(side_effect=[duplicate, fresh])
        t = await generate_topic(path=self.path, _generate_text=stub)
        self.assertEqual(t["hook"], "A brand new hook.")
        self.assertTrue(t["ai_generated"])


if __name__ == "__main__":
    unittest.main()
