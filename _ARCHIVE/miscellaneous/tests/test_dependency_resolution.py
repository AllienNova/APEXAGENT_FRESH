import unittest
import asyncio
import os
import json
import shutil
import logging
from typing import Dict, Any, Optional, List

from agent_project.src.plugin_manager import PluginManager
from agent_project.src.core.exceptions import PluginDependencyError

# Configure basic logging for tests
logging.basicConfig(level=logging.INFO, format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\')

# Define temporary directories for test plugins
TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS = "/home/ubuntu/agent_project/tests/temp_dep_plugins_root"
PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS = "/home/ubuntu/agent_project/docs/plugin_metadata_schema.json"

# Helper function to create dummy plugin metadata
def create_dummy_plugin_metadata(
    plugin_dir_name: str, 
    plugin_id: str, 
    version: str = "1.0.0", 
    dependencies: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    entry_point: str = "plugins.dummy_module.DummyPlugin"
) -> str:
    plugin_path = os.path.join(TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS, plugin_dir_name)
    os.makedirs(plugin_path, exist_ok=True)
    
    metadata = {
        "name": f"Test Plugin {plugin_id}",
        "id": plugin_id,
        "version": version,
        "description": "A test plugin for dependency resolution.",
        "author": "Test Framework",
        "entry_point": entry_point, # Needs a dummy class if we try to instantiate
        "actions": [{"name": "test_action", "description": "A test action."}]
    }
    if dependencies:
        metadata["dependencies"] = dependencies
    
    metadata_file_path = os.path.join(plugin_path, "plugin.json")
    with open(metadata_file_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Create a dummy entry point file if it doesn_t exist to avoid import errors during instantiation tests
    # This is a simplified approach for testing dependency loading, not full instantiation.
    # For full instantiation tests, a proper dummy plugin class would be needed.
    entry_module_path_parts = entry_point.split(".")[:-1]
    dummy_module_dir = os.path.join("/home/ubuntu/agent_project/src", *entry_module_path_parts[:-1])
    dummy_module_file = os.path.join(dummy_module_dir, entry_module_path_parts[-1] + ".py")
    os.makedirs(dummy_module_dir, exist_ok=True)
    if not os.path.exists(dummy_module_file):
        with open(dummy_module_file, "w") as f:
            f.write(f"class {entry_point.split(\".\")[-1]}:\n    def __init__(self, *args, **kwargs): pass\n    async def execute_action(self, action_name, **kwargs): return \"dummy_action_executed\"")
    # Also create __init__.py in the plugins directory if not present
    init_py_path = os.path.join(os.path.dirname(dummy_module_dir), "__init__.py")
    if not os.path.exists(init_py_path):
        with open(init_py_path, "w") as f:
            f.write("")

    return plugin_path

class TestDependencyResolution(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS):
            raise FileNotFoundError(f"CRITICAL: Plugin schema not found at {PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS}")
        if os.path.exists(TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS):
            shutil.rmtree(TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS)
        os.makedirs(TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS):
            shutil.rmtree(TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS)

    def tearDown(self):
        # Clean up plugin directories created by individual tests if any specific ones are made
        # For now, relying on setUpClass and tearDownClass for the root test plugin dir
        pass

    async def test_plugin_no_dependencies(self):
        create_dummy_plugin_metadata("plugin_a", "com.example.plugin.a")
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.a"), "loaded")

    async def test_plugin_dependency_met_exact_version(self):
        create_dummy_plugin_metadata("plugin_b_dep", "com.example.plugin.b", version="1.0.0")
        create_dummy_plugin_metadata("plugin_c_user", "com.example.plugin.c", 
                                     dependencies={"plugins": [{"id": "com.example.plugin.b", "version_specifier": "==1.0.0"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.b"), "loaded")
        self.assertEqual(manager.plugin_status.get("com.example.plugin.c"), "loaded")

    async def test_plugin_dependency_met_version_range(self):
        create_dummy_plugin_metadata("plugin_d_dep", "com.example.plugin.d", version="1.5.0")
        create_dummy_plugin_metadata("plugin_e_user", "com.example.plugin.e", 
                                     dependencies={"plugins": [{"id": "com.example.plugin.d", "version_specifier": ">=1.0.0,<2.0.0"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.d"), "loaded")
        self.assertEqual(manager.plugin_status.get("com.example.plugin.e"), "loaded")

    async def test_plugin_dependency_not_found(self):
        create_dummy_plugin_metadata("plugin_f_user", "com.example.plugin.f", 
                                     dependencies={"plugins": [{"id": "com.example.plugin.nonexistent"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.f"), "disabled_dependency_issue")
        with self.assertRaises(PluginDependencyError):
            manager.get_plugin_instance("com.example.plugin.f")

    async def test_plugin_dependency_version_mismatch_exact(self):
        create_dummy_plugin_metadata("plugin_g_dep", "com.example.plugin.g", version="1.0.0")
        create_dummy_plugin_metadata("plugin_h_user", "com.example.plugin.h", 
                                     dependencies={"plugins": [{"id": "com.example.plugin.g", "version_specifier": "==1.0.1"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.g"), "loaded") # G loads fine
        self.assertEqual(manager.plugin_status.get("com.example.plugin.h"), "disabled_dependency_issue")

    async def test_plugin_dependency_version_mismatch_range(self):
        create_dummy_plugin_metadata("plugin_i_dep", "com.example.plugin.i", version="2.0.0")
        create_dummy_plugin_metadata("plugin_j_user", "com.example.plugin.j", 
                                     dependencies={"plugins": [{"id": "com.example.plugin.i", "version_specifier": ">=1.0.0,<2.0.0"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.i"), "loaded")
        self.assertEqual(manager.plugin_status.get("com.example.plugin.j"), "disabled_dependency_issue")

    async def test_python_library_dependency_met_no_version(self):
        # Uses 'json' which is a built-in module, always available
        create_dummy_plugin_metadata("plugin_k_user", "com.example.plugin.k", 
                                     dependencies={"python_libraries": [{"name": "json"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.k"), "loaded")

    async def test_python_library_dependency_met_with_version(self):
        # Uses 'packaging' which we know is installed and its version can be checked.
        # We assume packaging version is something like 20.0 or higher for this test.
        create_dummy_plugin_metadata("plugin_l_user", "com.example.plugin.l", 
                                     dependencies={"python_libraries": [{"name": "packaging", "version_specifier": ">=20.0"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.l"), "loaded")

    async def test_python_library_dependency_not_found(self):
        create_dummy_plugin_metadata("plugin_m_user", "com.example.plugin.m", 
                                     dependencies={"python_libraries": [{"name": "non_existent_library_for_test"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.m"), "disabled_dependency_issue")

    async def test_python_library_dependency_version_mismatch(self):
        # Assuming 'packaging' version is not < 10.0
        create_dummy_plugin_metadata("plugin_n_user", "com.example.plugin.n", 
                                     dependencies={"python_libraries": [{"name": "packaging", "version_specifier": "<10.0"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.n"), "disabled_dependency_issue")

    async def test_combined_dependencies_all_met(self):
        create_dummy_plugin_metadata("plugin_o_dep", "com.example.plugin.o", version="1.0.0")
        create_dummy_plugin_metadata("plugin_p_user", "com.example.plugin.p", 
                                     dependencies={
                                         "plugins": [{"id": "com.example.plugin.o", "version_specifier": "==1.0.0"}],
                                         "python_libraries": [{"name": "json"}]
                                     })
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.o"), "loaded")
        self.assertEqual(manager.plugin_status.get("com.example.plugin.p"), "loaded")

    async def test_combined_dependencies_plugin_fails(self):
        create_dummy_plugin_metadata("plugin_q_user", "com.example.plugin.q", 
                                     dependencies={
                                         "plugins": [{"id": "com.example.plugin.nonexistent_o"}],
                                         "python_libraries": [{"name": "json"}]
                                     })
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.q"), "disabled_dependency_issue")

    async def test_combined_dependencies_library_fails(self):
        create_dummy_plugin_metadata("plugin_r_dep", "com.example.plugin.r", version="1.0.0")
        create_dummy_plugin_metadata("plugin_s_user", "com.example.plugin.s", 
                                     dependencies={
                                         "plugins": [{"id": "com.example.plugin.r", "version_specifier": "==1.0.0"}],
                                         "python_libraries": [{"name": "non_existent_library_for_test_s"}]
                                     })
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.plugin.r"), "loaded")
        self.assertEqual(manager.plugin_status.get("com.example.plugin.s"), "disabled_dependency_issue")
    
    async def test_circular_dependencies_compatible(self):
        # A depends on B, B depends on A. Both compatible.
        create_dummy_plugin_metadata("plugin_circ_a", "com.example.circ.a", version="1.0.0",
                                     dependencies={"plugins": [{"id": "com.example.circ.b", "version_specifier": ">=1.0.0"}]})
        create_dummy_plugin_metadata("plugin_circ_b", "com.example.circ.b", version="1.0.0",
                                     dependencies={"plugins": [{"id": "com.example.circ.a", "version_specifier": ">=1.0.0"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        self.assertEqual(manager.plugin_status.get("com.example.circ.a"), "loaded")
        self.assertEqual(manager.plugin_status.get("com.example.circ.b"), "loaded")

    async def test_circular_dependencies_incompatible(self):
        # A depends on B==1.0.0, B (v1.0.0) depends on A==2.0.0. A (v1.0.0) is present.
        # B should fail because A v2.0.0 is not met. Then A should fail because B is not loaded.
        create_dummy_plugin_metadata("plugin_circ_x_v1", "com.example.circ.x", version="1.0.0",
                                     dependencies={"plugins": [{"id": "com.example.circ.y", "version_specifier": "==1.0.0"}]})
        create_dummy_plugin_metadata("plugin_circ_y_v1", "com.example.circ.y", version="1.0.0",
                                     dependencies={"plugins": [{"id": "com.example.circ.x", "version_specifier": "==2.0.0"}]})
        manager = PluginManager([TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS], PLUGIN_SCHEMA_PATH_FOR_DEP_TESTS)
        # The order of failure might depend on processing order, but both should be disabled.
        self.assertEqual(manager.plugin_status.get("com.example.circ.x"), "disabled_dependency_issue")
        self.assertEqual(manager.plugin_status.get("com.example.circ.y"), "disabled_dependency_issue")

    def setUp(self):
        # Clean the test plugin directory before each test to ensure isolation
        if os.path.exists(TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS):
            shutil.rmtree(TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS)
        os.makedirs(TEST_PLUGINS_ROOT_DIR_FOR_DEP_TESTS, exist_ok=True)

if __name__ == "__main__":
    unittest.main()

