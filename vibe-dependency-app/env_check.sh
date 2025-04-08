#!/bin/bash

# Colors for console output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}Environment Check for dependency.pics${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# Check if required commands are available
echo -e "${BLUE}Checking required tools:${NC}"
tools=("python" "pip" "node" "npm")
missing_tools=0

for tool in "${tools[@]}"
do
  if command -v $tool >/dev/null 2>&1; then
    version=$($tool --version 2>&1 | head -n 1)
    echo -e "  ${GREEN}✓${NC} $tool is installed ($version)"
  else
    echo -e "  ${RED}✗${NC} $tool is not installed"
    missing_tools=$((missing_tools+1))
  fi
done

if [ $missing_tools -gt 0 ]; then
  echo -e "\n${RED}Please install the missing tools before proceeding.${NC}"
  exit 1
fi

echo ""

# Check Python version
python_version=$(python --version 2>&1 | cut -d' ' -f2)
python_major=$(echo $python_version | cut -d'.' -f1)
python_minor=$(echo $python_version | cut -d'.' -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
  echo -e "${YELLOW}Warning: Python version $python_version detected.${NC}"
  echo -e "${YELLOW}It's recommended to use Python 3.8 or newer.${NC}"
else
  echo -e "${GREEN}Python version $python_version is compatible.${NC}"
fi

echo ""

# Check Node.js version
node_version=$(node --version 2>&1 | cut -d'v' -f2)
node_major=$(echo $node_version | cut -d'.' -f1)

if [ "$node_major" -lt 16 ]; then
  echo -e "${YELLOW}Warning: Node.js version $node_version detected.${NC}"
  echo -e "${YELLOW}It's recommended to use Node.js 16 or newer.${NC}"
else
  echo -e "${GREEN}Node.js version $node_version is compatible.${NC}"
fi

echo ""

# Check Google credentials
echo -e "${BLUE}Checking Google Cloud credentials:${NC}"
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo -e "  ${YELLOW}⚠${NC} GOOGLE_APPLICATION_CREDENTIALS environment variable is not set."
  echo -e "  ${YELLOW}⚠${NC} The application will run in demo mode with mock data."
  echo -e "  ${YELLOW}⚠${NC} To use real data, set this variable to your credentials file path:"
  echo -e "      export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json"
else
  echo -e "  ${GREEN}✓${NC} GOOGLE_APPLICATION_CREDENTIALS is set to: $GOOGLE_APPLICATION_CREDENTIALS"
  # Check if the file exists
  if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "  ${RED}✗${NC} The credentials file does not exist at the specified path."
    echo -e "  ${YELLOW}⚠${NC} The application will run in demo mode with mock data."
  else
    echo -e "  ${GREEN}✓${NC} Credentials file exists."
    # Check if the file is readable
    if [ -r "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
      echo -e "  ${GREEN}✓${NC} Credentials file is readable."
      # Check if it's a valid JSON file
      if jq -e . >/dev/null 2>&1 <<<"$(cat $GOOGLE_APPLICATION_CREDENTIALS)"; then
        echo -e "  ${GREEN}✓${NC} Credentials file contains valid JSON."
      else
        echo -e "  ${RED}✗${NC} Credentials file does not contain valid JSON."
        echo -e "  ${YELLOW}⚠${NC} The application may not be able to authenticate with Google Cloud."
      fi
    else
      echo -e "  ${RED}✗${NC} Credentials file is not readable."
      echo -e "  ${YELLOW}⚠${NC} The application may not be able to authenticate with Google Cloud."
    fi
  fi
fi

echo ""

# Check port availability
echo -e "${BLUE}Checking port availability:${NC}"
ports=(5000 3000)

for port in "${ports[@]}"
do
  if nc -z localhost $port >/dev/null 2>&1; then
    echo -e "  ${RED}✗${NC} Port $port is already in use."
    echo -e "  ${YELLOW}⚠${NC} This may cause conflicts when starting the application."
    # Try to find what's using the port
    if command -v lsof >/dev/null 2>&1; then
      process=$(lsof -i :$port -t)
      if [ -n "$process" ]; then
        process_name=$(ps -p $process -o comm=)
        echo -e "  ${YELLOW}⚠${NC} Port $port is being used by process: $process_name (PID: $process)"
      fi
    fi
  else
    echo -e "  ${GREEN}✓${NC} Port $port is available."
  fi
done

echo ""
echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}Environment check completed.${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""
echo -e "To start the application, run:"
echo -e "  ${GREEN}cd $(pwd)${NC}"
echo -e "  ${GREEN}./start.sh${NC}"
echo ""

# Final status
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ] || [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo -e "${YELLOW}The application will run in demo mode with mock data.${NC}"
  echo -e "${YELLOW}Set GOOGLE_APPLICATION_CREDENTIALS to use actual data from Google Cloud.${NC}"
else
  echo -e "${GREEN}The application is configured to use actual data from Google Cloud.${NC}"
fi 