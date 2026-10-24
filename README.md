# Dr-RAG

A retrieval-augmented generation project for document-based question answering.
The current version uploads text and PDF files, registers them in MongoDB, and
stores their extracted text chunks.

## Prerequisites

- Git
- Conda (Miniconda or Anaconda)
- Docker with Compose

The commands below use Ubuntu in WSL. Start Docker Desktop and enable its
integration for your Ubuntu distribution before running Docker commands.

## Setup

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

## Start MongoDB

From the repository root:

```bash
cd docker
cp .env.example .env
```

Set `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD` in `docker/.env`.
Choose your own credentials and keep the file out of Git. Compose rejects empty
credentials.

```bash
docker compose up -d
docker compose ps
cd ..
```

MongoDB listens at `127.0.0.1:27038`. The Compose project is named `dr-rag`, and
database files are stored in its `dr-rag_mongodata` volume.

Edit the root `.env` and replace `USERNAME` and `PASSWORD` in `MONGODB_URL` with
the credentials from `docker/.env`. URL-encode special characters in the username
or password. Keep `authSource=admin` because the initialization user belongs to
the `admin` database. `MONGODB_DB_NAME` selects the separate application database.

The two `.env` files have separate roles: `docker/.env` initializes MongoDB;
the root `.env` configures the API connection. Both are ignored by Git.

## Run the application

Start the development server from the repository root (`Dr-RAG/`):

```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 5000
```

The API verifies its database connection and creates collection indexes before
accepting requests. If startup fails, check that MongoDB is running and that the
root `.env` contains the correct credentials and port.

- Application information: <http://127.0.0.1:5000/api/v1/>
- Interactive API documentation: <http://127.0.0.1:5000/docs>

The Postman collection in `src/assets/dr-rag.postman_collection.json` includes
upload, single-file processing, and all-file processing requests. Set its
`file_id` variable to the asset ID returned by an upload.

## Upload a file

```bash
curl -F 'file=@notes.txt;type=text/plain' \
  http://127.0.0.1:5000/api/v1/data/upload/demo
```

The response contains `file_upload_success` and a `file_id`. This ID identifies
the MongoDB asset record; it is not the stored filename. Original file bytes are
saved under `src/assets/files/demo/`, which is ignored by Git.

Project IDs may contain letters, digits, underscores, and hyphens, and must
start with a letter or digit.

## Process documents

Use the asset ID returned by upload and the same project ID:

```bash
curl -X POST http://127.0.0.1:5000/api/v1/data/process/demo \
  -H 'Content-Type: application/json' \
  -d '{"file_id":"YOUR_ASSET_ID","chunk_size":100,"overlap_size":20}'
```

Omit `file_id` to process every registered file in the project:

```bash
curl -X POST http://127.0.0.1:5000/api/v1/data/process/demo \
  -H 'Content-Type: application/json' \
  -d '{"chunk_size":100,"overlap_size":20,"do_reset":0}'
```

The response contains `file_processing_success`, the internal project ID,
`no_records` for newly inserted chunks, and `processed_files` for this request.
Chunk text, metadata, order, and project/asset references are saved in MongoDB's
`chunks` collection. The API returns a summary rather than the chunks themselves.

Chunk size and overlap are measured in characters. The defaults are 100 and 20;
size must be positive, and overlap must be nonnegative and smaller than size.
Text files must use UTF-8. PDF chunks retain source and page metadata.
Password-protected and image-only PDFs are not supported; OCR is not included.

Processing appends chunks by default, so repeating a request creates duplicates.
Set `do_reset` to `1` to delete **all existing chunks for that project**, even when
selecting only one file. Every selected file is loaded and split before reset.
Database batches are not one transaction: a database failure can still leave
partial changes after deletion or insertion.

Files uploaded before asset registration existed must be uploaded again.
Processing selects MongoDB asset records and does not scan the upload directory.
No embeddings or vector search are included yet.

## Database operations

From `docker/`, check database authentication using your configured username:

```bash
docker compose exec mongodb mongosh --username YOUR_USERNAME --authenticationDatabase admin
```

Enter the password when prompted. Inside the shell, run
`db.runCommand({ ping: 1 })`; a ready server returns `ok: 1`. Use `exit` to leave.
Check startup problems with `docker compose logs mongodb`.

Stop the service with `docker compose down`. The named volume keeps its data;
adding `--volumes` deletes that data. Initialization credentials apply only when
the volume is empty. Editing `docker/.env` does not change an existing user's
password. Run `cd ..` before starting the API from the repository root.

## Configuration

Edit the root `.env` for application settings:

- `APP_NAME` and `APP_VERSION`: application metadata.
- `OPENAI_API_KEY`: leave empty until model integration is added.
- `FILE_ALLOWED_TYPES`: accepted media types; defaults to text and PDF.
- `FILE_MAX_SIZE_MB`: maximum upload size in MiB; defaults to 10.
- `FILE_DEFAULT_CHUNK_SIZE`: bytes read per upload write; defaults to 512000.
- `FILE_STORAGE_DIR`: optional path for uploaded files.
- `MONGODB_URL`: required MongoDB connection URI.
- `MONGODB_DB_NAME`: application database; defaults to `dr-rag`.

## Dependencies

`requirements.txt` pins the direct application dependencies. pip resolves their
compatible dependencies. MongoDB access uses PyMongo's asynchronous client.

Document loading uses `PyMuPDFLoader` and `TextLoader` from `langchain-community`.
This package is [archived](https://github.com/langchain-ai/langchain-community);
version 0.4.2 is pinned to retain these loaders. Recursive splitting uses
`langchain-text-splitters`.

## License

[MIT](LICENSE). Copyright (c) 2026 Dreahim.

PyMuPDF has separate [AGPL/commercial license terms](https://pypi.org/project/PyMuPDF/1.28.2/).
