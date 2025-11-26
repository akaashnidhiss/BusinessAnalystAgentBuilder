from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from ..data_agent.dataset_registry import datasets_root, get_dataset, list_datasets
from ..data_agent.duckdb_query import run_query
from ..data_agent.orchestrator import create_dataset, run_dataset_agent


router = APIRouter()


class PreviewResponse(BaseModel):
    upload_id: str
    columns: List[str]
    inferred_types: Dict[str, str]


class DatasetCreateRequest(BaseModel):
    upload_id: str
    dims: List[str]
    metrics: List[str] = []
    display_name: Optional[str] = None


class DatasetCreateResponse(BaseModel):
    dataset_id: str
    display_name: str
    dims: List[str]
    metrics: List[str]
    stats: Dict[str, Any]


class FiltersRunRequest(BaseModel):
    filters: Dict[str, List[str]]
    limit: Optional[int] = None


class AgentRunRequest(BaseModel):
    natural_query: str
    email: Optional[str] = None
    client_id: Optional[str] = None
    session_id: Optional[str] = None


class DatasetSummary(BaseModel):
    dataset_id: str
    display_name: str
    dims: List[str]
    metrics: List[str]
    stats: Dict[str, Any]
    taxonomy_yaml: str
    is_current: bool


def _uploads_dir() -> Path:
    root = datasets_root().parent
    d = root / "uploads"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _user_map_path() -> Path:
    root = datasets_root().parent
    return root / "user_datasets.json"


def _load_user_map() -> Dict[str, str]:
    path = _user_map_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_user_map(mapping: Dict[str, str]) -> None:
    path = _user_map_path()
    path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")


def _set_user_dataset(user_id: str, dataset_id: str) -> None:
    mapping = _load_user_map()
    mapping[user_id] = dataset_id
    _save_user_map(mapping)


def _get_user_dataset(user_id: str) -> str:
    mapping = _load_user_map()
    if user_id not in mapping:
        raise HTTPException(status_code=404, detail="No dataset configured for this user")
    return mapping[user_id]


@router.post("/users/{user_id}/datasets/preview", response_model=PreviewResponse)
async def preview_dataset(user_id: str, file: UploadFile = File(...)) -> PreviewResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")
    upload_id = uuid.uuid4().hex
    dest = _uploads_dir() / f"{upload_id}.csv"
    content = await file.read()
    dest.write_bytes(content)

    try:
        df = pd.read_csv(dest, nrows=100)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {e}")

    cols = list(df.columns)
    inferred: Dict[str, str] = {}
    for c in cols:
        dt = df[c].dtype
        if pd.api.types.is_numeric_dtype(dt):
            inferred[c] = "number"
        elif pd.api.types.is_datetime64_any_dtype(dt):
            inferred[c] = "datetime"
        else:
            inferred[c] = "string"

    return PreviewResponse(upload_id=upload_id, columns=cols, inferred_types=inferred)


@router.post("/users/{user_id}/datasets", response_model=DatasetCreateResponse)
async def create_user_dataset(user_id: str, body: DatasetCreateRequest) -> DatasetCreateResponse:
    upload_path = _uploads_dir() / f"{body.upload_id}.csv"
    if not upload_path.exists():
        raise HTTPException(status_code=404, detail="Upload not found; preview may have expired")

    dataset_id = f"{user_id}_{int(time.time())}"
    meta = create_dataset(
        dataset_id=dataset_id,
        raw_file_path=str(upload_path),
        dims=body.dims,
        metrics=body.metrics,
        display_name=body.display_name or dataset_id,
    )
    _set_user_dataset(user_id, dataset_id)

    return DatasetCreateResponse(
        dataset_id=meta.dataset_id,
        display_name=meta.display_name or meta.dataset_id,
        dims=meta.dims,
        metrics=meta.metrics,
        stats=meta.stats,
    )


@router.get("/users/{user_id}/datasets", response_model=List[DatasetSummary])
async def list_user_datasets(user_id: str) -> List[DatasetSummary]:
    mapping = _load_user_map()
    current_id = mapping.get(user_id)
    summaries: List[DatasetSummary] = []
    prefix = f"{user_id}_"
    for meta in list_datasets():
        if not meta.dataset_id.startswith(prefix):
            continue
        yaml_str = ""
        if meta.taxonomy_yaml_path:
            p = Path(meta.taxonomy_yaml_path)
            if p.exists():
                yaml_str = p.read_text(encoding="utf-8")
        summaries.append(
            DatasetSummary(
                dataset_id=meta.dataset_id,
                display_name=meta.display_name or meta.dataset_id,
                dims=meta.dims,
                metrics=meta.metrics,
                stats=meta.stats,
                taxonomy_yaml=yaml_str,
                is_current=(meta.dataset_id == current_id),
            )
        )
    return summaries


@router.get("/users/{user_id}/taxonomy")
async def get_user_taxonomy(user_id: str) -> Dict[str, Any]:
    dataset_id = _get_user_dataset(user_id)
    meta = get_dataset(dataset_id)

    yaml_str = ""
    if meta.taxonomy_yaml_path:
        p = Path(meta.taxonomy_yaml_path)
        if p.exists():
            yaml_str = p.read_text(encoding="utf-8")

    per_dim: Dict[str, List[str]] = {}
    if meta.valid_sets_path:
        vp = Path(meta.valid_sets_path)
        if vp.exists():
            try:
                vs = json.loads(vp.read_text(encoding="utf-8"))
                per_dim = vs.get("per_dim", {}) or {}
            except Exception:
                per_dim = {}

    return {
        "ok": True,
        "dataset_id": meta.dataset_id,
        "display_name": meta.display_name or meta.dataset_id,
        "dims": meta.dims,
        "metrics": meta.metrics,
        "stats": meta.stats,
        "taxonomy_yaml": yaml_str,
        "per_dim_values": per_dim,
    }


@router.post("/users/{user_id}/run/filters")
async def run_user_filters(user_id: str, body: FiltersRunRequest) -> Dict[str, Any]:
    dataset_id = _get_user_dataset(user_id)
    meta = get_dataset(dataset_id)

    filt_norm: Dict[str, List[str]] = {}
    for dim, vals in (body.filters or {}).items():
        if dim not in meta.dims:
            continue
        cleaned: List[str] = []
        for v in vals:
            if v is None:
                continue
            s = str(v).strip()
            if s:
                cleaned.append(s)
        if cleaned:
            filt_norm[dim] = cleaned

    diag: Dict[str, Any] = {"requested": body.filters, "used": filt_norm}
    if not filt_norm:
        return {
            "ok": False,
            "filters": body.filters,
            "canonical_filters": {},
            "rows": [],
            "row_count": 0,
            "diag": {**diag, "reason": "no_valid_filters"},
        }

    rows, row_count = run_query(dataset_id, filt_norm, limit=body.limit, meta=meta)
    return {
        "ok": True,
        "filters": body.filters,
        "canonical_filters": filt_norm,
        "rows": rows,
        "row_count": row_count,
        "diag": diag,
    }


@router.post("/users/{user_id}/run/agent")
async def run_user_agent(user_id: str, body: AgentRunRequest) -> Dict[str, Any]:
    dataset_id = _get_user_dataset(user_id)
    result = run_dataset_agent(
        dataset_id=dataset_id,
        natural_query=body.natural_query,
        email=body.email,
        client_id=body.client_id,
        session_id=body.session_id,
    )
    return result

