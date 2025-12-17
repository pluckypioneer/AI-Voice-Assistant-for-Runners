import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { Platform } from 'react-native';

// Create Axios instance
const apiClient: AxiosInstance = axios.create({
  // Use 10.0.2.2 for Android Emulator to access host machine's localhost
  baseURL: Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000',
  timeout: 10000, // Request timeout
});

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Can add auth token here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    // Handle errors globally
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;