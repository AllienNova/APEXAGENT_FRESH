import sys
import os

# Add project root to PYTHONPATH to allow imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.core.plugin_manager import PluginManager

def main():
    print("Verifying LLM Provider Discovery...")

    # Define plugin directories
    base_dir = os.path.join(project_root, "src", "plugins")
    tool_dirs = [os.path.join(base_dir, "tools", "internal")]
    llm_provider_dirs = [os.path.join(base_dir, "llm_providers", "internal")]

    print(f"Project Root: {project_root}")
    print(f"Tool Plugin Dirs: {tool_dirs}")
    print(f"LLM Provider Plugin Dirs: {llm_provider_dirs}")

    # Instantiate PluginManager
    plugin_mgr = PluginManager(tool_plugin_dirs=tool_dirs, llm_provider_plugin_dirs=llm_provider_dirs)

    # Get details of available LLM providers
    provider_details = plugin_mgr.get_available_llm_providers_details()
    
    print("\nAvailable LLM Providers Details:")
    if provider_details:
        for detail in provider_details:
            print(f"  Name: {detail['name']}")
            print(f"    Display Name: {detail['display_name']}")
            print(f"    Requires API Key: {detail['requires_api_key']}")
            if detail['requires_api_key']:
                print(f"    API Key Name: {detail['api_key_name']}")
            print("-" * 20)
    else:
        print("  No LLM providers found.")

    # Check for specific new and existing providers
    # Existing ones based on file context: ollama, anthropic_claude
    # New ones: google_gemini, openai
    expected_providers = ["ollama", "anthropic_claude", "google_gemini", "openai"]
    found_providers_names = [p['name'] for p in provider_details]
    
    all_expected_found = True
    print("\nVerification Results for Expected Providers:")
    for provider_name in expected_providers:
        if provider_name in found_providers_names:
            print(f"  [SUCCESS] Discovered: {provider_name}")
        else:
            print(f"  [FAILURE] Did NOT discover expected provider: {provider_name}")
            all_expected_found = False
            
    if all_expected_found and len(found_providers_names) >= len(expected_providers):
        print("\nLLM Provider discovery verification successful for all expected providers.")
    else:
        print("\nLLM Provider discovery verification FAILED for one or more expected providers.")

if __name__ == "__main__":
    main()

