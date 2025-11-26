from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from agents import Runner  # type: ignore[import]

from .agent_state import collect_rows_from_runs, reset_tool_runs, tool_run_notes
from .agents import build_agent
from .dataset_registry import DatasetMetadata, dataset_dir, save_dataset
from .taxonomy_builder import build_taxonomy


def create_dataset(
    dataset_id: str,
    raw_file_path: str,
    dims: List[str],
    metrics: List[str],
    display_name: Optional[str] = None,
    prompt_system_path: Optional[str] = None,
    prompt_dev_path: Optional[str] = None,
) -> DatasetMetadata:
    ddir = dataset_dir(dataset_id)
    raw_dest = ddir / "raw.csv"
    Path(raw_file_path).replace(raw_dest)

    meta = DatasetMetadata(
        dataset_id=dataset_id,
        display_name=display_name or dataset_id,
        raw_path=str(raw_dest),
        dims=dims,
        metrics=metrics,
        prompt_system_path=prompt_system_path,
        prompt_dev_path=prompt_dev_path,
    )
    save_dataset(meta)
    meta = build_taxonomy(meta)
    return meta


def _rows_to_excel(path: Path, rows: List[Dict[str, Any]]) -> None:
    df = pd.DataFrame(rows)
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")


def run_dataset_agent(
    dataset_id: str,
    natural_query: str,
    email: Optional[str] = None,
    client_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    reset_tool_runs()
    agent = build_agent(dataset_id)

    user_msg = json.dumps(
        {
            "dataset_id": dataset_id,
            "natural_query": natural_query,
            "email": email,
            "client_id": client_id,
            "session_id": session_id,
        },
        ensure_ascii=False,
    )

    try:
        result = Runner.run(agent, user_msg)  # type: ignore[call-arg]
    except Exception as e:
        return {
            "ok": False,
            "summary": f"Agent failed: {e}",
            "files": [],
            "payload": {},
            "diag": {"errors": tool_run_notes(), "effective_query": natural_query},
        }

    txt = getattr(result, "final_output", str(result))
    try:
        parsed = json.loads(txt)
    except Exception:
        parsed = {"summary": {"answer": txt, "sources": []}, "payload": {}}

    summary_block = parsed.get("summary") or {}
    payload_block = parsed.get("payload") or {}

    rows = collect_rows_from_runs()
    ddir = dataset_dir(dataset_id)
    excel_path = ddir / "latest_results.xlsx"
    if rows:
        _rows_to_excel(excel_path, rows)
        files = [
            {
                "type": "excel",
                "path": str(excel_path),
                "schema": {},
            }
        ]
    else:
        files = []

    out = {
        "ok": True,
        "summary": summary_block.get("answer", "") or "Run completed.",
        "files": files,
        "payload": payload_block,
        "diag": {
            "errors": payload_block.get("state", {}).get("diag", {}).get("errors", []),
            "rowcount": len(rows),
            "effective_query": natural_query,
        },
    }
    return out


