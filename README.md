# Dr-RAG

A retrieval-augmented generation project for document-based question answering.
The current version organizes its first API endpoints with FastAPI routers.

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
python -c "import fastapi, uvicorn, python_multipart; print('Setup successful')"
```

You should see `Setup successful`.

## Run the application

Start the development server:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 5000
```

Open these URLs after the server starts:

- Application information: <http://127.0.0.1:5000/api/v1/>
- Users placeholder: <http://127.0.0.1:5000/users>
- Interactive API documentation: <http://127.0.0.1:5000/docs>

The Postman collection in `assets/dr-rag.postman_collection.json` contains both
requests.

## Configuration

Edit `.env` for local settings. Keep this file out of Git.

- `APP_NAME`: application name.
- `APP_VERSION`: application version.
- `OPENAI_API_KEY`: leave empty until model integration is added.

## Dependencies

`requirements.txt` lists the four pinned application dependencies. pip resolves
their compatible dependencies during installation.

## License

[MIT](LICENSE). Copyright (c) 2026 Dreahim.
