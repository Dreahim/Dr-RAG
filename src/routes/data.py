"""Document upload and processing endpoints."""

import logging
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi import Path as PathParameter
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from starlette.concurrency import run_in_threadpool

from src.controllers.data import DataController
from src.controllers.process import ProcessController
from src.helpers.config import Settings, get_settings
from src.models.asset import AssetModel
from src.models.asset_type import AssetTypeEnum
from src.models.data_chunk import DataChunkModel
from src.models.db_schemes import Asset, DataChunk
from src.models.project import ProjectModel
from src.models.response_signal import ResponseSignal
from src.routes.schemes.data import ProcessRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


class UploadTooLarge(Exception):
    """The received file exceeded the configured size limit."""


@router.post("/upload/{project_id}", response_model=None)
async def upload_data(
    request: Request,
    project_id: Annotated[str, PathParameter(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")],
    file: UploadFile,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str] | JSONResponse:
    """Store one file and return its registered asset ID."""
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
            project = await ProjectModel(
                request.app.state.db_client
            ).get_project_or_create_one(project_id)
            asset = await AssetModel(request.app.state.db_client).create_asset(
                Asset(
                    asset_project_id=project.id,
                    asset_type=AssetTypeEnum.FILE.value,
                    asset_name=file_id,
                    asset_size=size,
                )
            )
            file_created = False
            return {
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset.id),
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
        except PyMongoError as error:
            logger.error(
                "Could not register the uploaded file (%s)", type(error).__name__
            )
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "signal": ResponseSignal.FILE_UPLOAD_FAILED.value,
                    "message": "Could not register the uploaded file",
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
                    logger.exception("Could not remove an unregistered upload")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "signal": ResponseSignal.FILE_UPLOAD_FAILED.value,
            "message": "Could not save the uploaded file",
        },
    )


@router.post("/process/{project_id}", response_model=None)
async def process_data(
    request: Request,
    project_id: Annotated[str, PathParameter(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")],
    process_request: ProcessRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str | int] | JSONResponse:
    """Persist chunks for one registered file or every file in a project."""
    db_client = request.app.state.db_client
    try:
        project = await ProjectModel(db_client).get_project(project_id)
        if project is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"signal": ResponseSignal.FILE_NO_FILES_ERROR.value},
            )

        asset_model = AssetModel(db_client)
        if process_request.file_id is not None:
            asset = await asset_model.get_asset_record(
                project.id, process_request.file_id
            )
            if asset is None:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"signal": ResponseSignal.FILE_ID_ERROR.value},
                )
            assets = [asset]
        else:
            assets = await asset_model.get_all_project_assets(
                project.id, AssetTypeEnum.FILE.value
            )
    except PyMongoError as error:
        logger.error("Could not retrieve project files (%s)", type(error).__name__)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"signal": ResponseSignal.FILE_PROCESSING_FAILED.value},
        )

    if not assets:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.FILE_NO_FILES_ERROR.value},
        )

    chunks: list[DataChunk] = []
    try:
        process_controller = ProcessController(settings, project_id)
        # Validate every selected file before a project-wide reset deletes data.
        for asset in assets:
            file_content = await run_in_threadpool(
                process_controller.get_file_content, asset.asset_name
            )
            file_chunks = await run_in_threadpool(
                process_controller.process_file_content,
                file_content,
                asset.asset_name,
                process_request.chunk_size,
                process_request.overlap_size,
            )
            if not file_chunks:
                raise ValueError("The document has no extracted text")
            chunks.extend(
                DataChunk(
                    chunk_text=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_order=order,
                    chunk_project_id=project.id,
                    chunk_asset_id=asset.id,
                )
                for order, chunk in enumerate(file_chunks, start=1)
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

    chunk_model = DataChunkModel(db_client)
    try:
        if process_request.do_reset:
            await chunk_model.delete_chunks_by_project_id(project.id)
        no_records = await chunk_model.insert_many_chunks(chunks)
    except PyMongoError as error:
        logger.error("Could not save document chunks (%s)", type(error).__name__)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "signal": ResponseSignal.FILE_PROCESSING_FAILED.value,
                "message": "Some chunk changes may already have been saved",
            },
        )

    return {
        "signal": ResponseSignal.FILE_PROCESSING_SUCCESS.value,
        "project_id": str(project.id),
        "no_records": no_records,
        "processed_files": len(assets),
    }
