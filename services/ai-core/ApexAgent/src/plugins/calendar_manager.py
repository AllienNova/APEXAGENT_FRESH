# Plugin: Calendar Management
import datetime

class CalendarManager:
    def __init__(self, api_key_manager=None):
        """
        Initializes the CalendarManager.
        Args:
            api_key_manager: An instance of ApiKeyManager to handle API keys/OAuth tokens.
        """
        self.api_key_manager = api_key_manager
        # In a real implementation, API clients (e.g., for Google, Outlook)
        # would be initialized here, likely using credentials from api_key_manager.
        print("CalendarManager initialized.")

    def _get_service_client(self, service_name: str):
        """Helper to get an authenticated client for the specified service."""
        if not self.api_key_manager:
            print(f"Error: ApiKeyManager not provided to CalendarManager.")
            return None
        
        token_info = self.api_key_manager.get_oauth_token(service_name)
        if not token_info:
            print(f"Error: OAuth token for {service_name} not found or expired.")
            # Here, you might trigger a re-authentication flow or notify the user.
            return None
        
        # Placeholder: Actual client initialization would happen here
        # For example, using google-api-python-client or microsoft-graph-client
        # from googleapiclient.discovery import build
        # from google.oauth2.credentials import Credentials
        # credentials = Credentials(token_info.get("access_token"), refresh_token=token_info.get("refresh_token"), ...)
        # service_client = build("calendar", "v3", credentials=credentials)
        # return service_client
        print(f"Authenticated client for {service_name} would be created here.")
        return f"{service_name.capitalize()}ServiceClientMock(token_access_token={token_info.get('access_token')[:10]}...)" # Mock client

    def list_calendars(self, service: str):
        """List all calendars for the specified service (e.g., google, outlook)."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}
        
        print(f"Listing calendars for {service} using client: {client}")
        # Actual API call placeholder
        if service == "google":
            return [{"id": "primary", "name": "Google Primary Calendar", "description": "Main calendar", "primary": True},
                    {"id": "work_cal_google", "name": "Google Work Calendar", "description": "Work related events", "primary": False}]
        elif service == "outlook":
            return [{"id": "primary", "name": "Outlook Primary Calendar", "description": "Main calendar", "primary": True}]
        else:
            return {"error": "Unsupported calendar service"}

    def list_events(self, service: str, calendar_id: str = "primary", start_time_iso: str = None, end_time_iso: str = None, query: str = None, max_results: int = 20):
        """Retrieves events from a specified calendar within a given time range."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        if not start_time_iso:
            start_time_iso = datetime.datetime.utcnow().isoformat() + "Z" # Default to now
        if not end_time_iso:
            end_time_iso = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + "Z" # Default to 7 days from now

        print(f"Listing events for {service}, calendar {calendar_id} from {start_time_iso} to {end_time_iso} using client: {client}")
        # Actual API call placeholder
        if (service == "google" and calendar_id == "primary") or (service == "outlook" and calendar_id == "primary") :
            return [
                {
                    "id": "event1_google_primary" if service == "google" else "event1_outlook_primary",
                    "summary": "Team Meeting", "description": "Weekly team sync for Project Phoenix",
                    "start_time": "2024-05-20T10:00:00Z", "end_time": "2024-05-20T11:00:00Z",
                    "location": "Office Room A101", "attendees": ["alice@example.com", "bob@example.com"],
                    "organizer": "scheduler@example.com", "html_link": f"https://calendar.{service}.com/event1"
                },
                {
                    "id": "event2_google_primary" if service == "google" else "event2_outlook_primary", 
                    "summary": "Client Call", "description": "Discuss Q3 strategy with Client X",
                    "start_time": "2024-05-21T14:00:00Z", "end_time": "2024-05-21T15:00:00Z",
                    "location": "Virtual Meeting", "attendees": ["client.rep@client.com", "bob@example.com"],
                    "organizer": "bob@example.com", "html_link": f"https://calendar.{service}.com/event2"
                }
            ]
        return []

    def create_event(self, service: str, calendar_id: str = "primary", summary: str = None, start_time_iso: str = None, end_time_iso: str = None, description: str = None, location: str = None, attendees: list = None, timezone: str = None):
        """Creates a new event in a specified calendar."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}
        
        if not all([summary, start_time_iso, end_time_iso]):
            return {"error": "Missing required fields: summary, start_time_iso, or end_time_iso"}

        print(f"Creating event for {service}, calendar {calendar_id} with summary 
              \"{summary}\" from {start_time_iso} to {end_time_iso} using client: {client}")
        # Actual API call placeholder
        new_event_id = f"newEvent_{datetime.datetime.utcnow().timestamp()}"
        return {
            "id": new_event_id, "summary": summary, "description": description,
            "start_time": start_time_iso, "end_time": end_time_iso,
            "location": location, "attendees": attendees if attendees else [],
            "organizer": "current_user@example.com", "html_link": f"https://calendar.{service}.com/{new_event_id}",
            "status": "confirmed"
        }

    def get_event(self, service: str, event_id: str, calendar_id: str = "primary"):
        """Retrieves a specific event by its ID."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Getting event {event_id} for {service}, calendar {calendar_id} using client: {client}")
        # Actual API call placeholder - assuming event1 exists for demo
        if event_id == ("event1_google_primary" if service == "google" else "event1_outlook_primary"):
            return {
                "id": event_id,
                "summary": "Team Meeting", "description": "Weekly team sync for Project Phoenix",
                "start_time": "2024-05-20T10:00:00Z", "end_time": "2024-05-20T11:00:00Z",
                "location": "Office Room A101", "attendees": ["alice@example.com", "bob@example.com"],
                "organizer": "scheduler@example.com", "html_link": f"https://calendar.{service}.com/event1"
            }
        return {"error": "Event not found"}

    def update_event(self, service: str, event_id: str, calendar_id: str = "primary", summary: str = None, start_time_iso: str = None, end_time_iso: str = None, description: str = None, location: str = None, attendees: list = None, timezone: str = None):
        """Updates an existing event."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Updating event {event_id} for {service}, calendar {calendar_id} using client: {client}")
        # Actual API call placeholder - fetch existing, update, save
        # For demo, assume it exists and we return the updated mock data
        if event_id == ("event1_google_primary" if service == "google" else "event1_outlook_primary"):
            updated_event_data = {
                "id": event_id,
                "summary": summary if summary else "Team Meeting (Updated)", 
                "description": description if description else "Weekly team sync for Project Phoenix - updated details",
                "start_time": start_time_iso if start_time_iso else "2024-05-20T10:00:00Z", 
                "end_time": end_time_iso if end_time_iso else "2024-05-20T11:30:00Z", # Example: extended duration
                "location": location if location else "Office Room A102 (New)", 
                "attendees": attendees if attendees else ["alice@example.com", "bob@example.com", "charlie@example.com"],
                "organizer": "scheduler@example.com", "html_link": f"https://calendar.{service}.com/{event_id}"
            }
            return updated_event_data
        return {"error": "Event not found for update"}

    def delete_event(self, service: str, event_id: str, calendar_id: str = "primary"):
        """Deletes an event."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Deleting event {event_id} for {service}, calendar {calendar_id} using client: {client}")
        # Actual API call placeholder
        # For demo, assume deletion is successful if event might exist
        if event_id.startswith("event") or event_id.startswith("newEvent"):
            return {"status": "success", "message": f"Event {event_id} deleted successfully."}
        return {"error": "Event not found or already deleted"}

# Example usage (for testing, not part of the plugin itself)
if __name__ == "__main__":
    # Mock ApiKeyManager for standalone testing
    class MockApiKeyManager:
        def get_oauth_token(self, service_name):
            if service_name in ["google", "outlook"]:
                return {"access_token": f"mock_access_token_for_{service_name}", "refresh_token": "mock_refresh"}
            return None

    mock_manager = MockApiKeyManager()
    calendar_plugin = CalendarManager(api_key_manager=mock_manager)

    print("--- List Calendars ---")
    print("Google:", calendar_plugin.list_calendars(service="google"))
    print("Outlook:", calendar_plugin.list_calendars(service="outlook"))

    print("\n--- List Events ---")
    print("Google Primary:", calendar_plugin.list_events(service="google", calendar_id="primary"))

    print("\n--- Create Event ---")
    new_event = calendar_plugin.create_event(
        service="google", 
        summary="My New API Event", 
        start_time_iso="2024-05-25T10:00:00Z", 
        end_time_iso="2024-05-25T11:00:00Z", 
        description="Discussing important matters.",
        location="Virtual",
        attendees=["test@example.com"]
    )
    print("Created Google Event:", new_event)
    new_event_id_google = new_event.get("id")

    print("\n--- Get Event ---")
    if new_event_id_google:
      print("Get Created Google Event:", calendar_plugin.get_event(service="google", event_id=new_event_id_google))
    print("Get Existing Google Event:", calendar_plugin.get_event(service="google", event_id="event1_google_primary"))

    print("\n--- Update Event ---")
    if new_event_id_google:
        updated_event = calendar_plugin.update_event(
            service="google", 
            event_id=new_event_id_google, 
            summary="My Updated API Event", 
            location="Virtual - Confirmed"
        )
        print("Updated Google Event:", updated_event)

    print("\n--- Delete Event ---")
    if new_event_id_google:
        print("Delete Google Event:", calendar_plugin.delete_event(service="google", event_id=new_event_id_google))
    print("Delete Non-existent Event:", calendar_plugin.delete_event(service="google", event_id="non_existent_event"))


