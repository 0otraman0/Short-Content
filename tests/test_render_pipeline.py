import asyncio
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app, PROJECTS_DIR

def test_full_render_pipeline():
    client = TestClient(app)

    # 1. Create a project
    create_res = client.post("/api/projects", json={
        "title": "Pipeline Test Video",
        "script": "[fast]Greenland sharks live longer than most trees.[/fast] [pause 0.5] An *ancient* creature of the deep."
    })
    assert create_res.status_code == 200
    proj_id = create_res.json()["id"]

    try:
        # 2. Trigger background render
        render_res = client.post(f"/api/projects/{proj_id}/render")
        assert render_res.status_code == 200
        render_data = render_res.json()
        job_id = render_data["job_id"]
        assert job_id.startswith("job_")

        # 3. Poll render status
        max_wait = 45 # seconds
        start_time = time.time()
        completed = False

        while time.time() - start_time < max_wait:
            status_res = client.get(f"/api/projects/{proj_id}/render-status/{job_id}")
            assert status_res.status_code == 200
            status_data = status_res.json()

            if status_data["status"] == "completed":
                completed = True
                assert status_data["progress"] == 100
                assert status_data["video_url"] is not None
                print(f"Render completed in {time.time() - start_time:.1f}s. Duration: {status_data['duration']}s")
                break
            elif status_data["status"] == "failed":
                raise RuntimeError(f"Render job failed: {status_data.get('error')}")

            time.sleep(1.0)

        assert completed, "Render job timed out before completing"

        # 4. Verify video download endpoint
        video_res = client.get(f"/api/projects/{proj_id}/video")
        assert video_res.status_code == 200
        assert "video/mp4" in video_res.headers.get("content-type", "")
        assert len(video_res.content) > 10000

        # Verify files on disk
        folder = PROJECTS_DIR / proj_id
        assert (folder / "narration.mp3").exists()
        assert (folder / "subtitles.ass").exists()
        assert (folder / "output.mp4").exists()

        print("Full render pipeline test passed successfully!")

    finally:
        # Clean up test project
        client.delete(f"/api/projects/{proj_id}")

if __name__ == "__main__":
    test_full_render_pipeline()
