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
- Initially returned chunks in memory and added a processing request to Postman.

## MongoDB service

- Added a MongoDB service managed by Docker Compose.
- Pinned the server image to `mongo:8.0.34-noble`.
- Used a separate Compose project, network, named volume, and local port 27038.
- Added a credential template; local credentials remain ignored by Git.
- Documented startup, authentication, and persistent storage.
- Kept application integration and chunk persistence for a later stage.

## Persistent document ingestion

- Connected the API to MongoDB using PyMongo's asynchronous client and FastAPI lifespan.
- Added project, asset, and chunk schemas, persistence models, and collection indexes.
- Registered uploads as assets and used their database IDs for targeted processing.
- Added processing for every registered file in a project.
- Stored chunk text, metadata, order, and project/asset references in MongoDB.
- Kept append behavior and an explicit project-wide reset option.
- Validated selected documents before reset and handled database/write failures.
- Removed the unused users route and updated the README and Postman collection.

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
| PyMongo | 4.19.0 |
| uv | 0.13.1 |
| MongoDB | 8.0.34 |

## Validation

- Dependency pins, pip compatibility, Python compilation, lint, and formatting checked on WSL.
- All 19 temporary integration checks passed using a separate database and upload directory.
- Live startup with reload, API responses, OpenAPI, Swagger, and shutdown checked.
- Real rejected credentials prevented startup, and the async client closed on failure.
- Verified indexes on existing collections, concurrent project creation, pagination,
  asset uniqueness, and chunk insertion across multiple batches.
- Verified PDF metadata, UTF-8 text, character overlap, and long Unicode filenames.
- Verified single/all-file selection, append behavior, reset scope, and project containment.
- Invalid, empty, missing, or encrypted files were rejected without deleting existing chunks.
- Injected database and write failures checked upload cleanup and partial-write responses.
- Data survived API restart; the MongoDB service previously passed container-replacement checks.
- Temporary verification data was removed; no test suite is included in the repository.

`langchain-community` is archived. Its final stable release is pinned for the
document loaders. PyMongo provides database access; LLM integration has not started.

Native Windows execution has not been validated.

## Next

Embeddings, vector indexing, and retrieval have not started.
