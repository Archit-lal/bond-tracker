import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import apiService from '../services/apiService';

const BondList = () => {
  const navigate = useNavigate();
  
  // State variables
  const [bonds, setBonds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    source: 'all',
    minYield: '',
    maxYield: '',
  });
  
  // Fetch bonds on component mount
  useEffect(() => {
    const fetchBonds = async () => {
      try {
        const data = await apiService.getBonds();
        setBonds(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching bonds:', error);
        setError('Failed to load bonds');
        setLoading(false);
      }
    };
    
    fetchBonds();
  }, []);
  
  // Filter bonds based on search term and filters
  const filteredBonds = bonds.filter(bond => {
    const matchesSearch = 
      bond.isin.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bond.name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSource = 
      filters.source === 'all' || bond.exchange === filters.source;
    
    const matchesYield = 
      (!filters.minYield || bond.yield_to_maturity >= parseFloat(filters.minYield)) &&
      (!filters.maxYield || bond.yield_to_maturity <= parseFloat(filters.maxYield));
    
    return matchesSearch && matchesSource && matchesYield;
  });
  
  // Navigation handler for clicking on a bond
  const handleRowClick = (isin) => {
    if (!isin) {
      console.error('Invalid ISIN provided');
      return;
    }
    navigate(`/bonds/${isin}`);
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-rv-gray-900">Bond List</h1>
      </div>
      
      {/* Search and filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label htmlFor="search" className="block text-sm font-medium text-rv-gray-700 mb-1">
              Search Bonds
            </label>
            <input
              type="text"
              id="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by ISIN or name..."
              className="input-field"
            />
          </div>
          
          <div>
            <label htmlFor="source" className="block text-sm font-medium text-rv-gray-700 mb-1">
              Source
            </label>
            <select
              id="source"
              value={filters.source}
              onChange={(e) => setFilters({ ...filters, source: e.target.value })}
              className="input-field"
            >
              <option value="all">All Sources</option>
              <option value="NSE">NSE</option>
              <option value="BSE">BSE</option>
              <option value="NSDL">NSDL</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="yield" className="block text-sm font-medium text-rv-gray-700 mb-1">
              Yield Range (%)
            </label>
            <div className="flex space-x-2">
              <input
                type="number"
                value={filters.minYield}
                onChange={(e) => setFilters({ ...filters, minYield: e.target.value })}
                placeholder="Min"
                className="input-field"
              />
              <input
                type="number"
                value={filters.maxYield}
                onChange={(e) => setFilters({ ...filters, maxYield: e.target.value })}
                placeholder="Max"
                className="input-field"
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Bonds table */}
      <div className="card">
        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-rv-gray-100 rounded-lg animate-pulse"></div>
            ))}
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        ) : filteredBonds.length === 0 ? (
          <div className="bg-rv-gray-50 border border-rv-gray-200 text-rv-gray-700 px-4 py-3 rounded-lg">
            No bonds found matching your criteria
          </div>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead className="table-header">
                <tr>
                  <th className="table-header-cell">ISIN</th>
                  <th className="table-header-cell">Name</th>
                  <th className="table-header-cell">Maturity Date</th>
                  <th className="table-header-cell text-right">Coupon Rate</th>
                  <th className="table-header-cell text-right">Yield</th>
                  <th className="table-header-cell text-right">Price</th>
                  <th className="table-header-cell">Source</th>
                </tr>
              </thead>
              <tbody className="table-body">
                {filteredBonds.map((bond) => (
                  <tr 
                    key={bond.isin}
                    onClick={() => handleRowClick(bond.isin)}
                    className="table-row cursor-pointer"
                  >
                    <td className="table-cell">{bond.isin}</td>
                    <td className="table-cell">{bond.name}</td>
                    <td className="table-cell">
                      {bond.maturity_date ? 
                        format(new Date(bond.maturity_date), 'PP') : 'N/A'}
                    </td>
                    <td className="table-cell text-right">{bond.coupon_rate?.toFixed(2)}%</td>
                    <td className="table-cell text-right">{bond.yield_to_maturity?.toFixed(2)}%</td>
                    <td className="table-cell text-right">₹{bond.last_price?.toFixed(2) || 'N/A'}</td>
                    <td className="table-cell">
                      <span className={`badge ${
                        bond.exchange === 'NSE' ? 'badge-success' :
                        bond.exchange === 'BSE' ? 'badge-info' : 'badge-secondary'
                      }`}>
                        {bond.exchange}
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

export default BondList; 