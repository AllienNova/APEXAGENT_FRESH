import sys
import os
import asyncio
import unittest
import shutil

# Add project root to Python path to allow importing plugin
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, project_root)

from plugins.image_generator_plugin import ImageGenerationPlugin

class MockPluginManager:
    def __init__(self):
        self.notifications = []

    def notify_user(self, message, level):
        self.notifications.append((level, message))
        print(f"[PLUGIN_MANAGER_MOCK] [{level.upper()}] {message}")

class TestImageGenerationPlugin(unittest.TestCase):
    def setUp(self):
        self.test_output_dir = os.path.join(os.path.expanduser("~"), "apex_agent_test_generated_images")
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        self.agent_config = {
            "image_generation_plugin.default_model": "stabilityai/stable-diffusion-xl-base-1.0", # A common model
            # "image_generation_plugin.default_model": "hf-internal-testing/tiny-stable-diffusion-pipe", # A very small model for faster testing if available and works with AutoPipelineForText2Image
            "image_generation_plugin.default_output_dir": self.test_output_dir
        }
        self.plugin_manager = MockPluginManager()
        self.plugin = ImageGenerationPlugin(agent_config=self.agent_config, plugin_manager=self.plugin_manager, api_key_manager=None)

    def tearDown(self):
        # Clean up the test output directory
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        # Shutdown plugin to release resources
        if hasattr(self.plugin, 'shutdown'):
            self.plugin.shutdown()

    def test_01_plugin_initialization(self):
        self.assertIsNotNone(self.plugin, "Plugin should initialize")
        self.assertEqual(self.plugin.PLUGIN_NAME, "image_generation")
        self.assertTrue(os.path.exists(self.test_output_dir), "Test output directory should be created")
        # Check if model loading was attempted (even if it fails due to no internet/space, it should try)
        # A more robust check would be to see if self.plugin.pipeline is None and if there's an error notification
        # For now, we assume it tries. If it fails, other tests will show it.

    def test_02_get_actions(self):
        actions = self.plugin.get_actions()
        self.assertIsInstance(actions, list)
        self.assertGreater(len(actions), 0)
        generate_action = next((action for action in actions if action["name"] == "generate_image"), None)
        self.assertIsNotNone(generate_action)
        self.assertIn("prompt", [param["name"] for param in generate_action["parameters"]])

    # @unittest.skipIf(os.environ.get("SKIP_NETWORK_TESTS") == "1", "Skipping network-intensive test")
    def test_03_generate_image_action(self):
        # This test will download a large model if not cached and requires GPU/CPU time.
        # Using a very simple prompt.
        # Note: The actual model "stabilityai/stable-diffusion-xl-base-1.0" is large.
        # For CI/CD or quick tests, a smaller dummy model would be better if `diffusers` supports one
        # that works with AutoPipelineForText2Image. "hf-internal-testing/tiny-stable-diffusion-pipe" is one such model.
        # Let's try to switch to a tiny model for testing if it works, otherwise this test will be very slow.
        
        # Update: The plugin loads default model on init. To test a different one, we'd pass model_id.
        # For this test, we rely on the default model loaded in setUp.
        # If the default model is large, this test will be slow.
        
        if not self.plugin.pipeline:
            # If the default model failed to load in setUp, we might try a known small one here
            # or skip the test with a warning.
            print("Default model did not load in setUp. Attempting to load a tiny model for testing.")
            try:
                self.plugin._load_model("hf-internal-testing/tiny-stable-diffusion-pipe")
            except Exception as e:
                self.skipTest(f"Could not load any model for testing: {e}")

        if not self.plugin.pipeline:
             self.skipTest("Image generation model could not be loaded. Skipping generation test.")

        action_params = {
            "prompt": "A red apple on a table",
            "output_filename": "test_apple",
            "num_inference_steps": 1, # Use minimal steps for faster testing with tiny models
            "width": 64, # Use minimal dimensions for tiny models
            "height": 64
        }
        
        print(f"Starting image generation test with model: {self.plugin.current_model_id}")
        result = asyncio.run(self.plugin.execute_action("generate_image", action_params))
        print(f"Generation result: {result}")

        self.assertIsNotNone(result, "Execution result should not be None")
        self.assertEqual(result.get("status"), "success", f"Image generation failed: {result.get('message')}")
        self.assertIn("image_path", result, "Result should contain image_path")
        
        image_path = result["image_path"]
        self.assertTrue(os.path.exists(image_path), f"Generated image file should exist at {image_path}")
        self.assertTrue(os.path.getsize(image_path) > 0, "Generated image file should not be empty")
        
        # Verify filename (plugin appends .png)
        expected_filename = "test_apple.png"
        self.assertEqual(os.path.basename(image_path), expected_filename)

    def test_04_generate_image_without_filename(self):
        if not self.plugin.pipeline:
             self.skipTest("Image generation model could not be loaded. Skipping generation test.")

        action_params = {
            "prompt": "A blue bird flying",
            "num_inference_steps": 1,
            "width": 64,
            "height": 64
        }
        result = asyncio.run(self.plugin.execute_action("generate_image", action_params))
        self.assertEqual(result.get("status"), "success", f"Image generation failed: {result.get('message')}")
        self.assertIn("image_path", result)
        image_path = result["image_path"]
        self.assertTrue(os.path.exists(image_path))
        self.assertTrue(os.path.basename(image_path).startswith("generated_image_"))
        self.assertTrue(os.path.basename(image_path).endswith(".png"))

    def test_05_invalid_action(self):
        result = asyncio.run(self.plugin.execute_action("non_existent_action", {}))
        self.assertEqual(result.get("status"), "error")
        self.assertIn("not supported", result.get("message", ""))

    def test_06_generate_image_missing_prompt(self):
        result = asyncio.run(self.plugin.execute_action("generate_image", {}))
        self.assertEqual(result.get("status"), "error")
        self.assertIn("Prompt is required", result.get("message", ""))

if __name__ == '__main__':
    # To run tests: python -m unittest test_image_generator_plugin.py
    # Ensure that the necessary libraries (torch, diffusers, transformers, accelerate) are installed.
    # And that you have an internet connection for model download on first run.
    unittest.main()


