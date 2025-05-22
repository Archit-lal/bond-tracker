import { format, parseISO } from 'date-fns';

/**
 * Format a date string to a readable format
 * @param {string} dateString - The date string to format
 * @param {string} formatString - The format to use (default: 'PP')
 * @returns {string} The formatted date or 'N/A' if invalid
 */
export const formatDate = (dateString, formatString = 'PP') => {
  if (!dateString) return 'N/A';
  
  try {
    const date = typeof dateString === 'string' ? parseISO(dateString) : new Date(dateString);
    return format(date, formatString);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'N/A';
  }
};

/**
 * Format a time string to a readable format
 * @param {string} timeString - The time string to format (HH:MM:SS)
 * @param {string} formatString - The format to use (default: 'p')
 * @returns {string} The formatted time or 'N/A' if invalid
 */
export const formatTime = (timeString, formatString = 'p') => {
  if (!timeString) return 'N/A';
  
  try {
    // Create a dummy date with the time string
    const date = parseISO(`2000-01-01T${timeString}`);
    return format(date, formatString);
  } catch (error) {
    console.error('Error formatting time:', error);
    return 'N/A';
  }
};

/**
 * Format a currency value to Indian Rupees
 * @param {number} value - The value to format
 * @param {number} decimals - The number of decimal places (default: 2)
 * @returns {string} The formatted currency or 'N/A' if invalid
 */
export const formatCurrency = (value, decimals = 2) => {
  if (value === null || value === undefined) return 'N/A';
  
  try {
    return `₹${Number(value).toFixed(decimals)}`;
  } catch (error) {
    console.error('Error formatting currency:', error);
    return 'N/A';
  }
};

/**
 * Format a percentage value
 * @param {number} value - The value to format
 * @param {number} decimals - The number of decimal places (default: 2)
 * @returns {string} The formatted percentage or 'N/A' if invalid
 */
export const formatPercentage = (value, decimals = 2) => {
  if (value === null || value === undefined) return 'N/A';
  
  try {
    return `${Number(value).toFixed(decimals)}%`;
  } catch (error) {
    console.error('Error formatting percentage:', error);
    return 'N/A';
  }
};

/**
 * Format a number with thousand separators
 * @param {number} value - The value to format
 * @returns {string} The formatted number or 'N/A' if invalid
 */
export const formatNumber = (value) => {
  if (value === null || value === undefined) return 'N/A';
  
  try {
    return Number(value).toLocaleString();
  } catch (error) {
    console.error('Error formatting number:', error);
    return 'N/A';
  }
};

/**
 * Get color based on source
 * @param {string} source - The source (NSE, BSE, NSDL)
 * @returns {string} The color for the source
 */
export const getSourceColor = (source) => {
  switch (source) {
    case 'NSE':
      return 'primary';
    case 'BSE':
      return 'secondary';
    case 'NSDL':
      return 'default';
    default:
      return 'default';
  }
}; 