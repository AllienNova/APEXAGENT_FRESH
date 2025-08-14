import React from 'react';
import Layout from '../components/layout/Layout';

const DocumentationPage = () => {
  return (
    <Layout>
      <div className="bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
              <span className="block">Documentation</span>
            </h1>
            <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
              Comprehensive guides and resources for Aideon AI Lite.
            </p>
          </div>
          
          <div className="mt-12 grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {/* Documentation Categories */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900">Getting Started</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Quick start guides and installation instructions for all platforms.
                </p>
                <div className="mt-4">
                  <a href="/documentation/getting-started" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                    View guides <span aria-hidden="true">&rarr;</span>
                  </a>
                </div>
              </div>
            </div>
            
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900">Tool Integrations</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Documentation for all 106+ tool integrations across 15 domains.
                </p>
                <div className="mt-4">
                  <a href="/documentation/tool-integrations" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                    View documentation <span aria-hidden="true">&rarr;</span>
                  </a>
                </div>
              </div>
            </div>
            
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900">IDE Integrations</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Setup and usage guides for VS Code, JetBrains, Eclipse, and more.
                </p>
                <div className="mt-4">
                  <a href="/documentation/ide-integrations" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                    View guides <span aria-hidden="true">&rarr;</span>
                  </a>
                </div>
              </div>
            </div>
            
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900">Model Management</h3>
                <p className="mt-2 text-sm text-gray-500">
                  How to manage, update, and customize AI models.
                </p>
                <div className="mt-4">
                  <a href="/documentation/model-management" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                    View documentation <span aria-hidden="true">&rarr;</span>
                  </a>
                </div>
              </div>
            </div>
            
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900">Computer Vision</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Guides for using the computer vision capabilities.
                </p>
                <div className="mt-4">
                  <a href="/documentation/computer-vision" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                    View guides <span aria-hidden="true">&rarr;</span>
                  </a>
                </div>
              </div>
            </div>
            
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900">API Reference</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Complete API documentation for developers.
                </p>
                <div className="mt-4">
                  <a href="/documentation/api" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                    View reference <span aria-hidden="true">&rarr;</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default DocumentationPage;
