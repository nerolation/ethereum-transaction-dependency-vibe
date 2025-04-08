#!/bin/bash
set -e

echo "Starting frontend build process..."

# Navigate to the frontend directory
cd "$(dirname "$0")/frontend"

# Check if the frontend directory exists
if [ ! -d "$(pwd)" ]; then
    echo "Error: Frontend directory not found!"
    exit 1
fi

# Install dependencies
echo "Installing frontend dependencies..."
npm install --quiet

# Build the frontend
echo "Building frontend..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "Error: Frontend build failed!"
    exit 1
fi

echo "Frontend build completed successfully!" 