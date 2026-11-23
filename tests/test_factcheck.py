import asyncio
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from factcheck import clean_pacing_tags, extract_and_verify_claims, rewrite_claim_safely

class TestFactCheck(unittest.TestCase):
    def test_clean_pacing_tags(self):
        raw = "[fast]Greenland sharks live *400* years.[/fast] [pause 0.8] [whisper]Their secret is cold water.[/whisper]"
        cleaned = clean_pacing_tags(raw)
        self.assertNotIn("[fast]", cleaned)
        self.assertNotIn("[pause", cleaned)
        self.assertNotIn("*", cleaned)
        self.assertIn("Greenland sharks live 400 years.", cleaned)
        self.assertIn("Their secret is cold water.", cleaned)

    def test_extract_and_verify_claims(self):
        script = (
            "[fast]Greenland sharks can live for roughly 400 years in the freezing Arctic.[/fast] "
            "[pause 0.5] Aliens built the pyramids in Egypt 5000 years ago."
        )
        result = asyncio.run(extract_and_verify_claims(script))
        self.assertTrue(result.get("success"))
        claims = result.get("claims", [])
        self.assertGreaterEqual(len(claims), 2)

        for c in claims:
            self.assertIn("id", c)
            self.assertIn("text", c)
            self.assertIn("sentence", c)
            self.assertIn(c["label"], ["ĐÃ CHỨNG MINH", "CHƯA RÕ"])
            self.assertIsInstance(c["urls"], list)
            self.assertIsInstance(c["evidence"], str)

        print("\nExtracted & Verified Claims:")
        for c in claims:
            print(f"- [{c['label']}] {c['text']} -> Source: {c['urls'][:2]} ({c['evidence'][:60]}...)")

    def test_rewrite_claim_safely(self):
        sentence = "Aliens built the pyramids in Egypt."
        claim = "Aliens built the pyramids."
        safe_sentence = asyncio.run(rewrite_claim_safely(claim, sentence, reason="No historical evidence"))
        self.assertIsInstance(safe_sentence, str)
        self.assertGreater(len(safe_sentence), 10)
        print("\nSafe Rewritten Sentence:", safe_sentence)

if __name__ == "__main__":
    unittest.main()
