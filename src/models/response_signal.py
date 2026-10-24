"""Signals returned by document endpoints."""

from enum import Enum


class ResponseSignal(str, Enum):
    """Stable status values in document responses."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    FILE_NOT_SUPPORTED = "file_not_supported"
    FILE_TOO_LARGE = "file_too_large"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_PROCESSING_FAILED = "file_processing_failed"
    FILE_PROCESSING_SUCCESS = "file_processing_success"
