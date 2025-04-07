#!/bin/bash

# Setup backend if needed
if [ ! -d "backend/venv" ]; then
  echo "Setting up backend environment..."
  cd backend
  ./setup.sh
  cd ..
else
  echo "Ensuring backend dependencies are up to date..."
  cd backend
  source venv/bin/activate
  pip install -r requirements.txt
  cd ..
fi

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
  echo "Installing frontend dependencies..."
  cd frontend
  npm install
  cd ..
else
  echo "Frontend dependencies already installed."
fi

# Start frontend
echo "Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "Both servers are running!"
echo "- Frontend: http://localhost:3000"
echo "- Backend: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers."

# Handle cleanup when script is terminated
function cleanup {
  echo ""
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  echo "Servers stopped."
  exit 0
}

trap cleanup SIGINT

# Keep script running
wait 