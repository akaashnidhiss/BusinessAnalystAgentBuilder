"""
Lightweight ETL pipeline inspired by the supplier cataloging notebook.

Steps:
- Normalize column names to lowercase + underscores.
- Normalize filterable dimension values (lowercase + underscores, strip).
- Produce a normalized dataset file for DuckDB ingestion.
- Build a leaf_index table of distinct filterable combinations with counts.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from ..schemas import DatasetConfig


def _normalize_column(col: str) -> str:
    col = col.strip().lower()
    col = re.sub(r"[^a-z0-9]+", "_", col)
    return col.strip("_")


def _normalize_value(val) -> str:
    text = "" if val is None else str(val)
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "blank"


def run_etl(dataset_id: str, raw_path: str, config: DatasetConfig) -> Tuple[str, str, Dict[str, int]]:
    """
    Returns:
        normalized_path: CSV file with normalized column names/values.
        leaf_index_path: CSV file with counts per filterable combination.
        stats: simple counters (rows, leaf_rows).
    """
    df = pd.read_csv(raw_path)

    # Normalize columns once
    df.columns = [_normalize_column(c) for c in df.columns]

    # Ensure filterable/retrievable names are aligned to normalized form
    filterable = [_normalize_column(c) for c in config.filterable_columns]
    retrievable = [_normalize_column(c) for c in config.retrievable_columns]

    # Normalize dimension values; leave retrievable columns untouched
    for col in filterable:
        if col in df.columns:
            df[col] = df[col].apply(_normalize_value)

    # Paths
    raw_dir = Path(raw_path).resolve().parent
    normalized_path = raw_dir / f"{dataset_id}_normalized.csv"
    leaf_index_path = raw_dir / f"{dataset_id}_leaf_index.csv"

    df.to_csv(normalized_path, index=False)

    # Build leaf index (distinct filterable combos)
    leaf_index = (
        df[filterable]
        .drop_duplicates()
        .assign(count=1)
        .groupby(filterable)["count"]
        .sum()
        .reset_index()
    )
    leaf_index.to_csv(leaf_index_path, index=False)

    stats = {"rows": len(df), "leaf_rows": len(leaf_index)}
    return str(normalized_path), str(leaf_index_path), stats

