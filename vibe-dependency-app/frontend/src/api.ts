import axios from 'axios';

// Define the base URL for API requests
// In production, API calls are made to the same domain
// In development, we use the local backend server
const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export default api; 