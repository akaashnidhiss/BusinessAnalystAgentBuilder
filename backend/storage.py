"""
In-memory registry for uploaded datasets.

In production, replace this with a persistent store (DB or blob).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .schemas import DatasetConfig


@dataclass
class DatasetRecord:
    dataset_id: str
    raw_path: str
    original_filename: Optional[str] = None
    config: Optional[DatasetConfig] = None
    normalized_path: Optional[str] = None
    leaf_index_path: Optional[str] = None
    taxonomy_yaml: Optional[str] = None
    dims: List[str] = field(default_factory=list)
    duckdb_path: Optional[str] = None
    table_name: Optional[str] = None
    valid_sets: Dict[str, set] = field(default_factory=dict)

    def ensure_exists(self) -> None:
        Path(self.raw_path).resolve(strict=True)


_DATASETS: Dict[str, DatasetRecord] = {}


def register_dataset(dataset_id: str, raw_path: str, original_filename: Optional[str] = None) -> DatasetRecord:
    rec = DatasetRecord(dataset_id=dataset_id, raw_path=str(Path(raw_path)), original_filename=original_filename)
    _DATASETS[dataset_id] = rec
    return rec


def get_dataset(dataset_id: str) -> DatasetRecord:
    if dataset_id not in _DATASETS:
        raise KeyError(f"Unknown dataset_id: {dataset_id}")
    return _DATASETS[dataset_id]


def update_dataset(dataset_id: str, **kwargs) -> DatasetRecord:
    rec = get_dataset(dataset_id)
    for k, v in kwargs.items():
        setattr(rec, k, v)
    return rec


def list_datasets() -> List[DatasetRecord]:
    return list(_DATASETS.values())
