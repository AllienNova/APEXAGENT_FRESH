# Plugin: Email Management

class EmailManager:
    def __init__(self, api_key_manager=None):
        """
        Initializes the EmailManager.
        Args:
            api_key_manager: An instance of ApiKeyManager to handle API keys/OAuth tokens.
        """
        self.api_key_manager = api_key_manager
        # In a real implementation, API clients (e.g., for Gmail, Outlook)
        # would be initialized here, likely using credentials from api_key_manager.
        print("EmailManager initialized.")

    def _get_service_client(self, service_name: str):
        """Helper to get an authenticated client for the specified service."""
        if not self.api_key_manager:
            print(f"Error: ApiKeyManager not provided to EmailManager.")
            return None
        
        token_info = self.api_key_manager.get_oauth_token(service_name)
        if not token_info:
            print(f"Error: OAuth token for {service_name} not found or expired.")
            # Here, you might trigger a re-authentication flow or notify the user.
            return None
        
        # Placeholder: Actual client initialization would happen here
        # For example, using google-api-python-client for Gmail or Microsoft Graph SDK for Outlook
        print(f"Authenticated client for {service_name} would be created here.")
        return f"{service_name.capitalize()}ServiceClientMock(token_access_token={token_info.get("access_token")[:10]}...)"

    def list_emails(self, service: str, folder: str = "INBOX", query: str = None, max_results: int = 20, include_body: bool = False, unread_only: bool = False):
        """Retrieves a list of emails from a specified folder/label."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Listing emails for {service}, folder {folder} with query 
              \"{query}\" using client: {client}")
        # Actual API call placeholder
        # This would involve using the client to fetch emails based on the parameters.
        # The response would be formatted into a list of email objects.
        if service == "gmail":
            return [
                {
                    "id": "gmail_email_1",
                    "thread_id": "gmail_thread_1",
                    "subject": "Important Update",
                    "sender": "sender@example.com",
                    "recipients": ["recipient@example.com"],
                    "date_received": "2024-05-12T10:00:00Z",
                    "snippet": "This is an important update regarding...",
                    "body": "Full email body here..." if include_body else None,
                    "is_read": False,
                    "attachments": []
                }
            ]
        elif service == "outlook":
            return [
                {
                    "id": "outlook_email_1",
                    "thread_id": "outlook_thread_1",
                    "subject": "Meeting Invitation",
                    "sender": "organizer@example.com",
                    "recipients": ["attendee@example.com"],
                    "date_received": "2024-05-12T11:00:00Z",
                    "snippet": "You are invited to a meeting...",
                    "body": "Full email body here..." if include_body else None,
                    "is_read": True,
                    "attachments": []
                }
            ]
        return []

    def get_email(self, service: str, email_id: str, format: str = "full"):
        """Retrieves a specific email by its ID."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Getting email {email_id} for {service} using client: {client}")
        # Actual API call placeholder
        # This would use the client to fetch the specific email details.
        if email_id == "gmail_email_1" and service == "gmail":
            return {
                "id": "gmail_email_1",
                "thread_id": "gmail_thread_1",
                "subject": "Important Update",
                "sender": "sender@example.com",
                "recipients": ["recipient@example.com"],
                "date_received": "2024-05-12T10:00:00Z",
                "body": "This is the full email body for the important update.",
                "is_read": False,
                "attachments": []
            }
        return {"error": "Email not found"}

    def send_email(self, service: str, to_recipients: list, subject: str, body_text: str = None, body_html: str = None, cc_recipients: list = None, bcc_recipients: list = None, attachments: list = None):
        """Composes and sends a new email."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}
        
        if not to_recipients or not (body_text or body_html):
            return {"error": "Missing required fields: to_recipients and either body_text or body_html"}

        print(f"Sending email via {service} to {to_recipients} with subject 
              \"{subject}\" using client: {client}")
        # Actual API call placeholder
        # This would use the client to construct and send the email.
        return {"id": "sent_email_123", "thread_id": "thread_abc", "status": "sent"}

    def draft_email(self, service: str, to_recipients: list = None, subject: str = None, body_text: str = None, body_html: str = None, cc_recipients: list = None, bcc_recipients: list = None, attachments: list = None):
        """Creates a draft email."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Creating draft email via {service} using client: {client}")
        # Actual API call placeholder
        return {"id": "draft_email_456", "thread_id": "thread_def", "status": "draft"}

    def mark_email_as_read_unread(self, service: str, email_id: str, mark_as: str = "read"):
        """Marks an email as read or unread."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Marking email {email_id} as {mark_as} for {service} using client: {client}")
        # Actual API call placeholder
        return {"status": "success", "message": f"Email {email_id} marked as {mark_as}."}

    def archive_email(self, service: str, email_id: str):
        """Archives an email."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Archiving email {email_id} for {service} using client: {client}")
        # Actual API call placeholder
        return {"status": "success", "message": f"Email {email_id} archived."}

    def delete_email(self, service: str, email_id: str):
        """Deletes an email (moves to trash or permanently deletes based on service defaults)."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Deleting email {email_id} for {service} using client: {client}")
        # Actual API call placeholder
        return {"status": "success", "message": f"Email {email_id} deleted."}

    def download_attachment(self, service: str, email_id: str, attachment_id: str, save_path: str):
        """Downloads an email attachment."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Downloading attachment {attachment_id} from email {email_id} for {service} to {save_path} using client: {client}")
        # Actual API call placeholder
        # This would involve fetching the attachment data and saving it to save_path.
        # For now, we simulate success.
        try:
            with open(save_path, "w") as f:
                f.write("This is a dummy attachment content.")
            return {"file_path": save_path, "status": "success"}
        except Exception as e:
            return {"error": f"Failed to save attachment: {str(e)}"}

    def create_folder(self, service: str, folder_name: str):
        """Creates a new email folder/label."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Creating folder {folder_name} for {service} using client: {client}")
        # Actual API call placeholder
        return {"id": f"folder_{folder_name.lower().replace(\' \', \'_\')}", "name": folder_name, "status": "success"}

    def delete_folder(self, service: str, folder_id: str):
        """Deletes an email folder/label."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Deleting folder {folder_id} for {service} using client: {client}")
        # Actual API call placeholder
        return {"status": "success", "message": f"Folder {folder_id} deleted."}

    def rename_folder(self, service: str, folder_id: str, new_name: str):
        """Renames an email folder/label."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Renaming folder {folder_id} to {new_name} for {service} using client: {client}")
        # Actual API call placeholder
        return {"id": folder_id, "name": new_name, "status": "success"}

    def search_emails(self, service: str, query: str, max_results: int = 20):
        """Searches for emails based on a query string."""
        client = self._get_service_client(service)
        if not client:
            return {"error": f"Failed to get client for {service}"}

        print(f"Searching emails for {service} with query 
              \"{query}\" using client: {client}")
        # Actual API call placeholder
        # This would use the client to perform the search and return results.
        # For now, returning a sample based on a generic query.
        if "important" in query.lower():
            return [
                {
                    "id": "gmail_email_1",
                    "thread_id": "gmail_thread_1",
                    "subject": "Important Update",
                    "sender": "sender@example.com",
                    "recipients": ["recipient@example.com"],
                    "date_received": "2024-05-12T10:00:00Z",
                    "snippet": "This is an important update regarding...",
                    "body": None, # Body not included by default in search
                    "is_read": False,
                    "attachments": []
                }
            ]
        return []

# Example usage (for testing, not part of the plugin itself)
if __name__ == "__main__":
    # Mock ApiKeyManager for standalone testing
    class MockApiKeyManager:
        def get_oauth_token(self, service_name):
            if service_name in ["gmail", "outlook"]:
                return {"access_token": f"mock_access_token_for_{service_name}", "refresh_token": "mock_refresh"}
            return None

    mock_manager = MockApiKeyManager()
    email_plugin = EmailManager(api_key_manager=mock_manager)

    print("--- List Emails ---")
    print("Gmail:", email_plugin.list_emails(service="gmail"))
    print("Outlook:", email_plugin.list_emails(service="outlook", folder="Inbox"))

    print("\n--- Get Email ---")
    print("Gmail Email 1:", email_plugin.get_email(service="gmail", email_id="gmail_email_1"))

    print("\n--- Send Email ---")
    sent_email_info = email_plugin.send_email(
        service="gmail",
        to_recipients=["test@example.com"],
        subject="Test Email from ApexAgent",
        body_text="This is a test email sent via the EmailManager plugin."
    )
    print("Sent Email Info:", sent_email_info)

    print("\n--- Create Folder ---")
    created_folder_info = email_plugin.create_folder(service="gmail", folder_name="My Test Folder")
    print("Created Folder Info:", created_folder_info)

    if created_folder_info and created_folder_info.get("id"):
        print("\n--- Rename Folder ---")
        renamed_folder_info = email_plugin.rename_folder(service="gmail", folder_id=created_folder_info["id"], new_name="My Renamed Test Folder")
        print("Renamed Folder Info:", renamed_folder_info)

        print("\n--- Delete Folder ---")
        deleted_folder_info = email_plugin.delete_folder(service="gmail", folder_id=created_folder_info["id"])
        print("Deleted Folder Info:", deleted_folder_info)

    print("\n--- Search Emails ---")
    search_results = email_plugin.search_emails(service="gmail", query="important")
    print("Search Results:", search_results)

