import sys
import os

# Add project root to PYTHONPATH to allow imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.plugins.team_chat_manager import TeamChatManager

# Mock ApiKeyManager for standalone testing
class MockApiKeyManager:
    def __init__(self):
        self.oauth_tokens = {
            "slack": {"access_token": "mock_slack_access_token", "refresh_token": "mock_slack_refresh"},
            "msteams": {"access_token": "mock_msteams_access_token", "refresh_token": "mock_msteams_refresh"}
        }
        self.api_keys = {}

    def get_oauth_token(self, service_name):
        return self.oauth_tokens.get(service_name)
    
    def get_api_key(self, service_name):
        return self.api_keys.get(service_name)

def main():
    print("--- Testing TeamChatManager Plugin ---")
    mock_api_manager = MockApiKeyManager()
    chat_plugin = TeamChatManager(api_key_manager=mock_api_manager)

    test_dir = os.path.dirname(__file__)
    local_chat_upload_file_path = os.path.join(test_dir, "test_chat_upload.txt")

    # Create a dummy file for upload tests
    with open(local_chat_upload_file_path, "w") as f:
        f.write("This is a test file for chat upload by ApexAgent.")

    # Test list_channels_teams
    print("\nTesting list_channels_teams...")
    slack_channels = chat_plugin.list_channels_teams(service="slack")
    assert isinstance(slack_channels, list) and len(slack_channels) > 0, "list_channels_teams for slack failed or returned empty"
    print("Slack Channels:", slack_channels)
    msteams_teams = chat_plugin.list_channels_teams(service="msteams")
    assert isinstance(msteams_teams, list) and len(msteams_teams) > 0, "list_channels_teams for msteams failed or returned empty"
    print("MS Teams:", msteams_teams)

    # Test send_message
    print("\nTesting send_message...")
    send_slack_payload = {
        "service": "slack",
        "channel_id_or_user_id": "slack_channel_1", # From mock data
        "message_text": "Hello from ApexAgent TeamChatManager test!"
    }
    sent_slack_message = chat_plugin.send_message(**send_slack_payload)
    assert sent_slack_message and "message_id" in sent_slack_message and sent_slack_message.get("status") == "sent", "send_message to slack failed"
    print("Sent Slack Message Info:", sent_slack_message)

    # Test get_messages
    print("\nTesting get_messages...")
    slack_messages = chat_plugin.get_messages(service="slack", channel_id_or_user_id="slack_channel_1")
    assert isinstance(slack_messages, list) and len(slack_messages) > 0, "get_messages from slack failed or returned empty"
    print("Slack Messages (slack_channel_1):", slack_messages)

    # Test create_channel_team
    print("\nTesting create_channel_team...")
    created_slack_channel = chat_plugin.create_channel_team(service="slack", name="#apexagent-test-channel", description="Test channel by ApexAgent")
    assert created_slack_channel and "id" in created_slack_channel and created_slack_channel.get("status") == "created", "create_channel_team for slack failed"
    print("Created Slack Channel Info:", created_slack_channel)
    new_slack_channel_id = created_slack_channel["id"]

    # Test add_user_to_channel_team
    print("\nTesting add_user_to_channel_team...")
    if new_slack_channel_id:
        add_user_result = chat_plugin.add_user_to_channel_team(service="slack", channel_id_or_team_id=new_slack_channel_id, user_id_to_add="U_TESTUSER")
        assert add_user_result and add_user_result.get("status") == "success", "add_user_to_channel_team for slack failed"
        print("Add User to Slack Channel Result:", add_user_result)
    else:
        print("Skipping add_user_to_channel_team test as channel creation failed.")

    # Test upload_file_to_chat
    print("\nTesting upload_file_to_chat...")
    if new_slack_channel_id:
        upload_result = chat_plugin.upload_file_to_chat(service="slack", channel_id_or_user_id=new_slack_channel_id, local_file_path=local_chat_upload_file_path, initial_comment="Test file upload from ApexAgent.")
        assert upload_result and "file_id" in upload_result and upload_result.get("status") == "uploaded", "upload_file_to_chat for slack failed"
        print("Upload File to Slack Result:", upload_result)
    else:
        print("Skipping upload_file_to_chat test as channel creation failed.")

    # Clean up the dummy upload file
    if os.path.exists(local_chat_upload_file_path):
        os.remove(local_chat_upload_file_path)
        print(f"Cleaned up {local_chat_upload_file_path}")

    print("\n--- TeamChatManager Plugin Test Completed Successfully ---")

if __name__ == "__main__":
    main()

