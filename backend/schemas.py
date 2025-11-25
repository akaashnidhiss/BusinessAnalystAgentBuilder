"""
Pydantic models for the MCP demo backend.
These mirror the validation/backoff diagnostics used in the supplier discovery code.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    dataset_id: str
    filename: str
    rows_previewed: int = 0


class DatasetConfig(BaseModel):
    filterable_columns: List[str] = Field(..., description="Dimensions the router will validate (e.g., L1, Region).")
    retrievable_columns: List[str] = Field(..., description="Columns that can be returned in query results.")


class EtlRequest(BaseModel):
    dataset_id: str
    sample_rows: int = Field(50, description="Row limit to include in preview if needed.")


class TaxonomyResponse(BaseModel):
    dataset_id: str
    yaml: str
    counts: Dict[str, int] = Field(default_factory=dict)
    dims: List[str] = Field(default_factory=list, description="Ordered filter dimensions.")


class QueryFilters(BaseModel):
    dataset_id: str
    filters: Dict[str, List[str]] = Field(default_factory=dict)
    limit: Optional[int] = 100


class BackoffDiag(BaseModel):
    requested: Dict[str, List[str]]
    canonical_candidates: Dict[str, List[str]] = Field(default_factory=dict)
    used: Optional[Dict[str, List[str]]] = None
    backoff_level: Optional[str] = None
    reason: Optional[str] = None
    counts: Dict[str, int] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    ok: bool
    rows: List[Dict[str, object]] = Field(default_factory=list)
    row_count: int = 0
    diag: BackoffDiag
    error: Optional[str] = None
    cache_hit: bool = False


class DatasetSummary(BaseModel):
    dataset_id: str
    filename: Optional[str] = None
    has_config: bool = False
    has_taxonomy: bool = False


class ColumnListResponse(BaseModel):
    dataset_id: str
    columns_raw: List[str]
    columns_normalized: List[str]
    sample_preview: List[Dict[str, object]] = Field(default_factory=list)
