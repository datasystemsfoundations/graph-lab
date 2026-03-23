"""
Graph Storage Visualizer — renders graph structures, storage layouts,
and traversal paths using graphviz.
"""

from __future__ import annotations
import subprocess
import shutil
import os
from typing import Optional


def _render_dot(dot_src: str, filename: str, output_dir: str, fmt: str = "png") -> str:
    dot_path = os.path.join(output_dir, f"{filename}.dot")
    img_path = os.path.join(output_dir, f"{filename}.{fmt}")
    with open(dot_path, "w") as f:
        f.write(dot_src)
    if shutil.which("dot"):
        subprocess.run(["dot", f"-T{fmt}", dot_path, "-o", img_path],
                       check=True, capture_output=True)
        return img_path
    return dot_path


def render_graph(
    edges: list[tuple[str, str, Optional[str]]],  # (src, dst, label)
    highlight_nodes: Optional[list[str]] = None,
    highlight_edges: Optional[list[tuple[str, str]]] = None,
    title: str = "Graph",
    filename: str = "graph",
    output_dir: str = ".",
    directed: bool = True,
) -> str:
    """Render a graph with optional highlighting."""
    gtype = "digraph" if directed else "graph"
    edge_op = "->" if directed else "--"
    highlight_nodes = highlight_nodes or []
    highlight_edges = highlight_edges or []

    dot = [f'{gtype} G {{']
    dot.append('    node [fontname="Courier", fontsize=11, style=filled, fillcolor=lightblue];')
    dot.append('    edge [fontname="Courier", fontsize=9];')
    dot.append(f'    labelloc="t"; label="{title}"; fontsize=13; fontname="Helvetica Bold";')

    # Collect all nodes
    nodes = set()
    for src, dst, _ in edges:
        nodes.add(src)
        nodes.add(dst)

    for n in nodes:
        color = "salmon" if n in highlight_nodes else "lightblue"
        dot.append(f'    "{n}" [fillcolor="{color}"];')

    for src, dst, label in edges:
        is_highlight = (src, dst) in highlight_edges or (dst, src) in highlight_edges
        color = "red" if is_highlight else "black"
        penwidth = "2.5" if is_highlight else "1.0"
        lbl = f' [label="  {label}", color={color}, penwidth={penwidth}]' if label else \
              f' [color={color}, penwidth={penwidth}]'
        dot.append(f'    "{src}" {edge_op} "{dst}"{lbl};')

    dot.append('}')
    return _render_dot("\n".join(dot), filename, output_dir)


def render_storage_layout(
    layout_name: str,
    sections: list[dict],  # [{title, rows: [[cell, cell, ...]], color}]
    title: str = "",
    filename: str = "layout",
    output_dir: str = ".",
) -> str:
    """Render a storage layout as a table-like diagram."""
    dot = ['digraph Layout {']
    dot.append('    rankdir=TB;')
    dot.append('    node [fontname="Courier", fontsize=10];')
    if title:
        dot.append(f'    labelloc="t"; label="{title}"; fontsize=13; fontname="Helvetica Bold";')

    for i, section in enumerate(sections):
        sec_id = f"sec_{i}"
        color = section.get("color", "lightyellow")

        # Build HTML-like table label
        rows_html = ""
        for row in section.get("rows", []):
            cells = "".join(f'<TD BGCOLOR="{color}">{cell}</TD>' for cell in row)
            rows_html += f"<TR>{cells}</TR>"

        header = section.get("title", "")
        if header:
            ncols = max(len(r) for r in section.get("rows", [[]])) if section.get("rows") else 1
            rows_html = f'<TR><TD COLSPAN="{ncols}" BGCOLOR="gray85"><B>{header}</B></TD></TR>' + rows_html

        dot.append(f'    {sec_id} [shape=none, label=<')
        dot.append(f'        <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">')
        dot.append(f'        {rows_html}')
        dot.append(f'        </TABLE>>];')

        if i > 0:
            dot.append(f'    sec_{i-1} -> {sec_id} [style=invis];')

    dot.append('}')
    return _render_dot("\n".join(dot), filename, output_dir)


def render_adjacency_list(
    adj: dict[str, list[str]],
    title: str = "Adjacency List",
    filename: str = "adj_list",
    output_dir: str = ".",
    highlight_node: Optional[str] = None,
) -> str:
    """Render an adjacency list storage layout."""
    dot = ['digraph AdjList {']
    dot.append('    rankdir=LR;')
    dot.append('    node [fontname="Courier", fontsize=10];')
    dot.append(f'    labelloc="t"; label="{title}"; fontsize=13; fontname="Helvetica Bold";')

    for node, neighbors in adj.items():
        color = "salmon" if node == highlight_node else "lightblue"
        # Node box
        dot.append(f'    "{node}" [shape=box, style=filled, fillcolor="{color}", '
                   f'label="{node}"];')
        # Neighbor chain
        if neighbors:
            chain = " → ".join(neighbors)
            chain_id = f"chain_{node}"
            dot.append(f'    {chain_id} [shape=record, style=filled, fillcolor=lightyellow, '
                       f'label="{chain}"];')
            dot.append(f'    "{node}" -> {chain_id} [label="  neighbors"];')
        else:
            dot.append(f'    empty_{node} [shape=plaintext, label="(none)"];')
            dot.append(f'    "{node}" -> empty_{node};')

    dot.append('}')
    return _render_dot("\n".join(dot), filename, output_dir)


def render_csr(
    nodes: list[str],
    offsets: list[int],
    edges: list[str],
    title: str = "CSR (Compressed Sparse Row)",
    filename: str = "csr",
    output_dir: str = ".",
    highlight_node_idx: Optional[int] = None,
) -> str:
    """Render CSR storage format."""
    dot = ['digraph CSR {']
    dot.append('    rankdir=TB;')
    dot.append('    node [fontname="Courier", fontsize=10];')
    dot.append(f'    labelloc="t"; label="{title}"; fontsize=13; fontname="Helvetica Bold";')

    # Offsets array
    offset_cells = "|".join([f"<o{i}> {v}" for i, v in enumerate(offsets)])
    dot.append(f'    offsets [shape=record, style=filled, fillcolor=lightyellow, '
               f'label="Offsets: |{offset_cells}"];')

    # Node labels
    node_cells = "|".join([f"<n{i}> {n}" for i, n in enumerate(nodes)])
    dot.append(f'    nodes [shape=record, style=filled, fillcolor=lightblue, '
               f'label="Nodes:   |{node_cells}"];')

    # Edges array
    edge_cells = "|".join([f"<e{i}> {e}" for i, e in enumerate(edges)])
    edge_color = "lightgreen"
    dot.append(f'    edges [shape=record, style=filled, fillcolor="{edge_color}", '
               f'label="Edges:   |{edge_cells}"];')

    dot.append('    nodes -> offsets [style=invis];')
    dot.append('    offsets -> edges [label="  offset[i]..offset[i+1] = neighbors of node i"];')

    # Highlight a specific node's neighbors
    if highlight_node_idx is not None and highlight_node_idx < len(nodes):
        start = offsets[highlight_node_idx]
        end = offsets[highlight_node_idx + 1] if highlight_node_idx + 1 < len(offsets) else len(edges)
        dot.append(f'    note [shape=plaintext, label="Node {nodes[highlight_node_idx]}: '
                   f'edges[{start}..{end}) = {edges[start:end]}"];')

    dot.append('}')
    return _render_dot("\n".join(dot), filename, output_dir)


def render_traversal_comparison(
    storage_models: list[dict],  # [{name, steps: [str], cost, color}]
    title: str = "Traversal Cost Comparison",
    filename: str = "traversal_cmp",
    output_dir: str = ".",
) -> str:
    """Render side-by-side traversal cost comparison."""
    dot = ['digraph TraversalCmp {']
    dot.append('    rankdir=TB;')
    dot.append('    node [fontname="Courier", fontsize=9];')
    dot.append(f'    labelloc="t"; label="{title}"; fontsize=13; fontname="Helvetica Bold";')

    for i, model in enumerate(storage_models):
        dot.append(f'    subgraph cluster_{i} {{')
        dot.append(f'        label="{model["name"]}\\n{model.get("cost", "")}";')
        dot.append(f'        style=rounded; color={model.get("color", "blue")}; fontsize=11;')

        for j, step in enumerate(model["steps"]):
            node_id = f"m{i}_s{j}"
            dot.append(f'        {node_id} [shape=box, style=filled, '
                       f'fillcolor="{model.get("color", "lightblue")}80", label="{step}"];')
            if j > 0:
                dot.append(f'        m{i}_s{j-1} -> {node_id};')

        dot.append('    }')

    dot.append('}')
    return _render_dot("\n".join(dot), filename, output_dir)
