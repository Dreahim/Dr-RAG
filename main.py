from fastapi import FastAPI

app = FastAPI()


@app.get("/welcome")
async def welcome() -> dict[str, str]:
    """Return a message confirming that the API is available."""
    return {"message": "Welcome to the FastAPI application! Hi there!"}
