import sys
import os

# Add project root to PYTHONPATH to allow imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.plugins.cloud_storage_manager import CloudStorageManager

# Mock ApiKeyManager for standalone testing
class MockApiKeyManager:
    def __init__(self):
        self.oauth_tokens = {
            "gdrive": {"access_token": "mock_gdrive_access_token", "refresh_token": "mock_gdrive_refresh"},
            "onedrive": {"access_token": "mock_onedrive_access_token", "refresh_token": "mock_onedrive_refresh"}
        }

    def get_oauth_token(self, service_name):
        return self.oauth_tokens.get(service_name)

def main():
    print("--- Testing CloudStorageManager Plugin ---")
    mock_api_manager = MockApiKeyManager()
    storage_plugin = CloudStorageManager(api_key_manager=mock_api_manager)
    
    # Define test file paths relative to the test script directory
    test_dir = os.path.dirname(__file__)
    local_upload_file_path = os.path.join(test_dir, "test_upload_file.txt")
    local_download_save_path = os.path.join(test_dir, "test_downloaded_file.txt")

    # Create a dummy file for upload tests
    with open(local_upload_file_path, "w") as f:
        f.write("This is a test file for cloud storage upload.")

    # Test list_files_folders
    print("\nTesting list_files_folders...")
    gdrive_files = storage_plugin.list_files_folders(service="gdrive")
    assert isinstance(gdrive_files, list) and len(gdrive_files) > 0, "list_files_folders for gdrive failed or returned empty"
    print("Google Drive Files (root):
", gdrive_files)
    onedrive_files = storage_plugin.list_files_folders(service="onedrive", folder_id="root")
    assert isinstance(onedrive_files, list) and len(onedrive_files) > 0, "list_files_folders for onedrive failed or returned empty"
    print("OneDrive Files (root):
", onedrive_files)

    # Test get_file_folder_metadata
    print("\nTesting get_file_folder_metadata...")
    gdrive_metadata = storage_plugin.get_file_folder_metadata(service="gdrive", item_id="gdrive_file_1")
    assert gdrive_metadata and "id" in gdrive_metadata and gdrive_metadata["id"] == "gdrive_file_1", "get_file_folder_metadata for gdrive failed"
    print("Google Drive File Metadata (gdrive_file_1):
", gdrive_metadata)

    # Test upload_file
    print("\nTesting upload_file...")
    upload_result = storage_plugin.upload_file(service="gdrive", local_file_path=local_upload_file_path, destination_folder_id="root", new_file_name="uploaded_by_apexagent.txt")
    assert upload_result and "id" in upload_result and upload_result.get("status") == "success", "upload_file to gdrive failed"
    print("Upload to Google Drive Result:
", upload_result)
    uploaded_file_id = upload_result["id"]

    # Test download_file (using the ID from the mock upload)
    print("\nTesting download_file...")
    # The mock upload_file returns a generic ID, the mock download_file might not use it directly but we test the flow
    download_result = storage_plugin.download_file(service="gdrive", file_id=uploaded_file_id, local_save_path=local_download_save_path)
    assert download_result and download_result.get("status") == "success" and os.path.exists(local_download_save_path), "download_file from gdrive failed or file not created"
    print("Download from Google Drive Result:
", download_result)
    if os.path.exists(local_download_save_path):
        with open(local_download_save_path, "r") as f_read:
            print(f"Contents of downloaded file: {f_read.read()}")
        os.remove(local_download_save_path)
        print(f"Cleaned up {local_download_save_path}")

    # Test create_folder
    print("\nTesting create_folder...")
    created_folder_info = storage_plugin.create_folder(service="onedrive", folder_name="ApexAgentTestFolder", parent_folder_id="root")
    assert created_folder_info and "id" in created_folder_info and created_folder_info.get("status") == "success", "create_folder in onedrive failed"
    print("Create Folder in OneDrive Result:
", created_folder_info)
    new_folder_id = created_folder_info["id"]

    # Test move_file_folder (mock move)
    print("\nTesting move_file_folder...")
    # We need a file ID to move. Let_s assume one of the listed files can be moved to the new folder.
    # The mock list_files_folders for onedrive returns onedrive_file_1
    if onedrive_files and new_folder_id:
        item_to_move_id = onedrive_files[0]["id"]
        move_result = storage_plugin.move_file_folder(service="onedrive", item_id=item_to_move_id, new_parent_folder_id=new_folder_id)
        assert move_result and move_result.get("status") == "success" and move_result.get("parent_id") == new_folder_id, "move_file_folder in onedrive failed"
        print(f"Move Item 	{item_to_move_id}	 to Folder 	{new_folder_id}	 Result:
", move_result)
    else:
        print("Skipping move_file_folder test due to missing initial data or folder creation failure.")

    # Test copy_file (mock copy)
    print("\nTesting copy_file...")
    if onedrive_files and new_folder_id:
        file_to_copy_id = onedrive_files[0]["id"]
        copy_result = storage_plugin.copy_file(service="onedrive", file_id=file_to_copy_id, destination_folder_id=new_folder_id, new_file_name="CopiedByApexAgent.xlsx")
        assert copy_result and "id" in copy_result and copy_result.get("status") == "success", "copy_file in onedrive failed"
        print(f"Copy File 	{file_to_copy_id}	 to Folder 	{new_folder_id}	 Result:
", copy_result)
    else:
        print("Skipping copy_file test due to missing initial data or folder creation failure.")

    # Test delete_file_folder (using the folder created earlier)
    print("\nTesting delete_file_folder...")
    if new_folder_id:
        delete_result = storage_plugin.delete_file_folder(service="onedrive", item_id=new_folder_id)
        assert delete_result and delete_result.get("status") == "success", "delete_file_folder for onedrive folder failed"
        print(f"Delete Folder 	{new_folder_id}	 Result:
", delete_result)
    else:
        print("Skipping delete_file_folder test for new folder due to creation failure.")

    # Clean up the dummy upload file
    if os.path.exists(local_upload_file_path):
        os.remove(local_upload_file_path)
        print(f"Cleaned up {local_upload_file_path}")

    print("\n--- CloudStorageManager Plugin Test Completed Successfully ---")

if __name__ == "__main__":
    main()

