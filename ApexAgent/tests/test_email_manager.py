import sys
import os

# Add project root to PYTHONPATH to allow imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.plugins.email_manager import EmailManager

# Mock ApiKeyManager for standalone testing
class MockApiKeyManager:
    def __init__(self):
        self.oauth_tokens = {
            "gmail": {"access_token": "mock_gmail_access_token", "refresh_token": "mock_gmail_refresh"},
            "outlook": {"access_token": "mock_outlook_access_token", "refresh_token": "mock_outlook_refresh"}
        }

    def get_oauth_token(self, service_name):
        return self.oauth_tokens.get(service_name)

def main():
    print("--- Testing EmailManager Plugin ---")
    mock_api_manager = MockApiKeyManager()
    email_plugin = EmailManager(api_key_manager=mock_api_manager)
    test_save_path = os.path.join(os.path.dirname(__file__), "test_attachment.txt") # Ensure save path is valid

    # Test list_emails
    print("\nTesting list_emails...")
    gmail_emails = email_plugin.list_emails(service="gmail")
    assert isinstance(gmail_emails, list) and len(gmail_emails) > 0, "list_emails for gmail failed or returned empty"
    print("Gmail Emails:", gmail_emails)
    outlook_emails = email_plugin.list_emails(service="outlook", folder="Inbox")
    assert isinstance(outlook_emails, list) and len(outlook_emails) > 0, "list_emails for outlook failed or returned empty"
    print("Outlook Emails:", outlook_emails)

    # Test get_email
    print("\nTesting get_email...")
    gmail_email_details = email_plugin.get_email(service="gmail", email_id="gmail_email_1")
    assert gmail_email_details and "id" in gmail_email_details and gmail_email_details["id"] == "gmail_email_1", "get_email for gmail failed"
    print("Gmail Email Details (gmail_email_1):", gmail_email_details)

    # Test send_email
    print("\nTesting send_email...")
    send_payload = {
        "service": "gmail",
        "to_recipients": ["recipient1@example.com"],
        "subject": "ApexAgent Test Email",
        "body_text": "This is a test email from ApexAgent."
    }
    sent_email_info = email_plugin.send_email(**send_payload)
    assert sent_email_info and "id" in sent_email_info and sent_email_info.get("status") == "sent", "send_email failed"
    print("Sent Email Info:", sent_email_info)

    # Test draft_email
    print("\nTesting draft_email...")
    draft_payload = {
        "service": "outlook",
        "to_recipients": ["draft_recipient@example.com"],
        "subject": "ApexAgent Draft Email",
        "body_html": "<p>This is a test draft email from ApexAgent.</p>"
    }
    draft_email_info = email_plugin.draft_email(**draft_payload)
    assert draft_email_info and "id" in draft_email_info and draft_email_info.get("status") == "draft", "draft_email failed"
    print("Draft Email Info:", draft_email_info)

    # Test mark_email_as_read_unread
    print("\nTesting mark_email_as_read_unread...")
    mark_read_result = email_plugin.mark_email_as_read_unread(service="gmail", email_id="gmail_email_1", mark_as="read")
    assert mark_read_result and mark_read_result.get("status") == "success", "mark_email_as_read failed"
    print("Mark as Read Result:", mark_read_result)
    mark_unread_result = email_plugin.mark_email_as_read_unread(service="outlook", email_id="outlook_email_1", mark_as="unread")
    assert mark_unread_result and mark_unread_result.get("status") == "success", "mark_email_as_unread failed"
    print("Mark as Unread Result:", mark_unread_result)

    # Test archive_email
    print("\nTesting archive_email...")
    archive_result = email_plugin.archive_email(service="gmail", email_id="gmail_email_1")
    assert archive_result and archive_result.get("status") == "success", "archive_email failed"
    print("Archive Email Result:", archive_result)

    # Test delete_email
    print("\nTesting delete_email...")
    delete_result = email_plugin.delete_email(service="outlook", email_id="outlook_email_1")
    assert delete_result and delete_result.get("status") == "success", "delete_email failed"
    print("Delete Email Result:", delete_result)

    # Test download_attachment (mock will create a dummy file)
    print("\nTesting download_attachment...")
    download_result = email_plugin.download_attachment(service="gmail", email_id="gmail_email_1", attachment_id="dummy_attach_id", save_path=test_save_path)
    assert download_result and download_result.get("status") == "success" and os.path.exists(test_save_path), "download_attachment failed or file not created"
    print("Download Attachment Result:", download_result)
    if os.path.exists(test_save_path):
        os.remove(test_save_path) # Clean up
        print(f"Cleaned up {test_save_path}")

    # Test create_folder
    print("\nTesting create_folder...")
    created_folder = email_plugin.create_folder(service="gmail", folder_name="ApexAgent Test Folder")
    assert created_folder and "id" in created_folder and created_folder.get("status") == "success", "create_folder failed"
    print("Created Folder:", created_folder)
    created_folder_id = created_folder["id"]

    # Test rename_folder
    print("\nTesting rename_folder...")
    renamed_folder = email_plugin.rename_folder(service="gmail", folder_id=created_folder_id, new_name="ApexAgent Renamed Folder")
    assert renamed_folder and renamed_folder.get("name") == "ApexAgent Renamed Folder", "rename_folder failed"
    print("Renamed Folder:", renamed_folder)

    # Test delete_folder
    print("\nTesting delete_folder...")
    deleted_folder_result = email_plugin.delete_folder(service="gmail", folder_id=created_folder_id)
    assert deleted_folder_result and deleted_folder_result.get("status") == "success", "delete_folder failed"
    print("Delete Folder Result:", deleted_folder_result)

    # Test search_emails
    print("\nTesting search_emails...")
    search_results = email_plugin.search_emails(service="gmail", query="important")
    assert isinstance(search_results, list), "search_emails failed to return a list"
    print("Search Results for 'important':", search_results)

    print("\n--- EmailManager Plugin Test Completed Successfully ---")

if __name__ == "__main__":
    main()

