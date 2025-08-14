# src/plugins/dummy_dependency_plugin.py
import logging
from .base_enhanced_plugin import BaseEnhancedPlugin # Assuming BaseEnhancedPlugin is in the same directory or accessible

logger = logging.getLogger(__name__)

class DummyDependencyPlugin(BaseEnhancedPlugin):
    def __init__(self, api_key_manager=None):
        super().__init__(api_key_manager=api_key_manager)
        self.plugin_name = "DummyDependencyPlugin"
        logger.info(f"{self.plugin_name} initialized.")

    async def test_action_with_deps(self, input_param: str) -> Dict[str, Any]:
        logger.info(f"{self.plugin_name} - test_action_with_deps called with: {input_param}")
        return {"status": "success", "message": f"Dummy action executed with {input_param}", "plugin": self.plugin_name}

    async def another_action(self) -> Dict[str, Any]:
        logger.info(f"{self.plugin_name} - another_action called")
        return {"status": "success", "message": "Another dummy action executed", "plugin": self.plugin_name}

