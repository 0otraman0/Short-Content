import asyncio
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gemini_client import (
    get_gemini_client,
    get_configured_model,
    generate_text,
    suggest_next_paragraphs,
    SYSTEM_INSTRUCTION_WRITING,
)

class TestGeminiClient(unittest.TestCase):
    def test_client_init(self):
        client = get_gemini_client()
        self.assertIsNotNone(client)

    def test_configured_model(self):
        model = get_configured_model()
        self.assertIsInstance(model, str)
        self.assertTrue(len(model) > 0)

    def test_generate_text(self):
        prompt = "Write one sentence about Greenland sharks living 400 years."
        res = asyncio.run(generate_text(prompt))
        self.assertIsInstance(res, str)
        self.assertTrue(len(res) > 10)
        print("\nGemini Generated Text:\n", res)

    def test_suggest_next(self):
        script = "Greenland sharks can live for over 400 years in the freezing Arctic waters."
        options = asyncio.run(suggest_next_paragraphs(script, notes="Focus on their slow metabolism"))
        self.assertIsInstance(options, list)
        self.assertTrue(len(options) >= 1)
        print("\nSuggested next options count:", len(options))
        print("Option 1:", options[0][:80], "...")

if __name__ == "__main__":
    unittest.main()
