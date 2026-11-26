"""
project_repository.py - Data Access Layer for project.json CRUD and export job paths.
Extracted from main.py as part of 3-Layer Architecture (Phase 12).
"""

import json
import os
import re
import shutil
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

_save_lock = threading.Lock()


def _sanitize_id(value: str, label: str) -> str:
    """P0-3: one shared check for every id that becomes a path segment."""
    if not isinstance(value, str) or not re.match(r"^[a-zA-Z0-9_-]+$", value):
        raise ValueError(f"Invalid {label}: {value!r}")
    return value


def _sanitize_project_id(project_id: str) -> str:
    """Validate project ID to prevent path traversal."""
    return _sanitize_id(project_id, "project ID")


def _sanitize_job_id(job_id: str) -> str:
    return _sanitize_id(job_id, "job ID")


def _sanitize_para_key(para_key: str) -> str:
    return _sanitize_id(para_key, "paragraph key")


def _sanitize_take_id(take_id: str) -> str:
    return _sanitize_id(take_id, "take ID")


class ProjectRepository:
    """Handles all file I/O for project.json and export job directories."""

    def get_folder(self, project_id: str) -> Path:
        _sanitize_project_id(project_id)
        return PROJECTS_DIR / project_id

    def get_json_path(self, project_id: str) -> Path:
        return self.get_folder(project_id) / "project.json"

    def get_export_job_dir(self, project_id: str, job_id: str) -> Path:
        _sanitize_job_id(job_id)
        return self.get_folder(project_id) / "exports" / job_id

    def get_take_file(self, project_id: str, para_key: str, take_id: str) -> Path:
        """P0-3: sanitized path to a paragraph take audio file."""
        _sanitize_para_key(para_key)
        _sanitize_take_id(take_id)
        return self.get_folder(project_id) / "takes" / para_key / f"{take_id}.mp3"

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Return parsed project.json dict or None if not found."""
        json_file = self.get_json_path(project_id)
        if not json_file.exists():
            return None
        try:
            return json.loads(json_file.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects sorted by updated_at descending."""
        projects = []
        if not PROJECTS_DIR.exists():
            return projects
        for folder in PROJECTS_DIR.iterdir():
            json_file = folder / "project.json"
            if json_file.exists():
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    projects.append({
                        "id": data.get("id", folder.name),
                        "title": data.get("title", "Untitled"),
                        "status": data.get("status", "draft"),
                        "word_count": len(data.get("script", "").split()),
                        "target_duration": data.get("target_duration", 90),
                        "pacing_preset": data.get("pacing_preset", "mystery"),
                        "updated_at": data.get("updated_at", ""),
                        "created_at": data.get("created_at", ""),
                    })
                except Exception:
                    pass
        projects.sort(key=lambda p: p.get("updated_at", ""), reverse=True)
        return projects

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Write project.json to disk. project_data must contain 'id'.

        P0-4: atomic write (temp file + os.replace) under a lock, so an
        autosave racing an export cannot leave a half-written JSON file.
        """
        project_id = project_data["id"]
        folder = self.get_folder(project_id)
        folder.mkdir(parents=True, exist_ok=True)
        json_file = folder / "project.json"
        payload = json.dumps(project_data, ensure_ascii=False, indent=2)
        with _save_lock:
            tmp_file = folder / "project.json.tmp"
            tmp_file.write_text(payload, encoding="utf-8")
            os.replace(tmp_file, json_file)
        return project_data

    def create_project(self, title: str = "Dự án chưa đặt tên", script: str = "") -> Dict[str, Any]:
        """Create a new project folder with project.json."""
        # Prefix matches the codebase convention (job_*, take_*, preview_*)
        # and what tests/test_projects.py expects: proj_<12 hex>.
        project_id = f"proj_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        data = {
            "id": project_id,
            "title": title,
            "script": script,
            "status": "draft",
            "target_duration": 90,
            "pacing_preset": "mystery",
            "claims": [],
            "takes": {},
            "exports": [],
            "created_at": now,
            "updated_at": now,
        }
        return self.save_project(data)

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a dict of updates to project.json and persist."""
        data = self.get_project(project_id)
        if data is None:
            raise FileNotFoundError(f"Project {project_id!r} not found.")
        data.update(updates)
        data["updated_at"] = datetime.now().isoformat()
        return self.save_project(data)

    def delete_project(self, project_id: str) -> None:
        """Delete the project folder entirely."""
        folder = self.get_folder(project_id)
        if folder.exists():
            shutil.rmtree(folder)

    def duplicate_project(self, project_id: str) -> Dict[str, Any]:
        """Duplicate an existing project to a new ID."""
        data = self.get_project(project_id)
        if data is None:
            raise FileNotFoundError(f"Project {project_id!r} not found.")
        new_id = f"proj_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        new_data = {
            **data,
            "id": new_id,
            "title": data.get("title", "Untitled") + " (Bản sao)",
            "status": "draft",
            "claims": [],
            "takes": {},
            "exports": [],
            "created_at": now,
            "updated_at": now,
        }
        new_folder = self.get_folder(new_id)
        new_folder.mkdir(parents=True, exist_ok=True)
        tmp_file = new_folder / "project.json.tmp"
        tmp_file.write_text(json.dumps(new_data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp_file, new_folder / "project.json")
        return new_data
