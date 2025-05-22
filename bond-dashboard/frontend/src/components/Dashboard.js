import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// Import hooks and services
import useWebSocket from '../hooks/useWebSocket';
import apiService from '../services/apiService';

// Colors for charts
const COLORS = ['#3a9a47', '#5ab366', '#8dce95'];

// Dashboard component
const Dashboard = () => {
  const navigate = useNavigate();
  
  // State variables
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState(null);
  
  // Get real-time transactions from WebSocket
  const { isConnected, transactions, isLoading, error } = useWebSocket();
  
  // Fetch market statistics on component mount
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiService.getMarketStats();
        setStats(data);
        setStatsLoading(false);
      } catch (error) {
        console.error('Error fetching market statistics:', error);
        setStatsError('Failed to load market statistics');
        setStatsLoading(false);
      }
    };
    
    fetchStats();
    
    // Refresh stats every 60 seconds
    const interval = setInterval(fetchStats, 60000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Prepare data for bond source chart
  const prepareBondSourceData = () => {
    if (!stats) return [];
    
    return [
      { name: 'NSE', value: stats.bonds.by_source.NSE },
      { name: 'BSE', value: stats.bonds.by_source.BSE },
      { name: 'NSDL', value: stats.bonds.by_source.NSDL },
    ];
  };
  
  // Prepare data for transaction source chart
  const prepareTransactionSourceData = () => {
    if (!stats) return [];
    
    return [
      { name: 'NSE', value: stats.transactions.by_source.NSE },
      { name: 'BSE', value: stats.transactions.by_source.BSE },
      { name: 'NSDL', value: stats.transactions.by_source.NSDL },
    ];
  };
  
  // Navigation handler for clicking on a bond transaction
  const handleRowClick = (isin) => {
    navigate(`/bonds/${isin}`);
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-rv-gray-900">Bond Market Dashboard</h1>
        
        {/* Connection status */}
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-rv-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-rv-gray-600">
            {isConnected ? 'Live Updates Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}
      
      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {statsLoading ? (
          <>
            <div className="card animate-pulse">
              <div className="h-4 bg-rv-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-rv-gray-200 rounded w-3/4"></div>
            </div>
            <div className="card animate-pulse">
              <div className="h-4 bg-rv-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-rv-gray-200 rounded w-3/4"></div>
            </div>
            <div className="card animate-pulse">
              <div className="h-4 bg-rv-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-rv-gray-200 rounded w-3/4"></div>
            </div>
          </>
        ) : statsError ? (
          <div className="col-span-3">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {statsError}
            </div>
          </div>
        ) : (
          <>
            <div className="card">
              <h3 className="text-sm font-medium text-rv-gray-500 mb-2">Total Bonds</h3>
              <p className="text-3xl font-semibold text-rv-gray-900">
                {stats?.bonds.total || 0}
              </p>
            </div>
            <div className="card">
              <h3 className="text-sm font-medium text-rv-gray-500 mb-2">Total Transactions</h3>
              <p className="text-3xl font-semibold text-rv-gray-900">
                {Object.values(stats?.transactions.by_source || {}).reduce((a, b) => a + b, 0)}
              </p>
            </div>
            <div className="card">
              <h3 className="text-sm font-medium text-rv-gray-500 mb-2">Last Updated</h3>
              <p className="text-lg font-medium text-rv-gray-900">
                {stats?.latest_update ? format(new Date(stats.latest_update), 'PPpp') : 'Never'}
              </p>
            </div>
          </>
        )}
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-rv-gray-900 mb-4">Bonds by Source</h3>
          {statsLoading ? (
            <div className="h-[300px] bg-rv-gray-100 rounded-lg animate-pulse"></div>
          ) : (
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={prepareBondSourceData()}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {prepareBondSourceData().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [value, 'Bonds']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
        
        <div className="card">
          <h3 className="text-lg font-medium text-rv-gray-900 mb-4">Transactions by Source</h3>
          {statsLoading ? (
            <div className="h-[300px] bg-rv-gray-100 rounded-lg animate-pulse"></div>
          ) : (
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={prepareTransactionSourceData()}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip 
                    formatter={(value) => [value, 'Transactions']}
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '0.5rem',
                      boxShadow: '0 2px 15px -3px rgba(0, 0, 0, 0.07)',
                    }}
                  />
                  <Legend />
                  <Bar dataKey="value" name="Transactions" fill="#3a9a47" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
      
      {/* Real-time transaction feed */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-rv-gray-900">Live Transaction Feed</h3>
          {isConnected && (
            <span className="badge badge-success">Real-time</span>
          )}
        </div>
        
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-rv-gray-100 rounded-lg animate-pulse"></div>
            ))}
          </div>
        ) : transactions.length === 0 ? (
          <div className="bg-rv-gray-50 border border-rv-gray-200 text-rv-gray-700 px-4 py-3 rounded-lg">
            No transactions available
          </div>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead className="table-header">
                <tr>
                  <th className="table-header-cell">ISIN</th>
                  <th className="table-header-cell">Name</th>
                  <th className="table-header-cell">Date/Time</th>
                  <th className="table-header-cell text-right">Price</th>
                  <th className="table-header-cell text-right">Yield</th>
                  <th className="table-header-cell text-right">Volume</th>
                  <th className="table-header-cell">Source</th>
                </tr>
              </thead>
              <tbody className="table-body">
                {transactions.slice(0, 10).map((transaction) => (
                  <tr 
                    key={transaction.id}
                    onClick={() => handleRowClick(transaction.isin)}
                    className="table-row cursor-pointer"
                  >
                    <td className="table-cell">{transaction.isin}</td>
                    <td className="table-cell">{transaction.name}</td>
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

export default Dashboard; 