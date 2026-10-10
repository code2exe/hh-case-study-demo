import os

from fastapi import FastAPI

app = FastAPI(title="hh-hello-api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/hello")
def hello(name: str) -> dict[str, str]:
    return {"message": f"{os.getenv('GREETING', 'Hello')}, {name}"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": os.getenv("APP_VERSION", "unknown")}
