import React from 'react';
import { Check, X } from 'lucide-react';

const ComparisonSection = () => {
  return (
    <div className="bg-white py-16 sm:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Why Choose Aideon AI Lite?
          </h2>
          <p className="mt-4 text-lg text-gray-500">
            See how Aideon AI Lite compares to other solutions in the market
          </p>
        </div>

        <div className="mt-12 overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 shadow-lg rounded-lg overflow-hidden">
            <thead className="bg-gradient-to-r from-indigo-600 to-purple-600">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                  Feature
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                  Aideon AI Lite
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                  Cloud-Only AI
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                  Traditional Software
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {/* Privacy */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Privacy
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center">
                    <Check className="h-5 w-5 text-green-500 mr-2" />
                    Process sensitive data locally
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center">
                    <X className="h-5 w-5 text-red-500 mr-2" />
                    Data sent to cloud
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Varies by application
                </td>
              </tr>

              {/* Offline Use */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Offline Use
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center">
                    <Check className="h-5 w-5 text-green-500 mr-2" />
                    Full functionality available offline
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center">
                    <X className="h-5 w-5 text-red-500 mr-2" />
                    Limited or no offline use
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Typically available offline
                </td>
              </tr>

              {/* Cost */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Cost
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Monthly subscription with credit-based usage system
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Ongoing subscription costs
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  One-time purchase
                </td>
              </tr>

              {/* Customization */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Customization
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center">
                    <Check className="h-5 w-5 text-green-500 mr-2" />
                    Extensive model and feature customization
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Limited to provided options
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Application-specific
                </td>
              </tr>

              {/* Performance */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Performance
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Adapts to your hardware
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Depends on internet speed
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Fixed based on application
                </td>
              </tr>

              {/* Integration */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Integration
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center">
                    <Check className="h-5 w-5 text-green-500 mr-2" />
                    Works with your existing tools
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Limited to platform ecosystem
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Application-specific
                </td>
              </tr>

              {/* Learning */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Learning
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Personalized without privacy compromise
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Learns across all users
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Minimal or no learning
                </td>
              </tr>

              {/* Stability */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Stability
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center">
                    <Check className="h-5 w-5 text-green-500 mr-2" />
                    No sandbox instability or work loss
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Varies by provider
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Generally stable
                </td>
              </tr>

              {/* Data Security */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Data Security
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center">
                    <Check className="h-5 w-5 text-green-500 mr-2" />
                    No third-party access to your data and code
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center">
                    <X className="h-5 w-5 text-red-500 mr-2" />
                    Data accessible to service providers
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Varies by application
                </td>
              </tr>

              {/* Memory */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Memory
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div className="flex items-center">
                    <Check className="h-5 w-5 text-green-500 mr-2" />
                    Long-term memory preservation
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Session-based memory
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  Limited or no memory
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ComparisonSection;
