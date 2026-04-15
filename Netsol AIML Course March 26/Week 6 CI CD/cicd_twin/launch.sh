#!/bin/bash
# ============================================================
# CI/CD Digital Twin — macOS Launcher
# Double-click this file or run: bash launch.sh
# ============================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo ""
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║      CI/CD Pipeline Digital Twin            ║"
echo "  ║      Starting up...                         ║"
echo "  ╚══════════════════════════════════════════════╝"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "  ERROR: Python 3 not found."
    echo "  Install it from https://python.org/downloads"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

PYTHON=$(command -v python3)
echo "  Python: $($PYTHON --version)"
echo ""

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    $PYTHON -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import flask_socketio" 2>/dev/null; then
    echo "  Installing dependencies (first run only)..."
    pip install -r requirements.txt --quiet
    echo "  Dependencies installed."
fi

echo ""
echo "  Starting server on http://localhost:5050"
echo "  Your browser will open automatically."
echo "  Press Ctrl+C to stop."
echo ""

python app.py
