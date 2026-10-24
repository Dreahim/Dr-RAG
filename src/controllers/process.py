"""Load uploaded documents and split their text into chunks."""

import os

import pymupdf
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.controllers.base import BaseController
from src.controllers.project import ProjectController
from src.helpers.config import Settings
from src.models.processing_file_type import ProcessingFileType


class ProcessController(BaseController):
    """Load and split a document belonging to one project."""

    def __init__(self, settings: Settings, project_id: str) -> None:
        super().__init__(settings)
        self.project_id = project_id
        self.project_dir = ProjectController(settings).get_project_path(project_id)

    def get_file_extension(self, file_id: str) -> str:
        """Return the file extension in lowercase."""
        return os.path.splitext(file_id)[-1].lower()

    def get_file_loader(self, file_id: str) -> PyMuPDFLoader | TextLoader:
        """Select the loader for a saved PDF or UTF-8 text file."""
        if (
            file_id in {".", ".."}
            or len(file_id.encode("utf-8")) > 255
            or os.path.basename(file_id) != file_id
            or any(character in file_id for character in ("\\", ":", "\x00"))
        ):
            raise ValueError("file_id must be a valid stored filename")

        file_path = os.path.join(self.project_dir, file_id)
        # Uploaded files must not link to files outside their project.
        if os.path.islink(self.project_dir) or os.path.islink(file_path):
            raise ValueError("Linked files and project folders are not supported")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(file_id)

        file_extension = self.get_file_extension(file_id)
        if file_extension == ProcessingFileType.PDF.value:
            # The loader fails internally when a PDF still needs a password.
            with pymupdf.open(file_path) as document:
                if document.needs_pass:
                    raise ValueError("Password-protected PDFs are not supported")
            return PyMuPDFLoader(file_path)
        if file_extension == ProcessingFileType.TEXT.value:
            return TextLoader(file_path, encoding="utf-8")
        raise ValueError("Unsupported file extension")

    def get_file_content(self, file_id: str) -> list[Document]:
        """Load the document using its selected loader."""
        loader = self.get_file_loader(file_id)
        return loader.load()

    def process_file_content(
        self,
        file_content: list[Document],
        file_id: str,
        chunk_size: int = 100,
        overlap_size: int = 20,
    ) -> list[Document]:
        """Split the loaded text while preserving each document's metadata."""
        if overlap_size >= chunk_size:
            raise ValueError("overlap_size must be smaller than chunk_size")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )
        file_content_texts = [record.page_content for record in file_content]
        file_content_metadata = [record.metadata for record in file_content]
        return text_splitter.create_documents(
            file_content_texts, metadatas=file_content_metadata
        )
