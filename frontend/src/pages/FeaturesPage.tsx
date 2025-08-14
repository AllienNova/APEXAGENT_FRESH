import React from 'react';
import Layout from '../components/layout/Layout';
import Features from '../components/home/Features';
import HybridAISection from '../components/home/HybridAISection';
import ToolIntegrationsSection from '../components/home/ToolIntegrationsSection';
import IDEIntegrationsSection from '../components/home/IDEIntegrationsSection';
import ComputerVisionSection from '../components/home/ComputerVisionSection';

const FeaturesPage = () => {
  return (
    <Layout>
      <div className="bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
              <span className="block">Aideon AI Lite Features</span>
            </h1>
            <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
              Explore the powerful capabilities of the world's first truly hybrid autonomous AI system.
            </p>
          </div>
        </div>
      </div>
      
      {/* Placeholder for Features components */}
      <div className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-gray-900">Hybrid AI Architecture</h2>
          <p className="mt-4 text-lg text-gray-500">
            Combining local processing power with cloud intelligence for optimal performance and privacy.
          </p>
        </div>
      </div>
      
      <div className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-gray-900">Tool Integrations</h2>
          <p className="mt-4 text-lg text-gray-500">
            Over 106 tool integrations across 15 domains for maximum productivity.
          </p>
        </div>
      </div>
      
      <div className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-gray-900">IDE Integrations</h2>
          <p className="mt-4 text-lg text-gray-500">
            Seamless integration with popular development environments.
          </p>
        </div>
      </div>
      
      <div className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-gray-900">Computer Vision</h2>
          <p className="mt-4 text-lg text-gray-500">
            Advanced computer vision capabilities for image analysis and recognition.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default FeaturesPage;
