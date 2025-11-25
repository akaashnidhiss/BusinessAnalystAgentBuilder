"""
FastAPI application entrypoint for the MCP demo scaffold.

- Provides dataset lifecycle endpoints (upload -> configure -> ETL -> taxonomy preview -> DuckDB init).
- Provides a single safe query endpoint that delegates to validation/backoff logic and DuckDB execution.

This is intentionally lightweight; plug in auth, persistence, and richer error handling as needed.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import datasets, query


def create_app() -> FastAPI:
    app = FastAPI(title="MCP Categorical Data Demo", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
    app.include_router(query.router, prefix="/api", tags=["query"])
    return app


app = create_app()

