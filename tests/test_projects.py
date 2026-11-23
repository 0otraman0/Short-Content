import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app, PROJECTS_DIR

def test_projects_crud():
    client = TestClient(app)

    # 1. Test List projects (initial)
    res = client.get("/api/projects")
    assert res.status_code == 200
    initial_projects = res.json()
    assert isinstance(initial_projects, list)

    # 2. Test Create project
    create_payload = {
        "title": "Test Video Facts",
        "script": "Did you know that Greenland sharks live longer than most trees?"
    }
    res = client.post("/api/projects", json=create_payload)
    assert res.status_code == 200
    created = res.json()
    proj_id = created["id"]
    assert proj_id.startswith("proj_")
    assert created["title"] == create_payload["title"]
    assert created["script"] == create_payload["script"]

    # Verify physical file on disk
    json_path = PROJECTS_DIR / proj_id / "project.json"
    assert json_path.exists(), f"File {json_path} must exist on disk"

    # 3. Test Get project by ID
    res = client.get(f"/api/projects/{proj_id}")
    assert res.status_code == 200
    fetched = res.json()
    assert fetched["id"] == proj_id
    assert fetched["title"] == create_payload["title"]

    # 4. Test Update project (autosave simulation)
    update_payload = {
        "title": "Updated Test Video Facts",
        "script": "Updated script text with *emphasis* and [pause 0.5]",
        "target_duration": 120
    }
    res = client.put(f"/api/projects/{proj_id}", json=update_payload)
    assert res.status_code == 200
    updated = res.json()
    assert updated["title"] == update_payload["title"]
    assert updated["script"] == update_payload["script"]
    assert updated["target_duration"] == 120

    # 5. Test Duplicate project
    res = client.post(f"/api/projects/{proj_id}/duplicate")
    assert res.status_code == 200
    duplicated = res.json()
    dup_id = duplicated["id"]
    assert dup_id != proj_id
    assert dup_id.startswith("proj_")
    assert "Bản sao" in duplicated["title"]
    assert duplicated["script"] == update_payload["script"]
    assert (PROJECTS_DIR / dup_id / "project.json").exists()

    # 6. Test Delete project
    res = client.delete(f"/api/projects/{proj_id}")
    assert res.status_code == 200
    assert not (PROJECTS_DIR / proj_id).exists(), "Folder should be deleted"

    # Clean up duplicate project
    res = client.delete(f"/api/projects/{dup_id}")
    assert res.status_code == 200
    assert not (PROJECTS_DIR / dup_id).exists()

    print("All Project CRUD tests passed successfully!")

if __name__ == "__main__":
    test_projects_crud()
