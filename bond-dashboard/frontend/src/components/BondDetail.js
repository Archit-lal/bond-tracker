import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
// import axios from 'axios';

// Import services
import apiService from '../services/apiService';
import websocketService from '../services/websocketService';

// BondDetail component
const BondDetail = () => {
  const { isin } = useParams();
  const navigate = useNavigate();
  
  // Redirect to bond list if no ISIN is provided
  useEffect(() => {
    if (!isin) {
      navigate('/bonds');
    }
  }, [isin, navigate]);

  // State variables
  const [bond, setBond] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('1M'); // 1D, 1W, 1M, 3M, 1Y
  
  // Fetch bond details and transactions on component mount
  useEffect(() => {
    const fetchData = async () => {
      if (!isin) return; // Don't fetch if no ISIN
      
      try {
        setLoading(true);
        setError(null);
        
        const [bondData, transactionsData] = await Promise.all([
          apiService.getBondByIsin(isin),
          apiService.getTransactionsByIsin(isin),
        ]);
        
        setBond(bondData);
        setTransactions(transactionsData);
      } catch (error) {
        console.error('Error fetching bond details:', error);
        setError(error.response?.data?.detail || 'Failed to load bond details');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [isin]);

  // Set up WebSocket subscriptions
  useEffect(() => {
    // Subscribe to bond updates
    const handleBondUpdate = (updatedBond) => {
      if (updatedBond.isin === isin) {
        setBond(prevBond => ({
          ...prevBond,
          ...updatedBond,
        }));
      }
    };

    // Subscribe to new transactions
    const handleNewTransaction = (transaction) => {
      if (transaction.bond_id === bond?.id) {
        setTransactions(prevTransactions => [transaction, ...prevTransactions]);
      }
    };

    // Subscribe to WebSocket events
    websocketService.subscribe('bond_update', handleBondUpdate);
    websocketService.subscribe('new_transaction', handleNewTransaction);

    // Cleanup subscriptions on unmount
    return () => {
      websocketService.unsubscribe('bond_update', handleBondUpdate);
      websocketService.unsubscribe('new_transaction', handleNewTransaction);
    };
  }, [isin, bond?.id]);
  
  // Prepare price history data for chart
  const preparePriceHistoryData = () => {
    if (!transactions.length) return [];
    
    // Sort transactions by date
    const sortedTransactions = [...transactions].sort((a, b) => 
      new Date(a.trade_date) - new Date(b.trade_date)
    );
    
    // Filter based on selected time range
    const now = new Date();
    const filteredTransactions = sortedTransactions.filter(t => {
      const date = new Date(t.trade_date);
      const diff = now - date;
      
      switch (timeRange) {
        case '1D':
          return diff <= 24 * 60 * 60 * 1000;
        case '1W':
          return diff <= 7 * 24 * 60 * 60 * 1000;
        case '1M':
          return diff <= 30 * 24 * 60 * 60 * 1000;
        case '3M':
          return diff <= 90 * 24 * 60 * 60 * 1000;
        case '1Y':
          return diff <= 365 * 24 * 60 * 60 * 1000;
        default:
          return true;
      }
    });
    
    return filteredTransactions.map(t => ({
      date: format(new Date(t.trade_date), 'MMM d'),
      price: t.price,
      yield: t.yield_value,
    }));
  };
  
  // Calculate statistics
  const calculateStats = () => {
    if (!transactions.length) return null;
    
    const prices = transactions.map(t => t.price).filter(Boolean);
    const yields = transactions.map(t => t.yield_value).filter(Boolean);
    
    return {
      avgPrice: prices.reduce((a, b) => a + b, 0) / prices.length,
      minPrice: Math.min(...prices),
      maxPrice: Math.max(...prices),
      avgYield: yields.reduce((a, b) => a + b, 0) / yields.length,
      minYield: Math.min(...yields),
      maxYield: Math.max(...yields),
      totalVolume: transactions.reduce((sum, t) => sum + (t.volume || 0), 0),
    };
  };
  
  const stats = calculateStats();
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }

  if (!bond) {
    return (
      <div className="text-center py-10">
        <p className="text-gray-500">No bond data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Bond Details</h1>
        <button
          onClick={() => navigate('/bonds')}
          className="btn-secondary"
        >
          Back to List
        </button>
      </div>
      
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">{bond.name}</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">ISIN: {bond.isin}</p>
        </div>
        <div className="border-t border-gray-200">
          <dl>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Issuer</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{bond.issuer}</dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Exchange</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{bond.exchange}</dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Face Value</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">₹{bond.face_value}</dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Coupon Rate</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{bond.coupon_rate}%</dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Maturity Date</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {new Date(bond.maturity_date).toLocaleDateString()}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Yield to Maturity</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{bond.yield_to_maturity}%</dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Last Price</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">₹{bond.last_price}</dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Volume</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{bond.volume.toLocaleString()}</dd>
            </div>
            {stats && (
              <>
                <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Average Price</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">₹{stats.avgPrice.toFixed(2)}</dd>
                </div>
                <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Average Yield</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{stats.avgYield.toFixed(2)}%</dd>
                </div>
                <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Total Volume</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{stats.totalVolume.toLocaleString()}</dd>
                </div>
              </>
            )}
          </dl>
        </div>
      </div>
      
      {/* Price history chart */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Price History</h3>
          <div className="flex space-x-2">
            {['1D', '1W', '1M', '3M', '1Y'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 rounded-lg text-sm font-medium ${
                  timeRange === range
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>
        
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={preparePriceHistoryData()}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#6b7280" />
              <YAxis yAxisId="left" stroke="#3a9a47" />
              <YAxis yAxisId="right" orientation="right" stroke="#5ab366" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem',
                  boxShadow: '0 2px 15px -3px rgba(0, 0, 0, 0.07)',
                }}
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="price"
                name="Price"
                stroke="#3a9a47"
                dot={false}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="yield"
                name="Yield"
                stroke="#5ab366"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Recent transactions */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Transactions</h3>
        
        {transactions.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 text-gray-700 px-4 py-3 rounded-lg">
            No transactions available
          </div>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead className="table-header">
                <tr>
                  <th className="table-header-cell">Date/Time</th>
                  <th className="table-header-cell text-right">Price</th>
                  <th className="table-header-cell text-right">Yield</th>
                  <th className="table-header-cell text-right">Volume</th>
                  <th className="table-header-cell">Source</th>
                </tr>
              </thead>
              <tbody className="table-body">
                {transactions.slice(0, 10).map((transaction) => (
                  <tr key={transaction.id} className="table-row">
                    <td className="table-cell">
                      {transaction.trade_date ? 
                        format(new Date(transaction.trade_date), 'PP') : 'N/A'}
                      {transaction.trade_time ? 
                        ' ' + format(new Date(`2000-01-01T${transaction.trade_time}`), 'p') : ''}
                    </td>
                    <td className="table-cell text-right">₹{transaction.price?.toFixed(2) || 'N/A'}</td>
                    <td className="table-cell text-right">{transaction.yield_value?.toFixed(2)}%</td>
                    <td className="table-cell text-right">{transaction.volume?.toLocaleString() || 'N/A'}</td>
                    <td className="table-cell">
                      <span className={`badge ${
                        transaction.source === 'NSE' ? 'badge-success' :
                        transaction.source === 'BSE' ? 'badge-info' : 'badge-secondary'
                      }`}>
                        {transaction.source}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default BondDetail; 