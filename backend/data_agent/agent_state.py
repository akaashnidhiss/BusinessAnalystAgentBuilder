from __future__ import annotations

from typing import Any, Dict, List


def ensure_state(ctx: Any) -> Dict[str, Any]:
    if not hasattr(ctx, "state") or ctx.state is None:
        ctx.state = {}
    st = ctx.state
    st.setdefault("query_log", [])
    st.setdefault("results", [])
    st.setdefault("tools_run", [])
    st.setdefault("summary_answer", "")
    st.setdefault("summary_sources", [])
    diag = st.setdefault("diag", {})
    diag.setdefault("errors", [])
    diag.setdefault("timings", [])
    diag.setdefault("counts", {})
    return st


_TOOL_RUNS: List[Dict[str, Any]] = []


def reset_tool_runs() -> None:
    _TOOL_RUNS.clear()


def record_tool_run(
    tool: str,
    inputs: Dict[str, Any],
    output: Dict[str, Any],
    ok: bool = True,
) -> None:
    entry = {
        "tool": tool,
        "ok": bool(ok),
        "inputs": inputs,
        "output": output,
    }
    _TOOL_RUNS.append(entry)


def collect_rows_from_runs() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for entry in _TOOL_RUNS:
        out = entry.get("output") or {}
        rs = out.get("rows") or []
        for r in rs:
            if isinstance(r, dict):
                rows.append(r)
    return rows


def tool_run_notes() -> List[Dict[str, Any]]:
    notes: List[Dict[str, Any]] = []
    for entry in _TOOL_RUNS:
        out = entry.get("output") or {}
        note = {
            "name": entry.get("tool", "unknown"),
            "ok": bool(entry.get("ok", False)),
            "notes": str(out)[:200],
        }
        notes.append(note)
    return notes


