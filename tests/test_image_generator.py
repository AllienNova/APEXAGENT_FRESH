# This file is part of the Code Snippets Plugin for the Autonoma Framework.
# It is explicitly not part of the module's public API and is subject to change at any time.

import unittest
import os
from unittest.mock import MagicMock

# Assuming the image_generator_plugin.py is in the parent directory of the current file's directory
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.plugins.image_generator_plugin import ImageGenerationPlugin

class TestImageGenerationPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = ImageGenerationPlugin()

    def test_generate_image_with_valid_prompt(self):
        # This is a basic test to check if the method runs without errors.
        # It doesn't verify the content of the image, only that an image is created.
        prompt = "A beautiful sunset over a mountain range"
        filename = "test_image.png"
        result = self.plugin.generate_image(prompt, filename)
        self.assertTrue(os.path.exists(filename))
        # Clean up the created file
        os.remove(filename)

    def test_generate_image_with_custom_parameters(self):
        prompt = "A futuristic city with flying cars"
        filename = "custom_image.png"
        num_inference_steps = 30
        guidance_scale = 8.0
        result = self.plugin.generate_image(prompt, filename, num_inference_steps=num_inference_steps, guidance_scale=guidance_scale)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

    def test_generate_image_without_filename(self):
        prompt = "A cute cat wearing a hat"
        result = self.plugin.generate_image(prompt)
        self.assertTrue(os.path.exists(result["image_path"]))
        os.remove(result["image_path"]) # Clean up the generated file

    def test_generate_image_with_invalid_prompt(self):
        # Test with an empty prompt, expecting an error or specific handling
        with self.assertRaises(ValueError): # Assuming it raises a ValueError for empty prompts
            self.plugin.generate_image("")

    def test_generate_image_with_invalid_model_id(self):
        # Test with an invalid model ID, expecting an error
        with self.assertRaises(Exception): # Replace Exception with a more specific error if possible
            self.plugin.generate_image("A valid prompt", model_id="invalid_model_id")

if __name__ == '__main__':
    unittest.main()
