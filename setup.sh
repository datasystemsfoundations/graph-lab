#!/bin/bash
set -e

echo "=== Graph Data Storage Lab Setup ==="

python3 -m venv .venv
source .venv/bin/activate

pip install --quiet jupyter matplotlib numpy pyarrow graphviz

if ! command -v dot &> /dev/null; then
    if command -v brew &> /dev/null; then
        echo "Installing graphviz via Homebrew..."
        brew install graphviz
    else
        echo "WARNING: 'dot' (graphviz) not found. Install it manually:"
        echo "  macOS:  brew install graphviz"
        echo "  Ubuntu: sudo apt install graphviz"
    fi
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "To start the lab:"
echo "  source .venv/bin/activate"
echo "  jupyter notebook lab_graph.ipynb"
