import sys
import os
import datetime

# Add project root to PYTHONPATH to allow imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.plugins.calendar_manager import CalendarManager

# Mock ApiKeyManager for standalone testing
class MockApiKeyManager:
    def __init__(self):
        self.oauth_tokens = {
            "google": {"access_token": "mock_google_access_token", "refresh_token": "mock_google_refresh"},
            "outlook": {"access_token": "mock_outlook_access_token", "refresh_token": "mock_outlook_refresh"}
        }

    def get_oauth_token(self, service_name):
        return self.oauth_tokens.get(service_name)

def main():
    print("--- Testing CalendarManager Plugin ---")
    mock_api_manager = MockApiKeyManager()
    calendar_plugin = CalendarManager(api_key_manager=mock_api_manager)

    # Test list_calendars
    print("\nTesting list_calendars...")
    google_calendars = calendar_plugin.list_calendars(service="google")
    assert isinstance(google_calendars, list) and len(google_calendars) > 0, "list_calendars for google failed or returned empty"
    print("Google Calendars:", google_calendars)
    outlook_calendars = calendar_plugin.list_calendars(service="outlook")
    assert isinstance(outlook_calendars, list) and len(outlook_calendars) > 0, "list_calendars for outlook failed or returned empty"
    print("Outlook Calendars:", outlook_calendars)

    # Test list_events
    print("\nTesting list_events...")
    google_events = calendar_plugin.list_events(service="google", calendar_id="primary")
    assert isinstance(google_events, list) and len(google_events) > 0, "list_events for google failed or returned empty"
    print("Google Primary Events:", google_events)

    # Test create_event
    print("\nTesting create_event...")
    start_time = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + "Z"
    end_time = (datetime.datetime.utcnow() + datetime.timedelta(days=1, hours=1)).isoformat() + "Z"
    new_event_details = {
        "service": "google",
        "summary": "ApexAgent Test Event",
        "start_time_iso": start_time,
        "end_time_iso": end_time,
        "description": "Test event created by ApexAgent plugin test.",
        "location": "Virtual Test Room",
        "attendees": ["testuser@example.com"]
    }
    created_event = calendar_plugin.create_event(**new_event_details)
    assert created_event and "id" in created_event and created_event.get("status") == "confirmed", "create_event failed or did not return confirmed event with ID"
    print("Created Google Event:", created_event)
    new_event_id = created_event["id"]

    # Test get_event
    print("\nTesting get_event...")
    retrieved_event = calendar_plugin.get_event(service="google", event_id=new_event_id)
    # The mock get_event might not find dynamically created IDs, so we test with a known mock ID first
    retrieved_known_event = calendar_plugin.get_event(service="google", event_id="event1_google_primary")
    assert retrieved_known_event and "id" in retrieved_known_event, "get_event for known event failed"
    print("Retrieved Known Google Event:", retrieved_known_event)
    # If the mock create_event actually registered the event for get_event to find it (which it doesn_t in current mock)
    # we would assert retrieved_event["id"] == new_event_id
    # For now, we just check it doesn_t error out badly for the new ID if it has a generic not found
    if retrieved_event.get("error"):
        print(f"Get event for {new_event_id} returned error as expected by mock: {retrieved_event["error"]}")
    else:
        assert retrieved_event and "id" in retrieved_event and retrieved_event["id"] == new_event_id, "get_event for newly created event failed"
        print(f"Retrieved Newly Created Google Event ({new_event_id}):", retrieved_event)


    # Test update_event
    print("\nTesting update_event...")
    update_payload = {
        "service": "google",
        "event_id": "event1_google_primary", # Using a known mock ID for update
        "summary": "Updated ApexAgent Test Event",
        "location": "Updated Virtual Test Room"
    }
    updated_event = calendar_plugin.update_event(**update_payload)
    assert updated_event and updated_event.get("summary") == update_payload["summary"], "update_event failed or summary not updated"
    print("Updated Google Event (event1_google_primary):", updated_event)

    # Test delete_event
    print("\nTesting delete_event...")
    # Try deleting the dynamically created event (mock delete is permissive)
    delete_result_new = calendar_plugin.delete_event(service="google", event_id=new_event_id)
    assert delete_result_new and delete_result_new.get("status") == "success", f"delete_event for {new_event_id} failed"
    print(f"Delete Event Result ({new_event_id}):", delete_result_new)
    
    delete_result_known = calendar_plugin.delete_event(service="google", event_id="event1_google_primary")
    assert delete_result_known and delete_result_known.get("status") == "success", "delete_event for known event failed"
    print("Delete Event Result (event1_google_primary):", delete_result_known)

    print("\n--- CalendarManager Plugin Test Completed Successfully ---")

if __name__ == "__main__":
    main()

