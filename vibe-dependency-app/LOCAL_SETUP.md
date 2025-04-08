# Local Development Setup

This guide will help you set up and run the dependency.pics application on your local machine.

## Prerequisites

- Python 3.8 or newer
- Node.js 16 or newer
- npm
- (Optional) Google Cloud credentials for accessing real data

## Quick Start

1. Clone the repository:
   ```
   git clone https://github.com/nerolation/dependency.pics.git
   cd dependency.pics
   ```

2. Run the environment check script to verify your setup:
   ```
   ./vibe-dependency-app/env_check.sh
   ```

3. (Optional) Set up your Google Cloud credentials environment variable to use real data:
   ```
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
   ```

4. Start the application:
   ```
   cd vibe-dependency-app
   ./start.sh
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

## Troubleshooting

### Connection Issues

If you see errors like `ERR_CONNECTION_REFUSED` in the browser console, it means the frontend cannot connect to the backend. Here are some things to check:

1. Verify that the backend is running:
   ```
   ./check_backend.py
   ```

2. Check if another application is using port 5000:
   ```
   lsof -i :5000
   ```

3. Make sure your firewall isn't blocking the connections.

### Google Cloud Credentials Issues

If you're having trouble with Google Cloud credentials:

1. Make sure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set correctly:
   ```
   echo $GOOGLE_APPLICATION_CREDENTIALS
   ```

2. Verify that the credentials file exists and is readable:
   ```
   ls -l $GOOGLE_APPLICATION_CREDENTIALS
   ```

3. Check if the JSON in the credentials file is valid:
   ```
   jq . $GOOGLE_APPLICATION_CREDENTIALS
   ```

### Running in Demo Mode

If you don't have Google Cloud credentials, the application will run in demo mode with mock data. This is perfect for local development and testing.

## Manual Setup

If you prefer to set up the application manually:

### Backend Setup

1. Set up a Python virtual environment:
   ```
   cd vibe-dependency-app/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the backend:
   ```
   python app.py
   ```

### Frontend Setup

1. Install dependencies:
   ```
   cd vibe-dependency-app/frontend
   npm install
   ```

2. Start the frontend:
   ```
   npm start
   ```

## Project Structure

- `backend/`: Flask backend server
  - `app.py`: Main backend application
  - `requirements.txt`: Python dependencies

- `frontend/`: React frontend application
  - `src/`: Source code
    - `components/`: React components
    - `api.ts`: API configuration for backend communication

## Network Configuration

- Backend: http://localhost:5000
- Frontend: http://localhost:3000
- API endpoints: http://localhost:5000/api/*

If you need to change the ports or URLs, you can modify:
- Backend port: Edit `app.py` and change the port in the `app.run()` call
- Frontend API URL: Edit `src/api.ts` and update the `API_URL` constant 