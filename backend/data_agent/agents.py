from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents import Agent, Runner, RunContextWrapper, function_tool  # type: ignore[import]

from .agent_state import collect_rows_from_runs, ensure_state, record_tool_run
from .dataset_registry import DatasetMetadata, get_dataset
from .duckdb_query import run_query


def _load_text(path: Optional[str]) -> str:
    if not path:
        return ""
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def _load_taxonomy_yaml(meta: DatasetMetadata) -> str:
    if not meta.taxonomy_yaml_path:
        return ""
    return _load_text(meta.taxonomy_yaml_path)


def _build_system_prompt(meta: DatasetMetadata) -> str:
    yaml_str = _load_taxonomy_yaml(meta)
    dims = ", ".join(meta.dims)
    metrics = ", ".join(meta.metrics) or "none"
    header = (
        "You are a Data Exploration Agent.\n"
        f"The dataset_id is '{meta.dataset_id}'.\n"
        f"Filterable dimensions: {dims}.\n"
        f"Metrics: {metrics}.\n"
    )
    if yaml_str:
        header += "\nDATASET ROUTING MAP:\n```\n" + yaml_str + "\n```\n"
    return header


@function_tool(strict_mode=False)  # type: ignore[misc]
def DatasetQuery(
    ctx: RunContextWrapper[Any],
    dataset_id: str,
    filters: Dict[str, List[str]],
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    st = ensure_state(ctx)
    meta = get_dataset(dataset_id)

    filt_norm: Dict[str, List[str]] = {}
    for dim, vals in (filters or {}).items():
        if dim not in meta.dims:
            continue
        cleaned = []
        for v in vals:
            if v is None:
                continue
            s = str(v).strip().lower()
            if s:
                cleaned.append(s)
        if cleaned:
            filt_norm[dim] = cleaned

    diag: Dict[str, Any] = {"requested": filters, "used": filt_norm}
    if not filt_norm:
        diag["reason"] = "no_valid_filters"
        out = {
            "ok": False,
            "filters": filters,
            "canonical_filters": {},
            "rows": [],
            "row_count": 0,
            "diag": diag,
        }
        st["tools_run"].append({"name": "DatasetQuery", "ok": False, "notes": "no_valid_filters"})
        record_tool_run("DatasetQuery", {"filters": filters}, out, ok=False)
        return out

    rows, row_count = run_query(dataset_id, filt_norm, limit=limit, meta=meta)

    for r in rows:
        r.setdefault("source", "dataset")

    st["query_log"].append(f"DatasetQuery filters={json.dumps(filt_norm, ensure_ascii=False)}")
    st["results"].append(
        {
            "tool": "DatasetQuery",
            "dataset_id": dataset_id,
            "filters": filters,
            "canonical_filters": filt_norm,
            "rows": rows,
            "row_count": row_count,
            "diag": diag,
        }
    )
    st["diag"]["counts"]["rows_total"] = st["diag"]["counts"].get("rows_total", 0) + row_count
    st["tools_run"].append(
        {"name": "DatasetQuery", "ok": True, "notes": f"rows={row_count}, dims={list(filt_norm.keys())}"}
    )

    out = {
        "ok": True,
        "filters": filters,
        "canonical_filters": filt_norm,
        "rows": rows,
        "row_count": row_count,
        "diag": diag,
    }
    record_tool_run("DatasetQuery", {"filters": filters}, out, ok=True)
    return out


@function_tool(strict_mode=False)  # type: ignore[misc]
def SetSummary(
    ctx: RunContextWrapper[Any],
    answer: str,
    sources: Optional[List[str]] = None,
) -> Dict[str, Any]:
    st = ensure_state(ctx)
    st["summary_answer"] = (answer or "").strip()
    uniq_sources: List[str] = []
    for s in sources or []:
        if s not in uniq_sources:
            uniq_sources.append(s)
    st["summary_sources"] = uniq_sources[:8]
    st["tools_run"].append(
        {"name": "SetSummary", "ok": True, "notes": f"len(answer)={len(st['summary_answer'])}"}
    )
    record_tool_run(
        "SetSummary",
        {},
        {"answer": st["summary_answer"], "sources": st["summary_sources"]},
        ok=True,
    )
    return {"ok": True}


@function_tool(strict_mode=False)  # type: ignore[misc]
def ReturnState(ctx: RunContextWrapper[Any]) -> Dict[str, Any]:
    st = ensure_state(ctx)
    summary = {
        "answer": st.get("summary_answer", ""),
        "sources": st.get("summary_sources", []),
    }
    payload = {
        "tools_run": st.get("tools_run", []),
        "state": {
            "query_log": st.get("query_log", []),
            "results": st.get("results", []),
            "diag": st.get("diag", {}),
        },
    }
    return {"summary": summary, "payload": payload}


def build_agent(dataset_id: str) -> Agent:
    meta = get_dataset(dataset_id)
    system_prompt = _build_system_prompt(meta)
    dev_prompt = _load_text(meta.prompt_dev_path)
    instructions = system_prompt
    if dev_prompt:
        instructions += "\n" + dev_prompt
    return Agent(
        name=f"DatasetAgent_{dataset_id}",
        model="gpt-5.1",
        instructions=instructions,
        tools=[DatasetQuery, SetSummary, ReturnState],
    )


