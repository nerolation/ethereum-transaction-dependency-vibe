import axios from 'axios';

// Define the base URL for API requests
// In production, API calls are made to the same domain
// In development, we use the local backend server
const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:5000/api';

console.log(`API requests will be sent to: ${API_URL}`);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000 // 10 seconds timeout
});

// Add response interceptor to handle errors gracefully
api.interceptors.response.use(
  response => response,
  error => {
    // Handle connection errors with more useful messages
    if (!error.response) {
      console.error('API Connection Error:', error.message);
      if (error.message.includes('Network Error')) {
        console.error(
          'Backend server may not be running. Please start the backend server at http://localhost:5000'
        );
      }
    }
    return Promise.reject(error);
  }
);

export default api; 