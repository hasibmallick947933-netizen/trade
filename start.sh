#!/usr/bin/env bash
set -e

echo "=== Starting FOREX AI Platform ==="

# 1. Activate Python virtual environment and run backend
echo "[1/2] Starting Python FastAPI Backend on http://localhost:8000..."
source .venv/bin/activate
export PYTHONPATH=.
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 2. Start Next.js Frontend
echo "[2/2] Starting Next.js Frontend on http://localhost:3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "=== FOREX AI is live! ==="
echo "Backend API:  http://localhost:8000"
echo "API Docs:     http://localhost:8000/docs"
echo "Frontend UI:  http://localhost:3000"

# Trap exit signals to gracefully stop both servers
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" EXIT INT TERM
wait
