"""
Per-dataset DuckDB connections and safe query execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import duckdb  # type: ignore
import pandas as pd


@dataclass
class DuckDBHandle:
    conn: duckdb.DuckDBPyConnection
    table_name: str
    dims: List[str]


_HANDLES: Dict[str, DuckDBHandle] = {}


def register_duckdb(dataset_id: str, normalized_path: str, dims: List[str]) -> DuckDBHandle:
    table_name = f"ds_{dataset_id.replace('-', '_')}"
    conn = duckdb.connect(database=":memory:")
    conn.execute(
        f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT * FROM read_csv_auto(?, header=True);
        """,
        [normalized_path],
    )
    handle = DuckDBHandle(conn=conn, table_name=table_name, dims=dims)
    _HANDLES[dataset_id] = handle
    return handle


def get_handle(dataset_id: str) -> DuckDBHandle:
    if dataset_id not in _HANDLES:
        raise KeyError(f"DuckDB not initialized for dataset_id={dataset_id}")
    return _HANDLES[dataset_id]


def is_initialized(dataset_id: str) -> bool:
    return dataset_id in _HANDLES


def _clean_filter(values: Optional[List[str]]) -> Optional[List[str]]:
    if not values:
        return None
    cleaned: List[str] = []
    for v in values:
        if v is None:
            continue
        s = str(v).strip()
        if not s:
            continue
        if s.lower() == "blank":
            continue
        cleaned.append(s)
    return cleaned or None


def query(dataset_id: str, filters: Dict[str, List[str]], limit: Optional[int]) -> pd.DataFrame:
    h = get_handle(dataset_id)
    sql = f"SELECT * FROM {h.table_name} WHERE 1=1"
    params: List[str | int] = []

    for dim in h.dims:
        vals = _clean_filter(filters.get(dim))
        if vals:
            placeholders = ", ".join(["?"] * len(vals))
            sql += f" AND {dim} IN ({placeholders})"
            params.extend(vals)

    if limit is not None and limit > 0:
        sql += " LIMIT ?"
        params.append(int(limit))

    return h.conn.execute(sql, params).fetchdf()
