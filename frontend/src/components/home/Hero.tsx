import { ArrowRight, Check, Cpu, Database, Globe, Lock, Zap } from 'lucide-react';

const Hero = () => {
  return (
    <div className="relative overflow-hidden">
      {/* Modern gradient background with animation */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-purple-700 to-blue-700 animate-gradient-slow"></div>
      
      {/* Background pattern */}
      <div className="hidden sm:block sm:absolute sm:inset-y-0 sm:h-full sm:w-full">
        <div className="relative h-full max-w-screen-xl mx-auto">
          <svg
            className="absolute right-full transform translate-y-1/4 translate-x-1/4 lg:translate-x-1/2 opacity-20"
            width="404"
            height="784"
            fill="none"
            viewBox="0 0 404 784"
          >
            <defs>
              <pattern
                id="f210dbf6-a58d-4871-961e-36d5016a0f49"
                x="0"
                y="0"
                width="20"
                height="20"
                patternUnits="userSpaceOnUse"
              >
                <rect x="0" y="0" width="4" height="4" className="text-white" fill="currentColor" opacity="0.3" />
              </pattern>
            </defs>
            <rect width="404" height="784" fill="url(#f210dbf6-a58d-4871-961e-36d5016a0f49)" />
          </svg>
          <svg
            className="absolute left-full transform -translate-y-3/4 -translate-x-1/4 md:-translate-y-1/2 lg:-translate-x-1/2 opacity-20"
            width="404"
            height="784"
            fill="none"
            viewBox="0 0 404 784"
          >
            <defs>
              <pattern
                id="5d0dd344-b041-4d26-bec4-8d33ea57ec9b"
                x="0"
                y="0"
                width="20"
                height="20"
                patternUnits="userSpaceOnUse"
              >
                <rect x="0" y="0" width="4" height="4" className="text-white" fill="currentColor" opacity="0.3" />
              </pattern>
            </defs>
            <rect width="404" height="784" fill="url(#5d0dd344-b041-4d26-bec4-8d33ea57ec9b)" />
          </svg>
        </div>
      </div>

      <div className="relative pt-10 pb-16 sm:pb-24">
        <main className="mt-16 mx-auto max-w-7xl px-4 sm:mt-24 sm:px-6 lg:mt-32">
          <div className="lg:grid lg:grid-cols-12 lg:gap-8">
            <div className="sm:text-center md:max-w-2xl md:mx-auto lg:col-span-6 lg:text-left">
              <h1>
                <span className="block text-sm font-semibold uppercase tracking-wide text-gray-200 sm:text-base lg:text-sm xl:text-base">
                  Introducing
                </span>
                <span className="mt-1 block text-4xl tracking-tight font-extrabold sm:text-5xl xl:text-6xl">
                  <span className="block text-white">Aideon AI Lite</span>
                  <span className="block text-indigo-200">Intelligence Everywhere, Limits Nowhere</span>
                </span>
              </h1>
              <p className="mt-3 text-base text-gray-200 sm:mt-5 sm:text-xl lg:text-lg xl:text-xl">
                The world's first truly hybrid autonomous AI system that combines local PC processing with cloud intelligence. 
                Experience powerful AI capabilities with complete privacy and offline functionality.
              </p>
              
              {/* Feature badges */}
              <div className="mt-8 flex flex-wrap gap-3 justify-center lg:justify-start">
                <span className="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                  <Lock className="h-4 w-4 mr-1" />
                  Privacy-First
                </span>
                <span className="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                  <Cpu className="h-4 w-4 mr-1" />
                  Hybrid Processing
                </span>
                <span className="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  <Globe className="h-4 w-4 mr-1" />
                  100+ Tools
                </span>
              </div>
              
              <div className="mt-8 sm:max-w-lg sm:mx-auto sm:text-center lg:text-left lg:mx-0">
                <div className="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
                  <div className="rounded-md shadow">
                    <a
                      href="#/download"
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10 transition-all duration-200 transform hover:scale-105"
                    >
                      Download Now
                    </a>
                  </div>
                  <div className="mt-3 sm:mt-0 sm:ml-3">
                    <a
                      href="#/features"
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-indigo-700 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10 transition-all duration-200"
                    >
                      Learn More
                    </a>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-12 relative sm:max-w-lg sm:mx-auto lg:mt-0 lg:max-w-none lg:mx-0 lg:col-span-6 lg:flex lg:items-center">
              <div className="relative mx-auto w-full rounded-lg shadow-lg lg:max-w-md">
                <div className="relative block w-full bg-white rounded-lg overflow-hidden transform transition-all duration-500 hover:scale-105 hover:shadow-2xl">
                  <img
                    className="w-full"
                    src="./assets/hero-image.png"
                    alt="Aideon AI Lite interface"
                    onError={(e) => {
                      e.currentTarget.src = 'https://via.placeholder.com/600x400/4F46E5/FFFFFF?text=Aideon+AI+Lite';
                    }}
                  />
                  <div className="absolute inset-0 w-full h-full flex items-center justify-center">
                    <button
                      type="button"
                      className="flex items-center justify-center bg-white rounded-full p-3 text-indigo-500 hover:text-indigo-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200 transform hover:scale-110"
                    >
                      <span className="sr-only">Watch demo</span>
                      <svg className="h-10 w-10" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
      
      {/* Social proof section */}
      <div className="relative bg-gray-50 py-8 sm:py-12 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-2xl font-semibold text-gray-900">
              Trusted by developers and professionals worldwide
            </h2>
          </div>
          <div className="mt-10">
            <div className="flex flex-wrap justify-center gap-8 md:gap-16 grayscale opacity-60">
              <div className="flex justify-center">
                <img className="h-8" src="https://via.placeholder.com/160x40/4F46E5/FFFFFF?text=Company+1" alt="Company 1" />
              </div>
              <div className="flex justify-center">
                <img className="h-8" src="https://via.placeholder.com/160x40/4F46E5/FFFFFF?text=Company+2" alt="Company 2" />
              </div>
              <div className="flex justify-center">
                <img className="h-8" src="https://via.placeholder.com/160x40/4F46E5/FFFFFF?text=Company+3" alt="Company 3" />
              </div>
              <div className="flex justify-center">
                <img className="h-8" src="https://via.placeholder.com/160x40/4F46E5/FFFFFF?text=Company+4" alt="Company 4" />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Key features section */}
      <div className="relative bg-white py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Key Features
            </h2>
            <p className="mt-4 text-lg text-gray-500">
              Aideon AI Lite combines the best of local processing and cloud intelligence
            </p>
          </div>
          <div className="mt-12 grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-100 transition-all duration-300 hover:shadow-xl hover:border-indigo-100">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-md p-3">
                    <Lock className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">Complete Privacy</h3>
                  </div>
                </div>
                <div className="mt-4 text-base text-gray-500">
                  Process all data locally on your device with no cloud dependencies, ensuring your sensitive information never leaves your computer.
                </div>
              </div>
            </div>
            
            {/* Feature 2 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-100 transition-all duration-300 hover:shadow-xl hover:border-indigo-100">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-md p-3">
                    <Cpu className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">Hybrid Processing</h3>
                  </div>
                </div>
                <div className="mt-4 text-base text-gray-500">
                  Seamlessly switch between local and cloud processing based on your needs, optimizing for performance, privacy, and cost.
                </div>
              </div>
            </div>
            
            {/* Feature 3 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-100 transition-all duration-300 hover:shadow-xl hover:border-indigo-100">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-md p-3">
                    <Database className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">Bundled Models</h3>
                  </div>
                </div>
                <div className="mt-4 text-base text-gray-500">
                  Comes with pre-installed AI models for chat, embedding, speech, and vision tasks, ready to use offline with no additional downloads.
                </div>
              </div>
            </div>
            
            {/* Feature 4 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-100 transition-all duration-300 hover:shadow-xl hover:border-indigo-100">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-md p-3">
                    <Globe className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">100+ Tool Integrations</h3>
                  </div>
                </div>
                <div className="mt-4 text-base text-gray-500">
                  Integrate with over 100 tools across software development, data science, business, healthcare, legal, and more domains.
                </div>
              </div>
            </div>
            
            {/* Feature 5 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-100 transition-all duration-300 hover:shadow-xl hover:border-indigo-100">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-md p-3">
                    <Zap className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">IDE Integrations</h3>
                  </div>
                </div>
                <div className="mt-4 text-base text-gray-500">
                  Seamlessly integrate with popular development environments including VS Code, JetBrains IDEs, Eclipse, Sublime Text, and more.
                </div>
              </div>
            </div>
            
            {/* Feature 6 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-100 transition-all duration-300 hover:shadow-xl hover:border-indigo-100">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-md p-3">
                    <Check className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">Computer Vision</h3>
                  </div>
                </div>
                <div className="mt-4 text-base text-gray-500">
                  Powerful computer vision capabilities including image analysis, OCR, facial recognition, visual search, and camera integration.
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-10 text-center">
            <a
              href="#/features"
              className="inline-flex items-center text-indigo-600 hover:text-indigo-900 transition-colors duration-200"
            >
              Explore all features
              <ArrowRight className="ml-2 h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
