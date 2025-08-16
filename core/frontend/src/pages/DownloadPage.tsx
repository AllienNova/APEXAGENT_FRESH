import React from 'react';
import Layout from '../components/layout/Layout';

const DownloadPage = () => {
  return (
    <Layout>
      <div className="bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
              <span className="block">Download Aideon AI Lite</span>
            </h1>
            <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
              Get started with the world's first truly hybrid autonomous AI system today.
            </p>
          </div>
        </div>
      </div>
      
      {/* Placeholder for DownloadSection, FAQ, CTASection components */}
      <div className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-gray-900">Download Options</h2>
          <p className="mt-4 text-lg text-gray-500">
            Platform-specific installers and download links will be available here.
          </p>
        </div>
      </div>
      
      <div className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-gray-900">Frequently Asked Questions</h2>
          <p className="mt-4 text-lg text-gray-500">
            Answers to common questions about Aideon AI Lite.
          </p>
        </div>
      </div>

      <div className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-gray-900">Get Started Today</h2>
          <p className="mt-4 text-lg text-gray-500">
            Join the Aideon AI Lite community and revolutionize your workflow.
          </p>
        </div>
      </div>

    </Layout>
  );
};

export default DownloadPage;
