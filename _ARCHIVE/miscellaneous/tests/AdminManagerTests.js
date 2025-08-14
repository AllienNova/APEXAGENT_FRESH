/**
 * AdminManagerTests.js
 * Test suite for the admin recognition and payment exemption system
 */

const AdminManager = require('../src/payment/AdminManager');
const PaymentSystem = require('../src/payment/PaymentSystem');
const SubscriptionManager = require('../src/payment/SubscriptionManager');

/**
 * Run all admin manager tests
 */
async function runTests() {
  console.log('=== Running Admin Manager Tests ===');
  
  // Test individual admin manager functionality
  await testAdminRecognition();
  await testAdminPrivileges();
  await testPaymentExemption();
  
  // Test integration with payment system
  await testPaymentSystemIntegration();
  
  console.log('\n=== All tests completed ===');
}

/**
 * Test admin recognition functionality
 */
async function testAdminRecognition() {
  console.log('\n--- Testing Admin Recognition ---');
  
  const adminManager = new AdminManager();
  
  // Test initialization
  console.log('Testing initialization...');
  const initResult = adminManager.initialize();
  console.assert(initResult === true, 'Initialization should succeed');
  
  // Test admin recognition by install key
  console.log('Testing admin recognition by install key...');
  const isAdminByInstallKey = adminManager.isAdmin({
    installKey: 'aideon-admin-install-2025'
  });
  console.assert(isAdminByInstallKey === true, 'Should recognize admin by install key');
  
  // Test admin recognition by GCP project ID
  console.log('Testing admin recognition by GCP project ID...');
  const isAdminByGcp = adminManager.isAdmin({
    gcpProjectId: 'aideon-ai-lite-prod'
  });
  console.assert(isAdminByGcp === true, 'Should recognize admin by GCP project ID');
  
  // Test admin recognition by email domain
  console.log('Testing admin recognition by email domain...');
  const isAdminByEmail = adminManager.isAdmin({
    email: 'admin@aideon.ai'
  });
  console.assert(isAdminByEmail === true, 'Should recognize admin by email domain');
  
  // Test admin recognition by license key
  console.log('Testing admin recognition by license key...');
  const isAdminByLicense = adminManager.isAdmin({
    licenseKey: 'ADMIN-AIDEON-2025-MASTER'
  });
  console.assert(isAdminByLicense === true, 'Should recognize admin by license key');
  
  // Test non-admin recognition
  console.log('Testing non-admin recognition...');
  const isNonAdmin = adminManager.isAdmin({
    email: 'user@example.com',
    installKey: 'regular-user-key'
  });
  console.assert(isNonAdmin === false, 'Should not recognize non-admin');
  
  console.log('✓ Admin recognition tests passed');
}

/**
 * Test admin privileges functionality
 */
async function testAdminPrivileges() {
  console.log('\n--- Testing Admin Privileges ---');
  
  const adminManager = new AdminManager();
  adminManager.initialize();
  
  // Test granting admin privileges
  console.log('Testing granting admin privileges...');
  const privileges = adminManager.grantAdminPrivileges('admin_user_1');
  console.assert(privileges.userId === 'admin_user_1', 'Should grant privileges to correct user');
  console.assert(Array.isArray(privileges.privileges), 'Should return privileges array');
  console.assert(privileges.privileges.includes('payment_exempt'), 'Should include payment exemption');
  
  // Test checking admin privileges
  console.log('Testing checking admin privileges...');
  const hasPrivilege = adminManager.hasAdminPrivilege('admin_user_1', 'payment_exempt');
  console.assert(hasPrivilege === true, 'Admin should have payment exemption privilege');
  
  console.log('✓ Admin privileges tests passed');
}

/**
 * Test payment exemption functionality
 */
async function testPaymentExemption() {
  console.log('\n--- Testing Payment Exemption ---');
  
  const adminManager = new AdminManager();
  adminManager.initialize();
  
  // Test applying payment exemption
  console.log('Testing applying payment exemption...');
  try {
    const exemption = adminManager.applyPaymentExemption('admin@aideon.ai');
    console.assert(exemption.paymentExempt === true, 'Should apply payment exemption');
    console.assert(exemption.expiresAt === null, 'Exemption should never expire for admin');
    console.log('✓ Payment exemption application passed');
  } catch (error) {
    console.error(`✗ Payment exemption application failed: ${error.message}`);
  }
  
  // Test admin detection during installation
  console.log('Testing admin detection during installation...');
  const detectionResult = adminManager.detectAdminDuringSetup({
    installKey: 'aideon-admin-install-2025',
    userId: 'installer_admin'
  });
  
  console.assert(detectionResult.isAdmin === true, 'Should detect admin during installation');
  console.assert(detectionResult.detectionMethod === 'install_key', 'Should detect via install key');
  console.log('✓ Admin detection during installation passed');
}

/**
 * Test integration with payment system
 */
async function testPaymentSystemIntegration() {
  console.log('\n--- Testing Payment System Integration ---');
  
  const adminManager = new AdminManager();
  const paymentSystem = new PaymentSystem();
  const subscriptionManager = new SubscriptionManager();
  
  adminManager.initialize();
  paymentSystem.initialize({
    stripe: { apiKey: 'sk_test_stripe' }
  });
  subscriptionManager.initialize({
    stripe: { apiKey: 'sk_test_stripe' }
  });
  
  // Test end-to-end admin exemption flow
  console.log('Testing end-to-end admin exemption flow...');
  
  try {
    // 1. Detect admin during installation
    const adminData = adminManager.detectAdminDuringSetup({
      installKey: 'aideon-admin-install-2025',
      email: 'admin@aideon.ai',
      userId: 'admin_user_test'
    });
    
    console.assert(adminData.isAdmin === true, 'Should detect admin status');
    
    // 2. Create admin user with subscription (would normally cost money)
    const userData = {
      name: 'Admin User',
      email: 'admin@aideon.ai'
    };
    
    // 3. Apply admin exemption to subscription
    const exemption = adminManager.applyPaymentExemption(adminData.userId);
    console.assert(exemption.paymentExempt === true, 'Should apply payment exemption');
    
    // 4. Verify admin can access all features without payment
    const hasExpertFeatures = adminManager.hasAdminPrivilege(adminData.userId, 'payment_exempt');
    console.assert(hasExpertFeatures === true, 'Admin should have access to all features');
    
    console.log('✓ End-to-end admin exemption flow passed');
  } catch (error) {
    console.error(`✗ Admin exemption flow failed: ${error.message}`);
  }
  
  // Test admin dashboard access
  console.log('Testing admin dashboard access...');
  try {
    const dashboardData = adminManager.getAdminDashboardData('admin_user_test');
    console.assert(dashboardData.activeUsers > 0, 'Should return dashboard data');
    console.assert(typeof dashboardData.totalRevenue === 'number', 'Should include revenue data');
    console.log('✓ Admin dashboard access passed');
  } catch (error) {
    console.error(`✗ Admin dashboard access failed: ${error.message}`);
  }
}

// Run all tests
runTests().catch(error => {
  console.error('Test execution failed:', error);
});
