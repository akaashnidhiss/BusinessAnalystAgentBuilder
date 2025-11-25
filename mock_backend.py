"""
Lightweight mock backend to unblock frontend iteration.

Run:
    python -m uvicorn mock_backend:app --reload

Exposes the same endpoints but serves static/dummy data so you don't need uploads or DuckDB running.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mock MCP Backend", version="0.0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy in-memory dataset
DATASET_ID = "mock-ds-1"
DATASET = {
    "dataset_id": DATASET_ID,
    "filename": "demo.csv",
    "columns_raw": ["L1", "Region", "L2", "L3", "company_name", "revenue"],
    "columns_normalized": ["l1", "region", "l2", "l3", "company_name", "revenue"],
    "sample_preview": [
        {"L1": "chemicals", "Region": "americas", "L2": "additives", "L3": "adhesion", "company_name": "Acme", "revenue": "50M"},
        {"L1": "chemicals", "Region": "europe", "L2": "additives", "L3": "adhesion", "company_name": "Beta", "revenue": "30M"},
    ],
    "taxonomy_yaml": "chemicals (2):\n  americas (1):\n    additives (1):\n      adhesion (1)\n  europe (1):\n    additives (1):\n      adhesion (1)",
}


@app.get("/api/datasets")
def list_datasets():
    return [
        {
            "dataset_id": DATASET_ID,
            "filename": DATASET["filename"],
            "has_config": True,
            "has_taxonomy": True,
        }
    ]


@app.post("/api/datasets/upload")
def upload():
    return {"dataset_id": DATASET_ID, "filename": DATASET["filename"], "rows_previewed": len(DATASET["sample_preview"])}


@app.get("/api/datasets/{dataset_id}/columns")
def get_columns(dataset_id: str, preview_rows: int = 5):
    if dataset_id != DATASET_ID:
        return {"detail": "unknown dataset_id"}, 404
    return {
        "dataset_id": DATASET_ID,
        "columns_raw": DATASET["columns_raw"],
        "columns_normalized": DATASET["columns_normalized"],
        "sample_preview": DATASET["sample_preview"][:preview_rows],
    }


@app.get("/api/datasets/{dataset_id}/config")
def get_config(dataset_id: str):
    if dataset_id != DATASET_ID:
        return {"detail": "unknown dataset_id"}, 404
    return {
        "filterable_columns": ["L1", "Region", "L2", "L3"],
        "retrievable_columns": ["company_name", "revenue"],
    }


@app.post("/api/datasets/{dataset_id}/config")
def set_config(dataset_id: str, config: dict):
    if dataset_id != DATASET_ID:
        return {"detail": "unknown dataset_id"}, 404
    return config


@app.post("/api/datasets/{dataset_id}/etl")
def etl(dataset_id: str, payload: dict):
    if dataset_id != DATASET_ID:
        return {"detail": "unknown dataset_id"}, 404
    return {"dataset_id": DATASET_ID, "normalized_path": "/tmp/mock.csv", "leaf_index_path": "/tmp/mock_leaf.csv", "stats": {"rows": 2, "leaf_rows": 2}}


@app.post("/api/datasets/{dataset_id}/duckdb/init")
def init_db(dataset_id: str):
    if dataset_id != DATASET_ID:
        return {"detail": "unknown dataset_id"}, 404
    return {"ok": True, "table_name": "mock_table"}


@app.get("/api/datasets/{dataset_id}/taxonomy")
def taxonomy(dataset_id: str):
    if dataset_id != DATASET_ID:
        return {"detail": "unknown dataset_id"}, 404
    return {"dataset_id": DATASET_ID, "yaml": DATASET["taxonomy_yaml"], "counts": {"leaf_rows": 2}, "dims": ["L1", "Region", "L2", "L3"]}


@app.post("/api/query")
def query(payload: dict):
    # Echo back with dummy rows and diag
    return {
        "ok": True,
        "rows": DATASET["sample_preview"],
        "row_count": len(DATASET["sample_preview"]),
        "diag": {
            "requested": payload.get("filters", {}),
            "canonical_candidates": payload.get("filters", {}),
            "used": payload.get("filters", {}),
            "backoff_level": "exact",
            "reason": None,
            "counts": {"returned_rows": len(DATASET["sample_preview"])},
        },
    }

