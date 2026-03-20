#!/bin/bash
# Run Decision Desk in development mode
# Starts FastAPI backend + Vite dev server concurrently

export PATH="$HOME/.cargo/bin:$PATH"
export PYTHONPATH="$(pwd)/backend"

# Kill on exit
trap 'kill 0' EXIT

echo "🚀 Starting Decision Desk..."
echo ""

# Backend
echo "Starting FastAPI backend on :8000..."
cd backend && python3 -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to come up
sleep 2

# Frontend
echo "Starting Vite frontend on :5173..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Backend  → http://localhost:8000"
echo "✓ Frontend → http://localhost:5173"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Open http://localhost:5173 in your browser"
echo "Press Ctrl+C to stop"
echo ""

wait
