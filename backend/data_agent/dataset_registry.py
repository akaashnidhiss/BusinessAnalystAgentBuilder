from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


_DATASET_ROOT_DIRNAME = "data_agent"
_DATASET_SUBDIR = "datasets"


@dataclass
class DatasetMetadata:
    dataset_id: str
    display_name: Optional[str] = None
    raw_path: Optional[str] = None
    normalized_path: Optional[str] = None
    taxonomy_yaml_path: Optional[str] = None
    valid_sets_path: Optional[str] = None
    dims: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    retrievable_columns: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    prompt_system_path: Optional[str] = None
    prompt_dev_path: Optional[str] = None
    created_at: Optional[str] = None
    routing_version: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


_CACHE: Dict[str, DatasetMetadata] = {}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def datasets_root() -> Path:
    root = _project_root() / _DATASET_ROOT_DIRNAME / _DATASET_SUBDIR
    root.mkdir(parents=True, exist_ok=True)
    return root


def dataset_dir(dataset_id: str) -> Path:
    d = datasets_root() / dataset_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _metadata_path(dataset_id: str) -> Path:
    return dataset_dir(dataset_id) / "metadata.json"


def get_dataset(dataset_id: str) -> DatasetMetadata:
    if dataset_id in _CACHE:
        return _CACHE[dataset_id]
    path = _metadata_path(dataset_id)
    if not path.exists():
        raise KeyError(f"Unknown dataset_id: {dataset_id}")
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    meta = DatasetMetadata(**raw)
    _CACHE[dataset_id] = meta
    return meta


def save_dataset(meta: DatasetMetadata) -> None:
    data = asdict(meta)
    path = _metadata_path(meta.dataset_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    _CACHE[meta.dataset_id] = meta


def list_datasets() -> List[DatasetMetadata]:
    out: List[DatasetMetadata] = []
    root = datasets_root()
    for child in root.iterdir():
        if not child.is_dir():
            continue
        meta_path = child / "metadata.json"
        if not meta_path.exists():
            continue
        try:
            with meta_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            meta = DatasetMetadata(**raw)
            _CACHE[meta.dataset_id] = meta
            out.append(meta)
        except Exception:
            continue
    return out


