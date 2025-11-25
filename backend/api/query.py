"""Query endpoint that enforces validation/backoff and safe DuckDB execution."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import BackoffDiag, QueryFilters, QueryResponse
from ..services import duckdb_store, validation
from ..storage import get_dataset

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def run_query(payload: QueryFilters):
    try:
        rec = get_dataset(payload.dataset_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not rec.valid_sets:
        raise HTTPException(status_code=400, detail="Validation sets missing. Run ETL first.")
    if not duckdb_store.is_initialized(payload.dataset_id):
        raise HTTPException(status_code=400, detail="DuckDB not initialized. Call /duckdb/init.")

    ok, canonical_filters, diag_raw = validation.validate_and_backoff(
        payload.filters, rec.valid_sets, rec.dims
    )

    diag = BackoffDiag(**diag_raw)

    if not ok:
        return QueryResponse(ok=False, rows=[], row_count=0, diag=diag, error="invalid_filters")

    df = duckdb_store.query(payload.dataset_id, canonical_filters, payload.limit)
    rows = df.to_dict(orient="records")
    diag.counts["returned_rows"] = len(rows)

    return QueryResponse(ok=True, rows=rows, row_count=len(rows), diag=diag)
