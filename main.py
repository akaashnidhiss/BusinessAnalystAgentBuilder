from __future__ import annotations

from fastapi import FastAPI

from .backend.api import datasets as datasets_api
from .backend.api import query as query_api


app = FastAPI()

app.include_router(datasets_api.router, prefix="/api")
app.include_router(query_api.router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


