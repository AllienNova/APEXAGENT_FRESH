// src/components/dr-tardis/TroubleshootingInterface.tsx
import React, { useState } from 'react';
import { Play, Pause, RotateCcw, HelpCircle, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

interface DiagnosticStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'success' | 'warning' | 'error' | 'skipped';
  details?: string;
}

const TroubleshootingInterface: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  
  // Sample diagnostic steps
  const [diagnosticSteps, setDiagnosticSteps] = useState<DiagnosticStep[]>([
    {
      id: '1',
      name: 'System Environment Check',
      description: 'Verifying operating system, dependencies, and environment variables',
      status: 'pending'
    },
    {
      id: '2',
      name: 'Network Connectivity',
      description: 'Testing connection to required services and APIs',
      status: 'pending'
    },
    {
      id: '3',
      name: 'Authentication Status',
      description: 'Verifying authentication tokens and permissions',
      status: 'pending'
    },
    {
      id: '4',
      name: 'Plugin Compatibility',
      description: 'Checking for plugin conflicts and version compatibility',
      status: 'pending'
    },
    {
      id: '5',
      name: 'Resource Availability',
      description: 'Verifying available disk space, memory, and CPU resources',
      status: 'pending'
    },
    {
      id: '6',
      name: 'Configuration Validation',
      description: 'Validating configuration files and settings',
      status: 'pending'
    }
  ]);
  
  const startDiagnostic = () => {
    setIsRunning(true);
    runNextStep();
  };
  
  const pauseDiagnostic = () => {
    setIsRunning(false);
  };
  
  const resetDiagnostic = () => {
    setIsRunning(false);
    setCurrentStepIndex(0);
    setDiagnosticSteps(diagnosticSteps.map(step => ({
      ...step,
      status: 'pending',
      details: undefined
    })));
  };
  
  const runNextStep = () => {
    if (currentStepIndex < diagnosticSteps.length) {
      // Update current step to running
      const updatedSteps = [...diagnosticSteps];
      updatedSteps[currentStepIndex] = {
        ...updatedSteps[currentStepIndex],
        status: 'running'
      };
      setDiagnosticSteps(updatedSteps);
      
      // Simulate diagnostic process
      setTimeout(() => {
        // Generate random result for demo purposes
        const results = ['success', 'warning', 'error'];
        const randomResult = results[Math.floor(Math.random() * results.length)] as 'success' | 'warning' | 'error';
        
        let resultDetails = '';
        if (randomResult === 'success') {
          resultDetails = 'All checks passed successfully.';
        } else if (randomResult === 'warning') {
          resultDetails = 'Minor issues detected that may affect performance.';
        } else {
          resultDetails = 'Critical issues detected that need immediate attention.';
        }
        
        // Update step with result
        const finalUpdatedSteps = [...diagnosticSteps];
        finalUpdatedSteps[currentStepIndex] = {
          ...finalUpdatedSteps[currentStepIndex],
          status: randomResult,
          details: resultDetails
        };
        setDiagnosticSteps(finalUpdatedSteps);
        
        // Move to next step
        if (currentStepIndex < diagnosticSteps.length - 1 && isRunning) {
          setCurrentStepIndex(currentStepIndex + 1);
          runNextStep();
        } else {
          setIsRunning(false);
        }
      }, 1500);
    }
  };
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <div className="h-5 w-5 rounded-full border-2 border-muted-foreground"></div>;
      case 'running':
        return <div className="h-5 w-5 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>;
      case 'success':
        return <CheckCircle size={20} className="text-green-500" />;
      case 'warning':
        return <AlertTriangle size={20} className="text-amber-500" />;
      case 'error':
        return <XCircle size={20} className="text-red-500" />;
      case 'skipped':
        return <div className="h-5 w-5 rounded-full border-2 border-muted-foreground opacity-50"></div>;
      default:
        return <HelpCircle size={20} className="text-muted-foreground" />;
    }
  };
  
  return (
    <div className="troubleshooting-interface p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Dr. TARDIS</h1>
        <p className="text-muted-foreground">Troubleshooting and Diagnostic System</p>
      </header>
      
      <div className="bg-card border border-border rounded-lg overflow-hidden mb-6">
        <div className="p-4 border-b border-border bg-muted/50">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">System Diagnostic</h2>
            <div className="flex space-x-2">
              {!isRunning ? (
                <button 
                  onClick={startDiagnostic}
                  disabled={currentStepIndex === diagnosticSteps.length}
                  className="flex items-center space-x-1 px-3 py-1 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Play size={16} />
                  <span>{currentStepIndex === 0 ? 'Start' : 'Resume'}</span>
                </button>
              ) : (
                <button 
                  onClick={pauseDiagnostic}
                  className="flex items-center space-x-1 px-3 py-1 bg-amber-500 text-white rounded-md hover:bg-amber-600"
                >
                  <Pause size={16} />
                  <span>Pause</span>
                </button>
              )}
              <button 
                onClick={resetDiagnostic}
                className="flex items-center space-x-1 px-3 py-1 border border-border rounded-md hover:bg-accent"
              >
                <RotateCcw size={16} />
                <span>Reset</span>
              </button>
            </div>
          </div>
        </div>
        
        <div className="p-4">
          <div className="space-y-4">
            {diagnosticSteps.map((step, index) => (
              <div 
                key={step.id} 
                className={`p-4 rounded-md ${
                  step.status === 'running' ? 'bg-primary/10 border border-primary/30' :
                  step.status === 'success' ? 'bg-green-50 border border-green-200' :
                  step.status === 'warning' ? 'bg-amber-50 border border-amber-200' :
                  step.status === 'error' ? 'bg-red-50 border border-red-200' :
                  'bg-background border border-border'
                }`}
              >
                <div className="flex items-start">
                  <div className="flex-shrink-0 mt-1 mr-3">
                    {getStatusIcon(step.status)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium">{step.name}</h3>
                      <span className="text-xs px-2 py-1 rounded-full bg-muted">
                        Step {index + 1} of {diagnosticSteps.length}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{step.description}</p>
                    
                    {step.details && (
                      <div className={`mt-3 p-3 text-sm rounded ${
                        step.status === 'success' ? 'bg-green-100 text-green-800' :
                        step.status === 'warning' ? 'bg-amber-100 text-amber-800' :
                        step.status === 'error' ? 'bg-red-100 text-red-800' :
                        'bg-muted text-muted-foreground'
                      }`}>
                        {step.details}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <div className="p-4 border-b border-border bg-muted/50">
            <h2 className="font-semibold">System Information</h2>
          </div>
          <div className="p-4">
            <div className="space-y-3">
              {[
                { label: 'Operating System', value: 'Windows 11 Pro' },
                { label: 'ApexAgent Version', value: '2.3.1' },
                { label: 'CPU Usage', value: '32%' },
                { label: 'Memory Usage', value: '4.2 GB / 16 GB' },
                { label: 'Disk Space', value: '120 GB free' },
                { label: 'Last Update', value: '2 days ago' }
              ].map((item, index) => (
                <div key={index} className="flex justify-between">
                  <span className="text-sm text-muted-foreground">{item.label}</span>
                  <span className="text-sm font-medium">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <div className="p-4 border-b border-border bg-muted/50">
            <h2 className="font-semibold">Troubleshooting Actions</h2>
          </div>
          <div className="p-4">
            <div className="space-y-2">
              {[
                { label: 'Repair Installation', icon: '🔧' },
                { label: 'Clear Cache', icon: '🧹' },
                { label: 'Reset Configuration', icon: '⚙️' },
                { label: 'Check for Updates', icon: '🔄' },
                { label: 'Export Diagnostic Report', icon: '📊' },
                { label: 'Contact Support', icon: '🆘' }
              ].map((action, index) => (
                <button 
                  key={index}
                  className="w-full flex items-center p-3 rounded-md hover:bg-accent text-left"
                >
                  <span className="mr-3">{action.icon}</span>
                  <span>{action.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TroubleshootingInterface;
