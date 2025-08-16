import os
import json
import logging
import hashlib

logger = logging.getLogger(__name__)

class PluginStateManager:
    """
    Manages the persistence of plugin states.
    It handles saving and loading state data for plugins to/from JSON files
    in a structured directory, with enhanced security considerations.
    """
    def __init__(self, base_state_dir: str = "/home/ubuntu/agent_project/plugin_states"):
        """
        Initializes the PluginStateManager.

        Args:
            base_state_dir (str): The root directory where plugin states will be stored.
                                  Defaults to "/home/ubuntu/agent_project/plugin_states".
        """
        self.base_state_dir = os.path.abspath(base_state_dir)
        try:
            # Create base directory with restrictive permissions: rwx------ (0700)
            os.makedirs(self.base_state_dir, mode=0o700, exist_ok=True)
            logger.info(f"PluginStateManager initialized. State directory: {self.base_state_dir}")
        except OSError as e:
            logger.error(f"Error creating base state directory {self.base_state_dir} with permissions 0700: {e}")
            # Depending on policy, could raise an error here to prevent insecure operation
            # For now, log and continue, but this is a potential security risk if creation fails badly.

    def _get_state_file_path(self, plugin_id: str, plugin_version: str) -> str:
        """
        Constructs the full path to the state file for a given plugin and version.

        Args:
            plugin_id (str): The ID of the plugin.
            plugin_version (str): The version of the plugin.

        Returns:
            str: The absolute path to the state file.
        """
        # Sanitize plugin_id and plugin_version to prevent directory traversal or invalid characters
        # A more robust sanitization might be needed depending on expected inputs
        safe_plugin_id = "".join(c if c.isalnum() or c in (".", "-", "_") else "_" for c in plugin_id)
        safe_plugin_version = "".join(c if c.isalnum() or c in (".", "-", "_") else "_" for c in plugin_version)

        plugin_dir = os.path.join(self.base_state_dir, safe_plugin_id)
        state_filename = f"state_v{safe_plugin_version}.json"
        return os.path.join(plugin_dir, state_filename)

    def _calculate_checksum(self, data_bytes: bytes) -> str:
        """Calculates SHA256 checksum for the given data bytes."""
        return hashlib.sha256(data_bytes).hexdigest()

    def save_plugin_state(self, plugin_id: str, plugin_version: str, state_data: dict) -> None:
        """
        Saves the state data for a specific plugin and version to a JSON file,
        including a checksum for integrity.

        Args:
            plugin_id (str): The ID of the plugin.
            plugin_version (str): The version of the plugin.
            state_data (dict): The state data to save (must be JSON-serializable).

        Raises:
            IOError: If there are issues with file operations (e.g., permissions).
            TypeError: If state_data is not JSON-serializable.
            Exception: For other unexpected errors during saving.
        """
        state_file_path = self._get_state_file_path(plugin_id, plugin_version)
        plugin_specific_dir = os.path.dirname(state_file_path)
        
        try:
            # Create plugin-specific directory with restrictive permissions: rwx------ (0700)
            os.makedirs(plugin_specific_dir, mode=0o700, exist_ok=True)
        except OSError as e:
            logger.error(f"Error creating plugin-specific directory {plugin_specific_dir} with permissions 0700: {e}")
            raise IOError(f"Could not create plugin directory {plugin_specific_dir}: {e}") from e

        try:
            # Prepare data with checksum
            state_data_bytes = json.dumps(state_data, sort_keys=True).encode("utf-8") # Ensure consistent order for checksum
            checksum = self._calculate_checksum(state_data_bytes)
            payload_to_save = {
                "data": state_data,
                "checksum": checksum
            }

            # Save the file with restrictive permissions: rw------- (0600)
            # Using an opener to set mode during file creation is more robust
            fd = os.open(state_file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload_to_save, f, indent=4)
            logger.info(f"Successfully saved state for plugin {plugin_id} (v{plugin_version}) to {state_file_path}")
        except IOError as e:
            logger.error(f"IOError saving state for plugin {plugin_id} (v{plugin_version}) to {state_file_path}: {e}")
            raise
        except TypeError as e:
            logger.error(f"TypeError: State data for plugin {plugin_id} (v{plugin_version}) is not JSON-serializable: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving state for plugin {plugin_id} (v{plugin_version}): {e}")
            raise

    def load_plugin_state(self, plugin_id: str, plugin_version: str) -> dict | None:
        """
        Loads the state data for a specific plugin and version from a JSON file,
        verifying its integrity using a checksum.

        Args:
            plugin_id (str): The ID of the plugin.
            plugin_version (str): The version of the plugin.

        Returns:
            dict | None: The loaded state data as a dictionary, or None if the state file
                         does not exist, is corrupted, or an error occurs during loading.
        
        Raises:
            # No longer raises directly, logs errors and returns None for most load failures
            # to allow plugins to handle missing/corrupt state gracefully.
        """
        state_file_path = self._get_state_file_path(plugin_id, plugin_version)

        if not os.path.exists(state_file_path):
            logger.info(f"No state file found for plugin {plugin_id} (v{plugin_version}) at {state_file_path}. Returning None.")
            return None

        try:
            with open(state_file_path, "r", encoding="utf-8") as f:
                payload_loaded = json.load(f)
            
            if not isinstance(payload_loaded, dict) or "data" not in payload_loaded or "checksum" not in payload_loaded:
                logger.error(f"Invalid state file format for plugin {plugin_id} (v{plugin_version}) at {state_file_path}. Missing 'data' or 'checksum'.")
                return None

            loaded_data = payload_loaded["data"]
            expected_checksum = payload_loaded["checksum"]
            
            # Verify checksum
            loaded_data_bytes = json.dumps(loaded_data, sort_keys=True).encode("utf-8")
            calculated_checksum = self._calculate_checksum(loaded_data_bytes)

            if calculated_checksum == expected_checksum:
                logger.info(f"Successfully loaded and verified state for plugin {plugin_id} (v{plugin_version}) from {state_file_path}")
                return loaded_data
            else:
                logger.error(f"Checksum mismatch for plugin {plugin_id} (v{plugin_version}) state file {state_file_path}. Data may be corrupted. Expected: {expected_checksum}, Calculated: {calculated_checksum}")
                return None

        except FileNotFoundError:
            logger.info(f"State file not found for plugin {plugin_id} (v{plugin_version}) at {state_file_path} (during open). Returning None.")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError loading state for plugin {plugin_id} (v{plugin_version}) from {state_file_path}: {e}. File might be corrupted.")
            return None
        except IOError as e:
            logger.error(f"IOError loading state for plugin {plugin_id} (v{plugin_version}) from {state_file_path}: {e}")
            return None # Or consider raising for critical IO errors not related to file not found
        except Exception as e:
            logger.error(f"Unexpected error loading state for plugin {plugin_id} (v{plugin_version}): {e}")
            return None

