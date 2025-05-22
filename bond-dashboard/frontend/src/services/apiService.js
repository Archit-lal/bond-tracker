import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service for HTTP requests
const apiService = {
  // Get all bonds with optional filtering
  getBonds: async (params = {}) => {
    try {
      const response = await api.get('/bonds/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching bonds:', error);
      throw error;
    }
  },

  // Get a specific bond by ISIN
  getBondByIsin: async (isin) => {
    try {
      const response = await api.get(`/bonds/${isin}/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching bond with ISIN ${isin}:`, error);
      throw error;
    }
  },

  // Get latest transactions with optional filtering
  getTransactions: async (params = {}) => {
    try {
      const response = await api.get('/transactions/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching transactions:', error);
      throw error;
    }
  },

  // Get transactions for a specific bond by ISIN
  getTransactionsByIsin: async (isin, params = {}) => {
    try {
      const response = await api.get(`/transactions/${isin}/`, { params });
      return response.data;
    } catch (error) {
      console.error(`Error fetching transactions for bond with ISIN ${isin}:`, error);
      throw error;
    }
  },

  // Get market statistics
  getMarketStats: async () => {
    try {
      const response = await api.get('/stats/');
      return response.data;
    } catch (error) {
      console.error('Error fetching market statistics:', error);
      throw error;
    }
  },
};

export default apiService; 