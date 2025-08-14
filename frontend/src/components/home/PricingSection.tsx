import React from 'react';
import { Check } from 'lucide-react';

const PricingSection = () => {
  return (
    <div className="bg-gray-50 py-16 sm:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Choose Your Plan
          </h2>
          <p className="mt-4 text-lg text-gray-500">
            Select the perfect plan for your needs with flexible pricing options
          </p>
        </div>

        <div className="mt-12 space-y-12 lg:space-y-0 lg:grid lg:grid-cols-4 lg:gap-x-6">
          {/* Basic Plan */}
          <div className="relative p-6 bg-white rounded-2xl shadow-lg border border-gray-100 flex flex-col">
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-gray-900">Basic</h3>
              <p className="mt-4 flex items-baseline">
                <span className="text-5xl font-extrabold tracking-tight text-gray-900">$59.99</span>
                <span className="ml-1 text-xl font-medium text-gray-500">/month</span>
              </p>
              <p className="mt-1 text-sm text-gray-500">API provided</p>
              <p className="mt-1 text-sm text-gray-500">$29.99/month with your own API keys</p>

              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900">What's included:</h4>
                <ul className="mt-4 space-y-3">
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">2,000 initial credits</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Up to 2 standard LLMs</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Document creation & editing</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Purchase additional credits as needed</span>
                  </li>
                </ul>
              </div>
            </div>
            <div className="mt-8">
              <a
                href="#/download"
                className="w-full bg-indigo-600 border border-transparent rounded-md py-3 px-5 flex items-center justify-center text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200"
              >
                Get started
              </a>
            </div>
          </div>

          {/* Pro Plan */}
          <div className="relative p-6 bg-white rounded-2xl shadow-lg border-2 border-indigo-500 flex flex-col">
            <div className="absolute -top-5 inset-x-0">
              <div className="inline-block px-4 py-1 rounded-full bg-indigo-600 text-white text-sm font-semibold tracking-wide uppercase">
                Popular
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-gray-900">Pro</h3>
              <p className="mt-4 flex items-baseline">
                <span className="text-5xl font-extrabold tracking-tight text-gray-900">$149.99</span>
                <span className="ml-1 text-xl font-medium text-gray-500">/month</span>
              </p>
              <p className="mt-1 text-sm text-gray-500">API provided</p>
              <p className="mt-1 text-sm text-gray-500">$99.99/month with your own API keys</p>

              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900">What's included:</h4>
                <ul className="mt-4 space-y-3">
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">5,000 initial credits</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">3 standard LLMs</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">2 advanced LLMs (High reasoning)</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Document creation & editing</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Purchase additional credits as needed</span>
                  </li>
                </ul>
              </div>
            </div>
            <div className="mt-8">
              <a
                href="#/download"
                className="w-full bg-indigo-600 border border-transparent rounded-md py-3 px-5 flex items-center justify-center text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200"
              >
                Get started
              </a>
            </div>
          </div>

          {/* Expert Plan */}
          <div className="relative p-6 bg-white rounded-2xl shadow-lg border border-gray-100 flex flex-col">
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-gray-900">Expert</h3>
              <p className="mt-4 flex items-baseline">
                <span className="text-5xl font-extrabold tracking-tight text-gray-900">$249.99</span>
                <span className="ml-1 text-xl font-medium text-gray-500">/month</span>
              </p>
              <p className="mt-1 text-sm text-gray-500">API provided</p>
              <p className="mt-1 text-sm text-gray-500">$149.99/month with your own API keys</p>

              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900">What's included:</h4>
                <ul className="mt-4 space-y-3">
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">15,000 initial credits</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">All standard LLMs</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">All advanced LLMs</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Priority support</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Advanced document workflows</span>
                  </li>
                </ul>
              </div>
            </div>
            <div className="mt-8">
              <a
                href="#/download"
                className="w-full bg-indigo-600 border border-transparent rounded-md py-3 px-5 flex items-center justify-center text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200"
              >
                Get started
              </a>
            </div>
          </div>

          {/* Enterprise Plan */}
          <div className="relative p-6 bg-white rounded-2xl shadow-lg border border-gray-100 flex flex-col">
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-gray-900">Enterprise</h3>
              <p className="mt-4 flex items-baseline">
                <span className="text-5xl font-extrabold tracking-tight text-gray-900">Custom</span>
              </p>
              <p className="mt-1 text-sm text-gray-500">Contact us for pricing</p>

              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900">What's included:</h4>
                <ul className="mt-4 space-y-3">
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Custom credit allocation</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">All LLMs and features</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Dedicated account manager</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Custom integrations</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="flex-shrink-0 h-5 w-5 text-green-500" />
                    <span className="ml-3 text-sm text-gray-700">Team or per-computer pricing</span>
                  </li>
                </ul>
              </div>
            </div>
            <div className="mt-8">
              <a
                href="#/contact"
                className="w-full bg-gray-800 border border-transparent rounded-md py-3 px-5 flex items-center justify-center text-base font-medium text-white hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200"
              >
                Contact sales
              </a>
            </div>
          </div>
        </div>

        <div className="mt-12 text-center">
          <p className="text-base text-gray-600">
            All plans include unlimited credit purchases based on consumption.
          </p>
          <p className="mt-2 text-sm text-gray-500">
            When using your own API keys, operations don't count against your credit allocation.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PricingSection;
