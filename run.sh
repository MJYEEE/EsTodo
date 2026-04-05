#!/bin/bash
# Run EsTodo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if conda environment exists
if conda info --envs | grep -q "^estodo"; then
    echo "Activating conda environment: estodo"
    eval "$(conda shell.bash hook)"
    conda activate estodo
else
    echo "Warning: conda environment 'estodo' not found. Using current environment."
fi

# Run the app
cd "$SCRIPT_DIR"
python -m estodo.main
