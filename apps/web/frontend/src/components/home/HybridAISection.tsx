import React from 'react';

const HybridAISection = () => {
  return (
    <div className="py-16 bg-gray-50 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="lg:grid lg:grid-cols-2 lg:gap-8">
          <div>
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Hybrid AI Architecture
            </h2>
            <p className="mt-4 text-lg text-gray-500">
              Aideon AI Lite features a revolutionary hybrid architecture that combines the best of local processing and cloud intelligence.
            </p>
            <div className="mt-8 space-y-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p className="ml-3 text-base text-gray-500">
                  <strong className="font-medium text-gray-900">Local Processing:</strong> Run AI models directly on your device for maximum privacy and offline capabilities.
                </p>
              </div>
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p className="ml-3 text-base text-gray-500">
                  <strong className="font-medium text-gray-900">Cloud Intelligence:</strong> Access more powerful models in the cloud when needed for complex tasks.
                </p>
              </div>
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p className="ml-3 text-base text-gray-500">
                  <strong className="font-medium text-gray-900">Smart Switching:</strong> Automatically determine the optimal processing location based on task requirements.
                </p>
              </div>
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p className="ml-3 text-base text-gray-500">
                  <strong className="font-medium text-gray-900">Seamless Experience:</strong> Enjoy a consistent user experience regardless of processing location.
                </p>
              </div>
            </div>
          </div>
          <div className="mt-12 relative lg:mt-0">
            <div className="relative lg:max-w-none">
              <div className="aspect-w-16 aspect-h-9 rounded-xl shadow-xl overflow-hidden bg-gray-100">
                <div className="flex items-center justify-center h-full">
                  <svg className="h-24 w-24 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HybridAISection;
