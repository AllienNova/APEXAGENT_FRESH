/**
 * PaymentSystemTests.js
 * Test suite for the payment system implementation
 */

const PaymentSystem = require('../src/payment/PaymentSystem');
const SubscriptionManager = require('../src/payment/SubscriptionManager');
const ApiKeyManager = require('../src/payment/ApiKeyManager');

/**
 * Run all payment system tests
 */
async function runTests() {
  console.log('=== Running Payment System Tests ===');
  
  // Test individual components
  await testPaymentSystem();
  await testSubscriptionManager();
  await testApiKeyManager();
  
  // Test integration between components
  await testComponentIntegration();
  
  console.log('\n=== All tests completed ===');
}

/**
 * Test the core PaymentSystem functionality
 */
async function testPaymentSystem() {
  console.log('\n--- Testing PaymentSystem ---');
  
  const paymentSystem = new PaymentSystem();
  
  // Test initialization
  console.log('Testing initialization...');
  const initResult = paymentSystem.initialize({
    stripe: { apiKey: 'sk_test_stripe' },
    paypal: { clientId: 'test_client', secret: 'test_secret' }
  });
  console.assert(initResult === true, 'Initialization should succeed');
  
  // Test subscription creation
  console.log('Testing subscription creation...');
  try {
    const subscription = paymentSystem.createSubscription(
      'test_user_1',
      'basic',
      false,
      { processor: 'stripe' }
    );
    console.assert(subscription.tier === 'basic', 'Tier should be basic');
    console.assert(subscription.useOwnApi === false, 'Should use provided API');
    console.assert(subscription.price === 24.99, 'Price should be 24.99');
    console.log('✓ Subscription creation passed');
  } catch (error) {
    console.error(`✗ Subscription creation failed: ${error.message}`);
  }
  
  // Test subscription creation with own API
  console.log('Testing subscription with own API...');
  try {
    const subscription = paymentSystem.createSubscription(
      'test_user_2',
      'pro',
      true,
      { processor: 'stripe' }
    );
    console.assert(subscription.tier === 'pro', 'Tier should be pro');
    console.assert(subscription.useOwnApi === true, 'Should use own API');
    console.assert(subscription.price === 49.99, 'Price should be 49.99');
    console.log('✓ Subscription with own API passed');
  } catch (error) {
    console.error(`✗ Subscription with own API failed: ${error.message}`);
  }
  
  // Test enterprise subscription
  console.log('Testing enterprise subscription...');
  try {
    const subscription = paymentSystem.createSubscription(
      'test_user_3',
      'enterprise',
      false,
      { contactInfo: { name: 'Test Corp', email: 'test@corp.com' } }
    );
    console.assert(subscription.tier === 'enterprise', 'Tier should be enterprise');
    console.assert(subscription.status === 'pending_approval', 'Status should be pending approval');
    console.log('✓ Enterprise subscription passed');
  } catch (error) {
    console.error(`✗ Enterprise subscription failed: ${error.message}`);
  }
  
  // Test credit purchase
  console.log('Testing credit purchase...');
  try {
    const purchase = paymentSystem.purchaseCredits(
      'test_user_1',
      5000,
      { processor: 'stripe' }
    );
    console.assert(purchase.success === true, 'Purchase should succeed');
    console.assert(purchase.creditsPurchased === 5000, 'Should purchase 5000 credits');
    console.assert(purchase.cost === 50, 'Cost should be $50 for 5000 credits');
    console.log('✓ Credit purchase passed');
  } catch (error) {
    console.error(`✗ Credit purchase failed: ${error.message}`);
  }
  
  // Test credit consumption
  console.log('Testing credit consumption...');
  const consumeResult = paymentSystem.consumeCredits('test_user_1', 'advancedLLM', false);
  console.assert(consumeResult === true, 'Credit consumption should succeed');
  console.log('✓ Credit consumption passed');
  
  // Test credit consumption with own API
  console.log('Testing credit consumption with own API...');
  const consumeOwnApiResult = paymentSystem.consumeCredits('test_user_2', 'standardLLM', true);
  console.assert(consumeOwnApiResult === true, 'Credit consumption with own API should succeed');
  console.log('✓ Credit consumption with own API passed');
}

/**
 * Test the SubscriptionManager functionality
 */
async function testSubscriptionManager() {
  console.log('\n--- Testing SubscriptionManager ---');
  
  const subscriptionManager = new SubscriptionManager();
  
  // Test initialization
  console.log('Testing initialization...');
  const initResult = subscriptionManager.initialize({
    stripe: { apiKey: 'sk_test_stripe' },
    paypal: { clientId: 'test_client', secret: 'test_secret' }
  });
  console.assert(initResult === true, 'Initialization should succeed');
  
  // Test user signup
  console.log('Testing user signup...');
  try {
    const userData = {
      name: 'Test User',
      email: 'test@example.com'
    };
    
    const result = subscriptionManager.signUpUser(
      userData,
      'basic',
      false,
      { processor: 'stripe' }
    );
    
    console.assert(result.userId, 'Should return a user ID');
    console.assert(result.subscription.tier === 'basic', 'Tier should be basic');
    console.log('✓ User signup passed');
  } catch (error) {
    console.error(`✗ User signup failed: ${error.message}`);
  }
  
  // Test feature access
  console.log('Testing feature access...');
  const hasAccess = subscriptionManager.hasFeatureAccess('test_user', 'documentCreation');
  console.assert(hasAccess === true, 'Pro tier should have document creation access');
  
  const hasAdvancedAccess = subscriptionManager.hasFeatureAccess('test_user', 'advancedDocumentWorkflows');
  console.assert(hasAdvancedAccess === false, 'Pro tier should not have advanced document workflows');
  console.log('✓ Feature access checks passed');
  
  // Test model usage
  console.log('Testing model usage...');
  const canUseStandard = subscriptionManager.canUseModel('test_user', 'standard', 1);
  console.assert(canUseStandard === true, 'Pro tier should be able to use standard model 1');
  
  const canUseAdvanced = subscriptionManager.canUseModel('test_user', 'advanced', 1);
  console.assert(canUseAdvanced === true, 'Pro tier should be able to use advanced model 1');
  
  const canUseAdvanced2 = subscriptionManager.canUseModel('test_user', 'advanced', 2);
  console.assert(canUseAdvanced2 === false, 'Pro tier should not be able to use advanced model 2');
  console.log('✓ Model usage checks passed');
  
  // Test subscription details
  console.log('Testing subscription details...');
  const subscription = subscriptionManager.getUserSubscription('test_user');
  console.assert(subscription.tier === 'pro', 'Should return pro tier');
  console.assert(subscription.price === 49.99, 'Price should be 49.99');
  console.log('✓ Subscription details passed');
  
  // Test credit usage history
  console.log('Testing credit usage history...');
  const usageHistory = subscriptionManager.getCreditUsageHistory('test_user');
  console.assert(Array.isArray(usageHistory), 'Should return an array');
  console.assert(usageHistory.length > 0, 'Should have usage entries');
  console.log('✓ Credit usage history passed');
}

/**
 * Test the ApiKeyManager functionality
 */
async function testApiKeyManager() {
  console.log('\n--- Testing ApiKeyManager ---');
  
  const apiKeyManager = new ApiKeyManager();
  
  // Test API key storage
  console.log('Testing API key storage...');
  const storeResult = apiKeyManager.storeApiKeys('test_user', {
    openai: 'sk-test-openai-key',
    anthropic: 'sk-ant-test-anthropic-key'
  });
  console.assert(storeResult === true, 'API key storage should succeed');
  console.log('✓ API key storage passed');
  
  // Test API key retrieval
  console.log('Testing API key retrieval...');
  const apiKeys = apiKeyManager.getApiKeys('test_user');
  console.assert(apiKeys.openai, 'Should return OpenAI key');
  console.assert(apiKeys.anthropic, 'Should return Anthropic key');
  console.log('✓ API key retrieval passed');
  
  // Test specific API key retrieval
  console.log('Testing specific API key retrieval...');
  const openaiKey = apiKeyManager.getApiKeys('test_user', 'openai');
  console.assert(openaiKey, 'Should return OpenAI key');
  console.log('✓ Specific API key retrieval passed');
  
  // Test API key validation
  console.log('Testing API key validation...');
  const validOpenai = apiKeyManager.validateApiKey('openai', 'sk-test-valid-key-12345678901234567890');
  console.assert(validOpenai === true, 'Should validate correct OpenAI key format');
  
  const invalidOpenai = apiKeyManager.validateApiKey('openai', 'invalid-key');
  console.assert(invalidOpenai === false, 'Should reject incorrect OpenAI key format');
  console.log('✓ API key validation passed');
  
  // Test API key testing
  console.log('Testing API key testing...');
  const testResult = await apiKeyManager.testApiKey('openai', 'sk-test-valid-key-12345678901234567890');
  console.assert(testResult === true, 'Valid key test should succeed');
  
  const invalidTestResult = await apiKeyManager.testApiKey('openai', 'sk-test-invalid-key');
  console.assert(invalidTestResult === false, 'Invalid key test should fail');
  console.log('✓ API key testing passed');
}

/**
 * Test integration between components
 */
async function testComponentIntegration() {
  console.log('\n--- Testing Component Integration ---');
  
  const paymentSystem = new PaymentSystem();
  const subscriptionManager = new SubscriptionManager();
  const apiKeyManager = new ApiKeyManager();
  
  // Initialize all components
  paymentSystem.initialize({
    stripe: { apiKey: 'sk_test_stripe' }
  });
  
  subscriptionManager.initialize({
    stripe: { apiKey: 'sk_test_stripe' }
  });
  
  // Test end-to-end user signup with API keys
  console.log('Testing end-to-end user signup with API keys...');
  try {
    // 1. Sign up user with subscription
    const userData = {
      name: 'Integration Test User',
      email: 'integration@example.com'
    };
    
    const signupResult = subscriptionManager.signUpUser(
      userData,
      'pro',
      true, // Use own API
      { processor: 'stripe' }
    );
    
    const userId = signupResult.userId;
    console.assert(userId, 'Should return a user ID');
    
    // 2. Store API keys for the user
    const storeResult = apiKeyManager.storeApiKeys(userId, {
      openai: 'sk-test-openai-key',
      anthropic: 'sk-ant-test-anthropic-key'
    });
    console.assert(storeResult === true, 'API key storage should succeed');
    
    // 3. Verify subscription details
    const subscription = subscriptionManager.getUserSubscription(userId);
    console.assert(subscription.tier === 'pro', 'Should be pro tier');
    
    // 4. Test model usage with own API
    const modelUsageResult = subscriptionManager.processModelUsage(userId, 'standard');
    console.assert(modelUsageResult === true, 'Model usage should succeed');
    
    // 5. Purchase additional credits
    const purchaseResult = subscriptionManager.purchaseAdditionalCredits(
      userId,
      10000,
      { processor: 'stripe' }
    );
    console.assert(purchaseResult.success === true, 'Credit purchase should succeed');
    
    console.log('✓ End-to-end integration test passed');
  } catch (error) {
    console.error(`✗ Integration test failed: ${error.message}`);
  }
}

// Run all tests
runTests().catch(error => {
  console.error('Test execution failed:', error);
});
