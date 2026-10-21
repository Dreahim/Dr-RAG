"""Upload validation and stored filename generation."""

import re
from pathlib import Path

from fastapi import UploadFile

from src.controllers.base import BaseController
from src.controllers.project import ProjectController
from src.models.response_signal import ResponseSignal


class DataController(BaseController):
    """Apply file rules before writing an uploaded document."""

    def validate_uploaded_file(self, file: UploadFile) -> tuple[bool, ResponseSignal]:
        """Check the declared media type and available file size."""
        if file.content_type not in self.settings.allowed_file_types:
            return False, ResponseSignal.FILE_NOT_SUPPORTED
        if file.size is not None and file.size > self.settings.max_file_size_bytes:
            return False, ResponseSignal.FILE_TOO_LARGE
        return True, ResponseSignal.FILE_UPLOAD_SUCCESS

    def generate_unique_file_name(
        self, original_file_name: str | None, project_id: str
    ) -> tuple[Path, str]:
        """Create a candidate path; the caller must open it exclusively."""
        project_dir = ProjectController(self.settings).get_project_path(project_id)
        stored_name = (
            f"{self.get_unique_string()}_{self.clean_file_name(original_file_name)}"
        )
        return project_dir / stored_name, stored_name

    @staticmethod
    def clean_file_name(original_file_name: str | None) -> str:
        """Remove path components and unsafe filename characters."""
        name = (original_file_name or "").replace("\\", "/").rsplit("/", 1)[-1]
        cleaned = re.sub(r"[^\w.-]+", "_", name.strip()).strip("._")
        suffix = Path(cleaned).suffix
        if len(suffix.encode("utf-8")) > 32:
            suffix = ""
        stem = cleaned[:-len(suffix)] if suffix else cleaned
        # Filesystems limit encoded filename bytes, not Unicode characters.
        budget = 180 - len(suffix.encode("utf-8"))
        stem = stem.encode("utf-8")[:budget].decode("utf-8", errors="ignore")
        return (stem or "upload") + suffix
