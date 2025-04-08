#!/bin/bash

# Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Setup backend
echo "Setting up backend..."
cd backend
pip install -r requirements.txt
cd ..

echo "Build completed!" 