# Dr-RAG

A retrieval-augmented generation project for document-based question answering.
The current version accepts text and PDF files into project-specific local storage.

## Prerequisites

- Git
- Conda (Miniconda or Anaconda), available in your terminal

Setup has been tested on Ubuntu in WSL. The commands below use a WSL terminal.

## Setup

Clone the repository and create the environment:

```bash
git clone https://github.com/Dreahim/Dr-RAG.git
cd Dr-RAG
conda env create -f environment.yml
conda activate dr-rag
cp .env.example .env
```

For later sessions, activate the existing environment with `conda activate dr-rag`.

Check that the dependencies import successfully:

```bash
python -c "import fastapi, uvicorn, aiofiles, pydantic_settings; print('Setup successful')"
```

You should see `Setup successful`.

## Run the application

Start the development server:

```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 5000
```

Open these URLs after the server starts:

- Application information: <http://127.0.0.1:5000/api/v1/>
- Users placeholder: <http://127.0.0.1:5000/users>
- Interactive API documentation: <http://127.0.0.1:5000/docs>

The Postman collection in `src/assets/dr-rag.postman_collection.json` includes
these requests and a file upload request.

## Upload a file

Send a text or PDF file to a project ID:

```bash
curl -F 'file=@notes.txt;type=text/plain' \
  http://127.0.0.1:5000/api/v1/data/upload/demo
```

The response contains `file_upload_success` and a `file_id`. The ID is the stored
filename at this stage. The file is saved under `src/assets/files/demo/`, which
is ignored by Git. Project IDs may contain letters, digits, underscores, and
hyphens, and must start with a letter or digit.

## Configuration

Edit `.env` for local settings. Keep this file out of Git.

- `APP_NAME`: application name.
- `APP_VERSION`: application version.
- `OPENAI_API_KEY`: leave empty until model integration is added.
- `FILE_ALLOWED_TYPES`: comma-separated accepted media types; defaults to text and PDF.
- `FILE_MAX_SIZE_MB`: maximum upload size in MiB; defaults to 10.
- `FILE_DEFAULT_CHUNK_SIZE`: number of bytes read per write; defaults to 512000.
- `FILE_STORAGE_DIR`: optional path for local uploaded files.

## Dependencies

`requirements.txt` lists the pinned application dependencies. pip resolves
their compatible dependencies during installation.

## License

[MIT](LICENSE). Copyright (c) 2026 Dreahim.
