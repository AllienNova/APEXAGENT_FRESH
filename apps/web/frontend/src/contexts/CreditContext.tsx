import React, { createContext, useContext, useState, useEffect } from 'react';

interface CreditContextType {
  balance: number;
  monthlyAllocation: number;
  usedThisMonth: number;
  tier: 'Basic' | 'Pro' | 'Expert' | 'Enterprise';
  apiKeys: { [service: string]: boolean };
  consumeCredits: (amount: number, service: string) => boolean;
  purchaseCredits: (amount: number) => void;
  updateApiKeyStatus: (service: string, hasKey: boolean) => void;
}

const CreditContext = createContext<CreditContextType | undefined>(undefined);

export const useCreditSystem = () => {
  const context = useContext(CreditContext);
  if (!context) {
    throw new Error('useCreditSystem must be used within a CreditProvider');
  }
  return context;
};

interface CreditProviderProps {
  children: React.ReactNode;
}

export const CreditProvider: React.FC<CreditProviderProps> = ({ children }) => {
  const [balance, setBalance] = useState(3247);
  const [monthlyAllocation, setMonthlyAllocation] = useState(5000);
  const [usedThisMonth, setUsedThisMonth] = useState(1753);
  const [tier, setTier] = useState<'Basic' | 'Pro' | 'Expert' | 'Enterprise'>('Pro');
  const [apiKeys, setApiKeys] = useState<{ [service: string]: boolean }>({
    openai: true,
    anthropic: false,
    midjourney: true,
    runway: false,
    google: false,
    stability: false
  });

  // Credit costs per operation type and service
  const creditCosts = {
    text: {
      standard: { openai: 2, anthropic: 2, google: 2 },
      premium: { openai: 10, anthropic: 15, google: 12 }
    },
    image: {
      standard: { midjourney: 8, stability: 5, openai: 5 },
      premium: { midjourney: 25, stability: 20, openai: 20 }
    },
    video: {
      standard: { runway: 80, stability: 60 },
      premium: { runway: 180, stability: 150 }
    }
  };

  const consumeCredits = (amount: number, service: string): boolean => {
    // If user has their own API key for this service, don't consume credits
    if (apiKeys[service]) {
      return true;
    }

    // Check if user has enough credits
    if (balance < amount) {
      return false;
    }

    // Consume credits
    setBalance(prev => prev - amount);
    setUsedThisMonth(prev => prev + amount);
    
    // Store usage in localStorage for persistence
    const usage = JSON.parse(localStorage.getItem('creditUsage') || '{}');
    usage[service] = (usage[service] || 0) + amount;
    localStorage.setItem('creditUsage', JSON.stringify(usage));

    return true;
  };

  const purchaseCredits = (amount: number) => {
    setBalance(prev => prev + amount);
    
    // Store purchase in localStorage
    const purchases = JSON.parse(localStorage.getItem('creditPurchases') || '[]');
    purchases.push({
      amount,
      timestamp: new Date().toISOString(),
      price: calculateCreditPrice(amount)
    });
    localStorage.setItem('creditPurchases', JSON.stringify(purchases));
  };

  const updateApiKeyStatus = (service: string, hasKey: boolean) => {
    setApiKeys(prev => ({
      ...prev,
      [service]: hasKey
    }));
    
    // Store API key status in localStorage
    localStorage.setItem('apiKeyStatus', JSON.stringify({
      ...apiKeys,
      [service]: hasKey
    }));
  };

  const calculateCreditPrice = (credits: number): number => {
    // Pricing tiers for credit purchases
    if (credits >= 25000) return credits * 0.008; // $0.008 per credit for 25K+
    if (credits >= 10000) return credits * 0.0085; // $0.0085 per credit for 10K+
    if (credits >= 5000) return credits * 0.009; // $0.009 per credit for 5K+
    return credits * 0.01; // $0.01 per credit for smaller amounts
  };

  // Load saved data on component mount
  useEffect(() => {
    const savedApiKeys = localStorage.getItem('apiKeyStatus');
    if (savedApiKeys) {
      setApiKeys(JSON.parse(savedApiKeys));
    }

    const savedBalance = localStorage.getItem('creditBalance');
    if (savedBalance) {
      setBalance(parseInt(savedBalance));
    }

    const savedUsage = localStorage.getItem('monthlyUsage');
    if (savedUsage) {
      setUsedThisMonth(parseInt(savedUsage));
    }
  }, []);

  // Save balance changes to localStorage
  useEffect(() => {
    localStorage.setItem('creditBalance', balance.toString());
  }, [balance]);

  useEffect(() => {
    localStorage.setItem('monthlyUsage', usedThisMonth.toString());
  }, [usedThisMonth]);

  const value: CreditContextType = {
    balance,
    monthlyAllocation,
    usedThisMonth,
    tier,
    apiKeys,
    consumeCredits,
    purchaseCredits,
    updateApiKeyStatus
  };

  return (
    <CreditContext.Provider value={value}>
      {children}
    </CreditContext.Provider>
  );
};

// Hook for calculating credit cost for operations
export const useCreditCalculator = () => {
  const { apiKeys } = useCreditSystem();

  const calculateCost = (
    operationType: 'text' | 'image' | 'video',
    service: string,
    tier: 'standard' | 'premium' = 'standard',
    tokens: number = 1000
  ): number => {
    // If user has API key for this service, cost is 0
    if (apiKeys[service]) {
      return 0;
    }

    const baseCosts = {
      text: {
        standard: { openai: 2, anthropic: 2, google: 2 },
        premium: { openai: 10, anthropic: 15, google: 12 }
      },
      image: {
        standard: { midjourney: 8, stability: 5, openai: 5 },
        premium: { midjourney: 25, stability: 20, openai: 20 }
      },
      video: {
        standard: { runway: 80, stability: 60 },
        premium: { runway: 180, stability: 150 }
      }
    };

    const baseCost = baseCosts[operationType]?.[tier]?.[service] || 10;
    
    // For text operations, scale by tokens (per 1000 tokens)
    if (operationType === 'text') {
      return Math.ceil((tokens / 1000) * baseCost);
    }
    
    // For image and video, return base cost per operation
    return baseCost;
  };

  return { calculateCost };
};

// Hook for smart service routing
export const useServiceRouter = () => {
  const { apiKeys } = useCreditSystem();
  const { calculateCost } = useCreditCalculator();

  const selectOptimalService = (
    operationType: 'text' | 'image' | 'video',
    qualityPreference: 'cost' | 'quality' | 'balanced' = 'balanced'
  ): string => {
    const availableServices = {
      text: ['openai', 'anthropic', 'google'],
      image: ['midjourney', 'stability', 'openai'],
      video: ['runway', 'stability']
    };

    const services = availableServices[operationType] || [];
    
    // Prioritize services where user has API keys (0 cost)
    const userKeyServices = services.filter(service => apiKeys[service]);
    if (userKeyServices.length > 0) {
      return userKeyServices[0]; // Return first available user key service
    }

    // If no user keys, select based on preference
    if (qualityPreference === 'cost') {
      // Return service with lowest credit cost
      return services.reduce((cheapest, service) => {
        const currentCost = calculateCost(operationType, service, 'standard');
        const cheapestCost = calculateCost(operationType, cheapest, 'standard');
        return currentCost < cheapestCost ? service : cheapest;
      });
    }

    if (qualityPreference === 'quality') {
      // Return premium service (usually first in list)
      return services[0];
    }

    // Balanced: return mid-tier service
    return services[Math.floor(services.length / 2)] || services[0];
  };

  return { selectOptimalService };
};

export default CreditProvider;

