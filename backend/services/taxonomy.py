"""
Render a YAML-like taxonomy string from a leaf index table.
Modeled after the supplier routing map generator.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd


def fmt_bucket(n: int) -> str:
    n = int(n)
    if n >= 1000:
        return f"{n // 1000}K+"
    if n >= 100:
        return f"{(n // 100) * 100}+"
    if n >= 10:
        return f"{(n // 10) * 10}+"
    return str(n)


def build_tree(leaf_index: pd.DataFrame, dims: List[str]) -> dict:
    df = leaf_index.copy()
    for col in dims:
        df[col] = df[col].fillna("blank")

    count_col = "count" if "count" in df.columns else "supplier_count"
    agg = df.groupby(dims)[count_col].sum().reset_index()

    root: Dict[str, dict] = {}
    for _, row in agg.iterrows():
        node = root
        for idx, dim in enumerate(dims):
            value = row[dim]
            child = node.setdefault(
                value,
                {"_count": 0, "children": {}},
            )
            child["_count"] += int(row[count_col])
            if idx == len(dims) - 1:
                continue
            node = child["children"]
    return root


def tree_to_yaml(tree: dict, dims: List[str]) -> str:
    lines: List[str] = []
    lines.append("# Schema (auto-generated routing map)")
    lines.append(f"# Levels: {', '.join(dims)}")
    lines.append("# Numbers in parentheses = unique row counts (bucketed).")
    lines.append("# Use only the listed dimensions as filters.")
    lines.append("")

    def walk(node: dict, depth: int, name: str) -> None:
        indent = "  " * depth
        count = fmt_bucket(node.get("_count", 0))
        lines.append(f"{indent}{name} ({count})" + (":" if node.get("children") else ""))
        for child_name, child_node in sorted(
            node.get("children", {}).items(), key=lambda kv: kv[1].get("_count", 0), reverse=True
        ):
            if child_name == "blank":
                continue
            walk(child_node, depth + 1, child_name)

    for name, node in sorted(tree.items(), key=lambda kv: kv[1].get("_count", 0), reverse=True):
        if name == "blank":
            continue
        walk(node, 0, name)

    return "\n".join(lines)


def build_taxonomy_yaml(leaf_index_path: str, dims: List[str]) -> str:
    df = pd.read_csv(leaf_index_path)
    tree = build_tree(df, dims)
    return tree_to_yaml(tree, dims)

