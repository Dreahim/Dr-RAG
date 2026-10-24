# Development progress

## Project setup

- Created the `dr-rag` Conda environment on Ubuntu WSL.
- Pinned Python and the direct application dependencies.
- Added the configuration template and assets directory.
- Added Git ignore rules.

## FastAPI application

- Added the FastAPI application entry point.
- Organized endpoints in separate route modules.
- Added application metadata at `GET /api/v1/`.
- Added the placeholder `GET /users` endpoint.
- Updated the Postman collection for both routes.

## File uploads

- Moved the application modules into `src/` and kept setup files at the repository root.
- Added project-specific local storage for text and PDF uploads.
- Added configurable file limits, chunked writes, safe names, and upload response signals.
- Limited stored filename bytes while preserving extensions for long Unicode names.
- Expanded the Postman collection and README with an upload example.

## Document processing

- Added `ProcessController` with loader selection, document loading, and text splitting.
- Used `PyMuPDFLoader` for PDFs and `TextLoader` for UTF-8 text files.
- Added the processing request schema, file-type enum, and processing endpoint.
- Preserved document metadata when creating recursive character chunks.
- Kept chunks in memory and added a processing request to the Postman collection.

## MongoDB service

- Added a MongoDB service managed by Docker Compose.
- Pinned the server image to `mongo:8.0.34-noble`.
- Used a separate Compose project, network, named volume, and local port 27038.
- Added a credential template; local credentials remain ignored by Git.
- Documented startup, authentication, and persistent storage.
- Kept application integration and chunk persistence for a later stage.

## Dependencies

| Package | Version |
| --- | --- |
| Python | 3.14.8 |
| FastAPI | 0.145.0 |
| Uvicorn | 0.54.0 |
| python-multipart | 0.0.32 |
| python-dotenv | 1.2.4 |
| aiofiles | 25.1.0 |
| pydantic-settings | 2.15.0 |
| langchain-community | 0.4.2 |
| langchain-core | 1.6.12 |
| langchain-text-splitters | 1.1.3 |
| PyMuPDF | 1.28.2 |
| uv | 0.13.1 |
| MongoDB | 8.0.34 |

## Validation

- Dependency compatibility and imports checked on WSL.
- The setup command tested in a fresh Conda environment.
- Configuration defaults and Git ignore rules checked.
- Repository contents reviewed for credentials.
- Application imports, live startup, endpoint responses, documentation, and OpenAPI schema checked on WSL.
- Versioned routing, environment-backed metadata, and removal of the old welcome route checked on WSL.
- Upload endpoint, file storage, validation, and existing routes checked on WSL.
- All 21 temporary upload and processing checks passed on WSL, including PDF
  metadata, UTF-8 text, chunk overlap, invalid files, and project containment.
- Password-protected PDFs are rejected before calling the document loader.
- Pinned dependency checks, Python compilation, lint, and formatting passed.
- MongoDB Compose configuration and required credentials checked on WSL.
- Authenticated access, rejection of invalid credentials and unauthenticated
  writes, local port binding, and persistent storage verified with Docker.
- A temporary record survived container replacement; verification data was removed.
- All 21 application regression checks passed again with Python dependencies unchanged.

`langchain-community` is archived. Its final stable release is pinned for the
document loaders; no application-to-database or model integration is included.

Native Windows execution has not been validated.

## Next

Database integration and retrieval have not started.
