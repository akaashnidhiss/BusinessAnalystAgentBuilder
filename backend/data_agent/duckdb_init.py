from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

import duckdb

from .dataset_registry import DatasetMetadata


@dataclass
class DuckdbHandle:
    dataset_id: str
    conn: duckdb.DuckDBPyConnection
    table_name: str
    dims: List[str]
    retrievable_columns: List[str]


_HANDLES: Dict[str, DuckdbHandle] = {}


def _safe_table_name(dataset_id: str) -> str:
    s = dataset_id.lower()
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def get_handle(meta: DatasetMetadata) -> DuckdbHandle:
    if meta.dataset_id in _HANDLES:
        return _HANDLES[meta.dataset_id]
    if not meta.normalized_path:
        raise ValueError("DatasetMetadata.normalized_path is required for DuckDB init")

    conn = duckdb.connect(database=":memory:")
    table_name = _safe_table_name(meta.dataset_id)
    conn.execute(
        f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto(?, header=True)",
        [meta.normalized_path],
    )

    dims = list(meta.dims)
    retr = list(meta.retrievable_columns or (meta.dims + meta.metrics))
    handle = DuckdbHandle(
        dataset_id=meta.dataset_id,
        conn=conn,
        table_name=table_name,
        dims=dims,
        retrievable_columns=retr,
    )
    _HANDLES[meta.dataset_id] = handle
    return handle


def close_dataset(dataset_id: str) -> None:
    handle = _HANDLES.pop(dataset_id, None)
    if handle is not None:
        try:
            handle.conn.close()
        except Exception:
            pass


