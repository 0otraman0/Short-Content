from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app, PROJECTS_DIR

class TestFactCheckAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_factcheck_pipeline_api(self):
        # 1. Create a test project
        create_res = self.client.post("/api/projects", json={
            "title": "Factcheck API Test Project",
            "script": "Greenland sharks live in near-freezing Arctic waters for over 400 years. Dragons breathe real fire in the sky."
        })
        self.assertEqual(create_res.status_code, 200)
        proj_id = create_res.json()["id"]

        try:
            # 2. Call factcheck endpoint
            fc_res = self.client.post(f"/api/projects/{proj_id}/factcheck")
            self.assertEqual(fc_res.status_code, 200)
            fc_data = fc_res.json()
            self.assertTrue(fc_data.get("success"))
            claims = fc_data.get("claims", [])
            self.assertGreaterEqual(len(claims), 1)

            # Check structure of claims
            first_claim = claims[0]
            self.assertIn("id", first_claim)
            self.assertIn("text", first_claim)
            self.assertIn("label", first_claim)
            self.assertIn(first_claim["label"], ["ĐÃ CHỨNG MINH", "CHƯA RÕ"])

            # 3. Test manual claims update (override label or add URL) (R4.7)
            first_claim["label"] = "ĐÃ CHỨNG MINH"
            first_claim["urls"].append("https://en.wikipedia.org/wiki/Greenland_shark")

            update_res = self.client.put(f"/api/projects/{proj_id}/claims", json={"claims": claims})
            self.assertEqual(update_res.status_code, 200)
            updated_claims = update_res.json().get("claims", [])
            self.assertEqual(updated_claims[0]["label"], "ĐÃ CHỨNG MINH")
            self.assertIn("https://en.wikipedia.org/wiki/Greenland_shark", updated_claims[0]["urls"])

            # 4. Test safe rewrite endpoint (R4.6)
            rw_res = self.client.post("/api/factcheck/rewrite-sentence", json={
                "claim_text": "Dragons breathe real fire in the sky.",
                "sentence": "Dragons breathe real fire in the sky.",
                "reason": "Mythological creature, no scientific evidence"
            })
            self.assertEqual(rw_res.status_code, 200)
            rw_data = rw_res.json()
            self.assertTrue(rw_data.get("success"))
            self.assertIn("safe_sentence", rw_data)
            self.assertGreater(len(rw_data["safe_sentence"]), 10)

        finally:
            self.client.delete(f"/api/projects/{proj_id}")

if __name__ == "__main__":
    unittest.main()
