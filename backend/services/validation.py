"""
Validation and backoff logic for safe querying.

Heavily inspired by the supplier discovery validation helpers:
- Whitelist-based canonicalization per dimension.
- Backoff by dropping the deepest dimension until a valid combo is found.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd


def _norm(val: Optional[str]) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip().lower()
    return s or None


def derive_valid_sets(leaf_index_path: str, dims: List[str]) -> Dict[str, object]:
    df = pd.read_csv(leaf_index_path)
    for col in dims:
        df[col] = df[col].astype(str).str.strip().str.lower()
        df[col] = df[col].replace("blank", None)

    combos_full = set(tuple(row[d] if row[d] else None for d in dims) for _, row in df.iterrows())

    prefix_sets: List[set] = []
    for depth in range(len(dims)):
        prefix_sets.append(set(tuple(combo[: depth + 1]) for combo in combos_full))

    per_dim = {dim: set(df[dim].dropna().unique()) for dim in dims}
    return {
        "per_dim": per_dim,
        "combos_full": combos_full,
        "combos_prefix": prefix_sets,
        "stats": {"leaf_rows": len(df)},
    }


def _first_or_none(values: Sequence[str]) -> Optional[str]:
    return values[0] if values else None


def validate_and_backoff(
    filters: Dict[str, List[str]],
    valid_sets: Dict[str, object],
    dims: List[str],
) -> Tuple[bool, Dict[str, List[str]], Dict[str, object]]:
    per_dim: Dict[str, set] = valid_sets.get("per_dim", {})  # type: ignore
    combos_full: set = valid_sets.get("combos_full", set())  # type: ignore
    combos_prefix: List[set] = valid_sets.get("combos_prefix", [])  # type: ignore

    requested = {d: filters.get(d, []) or [] for d in dims}
    canonical_candidates = {
        dim: [_norm(v) for v in requested.get(dim, []) if _norm(v) in per_dim.get(dim, set())]
        for dim in dims
    }

    diag = {
        "requested": requested,
        "canonical_candidates": canonical_candidates,
        "used": None,
        "backoff_level": None,
        "reason": None,
        "counts": {"combos_full": len(combos_full)},
    }

    # Require first dimension to survive; extend to second if present
    if not canonical_candidates.get(dims[0]):
        diag["reason"] = f"invalid_{dims[0]}"
        return False, {}, diag
    if len(dims) > 1 and not canonical_candidates.get(dims[1]):
        diag["reason"] = f"invalid_{dims[1]}"
        return False, {}, diag

    # Collapse to a single value per dimension for now
    chosen = [_first_or_none(canonical_candidates.get(dim, [])) for dim in dims]

    def _filters_from_tuple(values: List[Optional[str]]) -> Dict[str, List[str]]:
        out: Dict[str, List[str]] = {}
        for dim, val in zip(dims, values):
            if val:
                out[dim] = [val]
        return out

    # 1) exact combo
    combo = tuple(chosen)
    if combo in combos_full:
        filters_used = _filters_from_tuple(chosen)
        diag["used"] = filters_used
        diag["backoff_level"] = "exact"
        return True, filters_used, diag

    # 2) back off by dropping deepest dimensions until match
    for depth in range(len(dims) - 1, -1, -1):
        prefix = tuple(chosen[: depth + 1])
        if depth < len(combos_prefix) and prefix in combos_prefix[depth]:
            filters_used = _filters_from_tuple(list(prefix) + [None] * (len(dims) - depth - 1))
            diag["used"] = filters_used
            diag["backoff_level"] = f"depth_{depth+1}"
            diag["reason"] = "backoff_drop_tail"
            return True, filters_used, diag

    diag["reason"] = "no_valid_combo"
    return False, {}, diag

