#!/usr/bin/env python3
"""
Localization and Internationalization Framework for ApexAgent

This module provides a comprehensive framework for managing translations,
locale-specific formatting, right-to-left (RTL) support, and other
internationalization features to make ApexAgent accessible globally.
"""

import os
import sys
import json
import uuid
import logging
import threading
import re
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Set, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import gettext
import locale
import babel
from babel import Locale, dates, numbers, support
from babel.messages import Catalog, extract, mofile, pofile
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("localization.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("localization")

# Type variables for generic functions
T = TypeVar("T")

class LocaleDirection(Enum):
    """Enumeration of text direction for locales."""
    LTR = "ltr"  # Left-to-right
    RTL = "rtl"  # Right-to-left

@dataclass
class LocalizationConfig:
    """Configuration for the localization system."""
    default_locale: str = "en_US"
    fallback_locale: str = "en_US"
    available_locales: List[str] = field(default_factory=lambda: ["en_US"])
    translations_dir: str = "translations"
    locale_data_dir: str = "locale_data"
    auto_detect_locale: bool = True
    use_system_locale: bool = True
    rtl_support: bool = True
    translation_memory_enabled: bool = True
    translation_memory_path: str = "translation_memory"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary."""
        return {
            "default_locale": self.default_locale,
            "fallback_locale": self.fallback_locale,
            "available_locales": self.available_locales,
            "translations_dir": self.translations_dir,
            "locale_data_dir": self.locale_data_dir,
            "auto_detect_locale": self.auto_detect_locale,
            "use_system_locale": self.use_system_locale,
            "rtl_support": self.rtl_support,
            "translation_memory_enabled": self.translation_memory_enabled,
            "translation_memory_path": self.translation_memory_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LocalizationConfig":
        """Create a configuration from a dictionary."""
        return cls(
            default_locale=data.get("default_locale", "en_US"),
            fallback_locale=data.get("fallback_locale", "en_US"),
            available_locales=data.get("available_locales", ["en_US"]),
            translations_dir=data.get("translations_dir", "translations"),
            locale_data_dir=data.get("locale_data_dir", "locale_data"),
            auto_detect_locale=data.get("auto_detect_locale", True),
            use_system_locale=data.get("use_system_locale", True),
            rtl_support=data.get("rtl_support", True),
            translation_memory_enabled=data.get("translation_memory_enabled", True),
            translation_memory_path=data.get("translation_memory_path", "translation_memory")
        )

@dataclass
class TranslationEntry:
    """A single translation entry."""
    message_id: str
    context: Optional[str]
    message_str: str
    locale: str
    plural_forms: Dict[int, str] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    source_locations: List[Tuple[str, int]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "context": self.context,
            "message_str": self.message_str,
            "locale": self.locale,
            "plural_forms": self.plural_forms,
            "flags": self.flags,
            "comments": self.comments,
            "source_locations": self.source_locations,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranslationEntry":
        """Create from dictionary."""
        return cls(
            message_id=data["message_id"],
            context=data.get("context"),
            message_str=data["message_str"],
            locale=data["locale"],
            plural_forms=data.get("plural_forms", {}),
            flags=data.get("flags", []),
            comments=data.get("comments", []),
            source_locations=data.get("source_locations", []),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )

@dataclass
class LocaleData:
    """Locale-specific data for formatting and display."""
    locale_code: str
    display_name: str
    native_name: str
    direction: LocaleDirection
    date_formats: Dict[str, str]
    time_formats: Dict[str, str]
    number_formats: Dict[str, str]
    currency_formats: Dict[str, str]
    decimal_separator: str
    thousands_separator: str
    currency_symbol: str
    percent_symbol: str
    first_day_of_week: int  # 0=Monday, 6=Sunday
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "locale_code": self.locale_code,
            "display_name": self.display_name,
            "native_name": self.native_name,
            "direction": self.direction.value,
            "date_formats": self.date_formats,
            "time_formats": self.time_formats,
            "number_formats": self.number_formats,
            "currency_formats": self.currency_formats,
            "decimal_separator": self.decimal_separator,
            "thousands_separator": self.thousands_separator,
            "currency_symbol": self.currency_symbol,
            "percent_symbol": self.percent_symbol,
            "first_day_of_week": self.first_day_of_week
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LocaleData":
        """Create from dictionary."""
        return cls(
            locale_code=data["locale_code"],
            display_name=data["display_name"],
            native_name=data["native_name"],
            direction=LocaleDirection(data["direction"]),
            date_formats=data["date_formats"],
            time_formats=data["time_formats"],
            number_formats=data["number_formats"],
            currency_formats=data["currency_formats"],
            decimal_separator=data["decimal_separator"],
            thousands_separator=data["thousands_separator"],
            currency_symbol=data["currency_symbol"],
            percent_symbol=data["percent_symbol"],
            first_day_of_week=data["first_day_of_week"]
        )
    
    @classmethod
    def from_babel_locale(cls, locale_code: str) -> "LocaleData":
        """Create from Babel locale."""
        try:
            babel_locale = Locale.parse(locale_code)
            
            # Determine text direction
            rtl_languages = {"ar", "he", "fa", "ur", "yi", "dv"}
            direction = LocaleDirection.RTL if babel_locale.language in rtl_languages else LocaleDirection.LTR
            
            # Get date and time formats
            date_formats = {
                "short": babel_locale.date_formats["short"].pattern,
                "medium": babel_locale.date_formats["medium"].pattern,
                "long": babel_locale.date_formats["long"].pattern,
                "full": babel_locale.date_formats["full"].pattern
            }
            
            time_formats = {
                "short": babel_locale.time_formats["short"].pattern,
                "medium": babel_locale.time_formats["medium"].pattern,
                "long": babel_locale.time_formats["long"].pattern,
                "full": babel_locale.time_formats["full"].pattern
            }
            
            # Get number formats
            number_formats = {
                "decimal": babel_locale.decimal_formats[None].pattern,
                "scientific": babel_locale.scientific_formats[None].pattern,
                "percent": babel_locale.percent_formats[None].pattern
            }
            
            # Get currency formats
            currency_formats = {
                "standard": babel_locale.currency_formats["standard"].pattern
            }
            
            return cls(
                locale_code=locale_code,
                display_name=babel_locale.english_name,
                native_name=babel_locale.display_name,
                direction=direction,
                date_formats=date_formats,
                time_formats=time_formats,
                number_formats=number_formats,
                currency_formats=currency_formats,
                decimal_separator=babel_locale.number_symbols.get("decimal", "."),
                thousands_separator=babel_locale.number_symbols.get("group", ","),
                currency_symbol=babel_locale.currency_symbols.get("USD", "$"),
                percent_symbol=babel_locale.number_symbols.get("percentSign", "%"),
                first_day_of_week=babel_locale.first_week_day
            )
        except Exception as e:
            logger.error(f"Failed to create LocaleData from Babel locale {locale_code}: {str(e)}")
            # Return English as fallback
            return cls.from_babel_locale("en_US")

@dataclass
class TranslationMemoryEntry:
    """An entry in the translation memory."""
    source_text: str
    target_text: str
    source_locale: str
    target_locale: str
    context: Optional[str] = None
    quality: float = 1.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_text": self.source_text,
            "target_text": self.target_text,
            "source_locale": self.source_locale,
            "target_locale": self.target_locale,
            "context": self.context,
            "quality": self.quality,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranslationMemoryEntry":
        """Create from dictionary."""
        return cls(
            source_text=data["source_text"],
            target_text=data["target_text"],
            source_locale=data["source_locale"],
            target_locale=data["target_locale"],
            context=data.get("context"),
            quality=data.get("quality", 1.0),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )

class TranslationManager:
    """Manages translations for the localization system."""
    
    def __init__(self, config: LocalizationConfig):
        """Initialize the translation manager."""
        self.config = config
        self.translations: Dict[str, Dict[Tuple[str, Optional[str]], TranslationEntry]] = {}
        self.gettext_translations: Dict[str, gettext.NullTranslations] = {}
        self._lock = threading.RLock()
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load translations from storage."""
        with self._lock:
            self.translations = {}
            self.gettext_translations = {}
            
            translations_dir = Path(self.config.translations_dir)
            translations_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize empty dictionaries for each locale
            for locale_code in self.config.available_locales:
                self.translations[locale_code] = {}
            
            # Load JSON translations
            for locale_code in self.config.available_locales:
                locale_dir = translations_dir / locale_code
                if not locale_dir.exists():
                    locale_dir.mkdir(parents=True, exist_ok=True)
                    continue
                
                for file_path in locale_dir.glob("*.json"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            entries_data = json.load(f)
                        
                        for entry_data in entries_data:
                            entry = TranslationEntry.from_dict(entry_data)
                            key = (entry.message_id, entry.context)
                            self.translations[locale_code][key] = entry
                    except Exception as e:
                        logger.error(f"Failed to load translations from {file_path}: {str(e)}")
            
            # Load gettext translations
            for locale_code in self.config.available_locales:
                locale_dir = translations_dir / "gettext" / "locale"
                if not locale_dir.exists():
                    continue
                
                try:
                    translation = gettext.translation(
                        "messages",
                        localedir=str(locale_dir),
                        languages=[locale_code],
                        fallback=True
                    )
                    self.gettext_translations[locale_code] = translation
                except Exception as e:
                    logger.error(f"Failed to load gettext translation for {locale_code}: {str(e)}")
                    self.gettext_translations[locale_code] = gettext.NullTranslations()
    
    def _save_translations(self, locale_code: str) -> None:
        """Save translations for a locale to storage."""
        translations_dir = Path(self.config.translations_dir)
        locale_dir = translations_dir / locale_code
        locale_dir.mkdir(parents=True, exist_ok=True)
        file_path = locale_dir / "translations.json"
        
        try:
            entries = list(self.translations.get(locale_code, {}).values())
            entries_data = [entry.to_dict() for entry in entries]
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(entries_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save translations for {locale_code}: {str(e)}")
    
    def add_translation(self, message_id: str, message_str: str, locale: str,
                       context: Optional[str] = None, plural_forms: Dict[int, str] = None,
                       flags: List[str] = None, comments: List[str] = None,
                       source_locations: List[Tuple[str, int]] = None) -> TranslationEntry:
        """Add a new translation entry."""
        with self._lock:
            if locale not in self.translations:
                self.translations[locale] = {}
            
            key = (message_id, context)
            entry = TranslationEntry(
                message_id=message_id,
                context=context,
                message_str=message_str,
                locale=locale,
                plural_forms=plural_forms or {},
                flags=flags or [],
                comments=comments or [],
                source_locations=source_locations or []
            )
            
            self.translations[locale][key] = entry
            self._save_translations(locale)
            
            # Invalidate gettext cache
            if locale in self.gettext_translations:
                self.gettext_translations.pop(locale)
            
            logger.info(f"Added translation for {message_id} in {locale}")
            return entry
    
    def update_translation(self, message_id: str, message_str: str, locale: str,
                          context: Optional[str] = None, **kwargs) -> Optional[TranslationEntry]:
        """Update an existing translation entry."""
        with self._lock:
            if locale not in self.translations:
                logger.error(f"Locale not found: {locale}")
                return None
            
            key = (message_id, context)
            if key not in self.translations[locale]:
                logger.error(f"Translation not found: {message_id} in {locale}")
                return None
            
            entry = self.translations[locale][key]
            entry.message_str = message_str
            entry.updated_at = datetime.now()
            
            for k, v in kwargs.items():
                if hasattr(entry, k):
                    setattr(entry, k, v)
            
            self._save_translations(locale)
            
            # Invalidate gettext cache
            if locale in self.gettext_translations:
                self.gettext_translations.pop(locale)
            
            logger.info(f"Updated translation for {message_id} in {locale}")
            return entry
    
    def get_translation(self, message_id: str, locale: str, context: Optional[str] = None) -> Optional[TranslationEntry]:
        """Get a translation entry."""
        with self._lock:
            if locale not in self.translations:
                return None
            
            key = (message_id, context)
            return self.translations[locale].get(key)
    
    def translate(self, message_id: str, locale: str, context: Optional[str] = None,
                 plural_id: Optional[str] = None, count: Optional[int] = None,
                 fallback: bool = True) -> str:
        """Translate a message."""
        with self._lock:
            # Try the requested locale
            if locale in self.translations:
                key = (message_id, context)
                if key in self.translations[locale]:
                    entry = self.translations[locale][key]
                    
                    # Handle plurals
                    if plural_id is not None and count is not None and entry.plural_forms:
                        # Get plural form index based on count and locale's plural rule
                        # This is a simplified version; real implementation would use proper plural rules
                        plural_idx = 0 if count == 1 else 1
                        if plural_idx in entry.plural_forms:
                            return entry.plural_forms[plural_idx]
                    
                    return entry.message_str
            
            # Try gettext fallback
            if locale in self.gettext_translations:
                translation = self.gettext_translations[locale]
                if plural_id is not None and count is not None:
                    return translation.ngettext(message_id, plural_id, count)
                elif context is not None:
                    return translation.pgettext(context, message_id)
                else:
                    return translation.gettext(message_id)
            
            # Try fallback locale
            if fallback and locale != self.config.fallback_locale:
                return self.translate(message_id, self.config.fallback_locale, context, plural_id, count, False)
            
            # Return the original message as last resort
            return message_id
    
    def extract_messages(self, source_files: List[str], keywords: List[str] = None) -> Dict[str, List[Tuple[str, int, str, List[str]]]]:
        """Extract translatable messages from source files."""
        if keywords is None:
            keywords = ["_", "gettext", "ngettext:1,2", "pgettext:1c,2", "npgettext:1c,2,3"]
        
        extracted = {}
        
        for filename in source_files:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    source = f.read()
                
                file_messages = []
                for lineno, funcname, message, comments in extract.extract_from_file(
                    "python", filename, keywords=keywords
                ):
                    file_messages.append((lineno, funcname, message, comments))
                
                if file_messages:
                    extracted[filename] = file_messages
            except Exception as e:
                logger.error(f"Failed to extract messages from {filename}: {str(e)}")
        
        return extracted
    
    def create_pot_file(self, extracted_messages: Dict[str, List[Tuple[str, int, str, List[str]]]],
                       output_file: str, project: str, version: str) -> None:
        """Create a POT (Portable Object Template) file from extracted messages."""
        catalog = Catalog(project=project, version=version)
        
        for filename, messages in extracted_messages.items():
            for lineno, funcname, message, comments in messages:
                if isinstance(message, tuple):
                    # Handle plural forms
                    catalog.add(message[0], None, [(filename, lineno)], auto_comments=comments, context=None, plural=message[1])
                else:
                    catalog.add(message, None, [(filename, lineno)], auto_comments=comments)
        
        with open(output_file, "wb") as f:
            pofile.write_po(f, catalog)
    
    def compile_po_to_mo(self, po_file: str, mo_file: str) -> None:
        """Compile a PO (Portable Object) file to MO (Machine Object) format."""
        try:
            with open(po_file, "rb") as f:
                catalog = pofile.read_po(f)
            
            with open(mo_file, "wb") as f:
                mofile.write_mo(f, catalog)
        except Exception as e:
            logger.error(f"Failed to compile {po_file} to {mo_file}: {str(e)}")
    
    def import_po_file(self, po_file: str, locale: str) -> int:
        """Import translations from a PO file."""
        try:
            with open(po_file, "rb") as f:
                catalog = pofile.read_po(f)
            
            count = 0
            for message in catalog:
                if message.id and message.string:
                    # Handle plural forms
                    plural_forms = {}
                    if message.pluralizable:
                        for i, string in enumerate(message.string):
                            plural_forms[i] = string
                    
                    self.add_translation(
                        message_id=message.id,
                        message_str=message.string[0] if message.pluralizable else message.string,
                        locale=locale,
                        context=message.context,
                        plural_forms=plural_forms,
                        comments=message.auto_comments,
                        source_locations=[(loc[0], loc[1]) for loc in message.locations]
                    )
                    count += 1
            
            return count
        except Exception as e:
            logger.error(f"Failed to import PO file {po_file}: {str(e)}")
            return 0
    
    def export_to_po_file(self, locale: str, output_file: str, project: str, version: str) -> int:
        """Export translations to a PO file."""
        try:
            catalog = Catalog(project=project, version=version, locale=locale)
            
            count = 0
            for key, entry in self.translations.get(locale, {}).items():
                message_id, context = key
                
                # Handle plural forms
                if entry.plural_forms:
                    plural_strings = [entry.message_str]
                    for i in range(1, max(entry.plural_forms.keys()) + 1):
                        plural_strings.append(entry.plural_forms.get(i, ""))
                    
                    catalog.add(
                        message_id, plural_strings, 
                        locations=entry.source_locations,
                        auto_comments=entry.comments,
                        context=context,
                        flags=entry.flags
                    )
                else:
                    catalog.add(
                        message_id, entry.message_str, 
                        locations=entry.source_locations,
                        auto_comments=entry.comments,
                        context=context,
                        flags=entry.flags
                    )
                count += 1
            
            with open(output_file, "wb") as f:
                pofile.write_po(f, catalog)
            
            return count
        except Exception as e:
            logger.error(f"Failed to export to PO file {output_file}: {str(e)}")
            return 0

class LocaleDataManager:
    """Manages locale-specific data for the localization system."""
    
    def __init__(self, config: LocalizationConfig):
        """Initialize the locale data manager."""
        self.config = config
        self.locale_data: Dict[str, LocaleData] = {}
        self._lock = threading.RLock()
        self._load_locale_data()
    
    def _load_locale_data(self) -> None:
        """Load locale data from storage."""
        with self._lock:
            self.locale_data = {}
            locale_data_dir = Path(self.config.locale_data_dir)
            locale_data_dir.mkdir(parents=True, exist_ok=True)
            
            # First try to load from files
            for locale_code in self.config.available_locales:
                file_path = locale_data_dir / f"{locale_code}.json"
                if file_path.exists():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        self.locale_data[locale_code] = LocaleData.from_dict(data)
                    except Exception as e:
                        logger.error(f"Failed to load locale data from {file_path}: {str(e)}")
            
            # Generate missing locale data from Babel
            for locale_code in self.config.available_locales:
                if locale_code not in self.locale_data:
                    try:
                        self.locale_data[locale_code] = LocaleData.from_babel_locale(locale_code)
                        self._save_locale_data(locale_code)
                    except Exception as e:
                        logger.error(f"Failed to generate locale data for {locale_code}: {str(e)}")
    
    def _save_locale_data(self, locale_code: str) -> None:
        """Save locale data to storage."""
        locale_data_dir = Path(self.config.locale_data_dir)
        locale_data_dir.mkdir(parents=True, exist_ok=True)
        file_path = locale_data_dir / f"{locale_code}.json"
        
        try:
            locale_data = self.locale_data.get(locale_code)
            if locale_data:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(locale_data.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save locale data for {locale_code}: {str(e)}")
    
    def get_locale_data(self, locale_code: str) -> Optional[LocaleData]:
        """Get locale data for a specific locale."""
        with self._lock:
            if locale_code in self.locale_data:
                return self.locale_data[locale_code]
            
            # Try to generate from Babel
            try:
                locale_data = LocaleData.from_babel_locale(locale_code)
                self.locale_data[locale_code] = locale_data
                self._save_locale_data(locale_code)
                return locale_data
            except Exception as e:
                logger.error(f"Failed to generate locale data for {locale_code}: {str(e)}")
                return None
    
    def get_available_locales(self) -> List[Tuple[str, str, str]]:
        """Get a list of available locales with their display names."""
        with self._lock:
            result = []
            for locale_code in self.config.available_locales:
                locale_data = self.get_locale_data(locale_code)
                if locale_data:
                    result.append((locale_code, locale_data.display_name, locale_data.native_name))
            return result
    
    def format_date(self, date: datetime, locale_code: str, format: str = "medium") -> str:
        """Format a date according to the locale's conventions."""
        try:
            return dates.format_date(date, format=format, locale=locale_code)
        except Exception as e:
            logger.error(f"Failed to format date for {locale_code}: {str(e)}")
            return str(date)
    
    def format_time(self, time: datetime, locale_code: str, format: str = "medium") -> str:
        """Format a time according to the locale's conventions."""
        try:
            return dates.format_time(time, format=format, locale=locale_code)
        except Exception as e:
            logger.error(f"Failed to format time for {locale_code}: {str(e)}")
            return str(time.time())
    
    def format_datetime(self, dt: datetime, locale_code: str, format: str = "medium") -> str:
        """Format a datetime according to the locale's conventions."""
        try:
            return dates.format_datetime(dt, format=format, locale=locale_code)
        except Exception as e:
            logger.error(f"Failed to format datetime for {locale_code}: {str(e)}")
            return str(dt)
    
    def format_number(self, number: float, locale_code: str) -> str:
        """Format a number according to the locale's conventions."""
        try:
            return numbers.format_number(number, locale=locale_code)
        except Exception as e:
            logger.error(f"Failed to format number for {locale_code}: {str(e)}")
            return str(number)
    
    def format_currency(self, amount: float, currency: str, locale_code: str) -> str:
        """Format a currency amount according to the locale's conventions."""
        try:
            return numbers.format_currency(amount, currency, locale=locale_code)
        except Exception as e:
            logger.error(f"Failed to format currency for {locale_code}: {str(e)}")
            return f"{currency} {amount}"
    
    def format_percent(self, number: float, locale_code: str) -> str:
        """Format a percentage according to the locale's conventions."""
        try:
            return numbers.format_percent(number, locale=locale_code)
        except Exception as e:
            logger.error(f"Failed to format percent for {locale_code}: {str(e)}")
            return f"{number}%"
    
    def get_text_direction(self, locale_code: str) -> LocaleDirection:
        """Get the text direction for a locale."""
        locale_data = self.get_locale_data(locale_code)
        if locale_data:
            return locale_data.direction
        return LocaleDirection.LTR
    
    def is_rtl(self, locale_code: str) -> bool:
        """Check if a locale uses right-to-left text direction."""
        return self.get_text_direction(locale_code) == LocaleDirection.RTL

class TranslationMemory:
    """Manages translation memory for the localization system."""
    
    def __init__(self, config: LocalizationConfig):
        """Initialize the translation memory."""
        self.config = config
        self.entries: Dict[str, Dict[str, List[TranslationMemoryEntry]]] = {}
        self._lock = threading.RLock()
        
        if self.config.translation_memory_enabled:
            self._load_translation_memory()
    
    def _load_translation_memory(self) -> None:
        """Load translation memory from storage."""
        with self._lock:
            self.entries = {}
            
            if not self.config.translation_memory_enabled:
                return
            
            memory_dir = Path(self.config.translation_memory_path)
            memory_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in memory_dir.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        entries_data = json.load(f)
                    
                    for entry_data in entries_data:
                        entry = TranslationMemoryEntry.from_dict(entry_data)
                        
                        # Initialize dictionaries if needed
                        if entry.source_locale not in self.entries:
                            self.entries[entry.source_locale] = {}
                        if entry.target_locale not in self.entries[entry.source_locale]:
                            self.entries[entry.source_locale][entry.target_locale] = []
                        
                        self.entries[entry.source_locale][entry.target_locale].append(entry)
                except Exception as e:
                    logger.error(f"Failed to load translation memory from {file_path}: {str(e)}")
    
    def _save_translation_memory(self, source_locale: str, target_locale: str) -> None:
        """Save translation memory to storage."""
        if not self.config.translation_memory_enabled:
            return
        
        memory_dir = Path(self.config.translation_memory_path)
        memory_dir.mkdir(parents=True, exist_ok=True)
        file_path = memory_dir / f"{source_locale}_{target_locale}.json"
        
        try:
            entries = self.entries.get(source_locale, {}).get(target_locale, [])
            entries_data = [entry.to_dict() for entry in entries]
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(entries_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save translation memory for {source_locale}->{target_locale}: {str(e)}")
    
    def add_entry(self, source_text: str, target_text: str, source_locale: str, target_locale: str,
                 context: Optional[str] = None, quality: float = 1.0) -> TranslationMemoryEntry:
        """Add a new entry to the translation memory."""
        with self._lock:
            if not self.config.translation_memory_enabled:
                return TranslationMemoryEntry(
                    source_text=source_text,
                    target_text=target_text,
                    source_locale=source_locale,
                    target_locale=target_locale,
                    context=context,
                    quality=quality
                )
            
            # Initialize dictionaries if needed
            if source_locale not in self.entries:
                self.entries[source_locale] = {}
            if target_locale not in self.entries[source_locale]:
                self.entries[source_locale][target_locale] = []
            
            # Check if entry already exists
            for existing in self.entries[source_locale][target_locale]:
                if (existing.source_text == source_text and 
                    existing.context == context):
                    # Update existing entry
                    existing.target_text = target_text
                    existing.quality = quality
                    existing.updated_at = datetime.now()
                    self._save_translation_memory(source_locale, target_locale)
                    return existing
            
            # Add new entry
            entry = TranslationMemoryEntry(
                source_text=source_text,
                target_text=target_text,
                source_locale=source_locale,
                target_locale=target_locale,
                context=context,
                quality=quality
            )
            
            self.entries[source_locale][target_locale].append(entry)
            self._save_translation_memory(source_locale, target_locale)
            
            return entry
    
    def find_matches(self, source_text: str, source_locale: str, target_locale: str,
                    context: Optional[str] = None, threshold: float = 0.7) -> List[Tuple[TranslationMemoryEntry, float]]:
        """Find matches in the translation memory."""
        with self._lock:
            if not self.config.translation_memory_enabled:
                return []
            
            if source_locale not in self.entries or target_locale not in self.entries[source_locale]:
                return []
            
            matches = []
            
            for entry in self.entries[source_locale][target_locale]:
                # Exact match
                if entry.source_text == source_text:
                    # Context match is better
                    if entry.context == context:
                        matches.append((entry, 1.0))
                    else:
                        matches.append((entry, 0.9))
                else:
                    # Fuzzy match using simple similarity metric
                    similarity = self._calculate_similarity(source_text, entry.source_text)
                    if similarity >= threshold:
                        # Adjust by quality and context match
                        adjusted_similarity = similarity * entry.quality
                        if entry.context == context:
                            adjusted_similarity += 0.1
                        matches.append((entry, min(adjusted_similarity, 0.99)))
            
            # Sort by similarity (descending)
            matches.sort(key=lambda x: x[1], reverse=True)
            
            return matches
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        # Simple implementation using character-level Levenshtein distance
        # In a real implementation, this would use more sophisticated algorithms
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        text1 = text1.lower()
        text2 = text2.lower()
        
        # Calculate Levenshtein distance
        m, n = len(text1), len(text2)
        if m == 0 or n == 0:
            return 0.0
        
        # Use simple ratio for short implementation
        # In production, use proper Levenshtein distance calculation
        common_prefix_len = 0
        for i in range(min(m, n)):
            if text1[i] == text2[i]:
                common_prefix_len += 1
            else:
                break
        
        common_suffix_len = 0
        for i in range(1, min(m, n) + 1):
            if text1[m-i] == text2[n-i]:
                common_suffix_len += 1
            else:
                break
        
        common_chars = common_prefix_len + common_suffix_len
        max_len = max(m, n)
        
        return common_chars / max_len

class LocalizationSystem:
    """Main localization system class."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> "LocalizationSystem":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = LocalizationSystem()
        return cls._instance
    
    def __init__(self):
        """Initialize the localization system."""
        self.config = LocalizationConfig()
        self.translation_manager = TranslationManager(self.config)
        self.locale_data_manager = LocaleDataManager(self.config)
        self.translation_memory = TranslationMemory(self.config)
        self.current_locale = self.config.default_locale
        self._initialized = False
        self._lock = threading.RLock()
    
    def initialize(self, config_path: Optional[str] = None) -> None:
        """Initialize the system with configuration."""
        with self._lock:
            if self._initialized:
                return
            
            if config_path and Path(config_path).exists():
                try:
                    with open(config_path, "r") as f:
                        config_data = json.load(f)
                    self.config = LocalizationConfig.from_dict(config_data)
                except Exception as e:
                    logger.error(f"Failed to load localization config from {config_path}: {str(e)}. Using defaults.")
                    self.config = LocalizationConfig()
            else:
                logger.warning("Localization config file not found. Using defaults.")
                self.config = LocalizationConfig()
            
            # Re-initialize managers with the loaded config
            self.translation_manager = TranslationManager(self.config)
            self.locale_data_manager = LocaleDataManager(self.config)
            self.translation_memory = TranslationMemory(self.config)
            
            # Set current locale
            if self.config.use_system_locale and self.config.auto_detect_locale:
                try:
                    system_locale = locale.getdefaultlocale()[0]
                    if system_locale and system_locale in self.config.available_locales:
                        self.current_locale = system_locale
                    else:
                        self.current_locale = self.config.default_locale
                except Exception:
                    self.current_locale = self.config.default_locale
            else:
                self.current_locale = self.config.default_locale
            
            self._initialized = True
            logger.info(f"Localization system initialized with locale {self.current_locale}")
    
    def shutdown(self) -> None:
        """Shutdown the system."""
        with self._lock:
            if not self._initialized:
                return
            
            self._initialized = False
            logger.info("Localization system shutdown")
    
    def ensure_initialized(self) -> None:
        """Ensure the system is initialized."""
        if not self._initialized:
            self.initialize()
    
    def set_locale(self, locale_code: str) -> bool:
        """Set the current locale."""
        self.ensure_initialized()
        
        with self._lock:
            if locale_code in self.config.available_locales:
                self.current_locale = locale_code
                logger.info(f"Locale set to {locale_code}")
                return True
            else:
                logger.warning(f"Locale {locale_code} not available, using {self.current_locale}")
                return False
    
    def get_current_locale(self) -> str:
        """Get the current locale."""
        self.ensure_initialized()
        return self.current_locale
    
    def get_available_locales(self) -> List[Tuple[str, str, str]]:
        """Get a list of available locales with their display names."""
        self.ensure_initialized()
        return self.locale_data_manager.get_available_locales()
    
    def translate(self, message_id: str, context: Optional[str] = None,
                plural_id: Optional[str] = None, count: Optional[int] = None,
                locale: Optional[str] = None) -> str:
        """Translate a message."""
        self.ensure_initialized()
        
        locale_code = locale or self.current_locale
        
        result = self.translation_manager.translate(
            message_id, locale_code, context, plural_id, count
        )
        
        return result
    
    def format_date(self, date: datetime, format: str = "medium", locale: Optional[str] = None) -> str:
        """Format a date according to the locale's conventions."""
        self.ensure_initialized()
        
        locale_code = locale or self.current_locale
        return self.locale_data_manager.format_date(date, locale_code, format)
    
    def format_time(self, time: datetime, format: str = "medium", locale: Optional[str] = None) -> str:
        """Format a time according to the locale's conventions."""
        self.ensure_initialized()
        
        locale_code = locale or self.current_locale
        return self.locale_data_manager.format_time(time, locale_code, format)
    
    def format_datetime(self, dt: datetime, format: str = "medium", locale: Optional[str] = None) -> str:
        """Format a datetime according to the locale's conventions."""
        self.ensure_initialized()
        
        locale_code = locale or self.current_locale
        return self.locale_data_manager.format_datetime(dt, locale_code, format)
    
    def format_number(self, number: float, locale: Optional[str] = None) -> str:
        """Format a number according to the locale's conventions."""
        self.ensure_initialized()
        
        locale_code = locale or self.current_locale
        return self.locale_data_manager.format_number(number, locale_code)
    
    def format_currency(self, amount: float, currency: str, locale: Optional[str] = None) -> str:
        """Format a currency amount according to the locale's conventions."""
        self.ensure_initialized()
        
        locale_code = locale or self.current_locale
        return self.locale_data_manager.format_currency(amount, currency, locale_code)
    
    def format_percent(self, number: float, locale: Optional[str] = None) -> str:
        """Format a percentage according to the locale's conventions."""
        self.ensure_initialized()
        
        locale_code = locale or self.current_locale
        return self.locale_data_manager.format_percent(number, locale_code)
    
    def is_rtl(self, locale: Optional[str] = None) -> bool:
        """Check if a locale uses right-to-left text direction."""
        self.ensure_initialized()
        
        locale_code = locale or self.current_locale
        return self.locale_data_manager.is_rtl(locale_code)
    
    def get_text_direction(self, locale: Optional[str] = None) -> LocaleDirection:
        """Get the text direction for a locale."""
        self.ensure_initialized()
        
        locale_code = locale or self.current_locale
        return self.locale_data_manager.get_text_direction(locale_code)
    
    def add_translation(self, message_id: str, message_str: str, locale: str,
                       context: Optional[str] = None, **kwargs) -> TranslationEntry:
        """Add a new translation entry."""
        self.ensure_initialized()
        
        entry = self.translation_manager.add_translation(
            message_id, message_str, locale, context, **kwargs
        )
        
        # Add to translation memory
        if self.config.translation_memory_enabled:
            source_locale = self.config.default_locale
            if source_locale != locale:
                # Get the source text from the default locale
                source_entry = self.translation_manager.get_translation(message_id, source_locale, context)
                if source_entry:
                    self.translation_memory.add_entry(
                        source_entry.message_str, message_str, source_locale, locale, context
                    )
        
        return entry
    
    def find_translation_memory_matches(self, source_text: str, target_locale: str,
                                      context: Optional[str] = None, threshold: float = 0.7,
                                      source_locale: Optional[str] = None) -> List[Tuple[str, float]]:
        """Find matches in the translation memory."""
        self.ensure_initialized()
        
        if not self.config.translation_memory_enabled:
            return []
        
        source_locale_code = source_locale or self.config.default_locale
        
        matches = self.translation_memory.find_matches(
            source_text, source_locale_code, target_locale, context, threshold
        )
        
        return [(match[0].target_text, match[1]) for match in matches]
    
    def extract_and_update_translations(self, source_files: List[str], output_dir: str,
                                      project: str, version: str) -> Dict[str, int]:
        """Extract translatable messages and update translation files."""
        self.ensure_initialized()
        
        # Extract messages
        extracted = self.translation_manager.extract_messages(source_files)
        
        # Create POT file
        pot_file = os.path.join(output_dir, f"{project}.pot")
        self.translation_manager.create_pot_file(extracted, pot_file, project, version)
        
        # Update PO files for each locale
        results = {}
        for locale_code in self.config.available_locales:
            if locale_code == self.config.default_locale:
                continue
            
            po_file = os.path.join(output_dir, f"{locale_code}.po")
            
            # Create PO file if it doesn't exist
            if not os.path.exists(po_file):
                # Copy POT to PO
                import shutil
                shutil.copy(pot_file, po_file)
            
            # Import existing translations
            count = self.translation_manager.import_po_file(po_file, locale_code)
            results[locale_code] = count
        
        return results

# Global instance for easy access
localization_system = LocalizationSystem.get_instance()

# --- Helper Functions --- #

def initialize_localization(config_path: Optional[str] = None) -> None:
    """Initialize the localization system."""
    localization_system.initialize(config_path)

def shutdown_localization() -> None:
    """Shutdown the localization system."""
    localization_system.shutdown()

def _(message_id: str, context: Optional[str] = None) -> str:
    """Translate a message (gettext style)."""
    return localization_system.translate(message_id, context)

def gettext(message_id: str) -> str:
    """Translate a message."""
    return localization_system.translate(message_id)

def pgettext(context: str, message_id: str) -> str:
    """Translate a message with context."""
    return localization_system.translate(message_id, context)

def ngettext(singular: str, plural: str, n: int) -> str:
    """Translate singular or plural based on count."""
    return localization_system.translate(singular, None, plural, n)

def npgettext(context: str, singular: str, plural: str, n: int) -> str:
    """Translate singular or plural with context based on count."""
    return localization_system.translate(singular, context, plural, n)

# Example usage
if __name__ == "__main__":
    # Initialize
    initialize_localization()
    
    # Add translations
    localization_system.add_translation(
        "Hello, world!",
        "¡Hola, mundo!",
        "es_ES"
    )
    
    localization_system.add_translation(
        "You have {0} new message",
        "Tienes {0} mensaje nuevo",
        "es_ES",
        plural_forms={1: "Tienes {0} mensajes nuevos"}
    )
    
    # Set locale
    localization_system.set_locale("es_ES")
    
    # Translate
    print(_("Hello, world!"))  # ¡Hola, mundo!
    
    # Format date
    now = datetime.now()
    print(localization_system.format_date(now))  # 27 may. 2025
    
    # Format number
    print(localization_system.format_number(1234.56))  # 1234,56
    
    # Format currency
    print(localization_system.format_currency(1234.56, "EUR"))  # 1234,56 €
    
    # Check text direction
    print(localization_system.is_rtl())  # False
    
    # Shutdown
    shutdown_localization()
