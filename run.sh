#!/bin/bash
set -e

# Ensure we are in the project root
cd "$(dirname "$0")"

# Check if .venv exists
if [ -d ".venv" ]; then
    PYTHON_EXEC=".venv/bin/python"
else
    PYTHON_EXEC="python3"
    echo "Warning: .venv not found, trying system python3"
fi

# Run the module
exec $PYTHON_EXEC -m main "$@"
