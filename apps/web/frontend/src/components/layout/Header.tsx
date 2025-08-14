import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">Aideon AI Lite</h1>
          </div>
          <nav className="hidden md:flex space-x-8">
            <a href="/" className="text-gray-700 hover:text-gray-900">Home</a>
            <a href="/features" className="text-gray-700 hover:text-gray-900">Features</a>
            <a href="/pricing" className="text-gray-700 hover:text-gray-900">Pricing</a>
            <a href="/download" className="text-gray-700 hover:text-gray-900">Download</a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;

