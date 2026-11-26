"""
project_service.py - Business logic for Project management.
Delegates I/O to ProjectRepository.
"""

from typing import Any, Dict, List, Optional
from repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, repository: Optional[ProjectRepository] = None):
        self.repo = repository or ProjectRepository()

    def list_projects(self) -> List[Dict[str, Any]]:
        return self.repo.list_projects()

    def create_project(self, title: str = "Dự án chưa đặt tên", script: str = "") -> Dict[str, Any]:
        return self.repo.create_project(title=title, script=script)

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        return self.repo.get_project(project_id)

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        return self.repo.update_project(project_id, updates)

    def delete_project(self, project_id: str) -> None:
        self.repo.delete_project(project_id)

    def duplicate_project(self, project_id: str) -> Dict[str, Any]:
        return self.repo.duplicate_project(project_id)
