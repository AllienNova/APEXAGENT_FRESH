import unittest
import os
import json
import shutil
import sys

# Add project root to sys.path to allow importing PluginManager
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(project_root, "src"))

from core.plugin_manager import PluginManager
from core.base_plugin import BasePlugin # Ensure BasePlugin is accessible
from packaging.version import parse as parse_version

# A simple helper for checksum calculation, assuming it's defined or imported
# For this test, we might need to redefine a minimal version or import from unit tests
# For simplicity, we will assume TestPluginManagerUnit is available in the same test run or its helper is accessible
try:
    from .test_plugin_manager_unit import TestPluginManagerUnit as UnitHelper
except ImportError:
    # Fallback if running standalone or structure is different
    class UnitHelper:
        def _calculate_checksum_for_plugin_dir(self, plugin_dir_path, algo=\"sha256\"):
            import hashlib # Local import for fallback
            hasher = hashlib.new(algo)
            for root, dirs, files_in_dir in os.walk(plugin_dir_path):
                dirs.sort()
                files_in_dir.sort()
                for name in files_in_dir:
                    filepath = os.path.join(root, name)
                    if name == \"plugin.json\" and os.path.abspath(root) == os.path.abspath(plugin_dir_path):
                        continue
                    try:
                        with open(filepath, \"rb\") as f:
                            while True:
                                chunk = f.read(4096)
                                if not chunk: break
                                hasher.update(chunk)
                        relative_path = os.path.relpath(filepath, plugin_dir_path)
                        hasher.update(relative_path.encode(\"utf-8\"))
                    except IOError:
                        return None
            return hasher.hexdigest()

class TestPluginManagerIntegration(unittest.TestCase):
    def setUp(self):
        self.base_project_dir = os.path.abspath(os.path.join(project_root, "tests", "test_temp_integration"))
        self.test_plugins_root_dir = os.path.join(self.base_project_dir, "plugins")
        self.schema_file_path = os.path.join(project_root, "docs", "plugin_metadata_schema.json")

        if os.path.exists(self.base_project_dir):
            shutil.rmtree(self.base_project_dir)
        os.makedirs(self.test_plugins_root_dir, exist_ok=True)

        if not os.path.exists(os.path.dirname(self.schema_file_path)):
             os.makedirs(os.path.dirname(self.schema_file_path), exist_ok=True)
        # Ensure a valid schema for tests
        valid_schema_content = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "ApexAgent Plugin Metadata", "type": "object",
            "properties": {
                "id": {"type": "string"}, "name": {"type": "string"},
                "version": {"type": "string", "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$"},
                "description": {"type": "string"}, "author": {"type": "string"},
                "entry_point": {"type": "string"}, "actions": {"type": "array"},
                "dependencies": {"type": "object"}, "default_enabled": {"type": "boolean"},
                "checksum": {"type": "object"}
            },
            "required": ["id", "name", "version", "description", "author", "entry_point", "actions"]
        }
        with open(self.schema_file_path, "w") as f:
            json.dump(valid_schema_content, f, indent=2)
        
        self.checksum_helper = UnitHelper() # For _calculate_checksum_for_plugin_dir

    def tearDown(self):
        if os.path.exists(self.base_project_dir):
            shutil.rmtree(self.base_project_dir)
        paths_to_remove = [p for p in sys.path if self.base_project_dir in p]
        for p in paths_to_remove:
            if p in sys.path:
                 sys.path.remove(p)

    def _create_plugin_structure(self, plugin_id_str, version_str, entry_module_name="main", entry_class_name="MyPlugin", extra_metadata=None, files_content=None, subdir_name=None):
        if subdir_name is None:
            subdir_name = f"{plugin_id_str.replace(".", "_")}_v{version_str.replace(".", "")}"
        plugin_dir = os.path.join(self.test_plugins_root_dir, subdir_name)
        os.makedirs(plugin_dir, exist_ok=True)

        metadata = {
            "id": plugin_id_str,
            "name": f"{plugin_id_str} Name v{version_str}",
            "version": version_str,
            "description": f"Test plugin {plugin_id_str} version {version_str}",
            "author": "Integ Test",
            "entry_point": f"{entry_module_name}.{entry_class_name}",
            "actions": [{"name": "test_action", "description": "A test action"}]
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        entry_file_content = f"from core.base_plugin import BasePlugin\n\nclass {entry_class_name}(BasePlugin):\n    def __init__(self, plugin_id, plugin_name, version, description, config=None):\n        super().__init__(plugin_id, plugin_name, version, description, config)\n    def initialize(self, agent_context=None): pass\n    def get_actions(self): return {metadata["actions"]}\n    def execute_action(self, action_name, params=None): return f\"{self.plugin_id} v{self.version} action: {action_name}\"\n    def get_version_message(self): return f\"Loaded {self.plugin_id} v{self.version}\"\n"
        
        entry_module_path = os.path.join(plugin_dir, f"{entry_module_name}.py")
        os.makedirs(os.path.dirname(entry_module_path), exist_ok=True)
        with open(entry_module_path, "w") as f:
            f.write(entry_file_content)

        if files_content:
            for file_name, content in files_content.items():
                file_path = os.path.join(plugin_dir, file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w") as f:
                    f.write(content)
        return plugin_dir

    def test_01_integration_discovery_validation_and_loading_single_version(self):
        plugin1_id = "com.example.integ.valid1"
        plugin1_version = "1.0.0"
        plugin1_code_file = "p1_code.py"
        plugin1_code = f"from core.base_plugin import BasePlugin\nclass PluginOne(BasePlugin):\n    def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs)\n    def run(self): return \"{plugin1_id} v{plugin1_version} running\""
        plugin1_dir = self._create_plugin_structure(plugin1_id, plugin1_version, entry_module_name=plugin1_code_file.replace(".py",""), entry_class_name="PluginOne", files_content={plugin1_code_file: plugin1_code}, subdir_name="plugin_one_valid")
        
        checksum_p1 = self.checksum_helper._calculate_checksum_for_plugin_dir(plugin1_dir)
        plugin1_metadata_updated = {
            "checksum": {"algorithm": "sha256", "value": checksum_p1}
        }
        # Re-write plugin.json with checksum
        with open(os.path.join(plugin1_dir, "plugin.json"), "r+") as f:
            data = json.load(f)
            data.update(plugin1_metadata_updated)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

        manager = PluginManager(plugin_dirs=[self.test_plugins_root_dir], schema_path=self.schema_file_path)
        self.assertIn(plugin1_id, manager.plugins)
        self.assertTrue(manager.is_plugin_enabled_by_default(plugin1_id, plugin1_version))
        p1_instance = manager.load_plugin(plugin1_id, version_specifier=f"=={plugin1_version}")
        self.assertIsNotNone(p1_instance)
        self.assertEqual(p1_instance.run(), f"{plugin1_id} v{plugin1_version} running")

    def test_02_integration_multiple_versions_load_specific_and_latest(self):
        plugin_id = "com.example.integ.multiver"
        self._create_plugin_structure(plugin_id, "1.0.0", subdir_name="mv_100")
        self._create_plugin_structure(plugin_id, "1.1.0", subdir_name="mv_110") # Latest valid
        self._create_plugin_structure(plugin_id, "0.9.0", subdir_name="mv_090")
        self._create_plugin_structure(plugin_id, "1.0.1-beta", subdir_name="mv_101b") # Pre-release

        manager = PluginManager(plugin_dirs=[self.test_plugins_root_dir], schema_path=self.schema_file_path)
        self.assertIn(plugin_id, manager.plugins)
        self.assertEqual(len(manager.plugins[plugin_id]), 4) # All 4 versions should be discovered

        # Load specific version 1.0.0
        instance_v100 = manager.load_plugin(plugin_id, version_specifier="==1.0.0")
        self.assertIsNotNone(instance_v100)
        self.assertEqual(instance_v100.version, "1.0.0")
        self.assertEqual(instance_v100.get_version_message(), f"Loaded {plugin_id} v1.0.0")

        # Load latest stable version (no specifier)
        instance_latest_stable = manager.load_plugin(plugin_id)
        self.assertIsNotNone(instance_latest_stable)
        self.assertEqual(instance_latest_stable.version, "1.1.0") # 1.1.0 is latest stable
        self.assertEqual(instance_latest_stable.get_version_message(), f"Loaded {plugin_id} v1.1.0")

        # Load with a range specifier that includes pre-release if allow_prereleases is True (default is False for get_best_match)
        # To test pre-release selection, we might need a more direct call or adjust PluginManager logic for tests
        # For now, let's test a range that should pick 1.1.0
        instance_range = manager.load_plugin(plugin_id, version_specifier=">=1.0.0,<1.2.0")
        self.assertIsNotNone(instance_range)
        self.assertEqual(instance_range.version, "1.1.0")

        # Test loading a version that doesn\'t exist
        instance_nonexist = manager.load_plugin(plugin_id, version_specifier="==2.0.0")
        self.assertIsNone(instance_nonexist)

    def test_03_integration_plugin_dependency_resolution_simple(self):
        dep_id = "com.example.dependency.core"
        plugin_id = "com.example.dependent.app"

        # Create dependency plugin (two versions)
        self._create_plugin_structure(dep_id, "1.0.0", subdir_name="dep_core_v100")
        self._create_plugin_structure(dep_id, "1.1.0", subdir_name="dep_core_v110")

        # Create dependent plugin that requires dep_id version >=1.0.0
        dependent_metadata = {
            "dependencies": {
                "plugins": [{"id": dep_id, "version_specifier": ">=1.0.0"}]
            }
        }
        self._create_plugin_structure(plugin_id, "1.0.0", extra_metadata=dependent_metadata, subdir_name="dependent_app_v100")

        manager = PluginManager(plugin_dirs=[self.test_plugins_root_dir], schema_path=self.schema_file_path)
        
        # PluginManager.discover_plugins() now has basic dependency check logging.
        # A full dependency resolution and loading test would require more sophisticated PluginManager logic
        # for now, we check if both are discovered and the dependent one can be loaded (implying its metadata was valid)
        self.assertIn(dep_id, manager.plugins)
        self.assertIn(plugin_id, manager.plugins)
        
        # Attempt to load the dependent plugin. PluginManager.load_plugin itself doesn\'t currently enforce dependency loading.
        # This test primarily ensures discovery and basic metadata parsing with dependencies is okay.
        # True dependency resolution would be a more advanced feature.
        dependent_instance = manager.load_plugin(plugin_id)
        self.assertIsNotNone(dependent_instance, "Dependent plugin should load if its own metadata is valid.")
        self.assertEqual(dependent_instance.version, "1.0.0")

    def test_04_integration_dependency_missing(self):
        plugin_id = "com.example.dependent.missingdep"
        dependent_metadata = {
            "dependencies": {
                "plugins": [{"id": "com.example.nonexistent.dependency", "version_specifier": "==1.0.0"}]
            }
        }
        self._create_plugin_structure(plugin_id, "1.0.0", extra_metadata=dependent_metadata, subdir_name="dep_missing_v100")
        
        manager = PluginManager(plugin_dirs=[self.test_plugins_root_dir], schema_path=self.schema_file_path)
        # The plugin itself should still be discovered if its own metadata is valid, 
        # but a warning about the missing dependency should be logged by PluginManager during discovery.
        self.assertIn(plugin_id, manager.plugins)
        # Further checks would require inspecting logs or more advanced PluginManager state.

    def test_05_integration_dependency_version_mismatch(self):
        dep_id = "com.example.dependency.core.v2"
        plugin_id = "com.example.dependent.app.v2"

        self._create_plugin_structure(dep_id, "1.0.0", subdir_name="dep_core_v2_100") # Only v1.0.0 of dependency exists

        dependent_metadata = {
            "dependencies": {
                "plugins": [{"id": dep_id, "version_specifier": ">=1.1.0"}] # Requires v1.1.0 or higher
            }
        }
        self._create_plugin_structure(plugin_id, "1.0.0", extra_metadata=dependent_metadata, subdir_name="dependent_app_v2_100")

        manager = PluginManager(plugin_dirs=[self.test_plugins_root_dir], schema_path=self.schema_file_path)
        self.assertIn(dep_id, manager.plugins)
        self.assertIn(plugin_id, manager.plugins)
        # Similar to missing dependency, a warning should be logged. Loading the dependent plugin might still succeed
        # if PluginManager doesn\'t strictly block loading based on unsatisfied dependencies yet.

if __name__ == "__main__":
    unittest.main()

