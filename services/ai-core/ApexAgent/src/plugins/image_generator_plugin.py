# ApexAgent Plugin: Image Generation
# This plugin allows ApexAgent to generate images based on text prompts using pre-trained models.

import os
import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image # For image type hinting, though not directly used for saving if pipeline handles it
import uuid # For generating unique filenames
from huggingface_hub import login # For authenticating with Hugging Face

# Assuming a BaseToolPlugin class exists in the project structure.
# If not, this class would inherit from object or a more generic base.
# from .base_tool_plugin import BaseToolPlugin # This would be the ideal import

# For the purpose of this task, let's define a placeholder if BaseToolPlugin is not available
# In a real scenario, this would be part of the agent's core plugin system.
class BaseToolPlugin:
    def __init__(self, agent_config, plugin_manager, api_key_manager):
        pass

class ImageGenerationPlugin(BaseToolPlugin):
    PLUGIN_NAME = "image_generation"
    PLUGIN_VERSION = "0.1.0"
    PLUGIN_DESCRIPTION = "Generates images from text prompts using local AI models."
    PLUGIN_AUTHOR = "ApexAgent Team"

    def __init__(self, agent_config=None, plugin_manager=None, api_key_manager=None):
        super().__init__(agent_config, plugin_manager, api_key_manager)
        self.agent_config = agent_config if agent_config else {}
        self.plugin_manager = plugin_manager # For potential notifications
        self.api_key_manager = api_key_manager # For accessing Hugging Face API key

        # Configuration - defaults can be overridden by agent_config
        self.default_model_id = self.agent_config.get(
            "image_generation_plugin.default_model",
            "stabilityai/stable-diffusion-xl-base-1.0"
        )
        self.default_output_dir = self.agent_config.get(
            "image_generation_plugin.default_output_dir",
            os.path.join(os.path.expanduser("~"), "apex_agent_generated_images")
        )

        os.makedirs(self.default_output_dir, exist_ok=True)

        # Authenticate with Hugging Face if API key is available
        self._authenticate_huggingface()

        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.pipeline = None
        self.current_model_id = None
        self._load_model(self.default_model_id)

    def _authenticate_huggingface(self):
        """Authenticate with Hugging Face using the stored API key if available."""
        if self.api_key_manager:
            hf_api_key = self.api_key_manager.get_api_key("huggingface")
            if hf_api_key:
                try:
                    login(token=hf_api_key)
                    if self.plugin_manager:
                        self.plugin_manager.notify_user(
                            "Successfully authenticated with Hugging Face using stored API key.", "info"
                        )
                    print("[ImageGenerationPlugin] Successfully authenticated with Hugging Face.")
                    return True
                except Exception as e:
                    error_message = f"[ImageGenerationPlugin] Failed to authenticate with Hugging Face: {str(e)}"
                    print(error_message)
                    if self.plugin_manager:
                        self.plugin_manager.notify_user(error_message, "warning")
        
        print("[ImageGenerationPlugin] No Hugging Face API key found or authentication failed. Proceeding without authentication.")
        return False

    def _load_model(self, model_id):
        print(f"[ImageGenerationPlugin] Attempting to load model: {model_id} on device: {self.device}")
        try:
            if hasattr(self, 'pipeline') and self.pipeline is not None:
                del self.pipeline # Release previous model if any
                if self.device == "cuda":
                    torch.cuda.empty_cache()
            
            dtype = torch.float16 if self.device != "cpu" else torch.float32
            
            # Check if we have a Hugging Face API key for potential private models or higher rate limits
            use_auth = False
            if self.api_key_manager:
                hf_api_key = self.api_key_manager.get_api_key("huggingface")
                use_auth = hf_api_key is not None
            
            # Load the model with appropriate authentication if available
            self.pipeline = AutoPipelineForText2Image.from_pretrained(
                model_id,
                torch_dtype=dtype,
                # variant="fp16", # Use if appropriate for the model and precision
                # use_safetensors=True, # Recommended if available for the model
                # If we have an API key, we're already authenticated via login() in _authenticate_huggingface
                # But we can also pass the token directly if needed for some reason
                # token=hf_api_key if use_auth else None,
            )
            self.pipeline = self.pipeline.to(self.device)
            self.current_model_id = model_id
            print(f"[ImageGenerationPlugin] Successfully loaded model {model_id} on {self.device}")
            if self.device == "cpu" and self.plugin_manager:
                self.plugin_manager.notify_user(
                    "Image generation plugin: No GPU detected. Image generation may be slow.", "warning"
                )
        except Exception as e:
            error_message = f"[ImageGenerationPlugin] Error loading image model {model_id}: {str(e)}"
            print(error_message)
            if self.plugin_manager:
                self.plugin_manager.notify_user(error_message, "error")
            self.pipeline = None
            self.current_model_id = None
            # Consider re-raising or returning an error status

    def get_actions(self):
        """Returns a list of actions this plugin can perform, with descriptions and parameters."""
        return [
            {
                "name": "generate_image",
                "description": "Generates an image based on a textual prompt.",
                "parameters": [
                    {"name": "prompt", "type": "string", "required": True, "description": "The text prompt describing the image to generate."},
                    {"name": "output_filename", "type": "string", "required": False, "description": "Optional filename (without extension) for the output image. If not provided, a unique name will be generated (e.g., image_12345.png)."},
                    {"name": "model_id", "type": "string", "required": False, "description": f"Specific model ID to use (e.g., 'stabilityai/sdxl-lightning'). Defaults to the current model: {self.current_model_id or self.default_model_id}."},
                    {"name": "num_inference_steps", "type": "integer", "required": False, "description": "Number of denoising steps (e.g., 20-50). Default depends on model."},
                    {"name": "guidance_scale", "type": "float", "required": False, "description": "Guidance scale (e.g., 7.5). Default depends on model."},
                    {"name": "negative_prompt", "type": "string", "required": False, "description": "Prompt to steer generation away from specific elements."},
                    {"name": "width", "type": "integer", "required": False, "description": "Width of the generated image in pixels."},
                    {"name": "height", "type": "integer", "required": False, "description": "Height of the generated image in pixels."},
                    {"name": "seed", "type": "integer", "required": False, "description": "Seed for random number generation, for reproducibility."}
                ]
            }
        ]

    async def execute_action(self, action_name: str, parameters: dict):
        if action_name == "generate_image":
            prompt = parameters.get("prompt")
            if not prompt:
                return {"status": "error", "message": "Prompt is required for image generation."}

            output_filename = parameters.get("output_filename")
            model_id = parameters.get("model_id")
            
            if model_id and model_id != self.current_model_id:
                self._load_model(model_id)
            
            if not self.pipeline:
                if not self.current_model_id: # If no model was ever loaded (e.g. initial load failed)
                    self._load_model(self.default_model_id)
                if not self.pipeline: # If still no pipeline after trying default
                    return {"status": "error", "message": "Image generation model is not loaded or failed to load. Please check configuration or try again."}

            # Prepare generation parameters, using defaults from the pipeline if not specified
            gen_kwargs = {}
            if parameters.get("num_inference_steps") is not None: gen_kwargs["num_inference_steps"] = parameters["num_inference_steps"]
            if parameters.get("guidance_scale") is not None: gen_kwargs["guidance_scale"] = parameters["guidance_scale"]
            if parameters.get("negative_prompt") is not None: gen_kwargs["negative_prompt"] = parameters["negative_prompt"]
            if parameters.get("width") is not None: gen_kwargs["width"] = parameters["width"]
            if parameters.get("height") is not None: gen_kwargs["height"] = parameters["height"]
            if parameters.get("seed") is not None:
                generator = torch.Generator(device=self.device).manual_seed(parameters["seed"])
                gen_kwargs["generator"] = generator

            try:
                if self.plugin_manager:
                    self.plugin_manager.notify_user("Starting image generation... this may take a moment.", "info")
                
                # Diffusers pipeline direct call
                # The pipeline might return a list if num_images_per_prompt > 1, but we assume 1 for now.
                generated_images = self.pipeline(prompt=prompt, **gen_kwargs).images
                if not generated_images:
                    return {"status": "error", "message": "Image generation failed: No image returned by the model."}
                
                image = generated_images[0] # Taking the first image

                if not output_filename:
                    output_filename = f"generated_image_{uuid.uuid4().hex[:8]}.png"
                elif not output_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # Append .png if no valid extension is provided, or ensure it's a common format
                    output_filename = f"{os.path.splitext(output_filename)[0]}.png"
                
                save_path = os.path.join(self.default_output_dir, output_filename)
                image.save(save_path)
                
                return {"status": "success", "image_path": save_path, "message": f"Image saved to {save_path}"}

            except Exception as e:
                error_msg = f"Image generation failed: {str(e)}"
                if self.plugin_manager:
                    self.plugin_manager.notify_user(error_msg, "error")
                return {"status": "error", "message": error_msg}
        else:
            return {"status": "error", "message": f"Action '{action_name}' not supported by ImageGenerationPlugin."}

    def shutdown(self):
        # Clean up resources, especially if running on GPU
        if hasattr(self, 'pipeline') and self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
        if self.device == "cuda":
            torch.cuda.empty_cache()
        print("ImageGenerationPlugin shutdown and resources released.")

# Example usage (conceptual, actual execution would be managed by ApexAgent core)
if __name__ == '__main__':
    # This is for standalone testing if needed, not part of the agent's direct execution path
    # Mock agent_config and plugin_manager for testing
    class MockPluginManager:
        def notify_user(self, message, level):
            print(f"[{level.upper()}] {message}")
    
    class MockApiKeyManager:
        def get_api_key(self, service_name):
            if service_name == "huggingface":
                return "YOUR_HUGGINGFACE_API_KEY_HERE"  # This would be retrieved from secure storage in a real scenario
            return None

    config = {
        "image_generation_plugin.default_model": "stabilityai/stable-diffusion-xl-base-1.0",
        "image_generation_plugin.default_output_dir": "./generated_images"
    }
    os.makedirs(config["image_generation_plugin.default_output_dir"], exist_ok=True)

    image_plugin = ImageGenerationPlugin(
        agent_config=config, 
        plugin_manager=MockPluginManager(), 
        api_key_manager=MockApiKeyManager()
    )
    
    # Example: Generate an image
    # Note: In a real scenario, execute_action would be called by the agent core.
    # For direct testing, you might call the method directly if it's not async, 
    # or use asyncio.run for async methods.
    # Since execute_action is async, we'd need an event loop to run it here.
    # For simplicity, we'll just show the structure.

    # To test execute_action (if it were synchronous for this example):
    # result = image_plugin.execute_action("generate_image", {"prompt": "A futuristic cat astronaut"})
    # print(result)

    # To test generate_image directly (if it were synchronous):
    # result = image_plugin.generate_image(prompt="A photo of a red apple on a wooden table")
    # print(result)
    
    # For async, you'd typically do:
    # import asyncio
    # async def main_test():
    #     result = await image_plugin.execute_action("generate_image", {"prompt": "A futuristic cat astronaut"})
    #     print(result)
    # asyncio.run(main_test())

    print("ImageGenerationPlugin class structure defined.")
    print("To test, you would integrate this with the ApexAgent core.")
    print("Simulating a call to generate an image (requires model download on first run):")
    
    # Simplified synchronous call for basic testing demonstration (actual plugin uses async execute_action)
    # This direct call bypasses the intended async execute_action flow for a quick check.
    # For proper testing, it should be run within an async context if execute_action is async.
    # However, the core generation logic itself is not async in the provided snippet.
    # Let's assume for this simple test, we call a hypothetical synchronous version or adapt. 
    # The provided snippet for execute_action is async, so this direct call is not quite right.
    # The main point is to show the class structure.
    pass
