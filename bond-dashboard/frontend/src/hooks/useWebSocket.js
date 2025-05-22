import { useState, useEffect, useCallback } from 'react';
import websocketService from '../services/websocketService';

// Custom hook for using WebSocket in components
const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Handle initial data from WebSocket
  const handleInitialData = useCallback((data) => {
    setTransactions(data || []);
    setIsLoading(false);
  }, []);

  // Handle new transactions from WebSocket
  const handleNewTransactions = useCallback((data) => {
    setTransactions(prevTransactions => {
      // Combine new transactions with existing ones, avoiding duplicates
      const combinedTransactions = [...data, ...prevTransactions];
      
      // Sort by created_at in descending order
      combinedTransactions.sort((a, b) => {
        if (!a.created_at || !b.created_at) return 0;
        return new Date(b.created_at) - new Date(a.created_at);
      });
      
      // Limit to 100 transactions for performance
      return combinedTransactions.slice(0, 100);
    });
  }, []);

  // Handle WebSocket open event
  const handleOpen = useCallback(() => {
    setIsConnected(true);
    setError(null);
  }, []);

  // Handle WebSocket close event
  const handleClose = useCallback(() => {
    setIsConnected(false);
  }, []);

  // Handle WebSocket error event
  const handleError = useCallback((event) => {
    setError('WebSocket connection error');
    setIsConnected(false);
  }, []);

  // Set up WebSocket connection and event listeners
  useEffect(() => {
    // Add event listeners
    const removeInitialDataListener = websocketService.addEventListener('initialData', handleInitialData);
    const removeNewTransactionsListener = websocketService.addEventListener('newTransactions', handleNewTransactions);
    const removeOpenListener = websocketService.addEventListener('open', handleOpen);
    const removeCloseListener = websocketService.addEventListener('close', handleClose);
    const removeErrorListener = websocketService.addEventListener('error', handleError);

    // Connect to WebSocket server
    websocketService.connect();

    // Clean up on unmount
    return () => {
      removeInitialDataListener();
      removeNewTransactionsListener();
      removeOpenListener();
      removeCloseListener();
      removeErrorListener();
    };
  }, [handleInitialData, handleNewTransactions, handleOpen, handleClose, handleError]);

  return {
    isConnected,
    transactions,
    isLoading,
    error,
  };
};

export default useWebSocket; 