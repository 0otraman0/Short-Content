from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app, PROJECTS_DIR

def test_full_export_pipeline():
    client = TestClient(app)

    # 1. Create a project with script and claims
    create_res = client.post("/api/projects", json={
        "title": "Export Test Project",
        "script": "[fast]Greenland sharks live longer than most trees.[/fast] [pause 0.5] An *ancient* creature of the deep."
    })
    assert create_res.status_code == 200
    proj_id = create_res.json()["id"]

    try:
        # Add a sample claim to project.json via PUT
        update_res = client.put(f"/api/projects/{proj_id}", json={
            "claims": [
                {
                    "id": "c1",
                    "text": "Greenland sharks live longer than most trees",
                    "label": "ĐÃ CHỨNG MINH",
                    "urls": ["https://en.wikipedia.org/wiki/Greenland_shark"]
                }
            ]
        })
        assert update_res.status_code == 200

        # 2. Trigger background export
        export_res = client.post(f"/api/projects/{proj_id}/export")
        assert export_res.status_code == 200
        export_data = export_res.json()
        job_id = export_data["job_id"]
        assert job_id.startswith("job_")

        # 3. Poll export status
        max_wait = 45  # seconds
        start_time = time.time()
        completed = False

        while time.time() - start_time < max_wait:
            status_res = client.get(f"/api/projects/{proj_id}/export-status/{job_id}")
            assert status_res.status_code == 200
            status_data = status_res.json()

            if status_data["status"] == "completed":
                completed = True
                assert status_data["progress"] == 100
                print(f"Export completed in {time.time() - start_time:.1f}s. Duration: {status_data['duration']}s")
                break
            elif status_data["status"] == "failed":
                raise RuntimeError(f"Export job failed: {status_data.get('error')}")

            time.sleep(1.0)

        assert completed, "Export job timed out before completing"

        # 4. Verify endpoints and downloaded content
        # Narration audio
        audio_res = client.get(f"/api/projects/{proj_id}/narration")
        assert audio_res.status_code == 200
        assert "audio/mpeg" in audio_res.headers.get("content-type", "")
        assert len(audio_res.content) > 1000

        # Subtitles SRT
        srt_res = client.get(f"/api/projects/{proj_id}/subtitles")
        assert srt_res.status_code == 200
        srt_text = srt_res.text
        assert "-->" in srt_text
        assert "Greenland" in srt_text

        # Sources TXT
        sources_res = client.get(f"/api/projects/{proj_id}/sources")
        assert sources_res.status_code == 200
        sources_text = sources_res.text
        assert "Greenland shark" in sources_text
        assert "ĐÃ CHỨNG MINH" in sources_text

        # Verify files on disk
        folder = PROJECTS_DIR / proj_id
        assert (folder / "narration.mp3").exists()
        assert (folder / "subtitles.srt").exists()
        assert (folder / "sources.txt").exists()

        print("Full export pipeline test passed successfully!")

    finally:
        # Clean up test project
        client.delete(f"/api/projects/{proj_id}")

if __name__ == "__main__":
    test_full_export_pipeline()
