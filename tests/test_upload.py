"""HTTP and storage checks for the initial upload workflow."""

import asyncio
import json
import socket
import tempfile
import threading
import time
import unittest
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import uvicorn
from fastapi import UploadFile
from starlette.datastructures import Headers

from src.controllers.data import DataController
from src.helpers.config import Settings, get_settings
from src.main import app
from src.routes.data import upload_data


class UploadTests(unittest.TestCase):
    """Exercise the public API and its local file storage."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.storage = tempfile.TemporaryDirectory()
        cls.settings = Settings(_env_file=None, FILE_STORAGE_DIR=Path(cls.storage.name))
        app.dependency_overrides[get_settings] = lambda: cls.settings

        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]

        cls.base_url = f"http://127.0.0.1:{port}"
        cls.server = uvicorn.Server(
            uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
        )
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()
        for _ in range(100):
            if cls.server.started:
                break
            time.sleep(0.05)
        else:
            raise RuntimeError("Test server did not start")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.should_exit = True
        cls.thread.join(timeout=5)
        app.dependency_overrides.clear()
        cls.storage.cleanup()

    def request(
        self, path: str, payload: bytes | None = None
    ) -> tuple[int, dict]:
        headers = {}
        if payload is not None:
            headers["Content-Type"] = "multipart/form-data; boundary=dr-rag-test"
        request = Request(
            self.base_url + path,
            data=payload,
            headers=headers,
            method="POST" if payload is not None else "GET",
        )
        try:
            with urlopen(request, timeout=10) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            with error:
                return error.code, json.load(error)

    @staticmethod
    def multipart(filename: str, content_type: str, content: bytes) -> bytes:
        return (
            b"--dr-rag-test\r\n"
            + f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
            + f"Content-Type: {content_type}\r\n\r\n".encode()
            + content
            + b"\r\n--dr-rag-test--\r\n"
        )

    def test_upload_saves_distinct_files_in_project_directory(self) -> None:
        payload = self.multipart("notes.txt", "text/plain", b"first document")
        first_status, first = self.request("/api/v1/data/upload/project_1", payload)
        second_status, second = self.request("/api/v1/data/upload/project_1", payload)

        self.assertEqual((first_status, second_status), (200, 200))
        self.assertEqual(first["signal"], "file_upload_success")
        self.assertNotEqual(first["file_id"], second["file_id"])
        self.assertEqual(
            (Path(self.storage.name) / "project_1" / first["file_id"]).read_bytes(),
            b"first document",
        )

    def test_pdf_is_accepted_and_substring_media_type_is_rejected(self) -> None:
        status, result = self.request(
            "/api/v1/data/upload/pdf",
            self.multipart("paper.pdf", "application/pdf", b"%PDF-1.4"),
        )
        self.assertEqual(status, 200)
        self.assertEqual(result["signal"], "file_upload_success")

        status, result = self.request(
            "/api/v1/data/upload/rejected",
            self.multipart("x.txt", "text/pla", b"hello"),
        )
        self.assertEqual(status, 400)
        self.assertEqual(result["signal"], "file_not_supported")
        self.assertFalse((Path(self.storage.name) / "rejected").exists())

    def test_unsafe_project_id_is_rejected(self) -> None:
        status, _ = self.request(
            "/api/v1/data/upload/%5Coutside",
            self.multipart("x.txt", "text/plain", b"hello"),
        )
        self.assertEqual(status, 422)
        self.assertFalse((Path(self.storage.name).parent / "outside").exists())

    def test_stream_limit_removes_partial_file_when_size_is_unknown(self) -> None:
        settings = Settings(
            _env_file=None,
            FILE_STORAGE_DIR=Path(self.storage.name),
            FILE_MAX_SIZE_MB=1,
        )
        upload = UploadFile(
            file=BytesIO(b"x" * (1024 * 1024 + 1)),
            filename="large.txt",
            headers=Headers({"content-type": "text/plain"}),
            size=None,
        )
        response = asyncio.run(upload_data("large", upload, settings))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.body)["signal"], "file_too_large")
        self.assertEqual(list((Path(self.storage.name) / "large").iterdir()), [])

    def test_reported_oversize_is_rejected_before_storage(self) -> None:
        settings = Settings(
            _env_file=None,
            FILE_STORAGE_DIR=Path(self.storage.name),
            FILE_MAX_SIZE_MB=1,
        )
        upload = UploadFile(
            file=BytesIO(b"x"),
            filename="large.txt",
            headers=Headers({"content-type": "text/plain"}),
            size=1024 * 1024 + 1,
        )
        response = asyncio.run(upload_data("precheck", upload, settings))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.body)["signal"], "file_too_large")
        self.assertFalse((Path(self.storage.name) / "precheck").exists())

    def test_filename_cleanup_and_existing_routes(self) -> None:
        self.assertEqual(DataController.clean_file_name(r"C:\notes\a b.txt"), "a_b.txt")
        status, result = self.request("/api/v1/")
        self.assertEqual(status, 200)
        self.assertEqual(result["app_name"], "Dr-RAG")
        status, result = self.request("/users")
        self.assertEqual(status, 200)
        self.assertEqual(result["message"], "Fetching all users...")
        status, schema = self.request("/openapi.json")
        self.assertEqual(status, 200)
        self.assertIn("/api/v1/data/upload/{project_id}", schema["paths"])


if __name__ == "__main__":
    unittest.main()
