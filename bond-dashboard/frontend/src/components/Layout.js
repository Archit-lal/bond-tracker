import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-rv-gray-50">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-soft transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-200 ease-in-out`}>
        <div className="flex items-center justify-between h-16 px-4 border-b border-rv-gray-200">
          <h1 className="text-xl font-semibold text-rv-green-600">Bond Dashboard</h1>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-md text-rv-gray-500 hover:text-rv-gray-700 hover:bg-rv-gray-100"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <nav className="px-4 py-4">
          <ul className="space-y-2">
            <li>
              <Link
                to="/"
                className={`flex items-center px-4 py-2 rounded-lg ${
                  isActive('/') 
                    ? 'bg-rv-green-50 text-rv-green-700' 
                    : 'text-rv-gray-700 hover:bg-rv-gray-50'
                }`}
              >
                <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Dashboard
              </Link>
            </li>
            <li>
              <Link
                to="/bonds"
                className={`flex items-center px-4 py-2 rounded-lg ${
                  isActive('/bonds') 
                    ? 'bg-rv-green-50 text-rv-green-700' 
                    : 'text-rv-gray-700 hover:bg-rv-gray-50'
                }`}
              >
                <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Bond List
              </Link>
            </li>
          </ul>
        </nav>
      </aside>

      {/* Main content */}
      <div className={`${sidebarOpen ? 'ml-64' : 'ml-0'} transition-margin duration-200 ease-in-out`}>
        {/* Top bar */}
        <header className="h-16 bg-white shadow-soft">
          <div className="flex items-center justify-between h-full px-6">
            <button
              onClick={() => setSidebarOpen(true)}
              className={`p-2 rounded-md text-rv-gray-500 hover:text-rv-gray-700 hover:bg-rv-gray-100 ${sidebarOpen ? 'hidden' : 'block'}`}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-rv-gray-600">Welcome to Bond Dashboard</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout; 