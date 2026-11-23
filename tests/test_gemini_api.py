from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

class TestGeminiAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_suggest_next_api(self):
        # Empty script validation
        res_err = self.client.post("/api/gemini/suggest-next", json={"script": ""})
        self.assertEqual(res_err.status_code, 400)

        # Valid request
        res = self.client.post("/api/gemini/suggest-next", json={
            "script": "Greenland sharks live in near-freezing Arctic waters for over 400 years.",
            "notes": "Explain their heart rate"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIsInstance(data.get("suggestions"), list)
        self.assertGreaterEqual(len(data.get("suggestions")), 1)

    def test_rewrite_api(self):
        # Empty script validation
        res_err = self.client.post("/api/gemini/rewrite", json={"script": ""})
        self.assertEqual(res_err.status_code, 400)

        # Valid rewrite
        res = self.client.post("/api/gemini/rewrite", json={
            "script": "Greenland sharks are super old. They swim very slow. They live 400 years.",
            "notes": "Make it dramatic and speakable",
            "target_duration": 60
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("original", data)
        self.assertIn("rewritten", data)
        self.assertGreater(len(data["rewritten"]), 15)

    def test_outline_api(self):
        # Empty topic validation
        res_err = self.client.post("/api/gemini/outline", json={"topic": ""})
        self.assertEqual(res_err.status_code, 400)

        # Valid outline
        res = self.client.post("/api/gemini/outline", json={
            "topic": "The immortal jellyfish Turritopsis dohrnii",
            "notes": "Hook with reverse aging",
            "target_duration": 60
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("draft", data)
        self.assertGreater(len(data["draft"]), 20)

    def test_auto_pace_api(self):
        # Empty script validation
        res_err = self.client.post("/api/gemini/auto-pace", json={"script": ""})
        self.assertEqual(res_err.status_code, 400)

        # Valid auto-pace
        res = self.client.post("/api/gemini/auto-pace", json={
            "script": "Greenland sharks live 400 years. But how do they survive in freezing water? Their secret is patience."
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("original", data)
        self.assertIn("paced", data)
        # Check that at least some pacing markup was inserted
        paced_text = data["paced"]
        has_tag = any(tag in paced_text for tag in ["[pause", "[slow]", "[fast]", "*", "[whisper]"])
        self.assertTrue(has_tag)
        print("\nAuto-paced Script Result:\n", paced_text)

if __name__ == "__main__":
    unittest.main()
