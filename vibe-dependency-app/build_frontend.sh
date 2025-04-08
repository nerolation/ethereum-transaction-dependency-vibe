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

# Ensure homepage is set correctly in package.json
if ! grep -q '"homepage": "."' package.json; then
    echo "Setting homepage in package.json..."
    # Use a temporary file for the sed operation
    sed -i 's/"private": true,/"private": true,\n  "homepage": ".",/g' package.json
fi

# Build the frontend
echo "Building frontend..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "Error: Frontend build failed!"
    exit 1
fi

# Verify static directory structure
echo "Checking build output structure..."
if [ -d "build/static" ]; then
    echo "Static directory exists in build"
    echo "Static directory contents:"
    ls -la build/static
else
    echo "Warning: Static directory not found in build output"
    echo "Build directory contents:"
    ls -la build
fi

echo "Frontend build completed successfully!" 