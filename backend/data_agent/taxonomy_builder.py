from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd

from .dataset_registry import DatasetMetadata, dataset_dir, save_dataset


def _normalize_col(name: str) -> str:
    name = name.strip()
    name = name.lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "col"


def _normalize_val(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip().lower()
    if not s or s in {"nan", "none", "null"}:
        return None
    return s


def _build_leaf_index(df: pd.DataFrame, dims: List[str], metrics: List[str]) -> pd.DataFrame:
    if not dims:
        df = df.copy()
        df["_rows_"] = 1
        agg = {"_rows_": "sum"}
        for m in metrics:
            if m in df.columns:
                agg[m] = "sum"
        out = df.agg(agg)
        return out.to_frame().T
    df = df.copy()
    df["_rows_"] = 1
    agg = {"_rows_": "sum"}
    for m in metrics:
        if m in df.columns:
            agg[m] = "sum"
    grouped = df.groupby(dims, dropna=False).agg(agg).reset_index()
    return grouped


def _taxonomy_yaml(
    dataset_id: str,
    dims: List[str],
    metrics: List[str],
    leaf_df: pd.DataFrame,
) -> str:
    lines: List[str] = []
    lines.append(f"dataset_id: {dataset_id}")
    lines.append("dims:")
    for d in dims:
        lines.append(f"  - {d}")
    if metrics:
        lines.append("metrics:")
        for m in metrics:
            lines.append(f"  - {m}")
    lines.append("routing:")
    if leaf_df.empty:
        return "\n".join(lines)

    rows = leaf_df[dims + ["_rows_"] + [m for m in metrics if m in leaf_df.columns]]
    rows = rows.sort_values(dims)
    prev_path: List[Optional[str]] = [None] * len(dims)

    for _, row in rows.iterrows():
        counts = int(row["_rows_"])
        metric_snippet = ""
        if metrics:
            m = metrics[0]
            if m in row and pd.notna(row[m]):
                metric_snippet = f", {m}≈{row[m]}"  # type: ignore[operator]
        for depth, dim in enumerate(dims):
            val = row[dim]
            if pd.isna(val):
                val = "nan"
            if prev_path[depth] == val:
                continue
            prev_path[depth] = val
            for j in range(depth + 1, len(dims)):
                prev_path[j] = None
            indent = "  " * (depth + 1)
            suffix = ""
            if depth == len(dims) - 1:
                suffix = f" (rows={counts}{metric_snippet})"
            lines.append(f"{indent}{val}{suffix}")
    return "\n".join(lines)


def _valid_sets(leaf_df: pd.DataFrame, dims: List[str]) -> Dict[str, Any]:
    per_dim: Dict[str, List[str]] = {}
    for d in dims:
        if d not in leaf_df.columns:
            continue;
        vals = leaf_df[d].dropna().astype(str).str.strip().str.lower().unique().tolist()
        vals = sorted({v for v in vals if v})
        per_dim[d] = vals
    combos_full: List[Tuple[str, ...]] = []
    if dims:
        for _, row in leaf_df[dims].iterrows():
            combo = tuple(str(row[d]).strip().lower() if pd.notna(row[d]) else "nan" for d in dims)
            combos_full.append(combo)
    return {"per_dim": per_dim, "combos_full": combos_full}


def build_taxonomy(
    meta: DatasetMetadata,
    sample_size: Optional[int] = None,
) -> DatasetMetadata:
    if not meta.raw_path:
        raise ValueError("DatasetMetadata.raw_path is required")
    raw_path = Path(meta.raw_path)
    if not raw_path.exists():
        raise FileNotFoundError(str(raw_path))

    df = pd.read_csv(raw_path)
    col_map = {_normalize_col(c): c for c in df.columns}
    df = df.rename(columns={v: k for k, v in col_map.items()})

    dims = [_normalize_col(d) for d in meta.dims]
    metrics = [_normalize_col(m) for m in meta.metrics]
    dims = [d for d in dims if d in df.columns]
    metrics = [m for m in metrics if m in df.columns]

    for d in dims:
        df[d] = df[d].map(_normalize_val)

    if sample_size is not None and sample_size > 0:
        df_sample = df.head(sample_size)
    else:
        df_sample = df

    leaf_df = _build_leaf_index(df_sample, dims, metrics)
    stats = {
        "total_rows": int(df.shape[0]),
        "leaf_rows": int(leaf_df.shape[0]),
        "cardinality": {d: int(df[d].nunique(dropna=True)) for d in dims},
    }

    yaml_str = _taxonomy_yaml(meta.dataset_id, dims, metrics, leaf_df)
    valid_sets = _valid_sets(leaf_df, dims)

    ddir = dataset_dir(meta.dataset_id)
    norm_path = ddir / "normalized.csv"
    yaml_path = ddir / "taxonomy.yaml"
    valid_path = ddir / "valid_sets.json"

    df.to_csv(norm_path, index=False)
    yaml_path.write_text(yaml_str, encoding="utf-8")
    with valid_path.open("w", encoding="utf-8") as f:
        json.dump(valid_sets, f, ensure_ascii=False, indent=2)

    meta.normalized_path = str(norm_path)
    meta.taxonomy_yaml_path = str(yaml_path)
    meta.valid_sets_path = str(valid_path)
    meta.dims = dims
    meta.metrics = metrics
    meta.stats = stats

    save_dataset(meta)
    return meta


