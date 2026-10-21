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
- Expanded the Postman collection and README with an upload example.

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
| uv | 0.13.1 |

## Validation

- Dependency compatibility and imports checked on WSL.
- The setup command tested in a fresh Conda environment.
- Configuration defaults and Git ignore rules checked.
- Repository contents reviewed for credentials.
- Application imports, live startup, endpoint responses, documentation, and OpenAPI schema checked on WSL.
- Versioned routing, environment-backed metadata, and removal of the old welcome route checked on WSL.
- Upload endpoint, file storage, validation, and existing routes checked on WSL.

Native Windows execution has not been validated.

## Next

Document ingestion and later retrieval work have not started.
