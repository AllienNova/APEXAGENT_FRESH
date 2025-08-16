import React, { useState, useEffect } from 'react';
import { useCreditSystem, useCreditCalculator, useServiceRouter } from '../contexts/CreditContext';
import { AlertCircle, CheckCircle, Zap, DollarSign } from 'lucide-react';

interface OperationRequest {
  type: 'text' | 'image' | 'video';
  service?: string;
  tokens?: number;
  quality?: 'standard' | 'premium';
  prompt?: string;
}

interface OperationResult {
  success: boolean;
  creditsUsed: number;
  service: string;
  message: string;
}

const SmartOperationHandler: React.FC = () => {
  const { balance, consumeCredits, apiKeys } = useCreditSystem();
  const { calculateCost } = useCreditCalculator();
  const { selectOptimalService } = useServiceRouter();
  
  const [operationHistory, setOperationHistory] = useState<Array<{
    id: string;
    type: string;
    service: string;
    creditsUsed: number;
    timestamp: Date;
    success: boolean;
  }>>([]);

  const executeOperation = async (request: OperationRequest): Promise<OperationResult> => {
    // Select optimal service if not specified
    const service = request.service || selectOptimalService(request.type, 'balanced');
    
    // Calculate credit cost
    const creditCost = calculateCost(
      request.type,
      service,
      request.quality || 'standard',
      request.tokens || 1000
    );

    // Check if user has API key for this service
    const hasApiKey = apiKeys[service];
    
    // Attempt to consume credits (will be 0 if user has API key)
    const success = consumeCredits(creditCost, service);
    
    if (!success && !hasApiKey) {
      return {
        success: false,
        creditsUsed: 0,
        service,
        message: `Insufficient credits. Need ${creditCost} credits, but only ${balance} available.`
      };
    }

    // Log the operation
    const operation = {
      id: Date.now().toString(),
      type: request.type,
      service,
      creditsUsed: hasApiKey ? 0 : creditCost,
      timestamp: new Date(),
      success: true
    };
    
    setOperationHistory(prev => [operation, ...prev.slice(0, 9)]); // Keep last 10 operations

    return {
      success: true,
      creditsUsed: hasApiKey ? 0 : creditCost,
      service,
      message: hasApiKey 
        ? `Operation completed using your ${service} API key (0 credits used)`
        : `Operation completed using system ${service} API (${creditCost} credits used)`
    };
  };

  return {
    executeOperation,
    operationHistory
  };
};

// Component for displaying operation status
const OperationStatusDisplay: React.FC<{
  operation: OperationResult;
  onClose: () => void;
}> = ({ operation, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000); // Auto-close after 5 seconds
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg border max-w-sm z-50 ${
      operation.success 
        ? 'bg-green-50 border-green-200 text-green-800' 
        : 'bg-red-50 border-red-200 text-red-800'
    }`}>
      <div className="flex items-start">
        {operation.success ? (
          <CheckCircle className="h-5 w-5 mt-0.5 mr-3 flex-shrink-0" />
        ) : (
          <AlertCircle className="h-5 w-5 mt-0.5 mr-3 flex-shrink-0" />
        )}
        <div className="flex-1">
          <p className="text-sm font-medium">
            {operation.success ? 'Operation Successful' : 'Operation Failed'}
          </p>
          <p className="text-xs mt-1">{operation.message}</p>
          {operation.success && operation.creditsUsed > 0 && (
            <p className="text-xs mt-1 font-medium">
              Credits used: {operation.creditsUsed}
            </p>
          )}
        </div>
        <button
          onClick={onClose}
          className="ml-2 text-gray-400 hover:text-gray-600"
        >
          ×
        </button>
      </div>
    </div>
  );
};

// Main integration component
const CreditApiIntegration: React.FC = () => {
  const { balance, apiKeys } = useCreditSystem();
  const { calculateCost } = useCreditCalculator();
  const { executeOperation, operationHistory } = SmartOperationHandler();
  
  const [currentOperation, setCurrentOperation] = useState<OperationResult | null>(null);
  const [testOperation, setTestOperation] = useState<OperationRequest>({
    type: 'text',
    tokens: 1000,
    quality: 'standard'
  });

  const handleTestOperation = async () => {
    const result = await executeOperation(testOperation);
    setCurrentOperation(result);
  };

  const getServiceStatus = (service: string) => {
    const hasKey = apiKeys[service];
    const cost = calculateCost('text', service, 'standard', 1000);
    
    return {
      hasKey,
      cost,
      status: hasKey ? 'Your API Key' : 'System API Key'
    };
  };

  const services = ['openai', 'anthropic', 'google', 'midjourney', 'runway', 'stability'];

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Current Status */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Credit & API Integration Status</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center">
              <DollarSign className="h-6 w-6 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-900">Credit Balance</p>
                <p className="text-xl font-bold text-blue-900">{balance.toLocaleString()}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center">
              <CheckCircle className="h-6 w-6 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-900">Your API Keys</p>
                <p className="text-xl font-bold text-green-900">
                  {Object.values(apiKeys).filter(Boolean).length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center">
              <Zap className="h-6 w-6 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-purple-900">Operations Today</p>
                <p className="text-xl font-bold text-purple-900">{operationHistory.length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Service Status Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map(service => {
            const status = getServiceStatus(service);
            return (
              <div key={service} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900 capitalize">{service}</h3>
                  {status.hasKey ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-yellow-500" />
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-1">{status.status}</p>
                <p className="text-xs text-gray-500">
                  Cost: {status.cost} credits per 1K tokens
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Test Operation */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Operation</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Operation Type
            </label>
            <select
              value={testOperation.type}
              onChange={(e) => setTestOperation(prev => ({
                ...prev,
                type: e.target.value as 'text' | 'image' | 'video'
              }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="text">Text Generation</option>
              <option value="image">Image Generation</option>
              <option value="video">Video Generation</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quality
            </label>
            <select
              value={testOperation.quality}
              onChange={(e) => setTestOperation(prev => ({
                ...prev,
                quality: e.target.value as 'standard' | 'premium'
              }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="standard">Standard</option>
              <option value="premium">Premium</option>
            </select>
          </div>
        </div>

        {testOperation.type === 'text' && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tokens
            </label>
            <input
              type="number"
              value={testOperation.tokens}
              onChange={(e) => setTestOperation(prev => ({
                ...prev,
                tokens: parseInt(e.target.value) || 1000
              }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              min="100"
              max="10000"
              step="100"
            />
          </div>
        )}

        <button
          onClick={handleTestOperation}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          Execute Test Operation
        </button>
      </div>

      {/* Operation History */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Operations</h3>
        
        {operationHistory.length > 0 ? (
          <div className="space-y-3">
            {operationHistory.map(op => (
              <div key={op.id} className="flex items-center justify-between border rounded-lg p-3">
                <div className="flex items-center">
                  {op.success ? (
                    <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-500 mr-3" />
                  )}
                  <div>
                    <p className="font-medium text-gray-900 capitalize">
                      {op.type} via {op.service}
                    </p>
                    <p className="text-sm text-gray-500">
                      {op.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium text-gray-900">
                    {op.creditsUsed} credits
                  </p>
                  <p className="text-sm text-gray-500">
                    {op.creditsUsed === 0 ? 'Own API' : 'System API'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            No operations yet. Try executing a test operation above.
          </p>
        )}
      </div>

      {/* Operation Status Notification */}
      {currentOperation && (
        <OperationStatusDisplay
          operation={currentOperation}
          onClose={() => setCurrentOperation(null)}
        />
      )}
    </div>
  );
};

export default CreditApiIntegration;

