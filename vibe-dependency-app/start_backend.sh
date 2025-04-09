#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting backend server in standalone mode...${NC}"

# Check for existing process on port 5000
if command -v lsof >/dev/null 2>&1; then
  PID_5000=$(lsof -ti:5000)
  if [ ! -z "$PID_5000" ]; then
    echo -e "${YELLOW}Port 5000 is already in use (PID: $PID_5000). Stopping it...${NC}"
    kill -9 $PID_5000 2>/dev/null
    sleep 1
  fi
fi

# Setup virtual environment if needed
if [ ! -d "backend/venv" ]; then
  echo -e "${YELLOW}Setting up virtual environment...${NC}"
  cd backend
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  cd ..
else
  cd backend
  source venv/bin/activate
fi

# Run the backend
echo -e "${GREEN}Starting backend on http://localhost:5000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"

# Set Google credentials if provided
if [ ! -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo -e "${GREEN}Using Google credentials from: $GOOGLE_APPLICATION_CREDENTIALS${NC}"
else
  echo -e "${YELLOW}No Google credentials set. Running in demo mode.${NC}"
fi

# Run the Flask app in foreground
python app.py 