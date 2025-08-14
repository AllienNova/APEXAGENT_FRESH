import unittest
import os
import json
import shutil
import logging
from unittest.mock import patch, mock_open

# Adjust the Python path to import PluginManager from the parent directory's src folder
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from plugin_manager import PluginManager

# Suppress logging during tests unless specifically testing logging output
logging.disable(logging.CRITICAL) # Disable all logging less than CRITICAL

class TestPluginManagerDiscovery(unittest.TestCase):
    base_test_dir = "/home/ubuntu/agent_project/tests/temp_plugin_test_env"
    schema_dir = os.path.join(base_test_dir, "docs")
    schema_file = os.path.join(schema_dir, "plugin_metadata_schema.json")
    plugins_dir_1 = os.path.join(base_test_dir, "plugins1")
    plugins_dir_2 = os.path.join(base_test_dir, "plugins2")

    @classmethod
    def setUpClass(cls):
        # Create the base directory for test files
        if os.path.exists(cls.base_test_dir):
            shutil.rmtree(cls.base_test_dir)
        os.makedirs(cls.schema_dir)
        os.makedirs(cls.plugins_dir_1)
        os.makedirs(cls.plugins_dir_2)

        # Create a valid schema file (simplified for testing focus on discovery)
        cls.valid_schema_content = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Test Plugin Metadata",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "version": {"type": "string"},
                "description": {"type": "string"},
                "author": {"type": "string"},
                "entry_point": {"type": "string"},
                "actions": {"type": "array"}
            },
            "required": ["id", "name", "version", "description", "author", "entry_point", "actions"]
        }
        with open(cls.schema_file, 'w') as f:
            json.dump(cls.valid_schema_content, f)

    @classmethod
    def tearDownClass(cls):
        # Clean up the base directory
        if os.path.exists(cls.base_test_dir):
            shutil.rmtree(cls.base_test_dir)
        logging.disable(logging.NOTSET) # Re-enable logging

    def setUp(self):
        # Ensure plugin directories are clean before each test
        if os.path.exists(self.plugins_dir_1):
            shutil.rmtree(self.plugins_dir_1)
        os.makedirs(self.plugins_dir_1)
        if os.path.exists(self.plugins_dir_2):
            shutil.rmtree(self.plugins_dir_2)
        os.makedirs(self.plugins_dir_2)
        self.manager = None # Reset manager

    def _create_plugin_files(self, plugin_dir_base, plugin_name, metadata_content, metadata_filename="plugin.json"):
        plugin_path = os.path.join(plugin_dir_base, plugin_name)
        os.makedirs(plugin_path, exist_ok=True)
        with open(os.path.join(plugin_path, metadata_filename), 'w') as f:
            if isinstance(metadata_content, dict):
                json.dump(metadata_content, f)
            else: # For malformed JSON test
                f.write(metadata_content)
        return plugin_path

    def test_discover_single_valid_plugin(self):
        valid_metadata = {
            "id": "com.example.valid1", "name": "Valid Plugin 1", "version": "1.0",
            "description": "Desc", "author": "Auth", "entry_point": "ep", "actions": []
        }
        self._create_plugin_files(self.plugins_dir_1, "valid_plugin_1", valid_metadata)
        self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1], schema_path=self.schema_file)
        self.assertIn("com.example.valid1", self.manager.plugin_registry)
        self.assertEqual(self.manager.get_plugin_metadata("com.example.valid1")["name"], "Valid Plugin 1")

    def test_discover_multiple_valid_plugins(self):
        p1_meta = {"id": "com.example.p1", "name": "P1", "version": "1.0", "description": "D", "author": "A", "entry_point": "E", "actions": []}
        p2_meta = {"id": "com.example.p2", "name": "P2", "version": "1.0", "description": "D", "author": "A", "entry_point": "E", "actions": []}
        self._create_plugin_files(self.plugins_dir_1, "plugin1", p1_meta)
        self._create_plugin_files(self.plugins_dir_1, "plugin2", p2_meta, metadata_filename="metadata.json") # Test alternative name
        self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1], schema_path=self.schema_file)
        self.assertIn("com.example.p1", self.manager.plugin_registry)
        self.assertIn("com.example.p2", self.manager.plugin_registry)
        self.assertEqual(len(self.manager.plugin_registry), 2)

    def test_discover_from_multiple_directories(self):
        p1_meta = {"id": "com.example.multi.p1", "name": "MultiP1", "version": "1.0", "description": "D", "author": "A", "entry_point": "E", "actions": []}
        p2_meta = {"id": "com.example.multi.p2", "name": "MultiP2", "version": "1.0", "description": "D", "author": "A", "entry_point": "E", "actions": []}
        self._create_plugin_files(self.plugins_dir_1, "multi_plugin1", p1_meta)
        self._create_plugin_files(self.plugins_dir_2, "multi_plugin2", p2_meta)
        self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1, self.plugins_dir_2], schema_path=self.schema_file)
        self.assertIn("com.example.multi.p1", self.manager.plugin_registry)
        self.assertIn("com.example.multi.p2", self.manager.plugin_registry)
        self.assertEqual(len(self.manager.plugin_registry), 2)

    def test_skip_plugin_with_missing_metadata_file(self):
        os.makedirs(os.path.join(self.plugins_dir_1, "no_metadata_plugin"))
        self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1], schema_path=self.schema_file)
        self.assertEqual(len(self.manager.plugin_registry), 0)

    def test_skip_plugin_with_malformed_json_metadata(self):
        self._create_plugin_files(self.plugins_dir_1, "malformed_json_plugin", "{\"id\": \"bad\"") # Incomplete JSON
        self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1], schema_path=self.schema_file)
        self.assertEqual(len(self.manager.plugin_registry), 0)

    def test_skip_plugin_with_metadata_not_conforming_to_schema(self):
        invalid_meta = {"name": "Invalid Schema Plugin", "version": "1.0"} # Missing required 'id', 'description', etc.
        self._create_plugin_files(self.plugins_dir_1, "invalid_schema_plugin", invalid_meta)
        self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1], schema_path=self.schema_file)
        self.assertEqual(len(self.manager.plugin_registry), 0)

    def test_skip_plugin_with_missing_id_in_metadata(self):
        no_id_meta = {"name": "No ID Plugin", "version": "1.0", "description": "D", "author": "A", "entry_point": "E", "actions": []}
        self._create_plugin_files(self.plugins_dir_1, "no_id_plugin", no_id_meta)
        self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1], schema_path=self.schema_file)
        self.assertEqual(len(self.manager.plugin_registry), 0)

    def test_handle_duplicate_plugin_ids(self):
        meta1 = {"id": "com.example.duplicate", "name": "Duplicate Plugin V1", "version": "1.0", "description": "D", "author": "A", "entry_point": "E1", "actions": []}
        meta2 = {"id": "com.example.duplicate", "name": "Duplicate Plugin V2", "version": "2.0", "description": "D", "author": "A", "entry_point": "E2", "actions": []}
        self._create_plugin_files(self.plugins_dir_1, "dup_plugin1", meta1)
        self._create_plugin_files(self.plugins_dir_1, "dup_plugin2", meta2)
        self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1], schema_path=self.schema_file)
        self.assertIn("com.example.duplicate", self.manager.plugin_registry)
        self.assertEqual(len(self.manager.plugin_registry), 1)
        # Check which one was kept (the first one encountered)
        self.assertEqual(self.manager.get_plugin_metadata("com.example.duplicate")["entry_point"], "E1")

    def test_non_existent_plugin_directory(self):
        self.manager = PluginManager(plugin_dirs=["/path/to/non_existent_dir"], schema_path=self.schema_file)
        self.assertEqual(len(self.manager.plugin_registry), 0)

    def test_schema_file_not_found(self):
        with self.assertLogs(level='ERROR') as log:
            self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1], schema_path="/path/to/non_existent_schema.json")
        self.assertTrue(any("Schema file not found" in message for message in log.output))
        self.assertEqual(len(self.manager.plugin_registry), 0)
        self.assertIsNone(self.manager.plugin_schema)

    def test_invalid_json_in_schema_file(self):
        invalid_schema_path = os.path.join(self.schema_dir, "invalid_schema.json")
        with open(invalid_schema_path, 'w') as f:
            f.write("{\"title\": \"Invalid Schema\"") # Malformed JSON
        with self.assertLogs(level='ERROR') as log:
            self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1], schema_path=invalid_schema_path)
        self.assertTrue(any("Error decoding JSON schema" in message for message in log.output))
        self.assertEqual(len(self.manager.plugin_registry), 0)
        self.assertIsNone(self.manager.plugin_schema)
        os.remove(invalid_schema_path)

    def test_get_all_plugins_metadata(self):
        p1_meta = {"id": "com.example.all.p1", "name": "AllP1", "version": "1.0", "description": "D", "author": "A", "entry_point": "E", "actions": []}
        p2_meta = {"id": "com.example.all.p2", "name": "AllP2", "version": "1.0", "description": "D", "author": "A", "entry_point": "E", "actions": []}
        self._create_plugin_files(self.plugins_dir_1, "all_plugin1", p1_meta)
        self._create_plugin_files(self.plugins_dir_2, "all_plugin2", p2_meta)
        self.manager = PluginManager(plugin_dirs=[self.plugins_dir_1, self.plugins_dir_2], schema_path=self.schema_file)
        all_meta = self.manager.get_all_plugins_metadata()
        self.assertEqual(len(all_meta), 2)
        self.assertIn("com.example.all.p1", all_meta)
        self.assertIn("com.example.all.p2", all_meta)
        self.assertEqual(all_meta["com.example.all.p1"]["name"], "AllP1")

if __name__ == '__main__':
    # Re-enable logging for test runner output if run directly
    logging.disable(logging.NOTSET)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    unittest.main()


