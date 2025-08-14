#!/usr/bin/env python3
"""
Test suite for the Localization Framework.

This module provides comprehensive tests for the localization framework
components of the ApexAgent system.
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import threading
import time
import datetime
import locale

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from localization.localization_framework import (
    LocalizationSystem, LocalizationConfig, Language, TranslationProvider,
    TranslationMemory, LocaleManager, MessageFormatter, ResourceBundle,
    TranslationEntry, LocalizationContext
)

class TestLocalizationSystem(unittest.TestCase):
    """Test cases for the LocalizationSystem class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = LocalizationConfig(
            enabled=True,
            data_directory=self.temp_dir,
            default_language=Language.ENGLISH,
            supported_languages=[
                Language.ENGLISH,
                Language.SPANISH,
                Language.FRENCH,
                Language.GERMAN,
                Language.JAPANESE
            ],
            auto_detect_language=True,
            fallback_language=Language.ENGLISH,
            translation_memory_enabled=True,
            external_provider_enabled=False
        )
        self.localization_system = LocalizationSystem.get_instance()
        self.localization_system.initialize(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.localization_system.shutdown()
    
    def test_singleton_pattern(self):
        """Test that the localization system follows the singleton pattern."""
        instance1 = LocalizationSystem.get_instance()
        instance2 = LocalizationSystem.get_instance()
        self.assertIs(instance1, instance2)
    
    def test_register_resource_bundle(self):
        """Test registering a resource bundle."""
        # Create a bundle
        bundle = ResourceBundle(
            bundle_id="common",
            language=Language.ENGLISH,
            translations={
                "welcome": "Welcome to the application",
                "goodbye": "Goodbye",
                "error.notfound": "Resource not found"
            }
        )
        
        # Register the bundle
        self.localization_system.register_resource_bundle(bundle)
        
        # Verify bundle was registered
        registered_bundle = self.localization_system.get_resource_bundle("common", Language.ENGLISH)
        self.assertEqual(registered_bundle, bundle)
    
    def test_get_translation(self):
        """Test getting a translation."""
        # Register bundles for different languages
        english_bundle = ResourceBundle(
            bundle_id="common",
            language=Language.ENGLISH,
            translations={
                "welcome": "Welcome to the application",
                "goodbye": "Goodbye"
            }
        )
        
        spanish_bundle = ResourceBundle(
            bundle_id="common",
            language=Language.SPANISH,
            translations={
                "welcome": "Bienvenido a la aplicación",
                "goodbye": "Adiós"
            }
        )
        
        self.localization_system.register_resource_bundle(english_bundle)
        self.localization_system.register_resource_bundle(spanish_bundle)
        
        # Get translation in English
        with patch.object(self.localization_system, 'get_current_language') as mock_get_language:
            mock_get_language.return_value = Language.ENGLISH
            
            translation = self.localization_system.get_translation("common", "welcome")
            self.assertEqual(translation, "Welcome to the application")
        
        # Get translation in Spanish
        with patch.object(self.localization_system, 'get_current_language') as mock_get_language:
            mock_get_language.return_value = Language.SPANISH
            
            translation = self.localization_system.get_translation("common", "welcome")
            self.assertEqual(translation, "Bienvenido a la aplicación")
    
    def test_get_translation_with_fallback(self):
        """Test getting a translation with fallback to default language."""
        # Register bundle for English only
        english_bundle = ResourceBundle(
            bundle_id="common",
            language=Language.ENGLISH,
            translations={
                "welcome": "Welcome to the application",
                "goodbye": "Goodbye"
            }
        )
        
        self.localization_system.register_resource_bundle(english_bundle)
        
        # Get translation in French (not available, should fall back to English)
        with patch.object(self.localization_system, 'get_current_language') as mock_get_language:
            mock_get_language.return_value = Language.FRENCH
            
            translation = self.localization_system.get_translation("common", "welcome")
            self.assertEqual(translation, "Welcome to the application")
    
    def test_get_translation_with_parameters(self):
        """Test getting a translation with parameter substitution."""
        # Register bundle with parameterized messages
        bundle = ResourceBundle(
            bundle_id="common",
            language=Language.ENGLISH,
            translations={
                "welcome.user": "Welcome, {username}!",
                "items.count": "You have {count} items in your cart.",
                "price.format": "The price is {price, number, currency}."
            }
        )
        
        self.localization_system.register_resource_bundle(bundle)
        
        # Get translation with parameters
        with patch.object(self.localization_system, 'get_current_language') as mock_get_language:
            mock_get_language.return_value = Language.ENGLISH
            
            # Simple parameter
            translation = self.localization_system.get_translation(
                "common", "welcome.user", {"username": "John"}
            )
            self.assertEqual(translation, "Welcome, John!")
            
            # Numeric parameter
            translation = self.localization_system.get_translation(
                "common", "items.count", {"count": 5}
            )
            self.assertEqual(translation, "You have 5 items in your cart.")
    
    def test_set_language(self):
        """Test setting the current language."""
        # Set language
        self.localization_system.set_language(Language.GERMAN)
        
        # Verify language was set
        self.assertEqual(self.localization_system.get_current_language(), Language.GERMAN)
    
    def test_detect_language(self):
        """Test detecting language from system locale."""
        with patch('locale.getdefaultlocale') as mock_locale:
            # Mock locale to return German
            mock_locale.return_value = ('de_DE', 'UTF-8')
            
            # Detect language
            detected = self.localization_system.detect_language()
            
            # Verify detected language
            self.assertEqual(detected, Language.GERMAN)
            
            # Mock locale to return unsupported language
            mock_locale.return_value = ('ru_RU', 'UTF-8')
            
            # Detect language (should fall back to default)
            detected = self.localization_system.detect_language()
            
            # Verify detected language
            self.assertEqual(detected, Language.ENGLISH)  # Default language
    
    @patch('localization.localization_framework.os.path.exists')
    @patch('localization.localization_framework.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_translations(self, mock_file, mock_makedirs, mock_exists):
        """Test exporting translations."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Register bundle
        bundle = ResourceBundle(
            bundle_id="common",
            language=Language.ENGLISH,
            translations={
                "welcome": "Welcome to the application",
                "goodbye": "Goodbye"
            }
        )
        self.localization_system.register_resource_bundle(bundle)
        
        # Export translations
        export_path = self.localization_system.export_translations(
            bundle_id="common",
            language=Language.ENGLISH,
            format="json",
            output_path=os.path.join(self.temp_dir, "common_en.json")
        )
        
        # Verify export
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        self.assertTrue(export_path.endswith("common_en.json"))
    
    @patch('localization.localization_framework.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_import_translations(self, mock_file, mock_exists):
        """Test importing translations."""
        # Mock path exists
        mock_exists.return_value = True
        
        # Mock file content
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps({
            "welcome": "Welcome to the application",
            "goodbye": "Goodbye"
        })
        
        # Import translations
        bundle = self.localization_system.import_translations(
            bundle_id="common",
            language=Language.ENGLISH,
            format="json",
            input_path=os.path.join(self.temp_dir, "common_en.json")
        )
        
        # Verify import
        self.assertEqual(bundle.bundle_id, "common")
        self.assertEqual(bundle.language, Language.ENGLISH)
        self.assertEqual(len(bundle.translations), 2)
        self.assertEqual(bundle.translations["welcome"], "Welcome to the application")
        self.assertEqual(bundle.translations["goodbye"], "Goodbye")

class TestResourceBundle(unittest.TestCase):
    """Test cases for the ResourceBundle class."""
    
    def test_bundle_creation(self):
        """Test creating a resource bundle."""
        bundle = ResourceBundle(
            bundle_id="common",
            language=Language.ENGLISH,
            translations={
                "welcome": "Welcome to the application",
                "goodbye": "Goodbye",
                "error.notfound": "Resource not found"
            },
            region="US"
        )
        
        self.assertEqual(bundle.bundle_id, "common")
        self.assertEqual(bundle.language, Language.ENGLISH)
        self.assertEqual(bundle.region, "US")
        self.assertEqual(len(bundle.translations), 3)
        self.assertEqual(bundle.translations["welcome"], "Welcome to the application")
        self.assertEqual(bundle.translations["goodbye"], "Goodbye")
        self.assertEqual(bundle.translations["error.notfound"], "Resource not found")
    
    def test_add_translation(self):
        """Test adding a translation to a bundle."""
        bundle = ResourceBundle(
            bundle_id="common",
            language=Language.ENGLISH
        )
        
        bundle.add_translation("welcome", "Welcome to the application")
        
        self.assertEqual(len(bundle.translations), 1)
        self.assertEqual(bundle.translations["welcome"], "Welcome to the application")
    
    def test_get_translation(self):
        """Test getting a translation from a bundle."""
        bundle = ResourceBundle(
            bundle_id="common",
            language=Language.ENGLISH,
            translations={
                "welcome": "Welcome to the application",
                "goodbye": "Goodbye"
            }
        )
        
        # Get existing translation
        translation = bundle.get_translation("welcome")
        self.assertEqual(translation, "Welcome to the application")
        
        # Get non-existent translation
        translation = bundle.get_translation("not.exists")
        self.assertIsNone(translation)
    
    def test_to_dict(self):
        """Test converting bundle to dictionary."""
        bundle = ResourceBundle(
            bundle_id="common",
            language=Language.ENGLISH,
            translations={
                "welcome": "Welcome to the application",
                "goodbye": "Goodbye"
            },
            region="US"
        )
        
        bundle_dict = bundle.to_dict()
        
        self.assertEqual(bundle_dict["bundle_id"], "common")
        self.assertEqual(bundle_dict["language"], "en")
        self.assertEqual(bundle_dict["region"], "US")
        self.assertEqual(len(bundle_dict["translations"]), 2)
        self.assertEqual(bundle_dict["translations"]["welcome"], "Welcome to the application")
        self.assertEqual(bundle_dict["translations"]["goodbye"], "Goodbye")
    
    def test_from_dict(self):
        """Test creating bundle from dictionary."""
        bundle_dict = {
            "bundle_id": "common",
            "language": "en",
            "region": "US",
            "translations": {
                "welcome": "Welcome to the application",
                "goodbye": "Goodbye"
            }
        }
        
        bundle = ResourceBundle.from_dict(bundle_dict)
        
        self.assertEqual(bundle.bundle_id, "common")
        self.assertEqual(bundle.language, Language.ENGLISH)
        self.assertEqual(bundle.region, "US")
        self.assertEqual(len(bundle.translations), 2)
        self.assertEqual(bundle.translations["welcome"], "Welcome to the application")
        self.assertEqual(bundle.translations["goodbye"], "Goodbye")

class TestMessageFormatter(unittest.TestCase):
    """Test cases for the MessageFormatter class."""
    
    def setUp(self):
        """Set up test environment."""
        self.formatter = MessageFormatter()
    
    def test_format_message_simple(self):
        """Test formatting a simple message with parameters."""
        message = "Hello, {name}!"
        params = {"name": "John"}
        
        formatted = self.formatter.format_message(message, params)
        
        self.assertEqual(formatted, "Hello, John!")
    
    def test_format_message_multiple_params(self):
        """Test formatting a message with multiple parameters."""
        message = "Hello, {first_name} {last_name}!"
        params = {"first_name": "John", "last_name": "Doe"}
        
        formatted = self.formatter.format_message(message, params)
        
        self.assertEqual(formatted, "Hello, John Doe!")
    
    def test_format_message_missing_param(self):
        """Test formatting a message with a missing parameter."""
        message = "Hello, {name}!"
        params = {}
        
        formatted = self.formatter.format_message(message, params)
        
        # Should keep the placeholder
        self.assertEqual(formatted, "Hello, {name}!")
    
    def test_format_message_with_number(self):
        """Test formatting a message with number formatting."""
        message = "You have {count, number} items."
        params = {"count": 1234}
        
        with patch.object(self.formatter, '_format_number') as mock_format:
            mock_format.return_value = "1,234"
            
            formatted = self.formatter.format_message(message, params)
            
            self.assertEqual(formatted, "You have 1,234 items.")
            mock_format.assert_called_once_with(1234, None)
    
    def test_format_message_with_date(self):
        """Test formatting a message with date formatting."""
        message = "Today is {date, date, short}."
        params = {"date": datetime.date(2023, 1, 15)}
        
        with patch.object(self.formatter, '_format_date') as mock_format:
            mock_format.return_value = "1/15/23"
            
            formatted = self.formatter.format_message(message, params)
            
            self.assertEqual(formatted, "Today is 1/15/23.")
            mock_format.assert_called_once_with(datetime.date(2023, 1, 15), "short")
    
    def test_format_number(self):
        """Test formatting a number."""
        # Integer
        formatted = self.formatter._format_number(1234, None)
        self.assertEqual(formatted, "1,234")
        
        # Decimal
        formatted = self.formatter._format_number(1234.56, None)
        self.assertEqual(formatted, "1,234.56")
        
        # Currency
        formatted = self.formatter._format_number(1234.56, "currency")
        self.assertTrue("$" in formatted or "€" in formatted)  # Depends on locale
    
    def test_format_date(self):
        """Test formatting a date."""
        date = datetime.date(2023, 1, 15)
        
        # Short format
        formatted = self.formatter._format_date(date, "short")
        self.assertTrue("1" in formatted and "15" in formatted and "23" in formatted)
        
        # Medium format
        formatted = self.formatter._format_date(date, "medium")
        self.assertTrue("Jan" in formatted or "January" in formatted)
        
        # Long format
        formatted = self.formatter._format_date(date, "long")
        self.assertTrue("January" in formatted and "2023" in formatted)

class TestTranslationMemory(unittest.TestCase):
    """Test cases for the TranslationMemory class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory = TranslationMemory(self.temp_dir)
    
    def test_add_entry(self):
        """Test adding a translation entry."""
        entry = TranslationEntry(
            source_text="Hello, world!",
            target_text="¡Hola, mundo!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH,
            context="greeting"
        )
        
        self.memory.add_entry(entry)
        
        # Verify entry was added
        entries = self.memory.get_entries(
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], entry)
    
    def test_find_translation(self):
        """Test finding a translation."""
        # Add entries
        entry1 = TranslationEntry(
            source_text="Hello, world!",
            target_text="¡Hola, mundo!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        
        entry2 = TranslationEntry(
            source_text="Goodbye, world!",
            target_text="¡Adiós, mundo!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        
        self.memory.add_entry(entry1)
        self.memory.add_entry(entry2)
        
        # Find translation
        translation = self.memory.find_translation(
            source_text="Hello, world!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        
        # Verify translation
        self.assertEqual(translation, "¡Hola, mundo!")
        
        # Find non-existent translation
        translation = self.memory.find_translation(
            source_text="Not in memory",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        
        # Verify no translation found
        self.assertIsNone(translation)
    
    def test_find_similar_translations(self):
        """Test finding similar translations."""
        # Add entries
        entry1 = TranslationEntry(
            source_text="Hello, world!",
            target_text="¡Hola, mundo!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        
        entry2 = TranslationEntry(
            source_text="Hello, friend!",
            target_text="¡Hola, amigo!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        
        entry3 = TranslationEntry(
            source_text="Goodbye, world!",
            target_text="¡Adiós, mundo!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        
        self.memory.add_entry(entry1)
        self.memory.add_entry(entry2)
        self.memory.add_entry(entry3)
        
        # Find similar translations
        similar = self.memory.find_similar_translations(
            source_text="Hello, everyone!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH,
            threshold=0.5
        )
        
        # Verify similar translations
        self.assertEqual(len(similar), 2)
        self.assertIn(entry1, similar)
        self.assertIn(entry2, similar)
    
    @patch('localization.localization_framework.os.path.exists')
    @patch('localization.localization_framework.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_memory(self, mock_file, mock_makedirs, mock_exists):
        """Test saving translation memory."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Add entries
        entry = TranslationEntry(
            source_text="Hello, world!",
            target_text="¡Hola, mundo!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        self.memory.add_entry(entry)
        
        # Save memory
        self.memory.save()
        
        # Verify memory was saved
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        mock_file().write.assert_called_once()
    
    @patch('localization.localization_framework.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_memory(self, mock_file, mock_exists):
        """Test loading translation memory."""
        # Mock path exists
        mock_exists.return_value = True
        
        # Mock file content
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps([
            {
                "source_text": "Hello, world!",
                "target_text": "¡Hola, mundo!",
                "source_language": "en",
                "target_language": "es",
                "context": "greeting",
                "timestamp": "2023-01-01T12:00:00"
            }
        ])
        
        # Load memory
        self.memory.load()
        
        # Verify memory was loaded
        entries = self.memory.get_entries(
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].source_text, "Hello, world!")
        self.assertEqual(entries[0].target_text, "¡Hola, mundo!")

class TestTranslationProvider(unittest.TestCase):
    """Test cases for the TranslationProvider class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = LocalizationConfig(
            enabled=True,
            external_provider_enabled=True,
            external_provider_api_key="test-api-key"
        )
        self.provider = TranslationProvider(self.config)
    
    @patch('localization.localization_framework.requests.post')
    def test_translate_text(self, mock_post):
        """Test translating text using external provider."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translations": [
                {
                    "text": "¡Hola, mundo!"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Translate text
        translation = self.provider.translate_text(
            text="Hello, world!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        
        # Verify translation
        self.assertEqual(translation, "¡Hola, mundo!")
        mock_post.assert_called_once()
    
    @patch('localization.localization_framework.requests.post')
    def test_translate_text_error(self, mock_post):
        """Test handling error when translating text."""
        # Mock API error
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        # Translate text
        translation = self.provider.translate_text(
            text="Hello, world!",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        
        # Verify no translation returned
        self.assertIsNone(translation)
    
    @patch('localization.localization_framework.requests.post')
    def test_batch_translate(self, mock_post):
        """Test batch translating texts."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translations": [
                {
                    "text": "¡Hola, mundo!"
                },
                {
                    "text": "¡Adiós, mundo!"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Batch translate
        translations = self.provider.batch_translate(
            texts=["Hello, world!", "Goodbye, world!"],
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH
        )
        
        # Verify translations
        self.assertEqual(len(translations), 2)
        self.assertEqual(translations[0], "¡Hola, mundo!")
        self.assertEqual(translations[1], "¡Adiós, mundo!")
        mock_post.assert_called_once()
    
    @patch('localization.localization_framework.requests.post')
    def test_detect_language(self, mock_post):
        """Test detecting language of text."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "language": "es",
            "confidence": 0.95
        }
        mock_post.return_value = mock_response
        
        # Detect language
        language, confidence = self.provider.detect_language("¡Hola, mundo!")
        
        # Verify detected language
        self.assertEqual(language, Language.SPANISH)
        self.assertEqual(confidence, 0.95)
        mock_post.assert_called_once()

class TestLocaleManager(unittest.TestCase):
    """Test cases for the LocaleManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.locale_manager = LocaleManager()
    
    def test_get_language_from_locale(self):
        """Test getting language from locale code."""
        # Test valid locales
        self.assertEqual(self.locale_manager.get_language_from_locale("en_US"), Language.ENGLISH)
        self.assertEqual(self.locale_manager.get_language_from_locale("es_ES"), Language.SPANISH)
        self.assertEqual(self.locale_manager.get_language_from_locale("fr_FR"), Language.FRENCH)
        self.assertEqual(self.locale_manager.get_language_from_locale("de_DE"), Language.GERMAN)
        self.assertEqual(self.locale_manager.get_language_from_locale("ja_JP"), Language.JAPANESE)
        
        # Test invalid locale
        self.assertIsNone(self.locale_manager.get_language_from_locale("xx_XX"))
    
    def test_get_locale_from_language(self):
        """Test getting locale code from language."""
        # Test valid languages
        self.assertEqual(self.locale_manager.get_locale_from_language(Language.ENGLISH), "en")
        self.assertEqual(self.locale_manager.get_locale_from_language(Language.SPANISH), "es")
        self.assertEqual(self.locale_manager.get_locale_from_language(Language.FRENCH), "fr")
        self.assertEqual(self.locale_manager.get_locale_from_language(Language.GERMAN), "de")
        self.assertEqual(self.locale_manager.get_locale_from_language(Language.JAPANESE), "ja")
    
    def test_get_display_name(self):
        """Test getting display name for a language."""
        # Test display names
        self.assertEqual(self.locale_manager.get_display_name(Language.ENGLISH), "English")
        self.assertEqual(self.locale_manager.get_display_name(Language.SPANISH), "Spanish")
        self.assertEqual(self.locale_manager.get_display_name(Language.FRENCH), "French")
        self.assertEqual(self.locale_manager.get_display_name(Language.GERMAN), "German")
        self.assertEqual(self.locale_manager.get_display_name(Language.JAPANESE), "Japanese")
    
    def test_get_native_name(self):
        """Test getting native name for a language."""
        # Test native names
        self.assertEqual(self.locale_manager.get_native_name(Language.ENGLISH), "English")
        self.assertEqual(self.locale_manager.get_native_name(Language.SPANISH), "Español")
        self.assertEqual(self.locale_manager.get_native_name(Language.FRENCH), "Français")
        self.assertEqual(self.locale_manager.get_native_name(Language.GERMAN), "Deutsch")
        self.assertEqual(self.locale_manager.get_native_name(Language.JAPANESE), "日本語")
    
    def test_format_number_for_locale(self):
        """Test formatting a number for a specific locale."""
        # Format number for different locales
        with patch('locale.setlocale') as mock_setlocale:
            with patch('locale.format_string') as mock_format:
                mock_format.return_value = "1,234.56"
                
                formatted = self.locale_manager.format_number_for_locale(1234.56, Language.ENGLISH)
                
                self.assertEqual(formatted, "1,234.56")
                mock_setlocale.assert_called_once()
                mock_format.assert_called_once()
    
    def test_format_date_for_locale(self):
        """Test formatting a date for a specific locale."""
        # Format date for different locales
        date = datetime.date(2023, 1, 15)
        
        with patch('locale.setlocale') as mock_setlocale:
            with patch('datetime.date.strftime') as mock_strftime:
                mock_strftime.return_value = "01/15/2023"
                
                formatted = self.locale_manager.format_date_for_locale(date, Language.ENGLISH, "short")
                
                self.assertEqual(formatted, "01/15/2023")
                mock_setlocale.assert_called_once()
                mock_strftime.assert_called_once()

class TestLocalizationContext(unittest.TestCase):
    """Test cases for the LocalizationContext class."""
    
    def test_context_creation(self):
        """Test creating a localization context."""
        context = LocalizationContext(
            language=Language.ENGLISH,
            region="US",
            timezone="America/New_York",
            user_id="user-123",
            device_type="desktop",
            platform="windows"
        )
        
        self.assertEqual(context.language, Language.ENGLISH)
        self.assertEqual(context.region, "US")
        self.assertEqual(context.timezone, "America/New_York")
        self.assertEqual(context.user_id, "user-123")
        self.assertEqual(context.device_type, "desktop")
        self.assertEqual(context.platform, "windows")
    
    def test_to_dict(self):
        """Test converting context to dictionary."""
        context = LocalizationContext(
            language=Language.ENGLISH,
            region="US",
            timezone="America/New_York",
            user_id="user-123",
            device_type="desktop",
            platform="windows"
        )
        
        context_dict = context.to_dict()
        
        self.assertEqual(context_dict["language"], "en")
        self.assertEqual(context_dict["region"], "US")
        self.assertEqual(context_dict["timezone"], "America/New_York")
        self.assertEqual(context_dict["user_id"], "user-123")
        self.assertEqual(context_dict["device_type"], "desktop")
        self.assertEqual(context_dict["platform"], "windows")
    
    def test_from_dict(self):
        """Test creating context from dictionary."""
        context_dict = {
            "language": "en",
            "region": "US",
            "timezone": "America/New_York",
            "user_id": "user-123",
            "device_type": "desktop",
            "platform": "windows"
        }
        
        context = LocalizationContext.from_dict(context_dict)
        
        self.assertEqual(context.language, Language.ENGLISH)
        self.assertEqual(context.region, "US")
        self.assertEqual(context.timezone, "America/New_York")
        self.assertEqual(context.user_id, "user-123")
        self.assertEqual(context.device_type, "desktop")
        self.assertEqual(context.platform, "windows")

if __name__ == '__main__':
    unittest.main()
