"""Dataset lifecycle endpoints: upload -> configure -> ETL -> taxonomy -> DuckDB init."""

from __future__ import annotations

from typing import Dict, List
import uuid
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from ..schemas import (
    ColumnListResponse,
    DatasetConfig,
    DatasetSummary,
    EtlRequest,
    TaxonomyResponse,
    UploadResponse,
)
from ..services import duckdb_store, etl, taxonomy, validation
from ..storage import get_dataset, list_datasets, register_dataset, update_dataset

router = APIRouter()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    dataset_id = str(uuid.uuid4())
    raw_path = DATA_DIR / f"{dataset_id}_raw.csv"

    content = await file.read()
    raw_path.write_bytes(content)

    register_dataset(dataset_id, str(raw_path), original_filename=file.filename)
    try:
        preview_df = pd.read_csv(raw_path, nrows=5)
        rows_previewed = len(preview_df)
    except Exception:
        rows_previewed = 0

    return UploadResponse(dataset_id=dataset_id, filename=file.filename, rows_previewed=rows_previewed)


@router.post("/{dataset_id}/config", response_model=DatasetConfig)
async def set_config(dataset_id: str, config: DatasetConfig):
    try:
        rec = get_dataset(dataset_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    update_dataset(dataset_id, config=config)
    return config


@router.get("/", response_model=list[DatasetSummary])
async def list_all_datasets():
    summaries: list[DatasetSummary] = []
    for rec in list_datasets():
        summaries.append(
            DatasetSummary(
                dataset_id=rec.dataset_id,
                filename=rec.original_filename,
                has_config=rec.config is not None,
                has_taxonomy=bool(rec.taxonomy_yaml),
            )
        )
    return summaries


@router.get("/{dataset_id}/columns", response_model=ColumnListResponse)
async def get_columns(dataset_id: str, preview_rows: int = 5):
    try:
        rec = get_dataset(dataset_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        df = pd.read_csv(rec.raw_path, nrows=max(preview_rows, 1))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read dataset: {e}")

    columns_raw = list(df.columns)
    columns_normalized = [etl._normalize_column(c) for c in columns_raw]  # type: ignore
    sample = df.to_dict(orient="records")
    return ColumnListResponse(
        dataset_id=dataset_id,
        columns_raw=columns_raw,
        columns_normalized=columns_normalized,
        sample_preview=sample,
    )


@router.get("/{dataset_id}/config", response_model=DatasetConfig)
async def get_config(dataset_id: str):
    try:
        rec = get_dataset(dataset_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if rec.config is None:
        raise HTTPException(status_code=404, detail="Config not set")
    return rec.config


@router.post("/{dataset_id}/etl")
async def trigger_etl(payload: EtlRequest):
    try:
        rec = get_dataset(payload.dataset_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if rec.config is None:
        raise HTTPException(status_code=400, detail="Dataset config not set. Call /config first.")

    normalized_path, leaf_index_path, stats = etl.run_etl(payload.dataset_id, rec.raw_path, rec.config)
    dims = [etl._normalize_column(c) for c in rec.config.filterable_columns]  # type: ignore
    yaml_text = taxonomy.build_taxonomy_yaml(leaf_index_path, dims)
    valid_sets = validation.derive_valid_sets(leaf_index_path, dims)

    update_dataset(
        payload.dataset_id,
        normalized_path=normalized_path,
        leaf_index_path=leaf_index_path,
        taxonomy_yaml=yaml_text,
        dims=dims,
        valid_sets=valid_sets,
    )
    return {
        "dataset_id": payload.dataset_id,
        "normalized_path": normalized_path,
        "leaf_index_path": leaf_index_path,
        "stats": stats,
    }


@router.get("/{dataset_id}/taxonomy", response_model=TaxonomyResponse)
async def get_taxonomy(dataset_id: str):
    try:
        rec = get_dataset(dataset_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not rec.taxonomy_yaml:
        raise HTTPException(status_code=400, detail="Taxonomy not built. Run /etl first.")

    return TaxonomyResponse(
        dataset_id=dataset_id,
        yaml=rec.taxonomy_yaml,
        counts={"leaf_rows": rec.valid_sets.get("stats", {}).get("leaf_rows", 0) if rec.valid_sets else 0},  # type: ignore
        dims=rec.dims,
    )


@router.get("/{dataset_id}/dimensions")
async def get_dimensions(dataset_id: str):
    """
    Expose the validated filter dimensions and their allowed values for a dataset.

    This is derived from the validation sets built during ETL and powers the
    dropdowns / chips in the agent query UI.
    """
    try:
        rec = get_dataset(dataset_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not rec.valid_sets:
        raise HTTPException(status_code=400, detail="Validation sets not available. Run /etl first.")

    per_dim = rec.valid_sets.get("per_dim", {})  # type: ignore[assignment]
    if not isinstance(per_dim, dict):
        raise HTTPException(status_code=500, detail="Invalid validation metadata for dataset.")

    dims: List[str] = rec.dims or list(per_dim.keys())
    values: Dict[str, List[str]] = {}
    for dim in dims:
        dim_values = per_dim.get(dim, set())
        try:
            # per_dim is built from sets; convert to a sorted list for JSON.
            values[dim] = sorted(list(dim_values))
        except TypeError:
            values[dim] = [str(v) for v in dim_values]

    return {
        "dataset_id": dataset_id,
        "dims": dims,
        "values": values,
    }


@router.post("/{dataset_id}/duckdb/init")
async def init_duckdb(dataset_id: str):
    try:
        rec = get_dataset(dataset_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not rec.normalized_path or not rec.dims:
        raise HTTPException(status_code=400, detail="Normalized data missing. Run /etl first.")

    handle = duckdb_store.register_duckdb(dataset_id, rec.normalized_path, rec.dims)
    update_dataset(dataset_id, duckdb_path=rec.normalized_path, table_name=handle.table_name)
    return {"ok": True, "table_name": handle.table_name}
