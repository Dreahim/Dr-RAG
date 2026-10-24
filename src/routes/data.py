"""Document upload and processing endpoints."""

import logging
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, status
from fastapi import Path as PathParameter
from fastapi.responses import JSONResponse
from langchain_core.documents import Document

from src.controllers.data import DataController
from src.controllers.process import ProcessController
from src.helpers.config import Settings, get_settings
from src.models.response_signal import ResponseSignal
from src.routes.schemes.data import ProcessRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


class UploadTooLarge(Exception):
    """The received file exceeded the configured size limit."""


@router.post("/upload/{project_id}", response_model=None)
async def upload_data(
    project_id: Annotated[str, PathParameter(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")],
    file: UploadFile,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str] | JSONResponse:
    """Validate and store one file in a project-specific directory."""
    controller = DataController(settings)
    is_valid, signal = controller.validate_uploaded_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": signal.value, "message": signal.value},
        )

    for _ in range(5):
        file_path: Path | None = None
        file_created = False
        try:
            file_path, file_id = controller.generate_unique_file_name(
                file.filename, project_id
            )
            size = 0
            async with aiofiles.open(file_path, "xb") as destination:
                file_created = True
                while chunk := await file.read(settings.FILE_DEFAULT_CHUNK_SIZE):
                    size += len(chunk)
                    if size > settings.max_file_size_bytes:
                        raise UploadTooLarge
                    await destination.write(chunk)
            file_created = False
            return {
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": file_id,
            }
        except FileExistsError:
            continue
        except UploadTooLarge:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_TOO_LARGE.value,
                    "message": ResponseSignal.FILE_TOO_LARGE.value,
                },
            )
        except OSError:
            logger.exception("Could not save the uploaded file")
            break
        finally:
            if file_created and file_path is not None:
                try:
                    file_path.unlink(missing_ok=True)
                except OSError:
                    logger.exception("Could not remove an incomplete upload")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "signal": ResponseSignal.FILE_UPLOAD_FAILED.value,
            "message": "Could not save the uploaded file",
        },
    )


@router.post("/process/{project_id}", response_model=None)
def process_data(
    project_id: Annotated[str, PathParameter(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")],
    process_request: ProcessRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[Document] | JSONResponse:
    """Load an uploaded document and return its text chunks."""
    process_controller = ProcessController(settings, project_id)
    try:
        file_content = process_controller.get_file_content(process_request.file_id)
        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=process_request.file_id,
            chunk_size=process_request.chunk_size,
            overlap_size=process_request.overlap_size,
        )
    except FileNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.FILE_PROCESSING_FAILED.value},
        )
    except (ValueError, RuntimeError, OSError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.FILE_PROCESSING_FAILED.value},
        )

    if not file_chunks:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.FILE_PROCESSING_FAILED.value},
        )
    return file_chunks
