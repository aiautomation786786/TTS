#!/usr/bin/env bash
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
