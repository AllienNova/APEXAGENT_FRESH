"""
Test module for pricing and credit logic in ApexAgent.

This module tests the pricing model, user API threshold policy, and credit allocation
logic for all subscription tiers and user scenarios.
"""

import unittest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime, timedelta

from src.billing.subscription import SubscriptionManager, SubscriptionTier, LicenseType, InstitutionType
from src.billing.api_key_manager import ApiKeyManager, ProviderType, ModelCategory
from src.billing.credit_manager import CreditManager, CreditOperationType


class MockDatabase:
    """Mock database connector for testing."""
    
    def __init__(self):
        self.subscriptions = {}
        self.enterprise_subscriptions = {}
        self.api_keys = {}
        self.credit_operations = []
        self.enterprise_credit_operations = []
        self.alerts = {}
        self.enterprise_alerts = {}
    
    def insert_subscription(self, data):
        subscription_id = f"sub_{len(self.subscriptions) + 1}"
        self.subscriptions[subscription_id] = {**data, "id": subscription_id}
        return subscription_id
    
    def insert_enterprise_subscription(self, data):
        subscription_id = f"ent_sub_{len(self.enterprise_subscriptions) + 1}"
        self.enterprise_subscriptions[subscription_id] = {**data, "id": subscription_id}
        return subscription_id
    
    def get_active_subscription(self, user_id):
        for sub_id, sub in self.subscriptions.items():
            if sub.get("user_id") == user_id and sub.get("status") == "active":
                return sub
        return None
    
    def get_active_enterprise_subscription(self, organization_id):
        for sub_id, sub in self.enterprise_subscriptions.items():
            if sub.get("organization_id") == organization_id and sub.get("status") == "active":
                return sub
        return None
    
    def get_subscription(self, subscription_id):
        return self.subscriptions.get(subscription_id)
    
    def update_subscription(self, subscription_id, updates):
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].update(updates)
            return True
        return False
    
    def update_enterprise_subscription(self, subscription_id, updates):
        if subscription_id in self.enterprise_subscriptions:
            self.enterprise_subscriptions[subscription_id].update(updates)
            return True
        return False
    
    def log_credit_purchase(self, data):
        self.credit_operations.append({**data, "type": "purchase"})
    
    def log_credit_usage(self, data):
        self.credit_operations.append({**data, "type": "usage"})
    
    def log_credit_operation(self, data):
        self.credit_operations.append(data)
    
    def log_enterprise_credit_operation(self, data):
        self.enterprise_credit_operations.append(data)
    
    def insert_api_key(self, data):
        key_id = data.get("key_id", f"key_{len(self.api_keys) + 1}")
        self.api_keys[key_id] = {**data, "id": key_id}
        return key_id
    
    def get_user_api_keys(self, user_id):
        return [key for key in self.api_keys.values() if key.get("user_id") == user_id]
    
    def get_api_key(self, key_id):
        return self.api_keys.get(key_id)
    
    def get_valid_api_keys(self, user_id, provider):
        return [key for key in self.api_keys.values() 
                if key.get("user_id") == user_id and 
                key.get("provider") == provider and 
                key.get("is_valid", False)]
    
    def update_api_key(self, key_id, updates):
        if key_id in self.api_keys:
            self.api_keys[key_id].update(updates)
            return True
        return False
    
    def has_sent_alert(self, user_id, alert_key):
        return self.alerts.get(f"{user_id}:{alert_key}", False)
    
    def mark_alert_sent(self, user_id, alert_key):
        self.alerts[f"{user_id}:{alert_key}"] = True
    
    def has_sent_enterprise_alert(self, organization_id, alert_key):
        return self.enterprise_alerts.get(f"{organization_id}:{alert_key}", False)
    
    def mark_enterprise_alert_sent(self, organization_id, alert_key):
        self.enterprise_alerts[f"{organization_id}:{alert_key}"] = True


class TestPricingModel(unittest.TestCase):
    """Test cases for the pricing model."""
    
    def setUp(self):
        self.db = MockDatabase()
        self.subscription_manager = SubscriptionManager(self.db)
    
    def test_basic_tier_pricing(self):
        """Test pricing for Basic tier."""
        # Test monthly pricing
        price = self.subscription_manager._calculate_subscription_price(
            SubscriptionTier.BASIC, False, False)
        self.assertEqual(price, 24.99)
        
        # Test annual pricing (17% discount)
        price = self.subscription_manager._calculate_subscription_price(
            SubscriptionTier.BASIC, True, False)
        self.assertAlmostEqual(price, 24.99 * 12 * 0.83, places=2)
        
        # Test user-provided API keys pricing
        price = self.subscription_manager._calculate_subscription_price(
            SubscriptionTier.BASIC, False, True)
        self.assertEqual(price, 19.99)
    
    def test_pro_tier_pricing(self):
        """Test pricing for Pro tier."""
        # Test monthly pricing
        price = self.subscription_manager._calculate_subscription_price(
            SubscriptionTier.PRO, False, False)
        self.assertEqual(price, 89.99)
        
        # Test annual pricing (17% discount)
        price = self.subscription_manager._calculate_subscription_price(
            SubscriptionTier.PRO, True, False)
        self.assertAlmostEqual(price, 89.99 * 12 * 0.83, places=2)
        
        # Test user-provided API keys pricing
        price = self.subscription_manager._calculate_subscription_price(
            SubscriptionTier.PRO, False, True)
        self.assertEqual(price, 49.99)
    
    def test_expert_tier_pricing(self):
        """Test pricing for Expert tier."""
        # Test monthly pricing
        price = self.subscription_manager._calculate_subscription_price(
            SubscriptionTier.EXPERT, False, False)
        self.assertEqual(price, 149.99)
        
        # Test annual pricing (17% discount)
        price = self.subscription_manager._calculate_subscription_price(
            SubscriptionTier.EXPERT, True, False)
        self.assertAlmostEqual(price, 149.99 * 12 * 0.83, places=2)
        
        # Test user-provided API keys pricing
        price = self.subscription_manager._calculate_subscription_price(
            SubscriptionTier.EXPERT, False, True)
        self.assertEqual(price, 99.99)
    
    def test_enterprise_per_seat_pricing(self):
        """Test per-seat pricing for Enterprise tier."""
        # Small team (5-20 users)
        price = self.subscription_manager._calculate_per_seat_price(10)
        self.assertEqual(price, 79.0 * 10)
        
        # Medium team (21-100 users)
        price = self.subscription_manager._calculate_per_seat_price(50)
        self.assertEqual(price, 69.0 * 50)
        
        # Large team (101-500 users)
        price = self.subscription_manager._calculate_per_seat_price(200)
        self.assertEqual(price, 59.0 * 200)
        
        # With education discount (35%)
        price = self.subscription_manager._calculate_per_seat_price(
            50, InstitutionType.EDUCATION)
        self.assertEqual(price, 69.0 * 50 * 0.65)
    
    def test_enterprise_per_device_pricing(self):
        """Test per-device pricing for Enterprise tier."""
        # Standard deployment
        price = self.subscription_manager._calculate_per_device_price(10, "standard")
        self.assertEqual(price, 129.0 * 10)
        
        # High-usage deployment
        price = self.subscription_manager._calculate_per_device_price(10, "high_usage")
        self.assertEqual(price, 189.0 * 10)
        
        # Shared device
        price = self.subscription_manager._calculate_per_device_price(10, "shared")
        self.assertEqual(price, 259.0 * 10)
    
    def test_enterprise_site_license_pricing(self):
        """Test site license pricing for Enterprise tier."""
        # Small institution (up to 500 users)
        price = self.subscription_manager._calculate_site_license_price(400)
        self.assertEqual(price, 18000.0)
        
        # Medium institution (501-2000 users)
        price = self.subscription_manager._calculate_site_license_price(1500)
        self.assertEqual(price, 39000.0)
        
        # Large institution (2001-10000 users)
        price = self.subscription_manager._calculate_site_license_price(5000)
        self.assertEqual(price, 79000.0)
        
        # With education discount (35%)
        price = self.subscription_manager._calculate_site_license_price(
            1500, InstitutionType.EDUCATION)
        self.assertEqual(price, 39000.0 * 0.65)
    
    def test_enterprise_credit_allocation(self):
        """Test credit allocation for Enterprise tier."""
        # Per-seat licensing
        credits = self.subscription_manager._calculate_enterprise_credits(
            LicenseType.PER_SEAT, 100)
        self.assertEqual(credits, 100 * 10000)
        
        # Per-device licensing
        credits = self.subscription_manager._calculate_enterprise_credits(
            LicenseType.PER_DEVICE, 100)
        self.assertEqual(credits, 100 * 7500)
        
        # Site license
        credits = self.subscription_manager._calculate_enterprise_credits(
            LicenseType.SITE_LICENSE, 1000)
        self.assertEqual(credits, 500000 + (1000 * 1000))
    
    def test_subscription_creation(self):
        """Test subscription creation."""
        # Create a Basic subscription
        subscription = self.subscription_manager.create_subscription(
            "user1", SubscriptionTier.BASIC, "payment1")
        
        self.assertEqual(subscription["tier"], SubscriptionTier.BASIC.value)
        self.assertEqual(subscription["price"], 24.99)
        self.assertEqual(subscription["credits_remaining"], 2000)
        self.assertEqual(subscription["user_api_keys"], False)
        
        # Create a Pro subscription with user API keys
        subscription = self.subscription_manager.create_subscription(
            "user2", SubscriptionTier.PRO, "payment2", user_api_keys=True)
        
        self.assertEqual(subscription["tier"], SubscriptionTier.PRO.value)
        self.assertEqual(subscription["price"], 49.99)
        self.assertEqual(subscription["credits_remaining"], 5000)
        self.assertEqual(subscription["user_api_keys"], True)
    
    def test_enterprise_subscription_creation(self):
        """Test enterprise subscription creation."""
        # Create a per-seat enterprise subscription
        subscription = self.subscription_manager.create_enterprise_subscription(
            "org1", LicenseType.PER_SEAT, seats=50)
        
        self.assertEqual(subscription["tier"], SubscriptionTier.ENTERPRISE.value)
        self.assertEqual(subscription["license_type"], LicenseType.PER_SEAT.value)
        self.assertEqual(subscription["price"], 69.0 * 50)
        self.assertEqual(subscription["credits_allocated"], 50 * 10000)
        
        # Create a per-device enterprise subscription
        subscription = self.subscription_manager.create_enterprise_subscription(
            "org2", LicenseType.PER_DEVICE, devices=20, device_type="high_usage")
        
        self.assertEqual(subscription["tier"], SubscriptionTier.ENTERPRISE.value)
        self.assertEqual(subscription["license_type"], LicenseType.PER_DEVICE.value)
        self.assertEqual(subscription["price"], 189.0 * 20)
        self.assertEqual(subscription["credits_allocated"], 20 * 7500)
        
        # Create a site license enterprise subscription
        subscription = self.subscription_manager.create_enterprise_subscription(
            "org3", LicenseType.SITE_LICENSE, institution_type=InstitutionType.EDUCATION,
            potential_users=1500)
        
        self.assertEqual(subscription["tier"], SubscriptionTier.ENTERPRISE.value)
        self.assertEqual(subscription["license_type"], LicenseType.SITE_LICENSE.value)
        self.assertEqual(subscription["price"], 39000.0 * 0.65)
        self.assertEqual(subscription["credits_allocated"], 500000 + (1500 * 1000))


class TestApiKeyManager(unittest.TestCase):
    """Test cases for the API key manager."""
    
    def setUp(self):
        self.db = MockDatabase()
        self.api_key_manager = ApiKeyManager(self.db, b"test_encryption_key_12345678901234567890")
    
    def test_add_api_key(self):
        """Test adding an API key."""
        # Add an OpenAI API key
        key_record = self.api_key_manager.add_api_key(
            "user1", ProviderType.OPENAI, "sk-test12345")
        
        self.assertEqual(key_record["user_id"], "user1")
        self.assertEqual(key_record["provider"], ProviderType.OPENAI.value)
        self.assertEqual(key_record["is_valid"], True)
        self.assertNotIn("encrypted_key", key_record)
        
        # Add an Anthropic API key
        key_record = self.api_key_manager.add_api_key(
            "user1", ProviderType.ANTHROPIC, "test12345")
        
        self.assertEqual(key_record["user_id"], "user1")
        self.assertEqual(key_record["provider"], ProviderType.ANTHROPIC.value)
        self.assertEqual(key_record["is_valid"], True)
        self.assertNotIn("encrypted_key", key_record)
    
    def test_get_api_keys(self):
        """Test getting API keys for a user."""
        # Add two API keys for a user
        self.api_key_manager.add_api_key("user1", ProviderType.OPENAI, "sk-test12345")
        self.api_key_manager.add_api_key("user1", ProviderType.ANTHROPIC, "test12345")
        
        # Get the keys
        keys = self.api_key_manager.get_api_keys("user1")
        
        self.assertEqual(len(keys), 2)
        self.assertEqual(keys[0]["provider"], ProviderType.OPENAI.value)
        self.assertEqual(keys[1]["provider"], ProviderType.ANTHROPIC.value)
    
    def test_get_model_category(self):
        """Test getting model category."""
        # Standard models
        category = self.api_key_manager.get_model_category(
            ProviderType.OPENAI, "gpt-3.5-turbo")
        self.assertEqual(category, ModelCategory.STANDARD)
        
        category = self.api_key_manager.get_model_category(
            ProviderType.ANTHROPIC, "claude-instant-1")
        self.assertEqual(category, ModelCategory.STANDARD)
        
        # High reasoning models
        category = self.api_key_manager.get_model_category(
            ProviderType.OPENAI, "gpt-4")
        self.assertEqual(category, ModelCategory.HIGH_REASONING)
        
        category = self.api_key_manager.get_model_category(
            ProviderType.ANTHROPIC, "claude-3-opus")
        self.assertEqual(category, ModelCategory.HIGH_REASONING)
    
    def test_check_user_has_access_to_model(self):
        """Test checking if a user has access to a model."""
        # Add an OpenAI API key
        self.api_key_manager.add_api_key("user1", ProviderType.OPENAI, "sk-test12345")
        
        # Check access to OpenAI model
        has_access = self.api_key_manager.check_user_has_access_to_model(
            "user1", ProviderType.OPENAI, "gpt-4")
        self.assertTrue(has_access)
        
        # Check access to Anthropic model (should be False)
        has_access = self.api_key_manager.check_user_has_access_to_model(
            "user1", ProviderType.ANTHROPIC, "claude-3-opus")
        self.assertFalse(has_access)


class TestCreditManager(unittest.TestCase):
    """Test cases for the credit manager."""
    
    def setUp(self):
        self.db = MockDatabase()
        self.subscription_manager = SubscriptionManager(self.db)
        self.api_key_manager = ApiKeyManager(self.db, b"test_encryption_key_12345678901234567890")
        self.credit_manager = CreditManager(self.db, self.subscription_manager, self.api_key_manager)
        
        # Create a test subscription
        self.subscription = self.subscription_manager.create_subscription(
            "user1", SubscriptionTier.BASIC, "payment1")
        
        # Create a test subscription with user API keys
        self.subscription_with_api_keys = self.subscription_manager.create_subscription(
            "user2", SubscriptionTier.PRO, "payment2", user_api_keys=True)
        
        # Add API keys for user2
        self.openai_key = self.api_key_manager.add_api_key(
            "user2", ProviderType.OPENAI, "sk-test12345")
        
        # Create a test enterprise subscription
        self.enterprise_subscription = self.subscription_manager.create_enterprise_subscription(
            "org1", LicenseType.PER_SEAT, seats=10)
    
    def test_calculate_llm_operation_cost(self):
        """Test calculating LLM operation cost."""
        # Standard model
        cost = self.credit_manager.calculate_llm_operation_cost(
            ProviderType.OPENAI, "gpt-3.5-turbo", 1000)
        self.assertEqual(cost, 1.0)
        
        # High reasoning model
        cost = self.credit_manager.calculate_llm_operation_cost(
            ProviderType.OPENAI, "gpt-4", 1000)
        self.assertEqual(cost, 3.0)
        
        # Different token count
        cost = self.credit_manager.calculate_llm_operation_cost(
            ProviderType.OPENAI, "gpt-3.5-turbo", 2000)
        self.assertEqual(cost, 2.0)
    
    def test_process_llm_operation_without_user_api_keys(self):
        """Test processing LLM operation without user API keys."""
        # Process operation for user1 (no API keys)
        success, credits_deducted = self.credit_manager.process_llm_operation(
            "user1", ProviderType.OPENAI, "gpt-3.5-turbo", 1000, {})
        
        self.assertTrue(success)
        self.assertTrue(credits_deducted)
        
        # Check credit deduction
        subscription = self.subscription_manager.get_subscription("user1")
        self.assertEqual(subscription["credits_remaining"], 2000 - 1.0)
        
        # Check operation log
        self.assertEqual(len(self.db.credit_operations), 2)  # 1 for deduction, 1 for log
        log_entry = self.db.credit_operations[-1]
        self.assertEqual(log_entry["operation_type"], CreditOperationType.LLM_API_CALL.value)
        self.assertEqual(log_entry["credits_used"], 1.0)
        self.assertEqual(json.loads(log_entry["details"])["user_api_key"], False)
    
    @patch.object(ApiKeyManager, 'get_api_key_for_request')
    @patch.object(ApiKeyManager, 'check_user_has_access_to_model')
    def test_process_llm_operation_with_user_api_keys(self, mock_check_access, mock_get_key):
        """Test processing LLM operation with user API keys."""
        # Mock API key access
        mock_check_access.return_value = True
        mock_get_key.return_value = ("sk-test12345", True)
        
        # Process operation for user2 (with API keys)
        success, credits_deducted = self.credit_manager.process_llm_operation(
            "user2", ProviderType.OPENAI, "gpt-3.5-turbo", 1000, {})
        
        self.assertTrue(success)
        self.assertFalse(credits_deducted)
        
        # Check credit deduction (should be unchanged)
        subscription = self.subscription_manager.get_subscription("user2")
        self.assertEqual(subscription["credits_remaining"], 5000)
        
        # Check operation log
        log_entry = self.db.credit_operations[-1]
        self.assertEqual(log_entry["operation_type"], CreditOperationType.LLM_API_CALL.value)
        self.assertEqual(log_entry["credits_used"], 0)
        self.assertEqual(json.loads(log_entry["details"])["user_api_key"], True)
    
    @patch.object(ApiKeyManager, 'get_api_key_for_request')
    @patch.object(ApiKeyManager, 'check_user_has_access_to_model')
    def test_process_llm_operation_fallback_to_apex_api(self, mock_check_access, mock_get_key):
        """Test processing LLM operation with fallback to ApexAgent API."""
        # Mock API key access (user has API keys but not for this model)
        mock_check_access.return_value = False
        mock_get_key.return_value = (None, False)
        
        # Process operation for user2 (with API keys but not for this model)
        success, credits_deducted = self.credit_manager.process_llm_operation(
            "user2", ProviderType.ANTHROPIC, "claude-3-opus", 1000, {})
        
        self.assertTrue(success)
        self.assertTrue(credits_deducted)
        
        # Check credit deduction
        subscription = self.subscription_manager.get_subscription("user2")
        self.assertEqual(subscription["credits_remaining"], 5000 - 3.0)
        
        # Check operation log
        log_entry = self.db.credit_operations[-1]
        self.assertEqual(log_entry["operation_type"], CreditOperationType.LLM_API_CALL.value)
        self.assertEqual(log_entry["credits_used"], 3.0)
        self.assertEqual(json.loads(log_entry["details"])["user_api_key"], False)
    
    def test_process_operation(self):
        """Test processing general operations."""
        # Process document operation
        success = self.credit_manager.process_operation(
            "user1", CreditOperationType.DOCUMENT_PROCESSING, {"size_mb": 2})
        
        self.assertTrue(success)
        
        # Check credit deduction
        subscription = self.subscription_manager.get_subscription("user1")
        self.assertEqual(subscription["credits_remaining"], 2000 - 4.0)  # 2.0 * 2
        
        # Process code execution operation
        success = self.credit_manager.process_operation(
            "user1", CreditOperationType.CODE_EXECUTION, {"execution_time_sec": 20})
        
        self.assertTrue(success)
        
        # Check credit deduction
        subscription = self.subscription_manager.get_subscription("user1")
        self.assertEqual(subscription["credits_remaining"], 2000 - 4.0 - 10.0)  # 5.0 * 2
    
    def test_process_enterprise_operation(self):
        """Test processing enterprise operations."""
        # Process LLM operation
        success = self.credit_manager.process_enterprise_operation(
            "org1", CreditOperationType.LLM_API_CALL, {
                "provider": ProviderType.OPENAI.value,
                "model": "gpt-4",
                "tokens": 1000
            })
        
        self.assertTrue(success)
        
        # Check credit deduction
        subscription = self.subscription_manager.get_enterprise_subscription("org1")
        self.assertEqual(subscription["credits_used"], 3.0)
        
        # Process document operation
        success = self.credit_manager.process_enterprise_operation(
            "org1", CreditOperationType.DOCUMENT_PROCESSING, {"size_mb": 5})
        
        self.assertTrue(success)
        
        # Check credit deduction
        subscription = self.subscription_manager.get_enterprise_subscription("org1")
        self.assertEqual(subscription["credits_used"], 3.0 + 10.0)  # 2.0 * 5
    
    def test_credit_usage_forecast(self):
        """Test credit usage forecasting."""
        # Add some usage history
        for i in range(10):
            self.credit_manager.process_llm_operation(
                "user1", ProviderType.OPENAI, "gpt-3.5-turbo", 1000, {})
        
        # Get forecast
        forecast = self.credit_manager.get_credit_usage_forecast("user1")
        
        self.assertGreater(forecast["forecast"], 0)
        self.assertGreater(forecast["avg_daily_usage"], 0)
        self.assertGreater(forecast["days_until_depletion"], 0)


if __name__ == "__main__":
    unittest.main()
