import sys
import os

# Add project root to Python path to allow importing ApiKeyManager
# This assumes the script is in agent_project/scripts/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.core.api_key_manager import ApiKeyManager

# The API key provided by the user
HUGGINGFACE_API_KEY = "YOUR_HUGGINGFACE_API_KEY_HERE"
SERVICE_NAME = "huggingface"

def store_key():
    manager = ApiKeyManager()
    manager.set_api_key(SERVICE_NAME, HUGGINGFACE_API_KEY)
    print(f"API key for {SERVICE_NAME} stored successfully.")
    retrieved_key = manager.get_api_key(SERVICE_NAME)
    if retrieved_key == HUGGINGFACE_API_KEY:
        print(f"Verification successful: Key for {SERVICE_NAME} matches the stored key.")
    else:
        print(f"Verification failed: Key for {SERVICE_NAME} does not match the stored key.")

if __name__ == "__main__":
    store_key()

