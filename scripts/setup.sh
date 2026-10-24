#!/usr/bin/env bash
# Life Inbox - Unix/Linux/macOS Setup Script
# Usage: ./scripts/setup.sh

set -e

echo "========================================"
echo " Life Inbox - Local Development Setup   "
echo "========================================"

# 1. Create virtual environment (.venv) if one doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "\n[1/5] Creating Python virtual environment (.venv)..."
    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        PYTHON_CMD="python"
    fi
    $PYTHON_CMD -m venv .venv
    echo "Virtual environment created."
else
    echo -e "\n[1/5] Virtual environment (.venv) already exists."
fi

VENV_PYTHON=".venv/bin/python"

# 2. Install requirements.txt
echo -e "\n[2/5] Installing dependencies from requirements.txt..."
$VENV_PYTHON -m pip install --upgrade pip --quiet
$VENV_PYTHON -m pip install -r requirements.txt --quiet
echo "Dependencies successfully installed."

# 3. Copy .env.example to .env if .env doesn't exist
echo -e "\n[3/5] Checking environment configuration (.env)..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example."
else
    echo ".env already exists."
fi

# 4. Run database migrations (alembic upgrade head)
echo -e "\n[4/5] Running database migrations (alembic upgrade head)..."
$VENV_PYTHON -m alembic upgrade head
echo "Database migrations up to date."

# 5. Instructions
echo -e "\n[5/5] Setup Complete! 🎉"
echo "----------------------------------------"
echo "Next steps:"
echo "1. Configure your NVIDIA NIM API key:"
echo "   Open .env and set: NVIDIA_API_KEY=nvapi-your-key-here"
echo "   (If left blank, Life Inbox runs in offline mode with deterministic fallback)"
echo "2. Start the development server:"
echo "   ./.venv/bin/python -m uvicorn app.main:app --reload --port 8000"
echo "3. Open your browser:"
echo "   http://localhost:8000"
echo "========================================"
