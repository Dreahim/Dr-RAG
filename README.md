# Dr-RAG

A retrieval-augmented generation project for document-based question answering.
The current version uploads text and PDF files and splits their extracted text
into chunks.

## Prerequisites

- Git
- Conda (Miniconda or Anaconda), available in your terminal
- Docker with Compose, for the MongoDB service

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
After pulling dependency changes, run `python -m pip install -r requirements.txt`
inside that environment.

Check that the dependencies import successfully:

```bash
python -c "from src.main import app; print('Setup successful')"
```

You should see `Setup successful`.

## Run the application

Start the development server from the repository root (`Dr-RAG/`):

```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 5000
```

Open these URLs after the server starts:

- Application information: <http://127.0.0.1:5000/api/v1/>
- Users placeholder: <http://127.0.0.1:5000/users>
- Interactive API documentation: <http://127.0.0.1:5000/docs>

The Postman collection in `src/assets/dr-rag.postman_collection.json` includes
these requests, file upload, and document processing. Set its `file_id` variable
to the filename returned by an upload before sending the processing request.

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

## Process an uploaded file

Replace `YOUR_FILE_ID` with the `file_id` returned by the upload request. Use
the same project ID for both calls:

```bash
curl -X POST http://127.0.0.1:5000/api/v1/data/process/demo \
  -H 'Content-Type: application/json' \
  -d '{"file_id":"YOUR_FILE_ID","chunk_size":100,"overlap_size":20}'
```

The response is a JSON array of chunks containing `page_content` and `metadata`.
PDF metadata includes the source path and a zero-based page number. Text files
must use UTF-8. Image-only PDFs need OCR, which is not included.

Chunk size and overlap are measured in characters. The defaults are 100 and 20;
size must be positive, and overlap must be nonnegative and smaller than size.
Chunks are returned in memory without saving them or creating embeddings.

## MongoDB

Install and start Docker with the Compose plugin. If you use Docker Desktop
with WSL, enable integration for your Ubuntu distribution.

From the repository root:

```bash
cd docker
cp .env.example .env
```

Set `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD` in this `.env`.
Choose your own credentials and keep the file out of Git. This file configures
MongoDB separately from the application's root `.env`.
Compose rejects empty credentials.

Start the database:

```bash
docker compose up -d
docker compose ps
```

MongoDB listens at `127.0.0.1:27038` on the host. The Compose project is named
`dr-rag`, and database files are stored in its `dr-rag_mongodata` volume.
The application does not connect to MongoDB yet; processing still returns
chunks in memory.

To check authentication, run the following from `docker/`, using the username
you set. Enter the password when prompted:

```bash
docker compose exec mongodb mongosh --username YOUR_USERNAME --authenticationDatabase admin
```

Inside the shell, run `db.runCommand({ ping: 1 })`; a ready server returns
`ok: 1`. Use `exit` to leave. If startup fails, check `docker compose logs mongodb`.

Stop the service with `docker compose down`. The named volume keeps its data.
Adding `--volumes` deletes that data. Initialization credentials are applied
only when the volume is empty; editing `.env` does not change an existing user's
password. Run `cd ..` before starting the API from the repository root.

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

Document loading uses `PyMuPDFLoader` and `TextLoader` from `langchain-community`.
This package is [archived](https://github.com/langchain-ai/langchain-community);
version 0.4.2 is pinned to retain these loaders.
Recursive splitting uses the separate `langchain-text-splitters` package.

## License

[MIT](LICENSE). Copyright (c) 2026 Dreahim.

PyMuPDF has separate [AGPL/commercial license terms](https://pypi.org/project/PyMuPDF/1.28.2/).
