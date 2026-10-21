"""Project-specific file storage."""

import re
from pathlib import Path

from src.controllers.base import BaseController

PROJECT_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")


class ProjectController(BaseController):
    """Locate and create a project's upload directory."""

    def get_project_path(self, project_id: str) -> Path:
        """Return a safe directory for one project identifier."""
        if not PROJECT_ID_PATTERN.fullmatch(project_id):
            raise ValueError(
                "Project ID must contain only letters, digits, underscores, or hyphens"
            )

        project_dir = self.files_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir
