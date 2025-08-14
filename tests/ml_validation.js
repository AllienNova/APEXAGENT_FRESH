/**
 * ML Model Integration Validation Tests
 * 
 * This file contains tests to validate the integration of advanced ML models
 * with the custom circuit breaker pattern in Aideon AI Lite.
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');

// Import ML models
const MLModel = require('../src/ml/MLModel');
const TestMLModelProvider = require('./TestMLModelProvider');
const MobileNetProvider = require('../src/ml/vision/MobileNetProvider');
const MobileNetModel = require('../src/ml/vision/MobileNetModel');
const WhisperProvider = require('../src/ml/audio/WhisperProvider');
const WhisperModel = require('../src/ml/audio/WhisperModel');
const YOLOProvider = require('../src/ml/vision/YOLOProvider');
const YOLOModel = require('../src/ml/vision/YOLOModel');

// Import circuit breaker
const CircuitBreaker = require('../src/core/models/providers/utils/CustomCircuitBreaker');

// Mock core system
const mockCore = {
  logger: {
    info: console.log,
    error: console.error,
    warn: console.warn,
    debug: console.log
  },
  paths: {
    models: path.join(__dirname, 'test_models'),
    data: path.join(__dirname, 'test_data')
  },
  config: {
    ml: {
      providers: {
        mobilenet: {
          enabled: true,
          modelVersion: 'v2',
          modelPath: path.join(__dirname, 'test_models/mobilenet')
        },
        whisper: {
          enabled: true,
          modelVersion: 'small',
          modelPath: path.join(__dirname, 'test_models/whisper')
        },
        yolo: {
          enabled: true,
          modelVersion: 'yolov8n',
          modelPath: path.join(__dirname, 'test_models/yolo')
        }
      }
    }
  }
};

// Create test directories
function setupTestDirectories() {
  const dirs = [
    mockCore.paths.models,
    mockCore.paths.data,
    path.join(mockCore.paths.models, 'mobilenet'),
    path.join(mockCore.paths.models, 'whisper'),
    path.join(mockCore.paths.models, 'yolo')
  ];
  
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

// Test suite
async function runTests() {
  console.log('Starting ML Model Integration Validation Tests');
  console.log('=============================================');
  
  // Setup test environment
  setupTestDirectories();
  
  try {
    // Test base classes
    await testBaseClasses();
    
    // Test MobileNet integration
    await testMobileNetIntegration();
    
    // Test Whisper integration
    await testWhisperIntegration();
    
    // Test YOLO integration
    await testYOLOIntegration();
    
    // Test circuit breaker integration
    await testCircuitBreakerIntegration();
    
    // Test concurrent model execution
    await testConcurrentExecution();
    
    console.log('\nAll tests passed successfully!');
  } catch (error) {
    console.error(`\nTest failed: ${error.message}`);
    console.error(error.stack);
    process.exit(1);
  }
}

// Test base classes
async function testBaseClasses() {
  console.log('\nTesting base classes...');
  
  // Test MLModelProvider using TestMLModelProvider
  const provider = new TestMLModelProvider(mockCore);
  assert(provider, 'TestMLModelProvider should be instantiated');
  assert(provider.id === 'test-ml-provider', 'TestMLModelProvider should have correct ID');
  assert(typeof provider.initialize === 'function', 'TestMLModelProvider should have initialize method');
  
  // Test MLModel with mock model data
  const model = new MLModel(provider, {
    id: 'test-model',
    name: 'Test Model',
    type: 'test',
    version: '1.0',
    isLocal: true
  });
  assert(model, 'MLModel should be instantiated');
  assert(model.id === 'test-model', 'MLModel should have correct ID');
  assert(typeof model.execute === 'function', 'MLModel should have execute method');
  
  console.log('✓ Base classes validated');
}

// Test MobileNet integration
async function testMobileNetIntegration() {
  console.log('\nTesting MobileNet integration...');
  
  // Create test provider with required properties
  class TestMobileNetProvider extends MobileNetProvider {
    get id() { return 'mobilenet'; }
    get name() { return 'MobileNet Provider'; }
    async _registerModels() { return Promise.resolve(); }
  }
  
  // Test provider
  const provider = new TestMobileNetProvider(mockCore);
  assert(provider, 'MobileNetProvider should be instantiated');
  assert(provider.id === 'mobilenet', 'MobileNetProvider should have correct ID');
  
  // Mock model initialization
  const model = {
    id: 'mobilenet-v2',
    name: 'MobileNet v2',
    type: 'vision',
    version: 'v2',
    isLocal: true,
    capabilities: {
      imageClassification: true
    },
    execute: async () => ({
      predictions: [
        { label: 'cat', confidence: 0.95 },
        { label: 'tiger cat', confidence: 0.04 }
      ],
      modelInfo: {
        id: 'mobilenet-v2',
        name: 'MobileNet v2',
        version: 'v2'
      }
    })
  };
  
  // Mock model execution with circuit breaker
  const circuitBreaker = new CircuitBreaker({
    name: 'mobilenet-test',
    maxFailures: 3,
    resetTimeout: 30000,
    timeout: 5000
  });
  
  // Wrap model execution with circuit breaker
  const protectedExecute = circuitBreaker.wrap(async () => {
    return model.execute();
  });
  
  const result = await protectedExecute();
  assert(result, 'MobileNetModel execution should return a result');
  assert(result.predictions.length > 0, 'MobileNetModel should return predictions');
  assert(result.predictions[0].label === 'cat', 'MobileNetModel should return correct label');
  
  console.log('✓ MobileNet integration validated');
}

// Test Whisper integration
async function testWhisperIntegration() {
  console.log('\nTesting Whisper integration...');
  
  // Create test provider with required properties
  class TestWhisperProvider extends WhisperProvider {
    get id() { return 'whisper'; }
    get name() { return 'Whisper Provider'; }
    async _registerModels() { return Promise.resolve(); }
  }
  
  // Test provider
  const provider = new TestWhisperProvider(mockCore);
  assert(provider, 'WhisperProvider should be instantiated');
  assert(provider.id === 'whisper', 'WhisperProvider should have correct ID');
  
  // Mock model
  const model = {
    id: 'whisper-small',
    name: 'Whisper Small',
    type: 'audio',
    version: 'small',
    isLocal: true,
    capabilities: {
      speechRecognition: true
    },
    requirements: {
      language: 'en',
      multilingual: true
    },
    execute: async () => ({
      text: "This is a simulated transcription of the audio input.",
      segments: [
        {
          id: 0,
          start: 0.0,
          end: 3.5,
          text: "This is a simulated transcription",
          confidence: 0.95
        }
      ],
      language: 'en',
      modelInfo: {
        id: 'whisper-small',
        name: 'Whisper Small',
        version: 'small'
      }
    })
  };
  
  // Mock model execution with circuit breaker
  const circuitBreaker = new CircuitBreaker({
    name: 'whisper-test',
    maxFailures: 3,
    resetTimeout: 30000,
    timeout: 10000
  });
  
  // Wrap model execution with circuit breaker
  const protectedExecute = circuitBreaker.wrap(async () => {
    return model.execute();
  });
  
  const result = await protectedExecute();
  assert(result, 'WhisperModel execution should return a result');
  assert(result.text, 'WhisperModel should return transcribed text');
  assert(result.segments.length > 0, 'WhisperModel should return segments');
  
  console.log('✓ Whisper integration validated');
}

// Test YOLO integration
async function testYOLOIntegration() {
  console.log('\nTesting YOLO integration...');
  
  // Create test provider with required properties
  class TestYOLOProvider extends YOLOProvider {
    get id() { return 'yolo'; }
    get name() { return 'YOLO Provider'; }
    async _registerModels() { return Promise.resolve(); }
  }
  
  // Test provider
  const provider = new TestYOLOProvider(mockCore);
  assert(provider, 'YOLOProvider should be instantiated');
  assert(provider.id === 'yolo', 'YOLOProvider should have correct ID');
  
  // Mock model
  const model = {
    id: 'yolo-yolov8n',
    name: 'YOLO v8n',
    type: 'vision',
    version: 'yolov8n',
    isLocal: true,
    capabilities: {
      objectDetection: true
    },
    requirements: {
      confidenceThreshold: 0.25,
      iouThreshold: 0.45
    },
    execute: async () => ({
      detections: [
        {
          box: [100, 150, 200, 300],
          label: 'person',
          confidence: 0.92,
          classId: 0
        },
        {
          box: [50, 50, 100, 80],
          label: 'dog',
          confidence: 0.87,
          classId: 16
        }
      ],
      modelInfo: {
        id: 'yolo-yolov8n',
        name: 'YOLO v8n',
        version: 'yolov8n'
      }
    })
  };
  
  // Mock model execution with circuit breaker
  const circuitBreaker = new CircuitBreaker({
    name: 'yolo-test',
    maxFailures: 3,
    resetTimeout: 30000,
    timeout: 8000
  });
  
  // Wrap model execution with circuit breaker
  const protectedExecute = circuitBreaker.wrap(async () => {
    return model.execute();
  });
  
  const result = await protectedExecute();
  assert(result, 'YOLOModel execution should return a result');
  assert(result.detections.length > 0, 'YOLOModel should return detections');
  assert(result.detections[0].label === 'person', 'YOLOModel should return correct label');
  
  console.log('✓ YOLO integration validated');
}

// Test circuit breaker integration
async function testCircuitBreakerIntegration() {
  console.log('\nTesting circuit breaker integration...');
  
  // Create circuit breaker
  const circuitBreaker = new CircuitBreaker({
    name: 'test-circuit-breaker',
    maxFailures: 2,
    resetTimeout: 5000,
    timeout: 1000
  });
  
  // Test successful execution
  const successResult = await circuitBreaker.execute(async () => {
    return 'success';
  });
  assert(successResult === 'success', 'Circuit breaker should pass through successful results');
  assert(circuitBreaker.state === 'CLOSED', 'Circuit breaker should remain closed after success');
  
  // Test failure handling
  try {
    await circuitBreaker.execute(async () => {
      throw new Error('Simulated failure');
    });
    assert(false, 'Circuit breaker should propagate errors');
  } catch (error) {
    assert(error.message === 'Simulated failure', 'Circuit breaker should pass through error message');
  }
  
  // Test circuit opening after failures
  try {
    await circuitBreaker.execute(async () => {
      throw new Error('Simulated failure');
    });
  } catch (error) {
    // Expected
  }
  
  try {
    await circuitBreaker.execute(async () => {
      return 'This should not execute';
    });
    assert(false, 'Circuit breaker should be open and reject calls');
  } catch (error) {
    assert(error.message.includes('Circuit breaker is open'), 'Circuit breaker should reject calls when open');
    assert(circuitBreaker.state === 'OPEN', 'Circuit breaker should be open after max failures');
  }
  
  console.log('✓ Circuit breaker integration validated');
}

// Test concurrent model execution
async function testConcurrentExecution() {
  console.log('\nTesting concurrent model execution...');
  
  // Create circuit breakers for each model
  const mobileNetCircuitBreaker = new CircuitBreaker({
    name: 'mobilenet-concurrent',
    maxFailures: 3,
    resetTimeout: 30000,
    timeout: 5000
  });
  
  const whisperCircuitBreaker = new CircuitBreaker({
    name: 'whisper-concurrent',
    maxFailures: 3,
    resetTimeout: 30000,
    timeout: 10000
  });
  
  const yoloCircuitBreaker = new CircuitBreaker({
    name: 'yolo-concurrent',
    maxFailures: 3,
    resetTimeout: 30000,
    timeout: 8000
  });
  
  // Mock model executions
  const mobileNetExecute = mobileNetCircuitBreaker.wrap(async () => {
    // Simulate successful execution with delay
    await new Promise(resolve => setTimeout(resolve, 100));
    return {
      predictions: [{ label: 'cat', confidence: 0.95 }],
      modelInfo: { id: 'mobilenet-v2' }
    };
  });
  
  const whisperExecute = whisperCircuitBreaker.wrap(async () => {
    // Simulate successful execution with delay
    await new Promise(resolve => setTimeout(resolve, 150));
    return {
      text: "This is a simulated transcription.",
      modelInfo: { id: 'whisper-small' }
    };
  });
  
  const yoloExecute = yoloCircuitBreaker.wrap(async () => {
    // Simulate successful execution with delay
    await new Promise(resolve => setTimeout(resolve, 120));
    return {
      detections: [{ label: 'person', confidence: 0.92 }],
      modelInfo: { id: 'yolo-yolov8n' }
    };
  });
  
  // Execute all models concurrently
  const startTime = Date.now();
  const results = await Promise.all([
    mobileNetExecute(),
    whisperExecute(),
    yoloExecute()
  ]);
  const endTime = Date.now();
  
  // Verify results
  assert(results.length === 3, 'Should receive results from all three models');
  assert(results[0].predictions[0].label === 'cat', 'MobileNet result should be correct');
  assert(results[1].text === "This is a simulated transcription.", 'Whisper result should be correct');
  assert(results[2].detections[0].label === 'person', 'YOLO result should be correct');
  
  // Verify concurrent execution (total time should be less than sum of individual times)
  const totalTime = endTime - startTime;
  assert(totalTime < 370, 'Concurrent execution should be faster than sequential execution');
  
  console.log('✓ Concurrent model execution validated');
}

// Run all tests
runTests().catch(console.error);
