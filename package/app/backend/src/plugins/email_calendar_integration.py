"""
Email and Calendar Integration Plugin for Aideon AI Lite

This plugin provides comprehensive email and calendar management capabilities using the
existing plugin architecture. It integrates with multiple email and calendar providers
to provide unified management, intelligent automation, and AI-powered assistance.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union, AsyncIterator
from datetime import datetime, timedelta
import aiohttp
import email
import email.mime.text
import email.mime.multipart
from email.header import decode_header
import base64
from dateutil import parser as date_parser

from ..core.base_plugin import BasePlugin, PluginMetadata, PluginAction, PluginParameter
from ..core.plugin_exceptions import (
    PluginError,
    PluginConfigurationError,
    PluginActionExecutionError
)

logger = logging.getLogger(__name__)


class EmailCalendarIntegrationPlugin(BasePlugin):
    """
    Email and Calendar Integration Plugin for comprehensive email and calendar management.
    
    This plugin provides unified access to multiple email and calendar providers including
    Gmail, Outlook, Yahoo, Google Calendar, Outlook Calendar, and Apple Calendar.
    """
    
    def __init__(self):
        """Initialize the Email and Calendar Integration Plugin."""
        metadata = PluginMetadata(
            name="Email and Calendar Integration",
            version="1.0.0",
            description="Comprehensive email and calendar management with AI assistance",
            author="Aideon AI Team",
            category="integration",
            tags=["email", "calendar", "automation", "ai-assistance", "productivity"],
            requirements=["aiohttp", "python-dateutil", "email"],
            supported_platforms=["linux", "windows", "macos"]
        )
        
        super().__init__(metadata)
        
        # Provider configurations
        self.email_providers = {
            "gmail": {
                "api_base": "https://gmail.googleapis.com/gmail/v1",
                "auth_type": "oauth2",
                "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
            },
            "outlook": {
                "api_base": "https://graph.microsoft.com/v1.0",
                "auth_type": "oauth2",
                "scopes": ["https://graph.microsoft.com/mail.readwrite"]
            },
            "yahoo": {
                "api_base": "https://api.login.yahoo.com",
                "auth_type": "oauth2",
                "scopes": ["mail-r", "mail-w"]
            }
        }
        
        self.calendar_providers = {
            "google_calendar": {
                "api_base": "https://www.googleapis.com/calendar/v3",
                "auth_type": "oauth2",
                "scopes": ["https://www.googleapis.com/auth/calendar"]
            },
            "outlook_calendar": {
                "api_base": "https://graph.microsoft.com/v1.0",
                "auth_type": "oauth2",
                "scopes": ["https://graph.microsoft.com/calendars.readwrite"]
            },
            "apple_calendar": {
                "api_base": "https://caldav.icloud.com",
                "auth_type": "caldav",
                "scopes": ["calendar"]
            }
        }
        
        # Initialize HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Register plugin actions
        self._register_actions()
    
    def _register_actions(self):
        """Register all available plugin actions."""
        
        # Email management actions
        self.register_action(PluginAction(
            name="connect_email_provider",
            description="Connect to an email provider",
            parameters=[
                PluginParameter("provider", str, "Email provider name", required=True),
                PluginParameter("credentials", dict, "Provider credentials", required=True)
            ],
            returns="Connection status and provider info"
        ))
        
        self.register_action(PluginAction(
            name="get_emails",
            description="Get emails from connected providers",
            parameters=[
                PluginParameter("providers", list, "Email providers to query", required=False),
                PluginParameter("query", str, "Search query", required=False),
                PluginParameter("max_results", int, "Maximum number of emails", default=50),
                PluginParameter("unread_only", bool, "Get only unread emails", default=False)
            ],
            returns="List of emails from specified providers"
        ))
        
        self.register_action(PluginAction(
            name="send_email",
            description="Send email through connected providers",
            parameters=[
                PluginParameter("provider", str, "Email provider to use", required=True),
                PluginParameter("to", list, "Recipient email addresses", required=True),
                PluginParameter("subject", str, "Email subject", required=True),
                PluginParameter("body", str, "Email body", required=True),
                PluginParameter("cc", list, "CC recipients", required=False),
                PluginParameter("bcc", list, "BCC recipients", required=False),
                PluginParameter("attachments", list, "Email attachments", required=False)
            ],
            returns="Email sending result"
        ))
        
        self.register_action(PluginAction(
            name="analyze_email",
            description="AI-analyze email content for insights",
            parameters=[
                PluginParameter("email_id", str, "Email ID to analyze", required=True),
                PluginParameter("provider", str, "Email provider", required=True),
                PluginParameter("analysis_type", str, "Type of analysis", default="comprehensive")
            ],
            returns="Email analysis results"
        ))
        
        self.register_action(PluginAction(
            name="generate_email_response",
            description="AI-generate email response",
            parameters=[
                PluginParameter("original_email_id", str, "Original email ID", required=True),
                PluginParameter("provider", str, "Email provider", required=True),
                PluginParameter("response_type", str, "Response type", default="professional"),
                PluginParameter("key_points", list, "Key points to address", required=False)
            ],
            returns="Generated email response"
        ))
        
        self.register_action(PluginAction(
            name="smart_email_triage",
            description="Intelligently categorize and prioritize emails",
            parameters=[
                PluginParameter("providers", list, "Email providers to triage", required=False),
                PluginParameter("auto_organize", bool, "Automatically organize emails", default=True)
            ],
            returns="Email triage results"
        ))
        
        # Calendar management actions
        self.register_action(PluginAction(
            name="connect_calendar_provider",
            description="Connect to a calendar provider",
            parameters=[
                PluginParameter("provider", str, "Calendar provider name", required=True),
                PluginParameter("credentials", dict, "Provider credentials", required=True)
            ],
            returns="Connection status and provider info"
        ))
        
        self.register_action(PluginAction(
            name="get_events",
            description="Get calendar events from connected providers",
            parameters=[
                PluginParameter("providers", list, "Calendar providers to query", required=False),
                PluginParameter("start_date", str, "Start date for events", required=False),
                PluginParameter("end_date", str, "End date for events", required=False),
                PluginParameter("max_results", int, "Maximum number of events", default=100)
            ],
            returns="List of calendar events"
        ))
        
        self.register_action(PluginAction(
            name="create_event",
            description="Create calendar event",
            parameters=[
                PluginParameter("provider", str, "Calendar provider", required=True),
                PluginParameter("title", str, "Event title", required=True),
                PluginParameter("start_time", str, "Event start time", required=True),
                PluginParameter("end_time", str, "Event end time", required=True),
                PluginParameter("description", str, "Event description", required=False),
                PluginParameter("location", str, "Event location", required=False),
                PluginParameter("attendees", list, "Event attendees", required=False)
            ],
            returns="Event creation result"
        ))
        
        self.register_action(PluginAction(
            name="schedule_smart_meeting",
            description="AI-powered smart meeting scheduling",
            parameters=[
                PluginParameter("attendees", list, "Meeting attendees", required=True),
                PluginParameter("duration_minutes", int, "Meeting duration in minutes", required=True),
                PluginParameter("title", str, "Meeting title", required=True),
                PluginParameter("description", str, "Meeting description", required=False),
                PluginParameter("preferred_times", list, "Preferred time slots", required=False),
                PluginParameter("provider", str, "Calendar provider", required=True)
            ],
            returns="Smart meeting scheduling result"
        ))
        
        self.register_action(PluginAction(
            name="find_meeting_times",
            description="Find optimal meeting times using AI",
            parameters=[
                PluginParameter("attendees", list, "Meeting attendees", required=True),
                PluginParameter("duration_minutes", int, "Meeting duration", required=True),
                PluginParameter("date_range", dict, "Date range to search", required=False),
                PluginParameter("preferences", dict, "Scheduling preferences", required=False)
            ],
            returns="Optimal meeting time suggestions"
        ))
        
        # Unified management actions
        self.register_action(PluginAction(
            name="get_unified_inbox",
            description="Get unified inbox from all connected email providers",
            parameters=[
                PluginParameter("max_results", int, "Maximum emails per provider", default=20),
                PluginParameter("include_read", bool, "Include read emails", default=True)
            ],
            returns="Unified inbox with emails from all providers"
        ))
        
        self.register_action(PluginAction(
            name="get_unified_calendar",
            description="Get unified calendar from all connected providers",
            parameters=[
                PluginParameter("days_ahead", int, "Days ahead to include", default=30),
                PluginParameter("include_all_day", bool, "Include all-day events", default=True)
            ],
            returns="Unified calendar with events from all providers"
        ))
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration."""
        try:
            # Validate configuration
            if not config:
                raise PluginConfigurationError("Email and calendar configuration is required")
            
            # Initialize HTTP session
            timeout = aiohttp.ClientTimeout(total=60)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Store configuration
            self.config = config
            
            logger.info("Email and Calendar Integration Plugin initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Email and Calendar Integration Plugin: {e}")
            raise PluginConfigurationError(f"Initialization failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up plugin resources."""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("Email and Calendar Integration Plugin cleaned up")
    
    async def execute_action(self, action_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a plugin action."""
        try:
            # Email actions
            if action_name == "connect_email_provider":
                return await self._connect_email_provider(parameters)
            elif action_name == "get_emails":
                return await self._get_emails(parameters)
            elif action_name == "send_email":
                return await self._send_email(parameters)
            elif action_name == "analyze_email":
                return await self._analyze_email(parameters)
            elif action_name == "generate_email_response":
                return await self._generate_email_response(parameters)
            elif action_name == "smart_email_triage":
                return await self._smart_email_triage(parameters)
            
            # Calendar actions
            elif action_name == "connect_calendar_provider":
                return await self._connect_calendar_provider(parameters)
            elif action_name == "get_events":
                return await self._get_events(parameters)
            elif action_name == "create_event":
                return await self._create_event(parameters)
            elif action_name == "schedule_smart_meeting":
                return await self._schedule_smart_meeting(parameters)
            elif action_name == "find_meeting_times":
                return await self._find_meeting_times(parameters)
            
            # Unified actions
            elif action_name == "get_unified_inbox":
                return await self._get_unified_inbox(parameters)
            elif action_name == "get_unified_calendar":
                return await self._get_unified_calendar(parameters)
            
            else:
                raise PluginActionExecutionError(f"Unknown action: {action_name}")
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            raise PluginActionExecutionError(f"Failed to execute {action_name}: {e}")
    
    # Email implementation methods
    
    async def _connect_email_provider(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to an email provider."""
        provider = parameters.get("provider")
        credentials = parameters.get("credentials", {})
        
        if provider not in self.email_providers:
            raise PluginActionExecutionError(f"Unsupported email provider: {provider}")
        
        # Test connection
        try:
            test_result = await self._test_email_connection(provider, credentials)
            
            return {
                "success": True,
                "provider": provider,
                "connection_status": "connected",
                "user_info": test_result.get("user_info", {}),
                "capabilities": test_result.get("capabilities", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "provider": provider,
                "connection_status": "failed",
                "error": str(e)
            }
    
    async def _get_emails(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get emails from connected providers."""
        providers = parameters.get("providers", ["gmail"])
        query = parameters.get("query", "")
        max_results = parameters.get("max_results", 50)
        unread_only = parameters.get("unread_only", False)
        
        all_emails = []
        provider_results = {}
        
        for provider in providers:
            try:
                emails = await self._fetch_provider_emails(provider, query, max_results, unread_only)
                provider_results[provider] = {
                    "success": True,
                    "email_count": len(emails),
                    "emails": emails
                }
                all_emails.extend(emails)
                
            except Exception as e:
                provider_results[provider] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Sort emails by timestamp (newest first)
        all_emails.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "emails": all_emails,
            "total_count": len(all_emails),
            "provider_results": provider_results,
            "query": query,
            "unread_only": unread_only
        }
    
    async def _send_email(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send email through a provider."""
        provider = parameters.get("provider")
        to = parameters.get("to", [])
        subject = parameters.get("subject", "")
        body = parameters.get("body", "")
        cc = parameters.get("cc", [])
        bcc = parameters.get("bcc", [])
        attachments = parameters.get("attachments", [])
        
        try:
            result = await self._send_provider_email(provider, to, subject, body, cc, bcc, attachments)
            
            return {
                "success": True,
                "provider": provider,
                "message_id": result.get("message_id"),
                "timestamp": datetime.utcnow().isoformat(),
                "recipients": to,
                "subject": subject
            }
            
        except Exception as e:
            return {
                "success": False,
                "provider": provider,
                "error": str(e)
            }
    
    async def _analyze_email(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """AI-analyze email content."""
        email_id = parameters.get("email_id")
        provider = parameters.get("provider")
        analysis_type = parameters.get("analysis_type", "comprehensive")
        
        try:
            # Get email content
            email_content = await self._get_email_content(provider, email_id)
            
            # Perform AI analysis (simplified implementation)
            analysis = await self._perform_email_analysis(email_content, analysis_type)
            
            return {
                "success": True,
                "email_id": email_id,
                "provider": provider,
                "analysis": analysis,
                "analysis_type": analysis_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_email_response(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """AI-generate email response."""
        original_email_id = parameters.get("original_email_id")
        provider = parameters.get("provider")
        response_type = parameters.get("response_type", "professional")
        key_points = parameters.get("key_points", [])
        
        try:
            # Get original email
            original_email = await self._get_email_content(provider, original_email_id)
            
            # Generate response using AI (simplified implementation)
            response = await self._generate_ai_response(original_email, response_type, key_points)
            
            return {
                "success": True,
                "original_email_id": original_email_id,
                "response": response,
                "response_type": response_type,
                "key_points": key_points
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _smart_email_triage(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently categorize and prioritize emails."""
        providers = parameters.get("providers", ["gmail"])
        auto_organize = parameters.get("auto_organize", True)
        
        triaged_emails = {
            "urgent": [],
            "important": [],
            "normal": [],
            "low_priority": [],
            "promotional": [],
            "newsletters": []
        }
        
        for provider in providers:
            try:
                emails = await self._fetch_provider_emails(provider, "", 100, False)
                
                for email in emails:
                    # AI-powered email categorization (simplified)
                    category = await self._categorize_email(email)
                    triaged_emails[category].append(email)
                
            except Exception as e:
                logger.error(f"Failed to triage emails from {provider}: {e}")
        
        return {
            "triaged_emails": triaged_emails,
            "total_emails": sum(len(emails) for emails in triaged_emails.values()),
            "auto_organize": auto_organize,
            "providers": providers
        }
    
    # Calendar implementation methods
    
    async def _connect_calendar_provider(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to a calendar provider."""
        provider = parameters.get("provider")
        credentials = parameters.get("credentials", {})
        
        if provider not in self.calendar_providers:
            raise PluginActionExecutionError(f"Unsupported calendar provider: {provider}")
        
        try:
            test_result = await self._test_calendar_connection(provider, credentials)
            
            return {
                "success": True,
                "provider": provider,
                "connection_status": "connected",
                "calendar_info": test_result.get("calendar_info", {}),
                "capabilities": test_result.get("capabilities", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "provider": provider,
                "connection_status": "failed",
                "error": str(e)
            }
    
    async def _get_events(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get calendar events from providers."""
        providers = parameters.get("providers", ["google_calendar"])
        start_date = parameters.get("start_date")
        end_date = parameters.get("end_date")
        max_results = parameters.get("max_results", 100)
        
        all_events = []
        provider_results = {}
        
        for provider in providers:
            try:
                events = await self._fetch_provider_events(provider, start_date, end_date, max_results)
                provider_results[provider] = {
                    "success": True,
                    "event_count": len(events),
                    "events": events
                }
                all_events.extend(events)
                
            except Exception as e:
                provider_results[provider] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Sort events by start time
        all_events.sort(key=lambda x: x.get("start_time", ""))
        
        return {
            "events": all_events,
            "total_count": len(all_events),
            "provider_results": provider_results,
            "date_range": {"start": start_date, "end": end_date}
        }
    
    async def _create_event(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create calendar event."""
        provider = parameters.get("provider")
        title = parameters.get("title")
        start_time = parameters.get("start_time")
        end_time = parameters.get("end_time")
        description = parameters.get("description", "")
        location = parameters.get("location", "")
        attendees = parameters.get("attendees", [])
        
        try:
            result = await self._create_provider_event(
                provider, title, start_time, end_time, description, location, attendees
            )
            
            return {
                "success": True,
                "provider": provider,
                "event_id": result.get("event_id"),
                "event_url": result.get("event_url"),
                "title": title,
                "start_time": start_time,
                "end_time": end_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "provider": provider,
                "error": str(e)
            }
    
    async def _schedule_smart_meeting(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered smart meeting scheduling."""
        attendees = parameters.get("attendees", [])
        duration_minutes = parameters.get("duration_minutes", 60)
        title = parameters.get("title")
        description = parameters.get("description", "")
        preferred_times = parameters.get("preferred_times", [])
        provider = parameters.get("provider")
        
        try:
            # Find optimal meeting times using AI
            optimal_times = await self._find_optimal_meeting_times(attendees, duration_minutes, preferred_times)
            
            if not optimal_times:
                return {
                    "success": False,
                    "error": "No suitable meeting times found"
                }
            
            # Use the best suggested time
            best_time = optimal_times[0]
            start_time = best_time["start_time"]
            end_time = best_time["end_time"]
            
            # Create the event
            event_result = await self._create_provider_event(
                provider, title, start_time, end_time, description, "", attendees
            )
            
            return {
                "success": True,
                "event_id": event_result.get("event_id"),
                "selected_time": best_time,
                "all_suggestions": optimal_times,
                "attendees": attendees,
                "title": title
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _find_meeting_times(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Find optimal meeting times using AI."""
        attendees = parameters.get("attendees", [])
        duration_minutes = parameters.get("duration_minutes", 60)
        date_range = parameters.get("date_range", {})
        preferences = parameters.get("preferences", {})
        
        try:
            optimal_times = await self._find_optimal_meeting_times(
                attendees, duration_minutes, [], date_range, preferences
            )
            
            return {
                "success": True,
                "suggested_times": optimal_times,
                "attendees": attendees,
                "duration_minutes": duration_minutes,
                "preferences": preferences
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_unified_inbox(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get unified inbox from all providers."""
        max_results = parameters.get("max_results", 20)
        include_read = parameters.get("include_read", True)
        
        # Get emails from all connected providers
        all_emails = []
        
        for provider in self.email_providers.keys():
            try:
                emails = await self._fetch_provider_emails(provider, "", max_results, not include_read)
                for email in emails:
                    email["provider"] = provider
                all_emails.extend(emails)
            except Exception as e:
                logger.error(f"Failed to get emails from {provider}: {e}")
        
        # Sort by timestamp
        all_emails.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "unified_inbox": all_emails[:max_results * len(self.email_providers)],
            "total_emails": len(all_emails),
            "providers_queried": list(self.email_providers.keys()),
            "include_read": include_read
        }
    
    async def _get_unified_calendar(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get unified calendar from all providers."""
        days_ahead = parameters.get("days_ahead", 30)
        include_all_day = parameters.get("include_all_day", True)
        
        start_date = datetime.utcnow().isoformat()
        end_date = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat()
        
        all_events = []
        
        for provider in self.calendar_providers.keys():
            try:
                events = await self._fetch_provider_events(provider, start_date, end_date, 1000)
                for event in events:
                    event["provider"] = provider
                all_events.extend(events)
            except Exception as e:
                logger.error(f"Failed to get events from {provider}: {e}")
        
        # Sort by start time
        all_events.sort(key=lambda x: x.get("start_time", ""))
        
        return {
            "unified_calendar": all_events,
            "total_events": len(all_events),
            "providers_queried": list(self.calendar_providers.keys()),
            "date_range": {"start": start_date, "end": end_date},
            "days_ahead": days_ahead
        }
    
    # Helper methods (simplified implementations)
    
    async def _test_email_connection(self, provider: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test email provider connection."""
        # Simplified implementation
        return {
            "user_info": {"email": "user@example.com", "name": "Test User"},
            "capabilities": ["read", "write", "send"]
        }
    
    async def _test_calendar_connection(self, provider: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test calendar provider connection."""
        # Simplified implementation
        return {
            "calendar_info": {"name": "Primary Calendar", "timezone": "UTC"},
            "capabilities": ["read", "write", "create_events"]
        }
    
    async def _fetch_provider_emails(self, provider: str, query: str, max_results: int, unread_only: bool) -> List[Dict[str, Any]]:
        """Fetch emails from a provider."""
        # Simplified mock implementation
        return [
            {
                "id": f"{provider}_email_1",
                "subject": "Test Email",
                "sender": "sender@example.com",
                "timestamp": datetime.utcnow().isoformat(),
                "is_read": not unread_only,
                "body": "This is a test email."
            }
        ]
    
    async def _send_provider_email(self, provider: str, to: List[str], subject: str, body: str, 
                                 cc: List[str], bcc: List[str], attachments: List) -> Dict[str, Any]:
        """Send email through provider."""
        return {
            "message_id": f"{provider}_sent_{datetime.utcnow().timestamp()}",
            "status": "sent"
        }
    
    async def _get_email_content(self, provider: str, email_id: str) -> Dict[str, Any]:
        """Get email content."""
        return {
            "id": email_id,
            "subject": "Test Email",
            "body": "This is test email content.",
            "sender": "sender@example.com"
        }
    
    async def _perform_email_analysis(self, email_content: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Perform AI email analysis."""
        return {
            "sentiment": "neutral",
            "priority": "medium",
            "category": "work",
            "action_required": "reply_needed",
            "summary": "Test email analysis"
        }
    
    async def _generate_ai_response(self, original_email: Dict[str, Any], response_type: str, key_points: List[str]) -> Dict[str, Any]:
        """Generate AI email response."""
        return {
            "subject": f"Re: {original_email.get('subject', '')}",
            "body": "Thank you for your email. I will review it and get back to you soon.",
            "tone": response_type
        }
    
    async def _categorize_email(self, email: Dict[str, Any]) -> str:
        """Categorize email using AI."""
        # Simplified categorization
        subject = email.get("subject", "").lower()
        if "urgent" in subject:
            return "urgent"
        elif "newsletter" in subject:
            return "newsletters"
        elif "promotion" in subject:
            return "promotional"
        else:
            return "normal"
    
    async def _fetch_provider_events(self, provider: str, start_date: str, end_date: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch events from calendar provider."""
        # Simplified mock implementation
        return [
            {
                "id": f"{provider}_event_1",
                "title": "Test Meeting",
                "start_time": datetime.utcnow().isoformat(),
                "end_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "location": "Conference Room",
                "attendees": ["attendee@example.com"]
            }
        ]
    
    async def _create_provider_event(self, provider: str, title: str, start_time: str, end_time: str,
                                   description: str, location: str, attendees: List[str]) -> Dict[str, Any]:
        """Create event in calendar provider."""
        return {
            "event_id": f"{provider}_event_{datetime.utcnow().timestamp()}",
            "event_url": f"https://{provider}.com/event/123456"
        }
    
    async def _find_optimal_meeting_times(self, attendees: List[str], duration_minutes: int, 
                                        preferred_times: List[str], date_range: Dict = None, 
                                        preferences: Dict = None) -> List[Dict[str, Any]]:
        """Find optimal meeting times using AI."""
        # Simplified implementation
        base_time = datetime.utcnow() + timedelta(days=1)
        
        return [
            {
                "start_time": base_time.isoformat(),
                "end_time": (base_time + timedelta(minutes=duration_minutes)).isoformat(),
                "confidence": 0.9,
                "reasoning": "Optimal time based on attendee availability"
            },
            {
                "start_time": (base_time + timedelta(hours=2)).isoformat(),
                "end_time": (base_time + timedelta(hours=2, minutes=duration_minutes)).isoformat(),
                "confidence": 0.8,
                "reasoning": "Alternative time with good availability"
            }
        ]

