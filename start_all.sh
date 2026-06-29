#!/usr/bin/env bash
echo "=============================================================="
echo "[1/3] Checking for application updates from Git..."
echo "=============================================================="
git fetch origin >/dev/null 2>&1
if git status -uno | grep -q 'behind'; then
    echo "[i] Updates found! Downloading the latest version..."
    git pull origin main
    echo "[OK] Update applied successfully!"
else
    echo "[OK] Application is already up to date."
fi
echo ""
echo "=============================================================="
echo "Cleaning up previous application sessions..."
echo "=============================================================="
lsof -ti:8000,8001,5173 | xargs kill -9 2>/dev/null || true
echo "Cleanup complete."
echo ""
echo "Starting AI Platform..."

cd backend || exit
source venv/bin/activate
echo "Starting Backend API..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting Voice Cloning Engine..."
source venv_clone/bin/activate
uvicorn voice_clone_worker.app:app --host 127.0.0.1 --port 8001 &
WORKER_PID=$!
cd ..

echo "Starting Frontend UI..."
cd frontend || exit
npm run dev &
FRONTEND_PID=$!
cd ..

echo "All services started! Access the app at http://localhost:5173"
echo "Press CTRL+C to stop all services."

trap "kill $BACKEND_PID $WORKER_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait
