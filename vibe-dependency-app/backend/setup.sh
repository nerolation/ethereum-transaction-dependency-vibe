#!/bin/bash

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate the virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo "Backend setup complete!"
echo "Use 'source venv/bin/activate' to activate the virtual environment." 