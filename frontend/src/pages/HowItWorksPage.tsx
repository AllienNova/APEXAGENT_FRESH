import React from 'react';
import { Cpu, Cloud, Zap, RefreshCw } from 'lucide-react';

const HowItWorksPage = () => {
  return (
    <div className="bg-white">
      {/* Hero section */}
      <div className="relative bg-gradient-to-r from-indigo-600 to-purple-600 py-16 sm:py-24">
        <div className="absolute inset-0 overflow-hidden">
          <svg
            className="absolute right-0 top-0 transform translate-x-1/3 -translate-y-1/4 lg:translate-x-1/2 xl:-translate-y-1/2 opacity-20"
            width="404"
            height="784"
            fill="none"
            viewBox="0 0 404 784"
          >
            <defs>
              <pattern
                id="pattern-1"
                x="0"
                y="0"
                width="20"
                height="20"
                patternUnits="userSpaceOnUse"
              >
                <rect x="0" y="0" width="4" height="4" className="text-white" fill="currentColor" opacity="0.3" />
              </pattern>
            </defs>
            <rect width="404" height="784" fill="url(#pattern-1)" />
          </svg>
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
              How Aideon AI Lite Works
            </h1>
            <p className="mt-6 max-w-3xl mx-auto text-xl text-indigo-100">
              Discover the revolutionary hybrid architecture that powers Aideon AI Lite, combining the best of local processing and cloud intelligence.
            </p>
          </div>
        </div>
      </div>

      {/* Architecture overview section */}
      <div className="py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Hybrid AI Architecture
            </h2>
            <p className="mt-4 max-w-3xl mx-auto text-xl text-gray-500">
              Aideon AI Lite features a revolutionary hybrid architecture that combines the best of local processing and cloud intelligence.
            </p>
          </div>

          <div className="mt-16 relative">
            <div className="absolute inset-0 flex items-center" aria-hidden="true">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center">
              <span className="bg-white px-3 text-lg font-medium text-gray-900">
                Core Components
              </span>
            </div>
          </div>

          <div className="mt-12 grid gap-8 grid-cols-1 md:grid-cols-2">
            {/* Local Processing */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                    <Cpu className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">Local Processing</h3>
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-base text-gray-500">
                    Run AI models directly on your device for maximum privacy and offline capabilities.
                  </p>
                  <ul className="mt-4 space-y-2">
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-gray-700">Bundled optimized models for common tasks</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-gray-700">Quantized versions of larger models</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-gray-700">Hardware acceleration support</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-gray-700">Complete data privacy</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Cloud Intelligence */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-purple-500 rounded-md p-3">
                    <Cloud className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">Cloud Intelligence</h3>
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-base text-gray-500">
                    Access more powerful models in the cloud when needed for complex tasks.
                  </p>
                  <ul className="mt-4 space-y-2">
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-gray-700">Access to state-of-the-art large language models</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-gray-700">API integration with leading AI providers</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-gray-700">Secure data transmission</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-gray-700">Optional user-provided API keys</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Smart switching section */}
      <div className="bg-gray-50 py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
            <div>
              <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                Smart Switching Technology
              </h2>
              <p className="mt-3 max-w-3xl text-lg text-gray-500">
                Aideon AI Lite intelligently determines the optimal processing location based on task requirements, available resources, and user preferences.
              </p>
              <div className="mt-8">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-green-500 rounded-md p-1">
                    <RefreshCw className="h-5 w-5 text-white" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">Automatic Task Analysis</h3>
                    <p className="mt-2 text-base text-gray-500">
                      Analyzes each task to determine complexity, privacy requirements, and resource needs.
                    </p>
                  </div>
                </div>
                <div className="mt-6 flex items-center">
                  <div className="flex-shrink-0 bg-green-500 rounded-md p-1">
                    <Zap className="h-5 w-5 text-white" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">Dynamic Resource Allocation</h3>
                    <p className="mt-2 text-base text-gray-500">
                      Monitors available system resources and network conditions to optimize performance.
                    </p>
                  </div>
                </div>
                <div className="mt-6 flex items-center">
                  <div className="flex-shrink-0 bg-green-500 rounded-md p-1">
                    <Cpu className="h-5 w-5 text-white" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">User Preference Respect</h3>
                    <p className="mt-2 text-base text-gray-500">
                      Honors user-defined preferences for privacy, performance, and cost optimization.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-10 lg:mt-0">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <img 
                    src="./assets/smart-switching-diagram.png" 
                    alt="Smart switching technology diagram"
                    className="w-full rounded-lg"
                    onError={(e) => {
                      e.currentTarget.src = 'https://via.placeholder.com/600x400/4F46E5/FFFFFF?text=Smart+Switching+Diagram';
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Technical workflow section */}
      <div className="py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Technical Workflow
            </h2>
            <p className="mt-4 max-w-3xl mx-auto text-xl text-gray-500">
              How Aideon AI Lite processes your requests from start to finish
            </p>
          </div>

          <div className="mt-16">
            <div className="relative">
              {/* Vertical line */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="h-full w-0.5 bg-gray-200"></div>
              </div>

              {/* Steps */}
              <div className="relative space-y-16">
                {/* Step 1 */}
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-indigo-600 h-12 w-12 rounded-full flex items-center justify-center z-10">
                    <span className="text-white font-bold">1</span>
                  </div>
                  <div className="ml-6 bg-white p-6 rounded-lg shadow-md border border-gray-100 w-full">
                    <h3 className="text-lg font-medium text-gray-900">User Input Processing</h3>
                    <p className="mt-2 text-base text-gray-500">
                      When you enter a request, Aideon AI Lite's natural language understanding system analyzes your input to determine intent, requirements, and context.
                    </p>
                  </div>
                </div>

                {/* Step 2 */}
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-indigo-600 h-12 w-12 rounded-full flex items-center justify-center z-10">
                    <span className="text-white font-bold">2</span>
                  </div>
                  <div className="ml-6 bg-white p-6 rounded-lg shadow-md border border-gray-100 w-full">
                    <h3 className="text-lg font-medium text-gray-900">Task Planning</h3>
                    <p className="mt-2 text-base text-gray-500">
                      The Planner Agent breaks down complex requests into manageable subtasks and determines the optimal execution strategy, including which models and tools to use.
                    </p>
                  </div>
                </div>

                {/* Step 3 */}
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-indigo-600 h-12 w-12 rounded-full flex items-center justify-center z-10">
                    <span className="text-white font-bold">3</span>
                  </div>
                  <div className="ml-6 bg-white p-6 rounded-lg shadow-md border border-gray-100 w-full">
                    <h3 className="text-lg font-medium text-gray-900">Processing Location Decision</h3>
                    <p className="mt-2 text-base text-gray-500">
                      For each subtask, the system determines whether to process locally or in the cloud based on task complexity, privacy requirements, available resources, and user preferences.
                    </p>
                  </div>
                </div>

                {/* Step 4 */}
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-indigo-600 h-12 w-12 rounded-full flex items-center justify-center z-10">
                    <span className="text-white font-bold">4</span>
                  </div>
                  <div className="ml-6 bg-white p-6 rounded-lg shadow-md border border-gray-100 w-full">
                    <h3 className="text-lg font-medium text-gray-900">Execution</h3>
                    <p className="mt-2 text-base text-gray-500">
                      The Execution Agent carries out each subtask using the appropriate models and tools, either locally or in the cloud, while the Verification Agent ensures accuracy and quality.
                    </p>
                  </div>
                </div>

                {/* Step 5 */}
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-indigo-600 h-12 w-12 rounded-full flex items-center justify-center z-10">
                    <span className="text-white font-bold">5</span>
                  </div>
                  <div className="ml-6 bg-white p-6 rounded-lg shadow-md border border-gray-100 w-full">
                    <h3 className="text-lg font-medium text-gray-900">Result Integration</h3>
                    <p className="mt-2 text-base text-gray-500">
                      Results from all subtasks are combined and refined to create a comprehensive, coherent response to your original request.
                    </p>
                  </div>
                </div>

                {/* Step 6 */}
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-indigo-600 h-12 w-12 rounded-full flex items-center justify-center z-10">
                    <span className="text-white font-bold">6</span>
                  </div>
                  <div className="ml-6 bg-white p-6 rounded-lg shadow-md border border-gray-100 w-full">
                    <h3 className="text-lg font-medium text-gray-900">Continuous Learning</h3>
                    <p className="mt-2 text-base text-gray-500">
                      The system learns from each interaction to improve future responses while maintaining your privacy preferences. All personalized learning happens locally on your device.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA section */}
      <div className="bg-indigo-700">
        <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            <span className="block">Experience the power of hybrid AI</span>
            <span className="block">Start using Aideon AI Lite today</span>
          </h2>
          <p className="mt-4 text-lg leading-6 text-indigo-200">
            Break free from traditional AI limitations with our revolutionary hybrid system that seamlessly blends powerful local processing with advanced cloud intelligence.
          </p>
          <div className="mt-8 flex justify-center">
            <div className="inline-flex rounded-md shadow">
              <a
                href="#/download"
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50"
              >
                Get started
              </a>
            </div>
            <div className="ml-3 inline-flex">
              <a
                href="#/documentation"
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-800 hover:bg-indigo-900"
              >
                Learn more
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HowItWorksPage;
