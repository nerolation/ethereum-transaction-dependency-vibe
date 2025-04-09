#!/bin/bash

# Colors for console output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Change to the script's directory
cd "$(dirname "$0")"

# Check if GOOGLE_APPLICATION_CREDENTIALS is set
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo -e "${YELLOW}WARNING: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.${NC}"
  echo -e "${YELLOW}The application will run in demo mode with mock data.${NC}"
  echo -e "${YELLOW}To use real data, please set this variable to your credentials file path.${NC}"
  echo ""
else
  echo -e "${GREEN}GOOGLE_APPLICATION_CREDENTIALS is set to: $GOOGLE_APPLICATION_CREDENTIALS${NC}"
  # Check if the file exists
  if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "${RED}WARNING: The credentials file does not exist at the specified path.${NC}"
    echo -e "${YELLOW}The application will run in demo mode with mock data.${NC}"
  else
    echo -e "${GREEN}Credentials file found.${NC}"
  fi
  echo ""
fi

# Setup backend if needed
if [ ! -d "backend/venv" ]; then
  echo -e "${YELLOW}Setting up backend environment...${NC}"
  cd backend
  ./setup.sh
  cd ..
else
  echo -e "${GREEN}Ensuring backend dependencies are up to date...${NC}"
  cd backend
  source venv/bin/activate
  pip install -r requirements.txt
  cd ..
fi

# Start backend
echo -e "${GREEN}Starting backend...${NC}"
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Give the backend time to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 5

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
  echo -e "${YELLOW}Installing frontend dependencies...${NC}"
  cd frontend
  npm install
  cd ..
else
  echo -e "${GREEN}Frontend dependencies already installed.${NC}"
fi

# Check if backend is running
echo -e "${YELLOW}Checking if backend is running...${NC}"
python check_backend.py
if [ $? -ne 0 ]; then
  echo -e "${RED}There was an issue with the backend server. See above for details.${NC}"
  echo -e "${RED}Trying to continue with frontend startup anyway...${NC}"
fi

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo -e "\n${GREEN}Both servers are running!${NC}"
echo -e "- Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "- Backend: ${GREEN}http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers.${NC}"

# Handle cleanup when script is terminated
function cleanup {
  echo ""
  echo -e "${YELLOW}Stopping servers...${NC}"
  kill $BACKEND_PID
  kill $FRONTEND_PID
  echo -e "${GREEN}Servers stopped.${NC}"
  exit 0
}

trap cleanup SIGINT

# Keep script running
wait 