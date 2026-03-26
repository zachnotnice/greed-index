#!/bin/bash
# Greed Index — Local Development Startup Script

set -e

echo "🔴 Starting Greed Index..."

# Backend
echo "→ Starting backend..."
cd backend
if [ ! -d "venv" ]; then
  echo "  Creating Python venv..."
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt -q

if [ ! -f "greed_index.db" ]; then
  echo "  Seeding database..."
  python -m data.seed
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "  Backend running at http://localhost:8000"
echo "  API docs at http://localhost:8000/docs"

# Frontend
echo "→ Starting frontend..."
cd ../frontend
if [ ! -d "node_modules" ]; then
  echo "  Installing npm dependencies..."
  npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "  Frontend running at http://localhost:3000"

echo ""
echo "✓ Greed Index is running!"
echo "  Leaderboard:  http://localhost:3000"
echo "  API:          http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop."

wait $BACKEND_PID $FRONTEND_PID
