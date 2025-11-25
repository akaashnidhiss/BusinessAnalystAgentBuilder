"""
MCP server scaffold exposing a single CategoricalDataQuery tool.

This intentionally mirrors the SupplierDiscovery Metacube tool:
- Accepts only whitelisted filters (no raw SQL).
- Uses validation/backoff derived from the taxonomy leaf index.
- Returns rows plus diagnostics describing how the request was relaxed.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from backend.services import duckdb_store, validation
from backend.storage import get_dataset


def get_tool_description() -> Dict[str, object]:
    return {
        "name": "CategoricalDataQuery",
        "description": "Safely query the uploaded categorical dataset using validated filters.",
        "schema": {
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string"},
                "filters": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "limit": {"type": "integer"},
            },
            "required": ["dataset_id", "filters"],
        },
    }


def categorical_data_query(dataset_id: str, filters: Dict[str, List[str]], limit: Optional[int] = None) -> Dict[str, object]:
    rec = get_dataset(dataset_id)
    if not rec.valid_sets:
        return {"ok": False, "error": "validation_missing", "diag": {"reason": "run_etl_first"}}
    if not duckdb_store.is_initialized(dataset_id):
        return {"ok": False, "error": "duckdb_missing", "diag": {"reason": "init_duckdb_first"}}

    ok, canonical_filters, diag = validation.validate_and_backoff(filters, rec.valid_sets, rec.dims)
    if not ok:
        return {"ok": False, "error": "invalid_filters", "diag": diag}

    df = duckdb_store.query(dataset_id, canonical_filters, limit)
    rows = df.to_dict(orient="records")
    diag["counts"] = diag.get("counts", {})
    diag["counts"]["returned_rows"] = len(rows)

    return {
        "ok": True,
        "rows": rows,
        "row_count": len(rows),
        "canonical_filters": canonical_filters,
        "diag": diag,
    }


def taxonomy_context(dataset_id: str) -> Dict[str, object]:
    """
    Helper to surface taxonomy and schema to the agent at init.
    """
    rec = get_dataset(dataset_id)
    return {
        "dataset_id": dataset_id,
        "taxonomy_yaml": rec.taxonomy_yaml or "",
        "dims": rec.dims,
        "filterable": rec.config.filterable_columns if rec.config else [],
        "retrievable": rec.config.retrievable_columns if rec.config else [],
    }
