# Dr-RAG

A retrieval-augmented generation project for document-based question answering.
This version prepares the development environment. There is no application to run
yet.

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

## Configuration

Edit `.env` for local settings. Keep this file out of Git.

- `APP_NAME`: application name.
- `APP_VERSION`: application version.
- `OPENAI_API_KEY`: leave empty until model integration is added.

## Dependencies

`requirements.txt` lists the three pinned application dependencies. pip resolves
their compatible dependencies during installation.

## License

[MIT](LICENSE). Copyright (c) 2026 Dreahim.
