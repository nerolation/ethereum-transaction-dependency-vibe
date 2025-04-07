# Ethereum Transaction Dependency Graph Viewer

This application allows users to visualize Ethereum transaction dependency graphs stored in Google Cloud Storage. It consists of a Flask backend for retrieving and processing graphs and a React frontend for visualization.

## Project Structure

```
vibe-dependency-app/
├── backend/                # Flask backend
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── setup.sh            # Backend setup script 
├── frontend/               # React frontend
│   ├── public/             # Static assets
│   ├── src/                # React components and styles
│   ├── package.json        # JavaScript dependencies
│   └── tsconfig.json       # TypeScript configuration
└── start.sh                # Script to start both servers
```

## Features

- View transaction dependency graphs for specific Ethereum blocks
- Search for graphs by block number
- Display the most recent 3 graphs available
- Show node and edge count statistics for each graph

## Setup and Running

### Quick Start

The easiest way to run the application is using the provided start script:

```
chmod +x start.sh
./start.sh
```

This script will:
1. Set up a Python virtual environment for the backend
2. Install all required Python dependencies
3. Install all required Node.js dependencies
4. Start both the backend and frontend servers

The application will be available at http://localhost:3000

### Manual Setup

#### Backend Setup

1. Make sure you have Python 3.8+ installed
2. Set up your Google Cloud credentials environment variable:
   ```
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
   ```
3. Create and set up the virtual environment:
   ```
   cd backend
   chmod +x setup.sh
   ./setup.sh
   ```
4. Run the Flask server:
   ```
   source venv/bin/activate
   python app.py
   ```
   The backend will run on http://localhost:5000

#### Frontend Setup

1. Make sure you have Node.js (14+) and npm installed
2. Install dependencies:
   ```
   cd frontend
   npm install
   ```
3. Run the development server:
   ```
   npm start
   ```
   The frontend will run on http://localhost:3000

## API Endpoints

- `GET /api/graph/<block_number>`: Get graph for a specific block number
- `GET /api/recent_graphs`: Get the 3 most recent graphs

## Technologies Used

- **Backend**: Flask, NetworkX, matplotlib, Google Cloud Storage, pygraphviz
- **Frontend**: React, TypeScript, Styled Components, Axios 