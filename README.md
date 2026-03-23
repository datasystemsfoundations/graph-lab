# Graph Data Storage: Forensic Exploration

Hands-on lab comparing five graph storage models — adjacency list (Neo4j), edge table in row storage (PostgreSQL), edge table in columnar (Parquet/Spark), CSR (igraph/cuGraph), and adjacency matrix. Benchmarks point traversals vs bulk analytics (PageRank) to show when each model wins, with special attention to why columnar storage excels at graph analytics at scale.

## Files

| File | Purpose |
|------|---------|
| `setup.sh` | Installs all dependencies (one-time) |
| `lab_graph.ipynb` | The lab notebook — run this |
| `graph_viz.py` | Graphviz visualizer for graphs, storage layouts, CSR, traversal comparisons |
| `.gitignore` | Keeps generated files out of the repo |

All generated artifacts (images, Parquet files, CSVs) are written to `_output/` at runtime.

## Setup

```bash
# 1. Install dependencies
bash setup.sh

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Open the lab
jupyter notebook lab_graph.ipynb
```

## Prerequisites

- Python 3.10+
- macOS or Linux
