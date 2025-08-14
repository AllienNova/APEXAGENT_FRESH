import sys
import os

# Add project root to PYTHONPATH to allow imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.plugins.crm_manager import CrmManager

# Mock ApiKeyManager for standalone testing
class MockApiKeyManager:
    def __init__(self):
        self.oauth_tokens = {
            "salesforce": {"access_token": "mock_sf_access_token", "refresh_token": "mock_sf_refresh"},
            "zoho": {"access_token": "mock_zoho_access_token", "refresh_token": "mock_zoho_refresh"}
        }
        self.api_keys = {
            "monday.com": "mock_monday_api_key_value"
        }

    def get_oauth_token(self, service_name):
        return self.oauth_tokens.get(service_name)

    def get_api_key(self, service_name):
        return self.api_keys.get(service_name)

def main():
    print("--- Testing CrmManager Plugin ---")
    mock_api_manager = MockApiKeyManager()
    crm_plugin = CrmManager(api_key_manager=mock_api_manager)

    # Test search_records
    print("\nTesting search_records...")
    sf_contacts = crm_plugin.search_records(service="salesforce", object_type="Contact", query_criteria="LastName = \'Doe\'")
    assert isinstance(sf_contacts, list) and len(sf_contacts) > 0, "search_records for salesforce contacts failed or returned empty"
    print("Salesforce Contacts (Doe):
", sf_contacts)
    zoho_leads = crm_plugin.search_records(service="zoho", object_type="Lead", query_criteria="(Company:equals:ABC Corp)")
    assert isinstance(zoho_leads, list) and len(zoho_leads) > 0, "search_records for zoho leads failed or returned empty"
    print("Zoho Leads (ABC Corp):
", zoho_leads)

    # Test get_record_details
    print("\nTesting get_record_details...")
    sf_contact_details = crm_plugin.get_record_details(service="salesforce", object_type="Contact", record_id="sf_contact_1")
    assert sf_contact_details and "Id" in sf_contact_details and sf_contact_details["Id"] == "sf_contact_1", "get_record_details for salesforce failed"
    print("Salesforce Contact Details (sf_contact_1):
", sf_contact_details)

    # Test create_record
    print("\nTesting create_record...")
    new_sf_lead_data = {"LastName": "ApexTestLead", "Company": "ApexAgent Solutions"}
    created_sf_lead = crm_plugin.create_record(service="salesforce", object_type="Lead", record_data=new_sf_lead_data)
    assert created_sf_lead and "id" in created_sf_lead and created_sf_lead.get("status") == "success", "create_record for salesforce lead failed"
    print("Created Salesforce Lead:
", created_sf_lead)
    new_sf_lead_id = created_sf_lead["id"]

    # Test update_record
    print("\nTesting update_record...")
    # Using the mock ID from get_record_details for update
    update_sf_contact_data = {"Phone": "555-0000-APEX"}
    updated_sf_contact = crm_plugin.update_record(service="salesforce", object_type="Contact", record_id="sf_contact_1", update_data=update_sf_contact_data)
    assert updated_sf_contact and updated_sf_contact.get("status") == "success", "update_record for salesforce contact failed"
    print("Updated Salesforce Contact (sf_contact_1) - (mock will show success, actual data not changed in mock):
", updated_sf_contact)
    # To verify, you_d ideally call get_record_details again if the mock update actually changed data for get.
    # For now, the mock update_record just returns success.

    # Test log_activity
    print("\nTesting log_activity...")
    log_activity_result = crm_plugin.log_activity(service="salesforce", related_record_id="sf_contact_1", activity_type="Email", subject="Sent follow-up email via ApexAgent", description="Followed up on initial query.")
    assert log_activity_result and "id" in log_activity_result and log_activity_result.get("status") == "success", "log_activity for salesforce failed"
    print("Log Activity on Salesforce Contact (sf_contact_1):
", log_activity_result)

    # Test delete_record (using the ID from the mock create_record)
    print("\nTesting delete_record...")
    if new_sf_lead_id:
        delete_sf_lead_result = crm_plugin.delete_record(service="salesforce", object_type="Lead", record_id=new_sf_lead_id)
        assert delete_sf_lead_result and delete_sf_lead_result.get("status") == "success", "delete_record for salesforce lead failed"
        print(f"Delete Salesforce Lead ({new_sf_lead_id}) Result:
", delete_sf_lead_result)
    else:
        print("Skipping delete_record test for new lead as creation might have failed or ID not available.")

    # Test with a service that might use API key (Monday.com mock)
    print("\nTesting search_records with Monday.com (mocked API key)...")
    monday_items = crm_plugin.search_records(service="monday.com", object_type="Item", query_criteria="board_id=123 status=active")
    # Mock CrmManager._get_service_client will print if it uses API key or OAuth
    # The mock search_records for monday.com currently returns [], so we check it_s a list
    assert isinstance(monday_items, list), "search_records for monday.com (mock) did not return a list"
    print("Monday.com Items (mocked search):
", monday_items)


    print("\n--- CrmManager Plugin Test Completed Successfully ---")

if __name__ == "__main__":
    main()

