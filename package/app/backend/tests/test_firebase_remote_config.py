"""
Test suite for Firebase Remote Config integration.

This module provides comprehensive tests for the Firebase Remote Config
functionality in Aideon AI Lite.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime, timedelta

# Import the modules to test
from ..firebase_remote_config import FirebaseRemoteConfigManager
from ..feature_flags import FeatureFlagMiddleware, require_feature, feature_enabled

class TestFirebaseRemoteConfigManager(unittest.TestCase):
    """Test cases for FirebaseRemoteConfigManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = FirebaseRemoteConfigManager()
        
        # Mock Firebase dependencies
        self.mock_template = Mock()
        self.mock_template.parameters = {}
    
    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin._apps', [])
    def test_initialize_firebase_success(self, mock_init_app):
        """Test successful Firebase initialization."""
        mock_app = Mock()
        mock_init_app.return_value = mock_app
        
        manager = FirebaseRemoteConfigManager()
        self.assertIsNotNone(manager._app)
    
    @patch('firebase_admin.remote_config.get_template')
    def test_get_remote_config_success(self, mock_get_template):
        """Test successful remote config retrieval."""
        # Mock template with parameters
        mock_param = Mock()
        mock_param.default_value.value = "true"
        
        mock_template = Mock()
        mock_template.parameters = {
            "test_feature_enabled": mock_param,
            "max_requests": Mock()
        }
        mock_template.parameters["max_requests"].default_value.value = "100"
        
        mock_get_template.return_value = mock_template
        
        config = self.manager.get_remote_config(use_cache=False)
        
        self.assertIn("test_feature_enabled", config)
        self.assertEqual(config["test_feature_enabled"], "true")
        self.assertEqual(config["max_requests"], "100")
    
    def test_get_feature_flag_boolean_conversion(self):
        """Test feature flag boolean conversion."""
        # Test with cached data
        self.manager._cache = {
            "feature1_enabled": "true",
            "feature2_enabled": "false",
            "feature3_enabled": True,
            "feature4_enabled": False
        }
        self.manager._cache_timestamp = datetime.now()
        
        self.assertTrue(self.manager.get_feature_flag("feature1"))
        self.assertFalse(self.manager.get_feature_flag("feature2"))
        self.assertTrue(self.manager.get_feature_flag("feature3"))
        self.assertFalse(self.manager.get_feature_flag("feature4"))
    
    def test_get_config_parameter_type_conversion(self):
        """Test configuration parameter type conversion."""
        # Test with cached data
        self.manager._cache = {
            "int_param": "123",
            "float_param": "45.67",
            "string_param": "hello",
            "bool_param": "true"
        }
        self.manager._cache_timestamp = datetime.now()
        
        self.assertEqual(self.manager.get_config_parameter("int_param"), 123)
        self.assertEqual(self.manager.get_config_parameter("float_param"), 45.67)
        self.assertEqual(self.manager.get_config_parameter("string_param"), "hello")
        self.assertEqual(self.manager.get_config_parameter("bool_param"), "true")
    
    def test_cache_validity(self):
        """Test cache validity logic."""
        # Test invalid cache (no timestamp)
        self.manager._cache_timestamp = None
        self.assertFalse(self.manager._is_cache_valid())
        
        # Test valid cache (recent timestamp)
        self.manager._cache_timestamp = datetime.now()
        self.assertTrue(self.manager._is_cache_valid())
        
        # Test expired cache (old timestamp)
        self.manager._cache_timestamp = datetime.now() - timedelta(minutes=10)
        self.assertFalse(self.manager._is_cache_valid())
    
    @patch('firebase_admin.remote_config.get_template')
    @patch('firebase_admin.remote_config.validate_template')
    @patch('firebase_admin.remote_config.publish_template')
    def test_update_remote_config_success(self, mock_publish, mock_validate, mock_get_template):
        """Test successful remote config update."""
        mock_template = Mock()
        mock_template.parameters = {}
        mock_get_template.return_value = mock_template
        mock_validate.return_value = mock_template
        
        updates = {
            "test_feature_enabled": True,
            "max_requests": 200
        }
        
        result = self.manager.update_remote_config(updates)
        
        self.assertTrue(result)
        mock_publish.assert_called_once()
    
    def test_fallback_config(self):
        """Test fallback configuration when remote config fails."""
        fallback = self.manager._get_fallback_config()
        
        # Should contain default feature flags
        self.assertIn("together_ai_enabled", fallback)
        self.assertIn("video_generation_enabled", fallback)
        
        # Should contain default config parameters
        self.assertIn("max_concurrent_requests", fallback)
        self.assertIn("request_timeout_seconds", fallback)
    
    def test_tier_daily_limits(self):
        """Test tier daily limit retrieval."""
        # Mock config data
        self.manager._cache = {
            "free_tier_daily_limit": 50,
            "premium_tier_daily_limit": 1000
        }
        self.manager._cache_timestamp = datetime.now()
        
        self.assertEqual(self.manager.get_tier_daily_limit("free"), 50)
        self.assertEqual(self.manager.get_tier_daily_limit("premium"), 1000)
        self.assertEqual(self.manager.get_tier_daily_limit("unknown"), 50)  # Default

class TestFeatureFlagMiddleware(unittest.TestCase):
    """Test cases for FeatureFlagMiddleware."""
    
    def setUp(self):
        """Set up test fixtures."""
        from flask import Flask
        self.app = Flask(__name__)
        self.middleware = FeatureFlagMiddleware(self.app)
        
        # Mock remote config manager
        self.mock_manager = Mock()
        self.middleware.remote_config_manager = self.mock_manager
    
    def test_before_request_normal_mode(self):
        """Test before_request in normal mode."""
        self.mock_manager.get_remote_config.return_value = {
            "test_feature_enabled": True
        }
        self.mock_manager.is_maintenance_mode.return_value = False
        
        with self.app.test_request_context():
            result = self.middleware.before_request()
            self.assertIsNone(result)  # Should not return anything in normal mode
    
    def test_before_request_maintenance_mode(self):
        """Test before_request in maintenance mode."""
        self.mock_manager.get_remote_config.return_value = {
            "maintenance_mode": True
        }
        self.mock_manager.is_maintenance_mode.return_value = True
        self.mock_manager.get_maintenance_message.return_value = "Under maintenance"
        
        with self.app.test_request_context():
            result = self.middleware.before_request()
            self.assertIsNotNone(result)
            response, status_code = result
            self.assertEqual(status_code, 503)
    
    def test_inject_feature_flags(self):
        """Test feature flag injection into template context."""
        with self.app.test_request_context():
            # Mock g object
            from flask import g
            g.feature_flags = {"test_feature_enabled": True}
            g.is_maintenance_mode = False
            
            context = self.middleware.inject_feature_flags()
            
            self.assertIn("feature_flags", context)
            self.assertIn("is_maintenance_mode", context)
            self.assertEqual(context["feature_flags"]["test_feature_enabled"], True)
            self.assertEqual(context["is_maintenance_mode"], False)

class TestFeatureFlagDecorators(unittest.TestCase):
    """Test cases for feature flag decorators."""
    
    def setUp(self):
        """Set up test fixtures."""
        from flask import Flask
        self.app = Flask(__name__)
        
        # Mock remote config manager
        self.mock_manager = Mock()
        
        # Patch the get_remote_config_manager function
        self.patcher = patch('src.feature_flags.get_remote_config_manager')
        self.mock_get_manager = self.patcher.start()
        self.mock_get_manager.return_value = self.mock_manager
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.patcher.stop()
    
    def test_require_feature_enabled(self):
        """Test require_feature decorator when feature is enabled."""
        self.mock_manager.is_feature_enabled.return_value = True
        
        @require_feature("test_feature")
        def test_endpoint():
            return "success"
        
        with self.app.test_request_context():
            result = test_endpoint()
            self.assertEqual(result, "success")
    
    def test_require_feature_disabled(self):
        """Test require_feature decorator when feature is disabled."""
        self.mock_manager.is_feature_enabled.return_value = False
        
        @require_feature("test_feature")
        def test_endpoint():
            return "success"
        
        with self.app.test_request_context():
            result = test_endpoint()
            response, status_code = result
            self.assertEqual(status_code, 403)
    
    def test_feature_enabled_function(self):
        """Test feature_enabled function."""
        with self.app.test_request_context():
            # Mock g object
            from flask import g
            g.feature_flags = {
                "test_feature_enabled": True,
                "other_feature_enabled": False
            }
            
            self.assertTrue(feature_enabled("test_feature"))
            self.assertFalse(feature_enabled("other_feature"))
            self.assertFalse(feature_enabled("nonexistent_feature"))

class TestRemoteConfigEndpoints(unittest.TestCase):
    """Test cases for remote config API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        from flask import Flask
        from ..api.remote_config_endpoints import remote_config_bp
        
        self.app = Flask(__name__)
        self.app.register_blueprint(remote_config_bp)
        self.client = self.app.test_client()
        
        # Mock remote config manager
        self.mock_manager = Mock()
        
        # Patch the get_remote_config_manager function
        self.patcher = patch('src.api.remote_config_endpoints.get_remote_config_manager')
        self.mock_get_manager = self.patcher.start()
        self.mock_get_manager.return_value = self.mock_manager
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.patcher.stop()
    
    def test_get_feature_flags_success(self):
        """Test successful feature flags retrieval."""
        self.mock_manager.get_remote_config.return_value = {
            "test_feature_enabled": True,
            "other_feature_enabled": False,
            "max_requests": 100
        }
        self.mock_manager.get_cache_info.return_value = {
            "cache_size": 3,
            "cache_valid": True
        }
        
        response = self.client.get('/api/v1/config/feature-flags')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("feature_flags", data)
        self.assertIn("test_feature_enabled", data["feature_flags"])
    
    def test_get_feature_flag_specific(self):
        """Test specific feature flag retrieval."""
        self.mock_manager.is_feature_enabled.return_value = True
        
        response = self.client.get('/api/v1/config/feature-flags/test_feature')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["feature_name"], "test_feature")
        self.assertTrue(data["enabled"])
    
    @patch('src.api.remote_config_endpoints._is_admin_user')
    def test_update_feature_flag_success(self, mock_is_admin):
        """Test successful feature flag update."""
        mock_is_admin.return_value = True
        self.mock_manager.update_remote_config.return_value = True
        
        response = self.client.put(
            '/api/v1/config/feature-flags/test_feature',
            json={"enabled": True},
            headers={"Authorization": "Bearer admin-token"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
    
    @patch('src.api.remote_config_endpoints._is_admin_user')
    def test_update_feature_flag_unauthorized(self, mock_is_admin):
        """Test unauthorized feature flag update."""
        mock_is_admin.return_value = False
        
        response = self.client.put(
            '/api/v1/config/feature-flags/test_feature',
            json={"enabled": True}
        )
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
    
    def test_get_config_status(self):
        """Test configuration status retrieval."""
        self.mock_manager.is_maintenance_mode.return_value = False
        self.mock_manager.get_rate_limit.return_value = 100
        self.mock_manager.get_tier_daily_limit.side_effect = lambda tier: {
            "free": 50,
            "premium": 1000
        }.get(tier, 50)
        self.mock_manager.get_cache_info.return_value = {
            "cache_size": 10,
            "cache_valid": True
        }
        
        response = self.client.get('/api/v1/config/status')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("status", data)
        self.assertFalse(data["status"]["maintenance_mode"])
        self.assertEqual(data["status"]["rate_limit_per_minute"], 100)

if __name__ == '__main__':
    unittest.main()

