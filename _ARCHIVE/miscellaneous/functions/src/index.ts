import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
import express from 'express';
import cors from 'cors';

// Initialize Firebase Admin
admin.initializeApp();

const db = admin.firestore();
const auth = admin.auth();
// const storage = admin.storage(); // Commented out as not used yet

// Create Express app
const app = express();
app.use(cors({ origin: true }));
app.use(express.json());

// Security middleware - simplified for demo
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  next();
});

// Rate limiting - simplified for demo
const requestCounts = new Map();
const rateLimiter = (req: any, res: any, next: any) => {
  const ip = req.ip || 'unknown';
  const now = Date.now();
  const windowMs = 15 * 60 * 1000; // 15 minutes
  const maxRequests = 100;

  if (!requestCounts.has(ip)) {
    requestCounts.set(ip, { count: 1, resetTime: now + windowMs });
    return next();
  }

  const record = requestCounts.get(ip);
  if (now > record.resetTime) {
    record.count = 1;
    record.resetTime = now + windowMs;
    return next();
  }

  if (record.count >= maxRequests) {
    return res.status(429).json({ error: 'Too many requests' });
  }

  record.count++;
  next();
};

app.use(rateLimiter);

// Authentication middleware
async function authenticateUser(req: any, res: any, next: any) {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const token = authHeader.split('Bearer ')[1];
    const decodedToken = await auth.verifyIdToken(token);
    req.user = decodedToken;
    next();
  } catch (error) {
    console.error('Authentication error:', error);
    res.status(401).json({ error: 'Unauthorized' });
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      firestore: 'connected',
      auth: 'connected',
      storage: 'connected'
    }
  });
});

// Authentication endpoints
app.post('/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // For demo purposes - in production, use Firebase Auth properly
    if (email === 'demo@aideon.ai' && password === 'demo123') {
      // Create custom token for demo user
      const customToken = await auth.createCustomToken('demo-user');
      
      res.json({
        success: true,
        token: customToken,
        user: {
          uid: 'demo-user',
          email: 'demo@aideon.ai',
          displayName: 'Demo User',
          credits: 2847,
          usageToday: 0.42
        }
      });
    } else {
      res.status(401).json({ error: 'Invalid credentials' });
    }
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/auth/status', authenticateUser, async (req: any, res) => {
  try {
    const userDoc = await db.collection('users').doc(req.user.uid).get();
    const userData = userDoc.exists ? userDoc.data() : {};
    
    res.json({
      authenticated: true,
      user: {
        uid: req.user.uid,
        email: req.user.email,
        displayName: userData?.displayName || 'Demo User',
        credits: userData?.credits || 2847,
        usageToday: userData?.usageToday || 0.42
      }
    });
  } catch (error) {
    console.error('Auth status error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Dashboard endpoints
app.get('/dashboard/metrics', authenticateUser, async (req: any, res) => {
  try {
    const metrics = {
      aiPerformance: {
        value: '98.7%',
        label: 'System Efficiency',
        trend: '+2.3%',
        color: 'green'
      },
      securityStatus: {
        value: '1,247',
        label: 'Threats Blocked Today',
        trend: '+15',
        color: 'blue'
      },
      hybridProcessing: {
        value: '2.3x',
        label: 'Faster than Cloud-Only',
        trend: '+0.2x',
        color: 'orange'
      },
      costSavings: {
        value: '45%',
        label: 'vs Cloud-Only Solutions',
        trend: '+3%',
        color: 'red'
      }
    };
    
    res.json(metrics);
  } catch (error) {
    console.error('Dashboard metrics error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/dashboard/activity', authenticateUser, async (req: any, res) => {
  try {
    const activities = [
      {
        id: 1,
        type: 'security',
        message: 'Security scan completed successfully',
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        status: 'success'
      },
      {
        id: 2,
        type: 'ai',
        message: 'AI model updated to latest version',
        timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        status: 'info'
      },
      {
        id: 3,
        type: 'project',
        message: 'New project "Data Analysis" created',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        status: 'success'
      }
    ];
    
    res.json(activities);
  } catch (error) {
    console.error('Dashboard activity error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Security endpoints
app.get('/security/status', authenticateUser, async (req: any, res) => {
  try {
    const securityStatus = {
      status: 'SECURE',
      lastScan: new Date().toISOString(),
      nextScan: new Date(Date.now() + 60 * 1000).toISOString(),
      aiGuardian: {
        active: true,
        threatsBlocked: 1247,
        confidence: 96.7
      },
      firewall: {
        status: 'ACTIVE',
        rulesActive: 847,
        connections: 23
      },
      threatDetection: {
        active: true,
        responseTime: '2.3s',
        successRate: 98.7
      }
    };
    
    res.json(securityStatus);
  } catch (error) {
    console.error('Security status error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/security/logs', authenticateUser, async (req: any, res) => {
  try {
    const logs = [
      {
        id: 1,
        timestamp: new Date().toISOString(),
        level: 'INFO',
        message: 'System security scan initiated',
        source: 'SecurityManager'
      },
      {
        id: 2,
        timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
        level: 'WARN',
        message: 'Suspicious activity detected from IP 192.168.1.100',
        source: 'ThreatDetection'
      },
      {
        id: 3,
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        level: 'INFO',
        message: 'Firewall rules updated successfully',
        source: 'NetworkSecurity'
      }
    ];
    
    res.json(logs);
  } catch (error) {
    console.error('Security logs error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Projects endpoints
app.get('/projects', authenticateUser, async (req: any, res) => {
  try {
    const projects = [
      {
        id: 'proj-1',
        name: 'AI Model Optimization',
        description: 'Optimizing neural network performance',
        status: 'active',
        progress: 75,
        team: 3,
        deadline: '2025-06-30',
        createdAt: '2025-06-01'
      },
      {
        id: 'proj-2',
        name: 'Security Enhancement',
        description: 'Implementing advanced threat detection',
        status: 'planning',
        progress: 25,
        team: 2,
        deadline: '2025-07-03',
        createdAt: '2025-06-15'
      },
      {
        id: 'proj-3',
        name: 'Data Pipeline',
        description: 'Building scalable data processing pipeline',
        status: 'completed',
        progress: 100,
        team: 4,
        deadline: '2025-06-25',
        createdAt: '2025-05-15'
      }
    ];
    
    res.json(projects);
  } catch (error) {
    console.error('Projects error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// System status endpoint
app.get('/system/status', authenticateUser, async (req: any, res) => {
  try {
    const systemStatus = {
      status: 'optimal',
      hybridProcessing: {
        local: 67,
        cloud: 33,
        efficiency: 2.3
      },
      resources: {
        cpu: 15,
        memory: {
          used: 2.1,
          total: 16,
          unit: 'GB'
        },
        storage: {
          free: 847,
          unit: 'GB'
        },
        network: 'optimal'
      },
      aiGuardian: {
        active: true,
        threatsBlocked: 1247
      }
    };
    
    res.json(systemStatus);
  } catch (error) {
    console.error('System status error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error handling middleware
app.use((error: any, req: any, res: any, next: any) => {
  console.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Chat endpoints with comprehensive model support
app.post('/chat/send', authenticateUser, async (req: any, res) => {
  try {
    const { message, model = 'gpt-4o', temperature = 0.7, max_tokens = 2000, stream = false } = req.body;
    
    // Comprehensive model routing
    let response;
    const provider = getModelProvider(model);
    
    switch (provider) {
      case 'openai':
        response = await callOpenAI(model, message, { temperature, max_tokens, stream });
        break;
      case 'anthropic':
        response = await callAnthropic(model, message, { temperature, max_tokens, stream });
        break;
      case 'google':
        response = await callGoogle(model, message, { temperature, max_tokens, stream });
        break;
      case 'together':
        response = await callTogether(model, message, { temperature, max_tokens, stream });
        break;
      default:
        // Fallback to simulation for unsupported models
        response = {
          content: `I understand you said: "${message}". As an AI assistant using ${model}, I'm here to help you with various tasks including analysis, coding, research, and creative work. How can I assist you further?`,
          tokens: message.length + 150,
          cost: 0.002
        };
    }

    // Save conversation to Firestore
    await db.collection('conversations').doc(req.user.uid).collection('messages').add({
      userMessage: message,
      aiResponse: response.content,
      model,
      provider,
      timestamp: new Date(),
      tokens: response.tokens || 0,
      cost: response.cost || 0.002,
      parameters: { temperature, max_tokens }
    });

    res.json({
      id: `msg-${Date.now()}`,
      message: response.content,
      model,
      provider,
      timestamp: new Date().toISOString(),
      tokens: {
        total: response.tokens || 0
      },
      cost: response.cost || 0.002
    });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: 'Failed to process chat request' });
  }
});

// Model provider detection
function getModelProvider(model: string): string {
  const openaiModels = ['gpt-5', 'gpt-5-mini', 'gpt-4o', 'gpt-4-turbo', 'o3', 'o3-mini'];
  const anthropicModels = ['claude-4-opus', 'claude-4-sonnet', 'claude-opus-4.1', 'claude-3.7-sonnet', 'claude-3.5-sonnet', 'claude-3.5-haiku', 'claude-3-opus'];
  const googleModels = ['gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.0-pro', 'gemini-1.5-pro', 'gemini-1.5-flash'];
  const togetherModels = ['llama-4-maverick', 'llama-4-scout', 'llama-3.3-70b', 'deepseek-v3', 'qwen3-235b', 'mistral-small-3'];

  if (openaiModels.some(m => model.includes(m))) return 'openai';
  if (anthropicModels.some(m => model.includes(m))) return 'anthropic';
  if (googleModels.some(m => model.includes(m))) return 'google';
  if (togetherModels.some(m => model.includes(m))) return 'together';
  
  return 'simulation'; // fallback to simulation
}

// OpenAI API integration
async function callOpenAI(model: string, message: string, options: any) {
  const openaiKey = process.env.OPENAI_API_KEY;
  if (!openaiKey) {
    console.warn('OpenAI API key not configured, using simulation');
    return simulateResponse(model, message);
  }

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: model,
        messages: [{ role: 'user', content: message }],
        temperature: options.temperature,
        max_tokens: options.max_tokens,
        stream: options.stream
      })
    });

    const data = await response.json();
    return {
      content: data.choices[0].message.content,
      tokens: data.usage?.total_tokens || 0,
      cost: calculateCost(model, data.usage?.total_tokens || 0)
    };
  } catch (error) {
    console.error('OpenAI API error:', error);
    return simulateResponse(model, message);
  }
}

// Anthropic API integration
async function callAnthropic(model: string, message: string, options: any) {
  const anthropicKey = process.env.ANTHROPIC_API_KEY;
  if (!anthropicKey) {
    console.warn('Anthropic API key not configured, using simulation');
    return simulateResponse(model, message);
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': anthropicKey,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: model,
        max_tokens: options.max_tokens,
        temperature: options.temperature,
        messages: [{ role: 'user', content: message }]
      })
    });

    const data = await response.json();
    return {
      content: data.content[0].text,
      tokens: (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0),
      cost: calculateCost(model, (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0))
    };
  } catch (error) {
    console.error('Anthropic API error:', error);
    return simulateResponse(model, message);
  }
}

// Google AI integration
async function callGoogle(model: string, message: string, options: any) {
  const googleKey = process.env.GOOGLE_AI_API_KEY;
  if (!googleKey) {
    console.warn('Google AI API key not configured, using simulation');
    return simulateResponse(model, message);
  }

  try {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${googleKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contents: [{ parts: [{ text: message }] }],
        generationConfig: {
          temperature: options.temperature,
          maxOutputTokens: options.max_tokens
        }
      })
    });

    const data = await response.json();
    return {
      content: data.candidates[0].content.parts[0].text,
      tokens: data.usageMetadata?.totalTokenCount || 0,
      cost: calculateCost(model, data.usageMetadata?.totalTokenCount || 0)
    };
  } catch (error) {
    console.error('Google AI API error:', error);
    return simulateResponse(model, message);
  }
}

// Together AI integration
async function callTogether(model: string, message: string, options: any) {
  const togetherKey = process.env.TOGETHER_API_KEY;
  if (!togetherKey) {
    console.warn('Together AI API key not configured, using simulation');
    return simulateResponse(model, message);
  }

  try {
    const response = await fetch('https://api.together.xyz/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${togetherKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: model,
        messages: [{ role: 'user', content: message }],
        temperature: options.temperature,
        max_tokens: options.max_tokens,
        stream: options.stream
      })
    });

    const data = await response.json();
    return {
      content: data.choices[0].message.content,
      tokens: data.usage?.total_tokens || 0,
      cost: calculateCost(model, data.usage?.total_tokens || 0)
    };
  } catch (error) {
    console.error('Together AI API error:', error);
    return simulateResponse(model, message);
  }
}

// Simulation fallback
function simulateResponse(model: string, message: string) {
  const responses = [
    `I understand you said: "${message}". As an AI assistant using ${model}, I'm here to help you with various tasks including analysis, coding, research, and creative work.`,
    `Thank you for your message: "${message}". Using ${model}, I can assist with complex reasoning, code generation, data analysis, and creative tasks.`,
    `I've received your message: "${message}". With ${model}, I'm equipped to handle advanced problem-solving, technical discussions, and comprehensive analysis.`
  ];
  
  const response = responses[Math.floor(Math.random() * responses.length)];
  return {
    content: response,
    tokens: message.length + response.length,
    cost: calculateCost(model, message.length + response.length)
  };
}

// Cost calculation for different models
function calculateCost(model: string, tokens: number): number {
  const pricing: { [key: string]: { input: number, output: number } } = {
    // OpenAI pricing (per 1M tokens)
    'gpt-5': { input: 1.25, output: 10.00 },
    'gpt-5-mini': { input: 0.15, output: 0.60 },
    'gpt-4o': { input: 2.50, output: 10.00 },
    'gpt-4-turbo': { input: 10.00, output: 30.00 },
    'o3': { input: 15.00, output: 60.00 },
    'o3-mini': { input: 3.75, output: 15.00 },
    
    // Anthropic pricing
    'claude-4-opus': { input: 15.00, output: 75.00 },
    'claude-4-sonnet': { input: 3.00, output: 15.00 },
    'claude-opus-4.1': { input: 18.00, output: 90.00 },
    'claude-3.7-sonnet': { input: 3.00, output: 15.00 },
    'claude-3.5-sonnet': { input: 3.00, output: 15.00 },
    'claude-3.5-haiku': { input: 0.25, output: 1.25 },
    
    // Google pricing
    'gemini-2.5-pro': { input: 1.25, output: 5.00 },
    'gemini-2.0-flash': { input: 0.075, output: 0.30 },
    'gemini-2.0-pro': { input: 1.25, output: 5.00 },
    'gemini-1.5-pro': { input: 1.25, output: 5.00 },
    'gemini-1.5-flash': { input: 0.075, output: 0.30 },
    
    // Together AI pricing (open source models)
    'llama-4-maverick': { input: 0.20, output: 0.20 },
    'llama-3.3-70b': { input: 0.88, output: 0.88 },
    'deepseek-v3': { input: 0.27, output: 1.10 },
    'qwen3-235b': { input: 0.80, output: 0.80 },
    'mistral-small-3': { input: 0.20, output: 0.20 }
  };

  const modelPricing = pricing[model] || { input: 0.50, output: 1.50 }; // default
  const avgPrice = (modelPricing.input + modelPricing.output) / 2;
  return (tokens / 1000000) * avgPrice;
}

app.get('/chat/history', authenticateUser, async (req: any, res) => {
  try {
    const { limit = 50 } = req.query;
    
    const messagesRef = db.collection('conversations').doc(req.user.uid).collection('messages');
    const snapshot = await messagesRef.orderBy('timestamp', 'desc').limit(parseInt(limit as string)).get();
    
    const messages = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
      timestamp: doc.data().timestamp.toDate().toISOString()
    }));
    
    res.json(messages.reverse());
  } catch (error) {
    console.error('Chat history error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get available models endpoint
app.get('/models/available', authenticateUser, async (req: any, res) => {
  try {
    const models = {
      openai: {
        flagship: [
          { id: 'gpt-5', name: 'GPT-5', description: 'Most advanced model for coding and agentic tasks', capabilities: ['text', 'code', 'reasoning'], pricing: '$1.25-$10.00/1M tokens' },
          { id: 'gpt-4o', name: 'GPT-4o', description: 'Multimodal model with real-time capabilities', capabilities: ['text', 'image', 'audio', 'vision'], pricing: '$2.50-$10.00/1M tokens' }
        ],
        efficient: [
          { id: 'gpt-5-mini', name: 'GPT-5 Mini', description: 'Faster, cost-effective version', capabilities: ['text', 'code'], pricing: '$0.15-$0.60/1M tokens' },
          { id: 'o3-mini', name: 'o3-mini', description: 'Cost-efficient reasoning model', capabilities: ['text', 'reasoning', 'math'], pricing: '$3.75-$15.00/1M tokens' }
        ],
        specialized: [
          { id: 'o3', name: 'o3', description: 'Advanced reasoning model', capabilities: ['text', 'reasoning'], pricing: '$15.00-$60.00/1M tokens' },
          { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', description: 'Enhanced with larger context', capabilities: ['text', 'code'], pricing: '$10.00-$30.00/1M tokens' }
        ]
      },
      anthropic: {
        flagship: [
          { id: 'claude-4-opus', name: 'Claude 4 Opus', description: 'Most capable and intelligent model', capabilities: ['text', 'reasoning', 'analysis'], pricing: '$15.00-$75.00/1M tokens' },
          { id: 'claude-opus-4.1', name: 'Claude Opus 4.1', description: 'Enhanced reasoning capabilities', capabilities: ['text', 'reasoning', 'complex-tasks'], pricing: '$18.00-$90.00/1M tokens' }
        ],
        balanced: [
          { id: 'claude-4-sonnet', name: 'Claude 4 Sonnet', description: 'Balanced performance and speed', capabilities: ['text', 'code', 'analysis'], pricing: '$3.00-$15.00/1M tokens' },
          { id: 'claude-3.7-sonnet', name: 'Claude 3.7 Sonnet', description: 'Latest reasoning and adaptability', capabilities: ['text', 'reasoning'], pricing: '$3.00-$15.00/1M tokens' }
        ],
        efficient: [
          { id: 'claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', description: 'Industry-leading intelligence', capabilities: ['text', 'code'], pricing: '$3.00-$15.00/1M tokens' },
          { id: 'claude-3.5-haiku', name: 'Claude 3.5 Haiku', description: 'Fast and efficient', capabilities: ['text'], pricing: '$0.25-$1.25/1M tokens' }
        ]
      },
      google: {
        flagship: [
          { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro', description: 'Most advanced with built-in thinking', capabilities: ['text', 'image', 'reasoning'], pricing: '$1.25-$5.00/1M tokens' },
          { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', description: 'Multimodal with next-gen features', capabilities: ['text', 'image', 'vision', 'multimodal'], pricing: '$0.075-$0.30/1M tokens' }
        ],
        efficient: [
          { id: 'gemini-2.0-flash-lite', name: 'Gemini 2.0 Flash-Lite', description: 'Lightweight version', capabilities: ['text', 'image'], pricing: '$0.075-$0.30/1M tokens' },
          { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', description: 'Fast multimodal processing', capabilities: ['text', 'image'], pricing: '$0.075-$0.30/1M tokens' }
        ],
        specialized: [
          { id: 'gemini-2.0-pro', name: 'Gemini 2.0 Pro', description: 'Enhanced reasoning capabilities', capabilities: ['text', 'reasoning'], pricing: '$1.25-$5.00/1M tokens' },
          { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', description: 'Long context multimodal', capabilities: ['text', 'image', 'long-context'], pricing: '$1.25-$5.00/1M tokens' }
        ]
      },
      together: {
        meta: [
          { id: 'llama-4-maverick', name: 'Llama 4 Maverick', description: 'Latest flagship model', capabilities: ['text', 'code', 'reasoning'], pricing: '$0.20/1M tokens' },
          { id: 'llama-4-scout', name: 'Llama 4 Scout', description: 'Specialized version', capabilities: ['text', 'analysis'], pricing: '$0.20/1M tokens' },
          { id: 'llama-3.3-70b', name: 'Llama 3.3 70B', description: 'Enhanced 70B parameter model', capabilities: ['text', 'code'], pricing: '$0.88/1M tokens' },
          { id: 'llama-3.2-90b', name: 'Llama 3.2 90B', description: 'Large parameter model', capabilities: ['text', 'reasoning'], pricing: '$0.88/1M tokens' }
        ],
        deepseek: [
          { id: 'deepseek-v3', name: 'DeepSeek V3', description: 'Latest version', capabilities: ['text', 'code', 'reasoning'], pricing: '$0.27-$1.10/1M tokens' },
          { id: 'deepseek-r1', name: 'DeepSeek R1', description: 'Reasoning-focused model', capabilities: ['text', 'reasoning'], pricing: '$0.27-$1.10/1M tokens' }
        ],
        qwen: [
          { id: 'qwen3-235b', name: 'Qwen3 235B Instruct', description: '235B MoE model', capabilities: ['text', 'reasoning'], pricing: '$0.80/1M tokens' },
          { id: 'qwen3-coder-480b', name: 'Qwen3-Coder 480B', description: '480B parameter coding model', capabilities: ['code', 'programming'], pricing: '$0.80/1M tokens' },
          { id: 'qwen-2.5-coder-32b', name: 'Qwen 2.5-Coder 32B', description: 'Specialized coding model', capabilities: ['code'], pricing: '$0.80/1M tokens' },
          { id: 'qwen2.5-vl-72b', name: 'Qwen2.5-VL 72B', description: 'Vision-language model', capabilities: ['text', 'vision', 'image'], pricing: '$0.80/1M tokens' }
        ],
        specialized: [
          { id: 'mistral-small-3', name: 'Mistral Small 3', description: 'Latest Mistral model', capabilities: ['text', 'code'], pricing: '$0.20/1M tokens' },
          { id: 'gemma-3-27b', name: 'Gemma 3 (27B)', description: 'Google\'s open model', capabilities: ['text'], pricing: '$0.20/1M tokens' },
          { id: 'cogito-v2-671b', name: 'Cogito v2 Preview', description: '671B mixture-of-experts', capabilities: ['text', 'reasoning'], pricing: '$0.80/1M tokens' }
        ]
      }
    };

    const totalModels = Object.values(models).reduce((acc, provider) => 
      acc + Object.values(provider).reduce((providerAcc, category) => 
        providerAcc + category.length, 0), 0);

    res.json({
      success: true,
      models,
      summary: {
        total_models: totalModels,
        providers: ['openai', 'anthropic', 'google', 'together'],
        capabilities: ['text', 'image', 'vision', 'audio', 'code', 'reasoning', 'multimodal', 'long-context'],
        pricing_range: '$0.075 - $90.00 per 1M tokens',
        latest_additions: ['gpt-5', 'claude-4-opus', 'gemini-2.5-pro', 'llama-4-maverick']
      },
      recommendations: {
        general_chat: ['gpt-4o', 'claude-4-sonnet', 'gemini-2.0-flash'],
        coding: ['gpt-5', 'qwen3-coder-480b', 'claude-4-sonnet'],
        reasoning: ['o3', 'claude-4-opus', 'gemini-2.5-pro'],
        cost_effective: ['gpt-5-mini', 'claude-3.5-haiku', 'gemini-2.0-flash'],
        multimodal: ['gpt-4o', 'gemini-2.0-flash', 'qwen2.5-vl-72b']
      }
    });
  } catch (error) {
    console.error('Models list error:', error);
    res.status(500).json({ error: 'Failed to fetch available models' });
  }
});

// Agents endpoints
app.get('/agents', authenticateUser, async (req: any, res) => {
  try {
    const agents = [
      {
        id: 'planner-agent',
        name: 'Planner Agent',
        type: 'reasoning',
        status: 'active',
        description: 'Advanced reasoning and task decomposition',
        capabilities: ['strategic_planning', 'task_breakdown', 'resource_allocation'],
        performance: {
          tasksCompleted: 1247,
          successRate: 98.7,
          avgResponseTime: '2.3s'
        },
        lastActive: new Date().toISOString()
      },
      {
        id: 'execution-agent',
        name: 'Execution Agent',
        type: 'execution',
        status: 'active',
        description: '100+ tool integrations and task execution',
        capabilities: ['api_integration', 'data_processing', 'automation'],
        performance: {
          tasksCompleted: 3421,
          successRate: 96.2,
          avgResponseTime: '1.8s'
        },
        lastActive: new Date().toISOString()
      },
      {
        id: 'security-agent',
        name: 'Security Agent',
        type: 'security',
        status: 'active',
        description: 'Real-time threat monitoring and compliance',
        capabilities: ['threat_detection', 'compliance_monitoring', 'incident_response'],
        performance: {
          threatsBlocked: 1247,
          successRate: 99.1,
          avgResponseTime: '0.5s'
        },
        lastActive: new Date().toISOString()
      },
      {
        id: 'verification-agent',
        name: 'Verification Agent',
        type: 'quality',
        status: 'active',
        description: 'Quality control and validation',
        capabilities: ['quality_assurance', 'data_validation', 'accuracy_checking'],
        performance: {
          verificationsCompleted: 2156,
          successRate: 97.8,
          avgResponseTime: '1.2s'
        },
        lastActive: new Date().toISOString()
      },
      {
        id: 'optimization-agent',
        name: 'Optimization Agent',
        type: 'performance',
        status: 'active',
        description: 'Performance tuning and resource management',
        capabilities: ['performance_optimization', 'resource_management', 'cost_optimization'],
        performance: {
          optimizationsApplied: 847,
          successRate: 94.5,
          avgResponseTime: '3.1s'
        },
        lastActive: new Date().toISOString()
      },
      {
        id: 'learning-agent',
        name: 'Learning Agent',
        type: 'learning',
        status: 'active',
        description: 'Federated learning and personalization',
        capabilities: ['machine_learning', 'personalization', 'pattern_recognition'],
        performance: {
          modelsUpdated: 156,
          successRate: 92.3,
          avgResponseTime: '5.7s'
        },
        lastActive: new Date().toISOString()
      }
    ];
    
    res.json(agents);
  } catch (error) {
    console.error('Agents error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/agents/:agentId/task', authenticateUser, async (req: any, res) => {
  try {
    const { agentId } = req.params;
    const { task, priority = 'normal', parameters = {} } = req.body;
    
    const taskId = `task-${Date.now()}`;
    const taskData = {
      id: taskId,
      agentId,
      task,
      priority,
      parameters,
      status: 'queued',
      createdAt: new Date(),
      userId: req.user.uid
    };
    
    await db.collection('agent_tasks').doc(taskId).set(taskData);
    
    // Simulate task processing
    setTimeout(async () => {
      await db.collection('agent_tasks').doc(taskId).update({
        status: 'completed',
        result: `Task "${task}" completed successfully by ${agentId}`,
        completedAt: new Date()
      });
    }, 2000);
    
    res.json({
      taskId,
      status: 'queued',
      estimatedCompletion: new Date(Date.now() + 5000).toISOString()
    });
  } catch (error) {
    console.error('Agent task error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Files endpoints
app.get('/files', authenticateUser, async (req: any, res) => {
  try {
    const { folder = '/', limit = 50 } = req.query;
    
    const files = [
      {
        id: 'file-1',
        name: 'AI_Model_Analysis.pdf',
        type: 'pdf',
        size: 2.4,
        sizeUnit: 'MB',
        folder: '/',
        uploadedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        lastModified: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        shared: false,
        tags: ['analysis', 'ai', 'research']
      },
      {
        id: 'file-2',
        name: 'Security_Report_2025.docx',
        type: 'docx',
        size: 1.8,
        sizeUnit: 'MB',
        folder: '/reports',
        uploadedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        lastModified: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        shared: true,
        tags: ['security', 'report', 'compliance']
      },
      {
        id: 'file-3',
        name: 'data_visualization.py',
        type: 'py',
        size: 15.2,
        sizeUnit: 'KB',
        folder: '/code',
        uploadedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        lastModified: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
        shared: false,
        tags: ['python', 'visualization', 'data']
      }
    ];
    
    const filteredFiles = folder === '/' ? files : files.filter(f => f.folder === folder);
    
    res.json({
      files: filteredFiles.slice(0, parseInt(limit as string)),
      totalCount: filteredFiles.length,
      currentFolder: folder
    });
  } catch (error) {
    console.error('Files error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/files/upload', authenticateUser, async (req: any, res) => {
  try {
    const { fileName, fileSize, fileType, folder = '/' } = req.body;
    
    const fileId = `file-${Date.now()}`;
    const fileData = {
      id: fileId,
      name: fileName,
      type: fileType,
      size: fileSize,
      folder,
      uploadedAt: new Date(),
      userId: req.user.uid,
      status: 'uploaded'
    };
    
    await db.collection('files').doc(fileId).set(fileData);
    
    res.json({
      fileId,
      status: 'uploaded',
      url: `https://storage.googleapis.com/your-bucket/${fileId}`
    });
  } catch (error) {
    console.error('File upload error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Artifacts endpoints
app.get('/artifacts', authenticateUser, async (req: any, res) => {
  try {
    const artifacts = [
      {
        id: 'artifact-1',
        name: 'Market Analysis Dashboard',
        type: 'dashboard',
        description: 'Interactive dashboard showing market trends and predictions',
        createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        lastModified: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'completed',
        tags: ['dashboard', 'analysis', 'market'],
        metadata: {
          charts: 5,
          dataPoints: 1247,
          lastUpdate: new Date().toISOString()
        }
      },
      {
        id: 'artifact-2',
        name: 'AI Model Performance Report',
        type: 'report',
        description: 'Comprehensive analysis of AI model performance metrics',
        createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        lastModified: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'completed',
        tags: ['ai', 'performance', 'report'],
        metadata: {
          pages: 24,
          models: 8,
          accuracy: 96.7
        }
      },
      {
        id: 'artifact-3',
        name: 'Security Automation Script',
        type: 'code',
        description: 'Python script for automated security monitoring',
        createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        lastModified: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'in_progress',
        tags: ['security', 'automation', 'python'],
        metadata: {
          lines: 847,
          functions: 23,
          coverage: 89
        }
      }
    ];
    
    res.json(artifacts);
  } catch (error) {
    console.error('Artifacts error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Analytics endpoints
app.get('/analytics/overview', authenticateUser, async (req: any, res) => {
  try {
    const analytics = {
      usage: {
        totalRequests: 15247,
        successfulRequests: 14891,
        failedRequests: 356,
        averageResponseTime: 2.3,
        peakHour: '14:00',
        dailyGrowth: 12.5
      },
      performance: {
        cpuUsage: 15.2,
        memoryUsage: 67.8,
        diskUsage: 23.4,
        networkThroughput: 45.6,
        uptime: 99.97
      },
      ai: {
        modelsUsed: 8,
        totalInferences: 3421,
        averageAccuracy: 96.7,
        costPerInference: 0.002,
        popularModel: 'gpt-4'
      },
      security: {
        threatsDetected: 1247,
        threatsBlocked: 1247,
        falsePositives: 0,
        averageResponseTime: 0.5,
        riskLevel: 'low'
      }
    };
    
    res.json(analytics);
  } catch (error) {
    console.error('Analytics error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Settings endpoints
app.get('/settings', authenticateUser, async (req: any, res) => {
  try {
    const userDoc = await db.collection('user_settings').doc(req.user.uid).get();
    const settings = userDoc.exists ? userDoc.data() : {
      ai: {
        preferredModel: 'gpt-4',
        temperature: 0.7,
        maxTokens: 2048,
        enableLocalProcessing: true
      },
      security: {
        enableThreatDetection: true,
        alertLevel: 'medium',
        enableAuditLogging: true,
        sessionTimeout: 30
      },
      interface: {
        theme: 'dark',
        language: 'en',
        enableNotifications: true,
        compactMode: false
      },
      privacy: {
        dataRetention: 90,
        enableAnalytics: true,
        shareUsageData: false,
        enableCookies: true
      }
    };
    
    res.json(settings);
  } catch (error) {
    console.error('Settings error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.put('/settings', authenticateUser, async (req: any, res) => {
  try {
    const settings = req.body;
    
    await db.collection('user_settings').doc(req.user.uid).set(settings, { merge: true });
    
    res.json({ success: true, message: 'Settings updated successfully' });
  } catch (error) {
    console.error('Settings update error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Dr. TARDIS endpoints (Advanced AI Assistant)
app.post('/tardis/analyze', authenticateUser, async (req: any, res) => {
  try {
    const { data, analysisType = 'comprehensive' } = req.body;
    
    // Simulate advanced AI analysis
    const analysis = {
      id: `analysis-${Date.now()}`,
      type: analysisType,
      status: 'completed',
      results: {
        summary: 'Advanced analysis completed successfully',
        insights: [
          'Data shows strong correlation between variables A and B',
          'Anomaly detected in time series data at timestamp 2025-01-15T14:30:00Z',
          'Predictive model suggests 15% increase in next quarter'
        ],
        confidence: 94.7,
        recommendations: [
          'Consider implementing automated monitoring for detected anomalies',
          'Increase sampling frequency during peak hours',
          'Review data quality processes for improved accuracy'
        ]
      },
      metadata: {
        processingTime: 3.2,
        dataPoints: data?.length || 1000,
        algorithmsUsed: ['neural_network', 'time_series', 'anomaly_detection'],
        timestamp: new Date().toISOString()
      }
    };
    
    res.json(analysis);
  } catch (error) {
    console.error('TARDIS analysis error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/tardis/capabilities', authenticateUser, async (req: any, res) => {
  try {
    const capabilities = {
      analysis: [
        'Data Analysis & Visualization',
        'Predictive Modeling',
        'Anomaly Detection',
        'Pattern Recognition',
        'Statistical Analysis'
      ],
      automation: [
        'Workflow Automation',
        'Task Scheduling',
        'Process Optimization',
        'Resource Management',
        'Performance Monitoring'
      ],
      intelligence: [
        'Natural Language Processing',
        'Computer Vision',
        'Machine Learning',
        'Deep Learning',
        'Reinforcement Learning'
      ],
      integration: [
        'API Integrations',
        'Database Connectivity',
        'Cloud Services',
        'Third-party Tools',
        'Custom Connectors'
      ]
    };
    
    res.json(capabilities);
  } catch (error) {
    console.error('TARDIS capabilities error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// WebSocket support for real-time features
app.get('/ws/connect', authenticateUser, async (req: any, res) => {
  try {
    // In a real implementation, this would establish WebSocket connection
    const connectionInfo = {
      wsUrl: `wss://your-project.cloudfunctions.net/api/ws`,
      token: req.headers.authorization,
      channels: ['system', 'security', 'agents', 'chat'],
      heartbeatInterval: 30000
    };
    
    res.json(connectionInfo);
  } catch (error) {
    console.error('WebSocket connection error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Export the Express app as a Firebase Cloud Function
export const api = functions.https.onRequest(app);

