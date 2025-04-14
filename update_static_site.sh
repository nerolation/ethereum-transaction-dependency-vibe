#!/bin/bash

# Exit on any error
set -e

echo "Starting static site update process"

# Get the root directory of the repository
REPO_DIR=$(pwd)
echo "Repository directory: $REPO_DIR"

# Run the static file generator
echo "Running static file generator..."
cd "$REPO_DIR/vibe-dependency-app/backend"
python static_generator.py

# Prepare the static content for GitHub Pages
echo "Preparing static content for GitHub Pages..."

# Create .nojekyll file to bypass Jekyll processing
touch "$REPO_DIR/static/.nojekyll"

# Copy frontend build files to the static directory if they exist
if [ -d "$REPO_DIR/vibe-dependency-app/frontend/build" ]; then
  echo "Copying frontend build files to static directory..."
  cp -r "$REPO_DIR/vibe-dependency-app/frontend/build"/* "$REPO_DIR/static/"
else
  echo "Frontend build not found. Building frontend..."
  cd "$REPO_DIR/vibe-dependency-app/frontend"
  npm install
  npm run build
  mkdir -p "$REPO_DIR/static"
  cp -r build/* "$REPO_DIR/static/"
fi

# Push to GitHub Pages repository
echo "Pushing to GitHub Pages repository..."
cd "$REPO_DIR/static"

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
  git init
  git remote add origin git@github.com:nerolation/dependency.pics-static.git
fi

# Add all files
git add -A

# Commit changes with timestamp
git commit -m "Update static site: $(date)"

# Push to the main branch
git push -u origin main -f

echo "Static site update completed" 