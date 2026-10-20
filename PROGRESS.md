# Development progress

## Project setup

- Created the `dr-rag` Conda environment on Ubuntu WSL.
- Pinned Python and the three direct application dependencies.
- Added the configuration template and assets directory.
- Added Git ignore rules.

## FastAPI application

- Added the FastAPI application entry point.
- Added `GET /welcome` as the first API endpoint.
- Added a Postman collection for the welcome request.

## Dependencies

| Package | Version |
| --- | --- |
| Python | 3.14.8 |
| FastAPI | 0.145.0 |
| Uvicorn | 0.54.0 |
| python-multipart | 0.0.32 |
| uv | 0.13.1 |

## Validation

- Dependency compatibility and imports checked on WSL.
- The setup command tested in a fresh Conda environment.
- Configuration defaults and Git ignore rules checked.
- Repository contents reviewed for credentials.
- Application import, startup, welcome response, and OpenAPI schema checked on WSL.

Native Windows execution has not been validated.

## Next

Organize the API with versioned routing. Not started.
