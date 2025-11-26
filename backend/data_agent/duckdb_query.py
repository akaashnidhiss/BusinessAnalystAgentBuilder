from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from .dataset_registry import DatasetMetadata, get_dataset
from .duckdb_init import get_handle


def _clean_filters(filters: Dict[str, List[str]]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for key, values in filters.items():
        vs = [v for v in values if v is not None and str(v).strip()]
        if vs:
            out[key] = vs
    return out


def _where_clause(filters: Dict[str, List[str]]) -> Tuple[str, List[str]]:
    clauses: List[str] = []
    params: List[str] = []
    for col, values in filters.items():
        if not values:
            continue
        placeholders = ", ".join(["?"] * len(values))
        clauses.append(f"{col} IN ({placeholders})")
        params.extend(values)
    if not clauses:
        return "", params
    return " WHERE " + " AND ".join(clauses), params


def run_query(
    dataset_id: str,
    filters: Dict[str, List[str]],
    limit: Optional[int] = None,
    meta: Optional[DatasetMetadata] = None,
) -> Tuple[List[Dict[str, object]], int]:
    if meta is None:
        meta = get_dataset(dataset_id)
    handle = get_handle(meta)

    filters = _clean_filters(filters)
    where_sql, params = _where_clause(filters)

    cols = list(meta.retrievable_columns or (meta.dims + meta.metrics))
    if not cols:
        cols = ["*"]
    select_list = ", ".join(cols)
    sql = f"SELECT {select_list} FROM {handle.table_name}{where_sql}"
    if limit is not None:
        sql += " LIMIT ?"
        params.append(str(int(limit)))

    cur = handle.conn.execute(sql, params)
    col_names = [d[0] for d in cur.description]
    rows_raw = cur.fetchall()
    rows: List[Dict[str, object]] = [
        {col_names[i]: value for i, value in enumerate(rec)} for rec in rows_raw
    ]
    return rows, len(rows)


