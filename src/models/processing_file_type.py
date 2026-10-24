"""File extensions supported by document processing."""

from enum import Enum


class ProcessingFileType(str, Enum):
    TEXT = ".txt"
    PDF = ".pdf"
