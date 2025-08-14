# src/plugins/tools/internal/desktop_automation_tool.py
import pyautogui
from typing import Dict, Any, Optional, List, Union

from src.plugins.tools.base_tool_plugin import BaseToolPlugin, ToolInfo, ToolInput, ToolOutput

class DesktopAutomationTool(BaseToolPlugin):
    def get_tool_info(self) -> ToolInfo:
        return ToolInfo(
            name="desktop_automation_agent",
            description="A tool for automating desktop GUI interactions like mouse movement, clicks, keyboard input, and taking screenshots.",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string", 
                        "enum": [
                            "move_mouse_to", 
                            "click", 
                            "double_click", 
                            "right_click", 
                            "drag_mouse_to", 
                            "type_text", 
                            "press_key", 
                            "hotkey", 
                            "screenshot",
                            "locate_on_screen" # New action
                        ]
                    },
                    "x": {"type": "integer", "description": "X-coordinate for mouse actions."},
                    "y": {"type": "integer", "description": "Y-coordinate for mouse actions."},
                    "duration": {"type": "number", "description": "Duration in seconds for mouse movement or drag.", "default": 0.5},
                    "button": {"type": "string", "enum": ["left", "middle", "right"], "description": "Mouse button to click or drag.", "default": "left"},
                    "text_to_type": {"type": "string", "description": "Text to type using the keyboard."},
                    "keys": {"type": "array", "items": {"type": "string"}, "description": "List of keys to press or for a hotkey combination (e.g., ["ctrl", "c"])."},
                    "screenshot_path": {"type": "string", "description": "Full path to save the screenshot (e.g., /path/to/image.png)."},
                    "region": {"type": "array", "items": {"type": "integer"}, "description": "Optional region for screenshot or locate_on_screen [left, top, width, height]."},
                    "image_to_locate": {"type": "string", "description": "Path to an image file to locate on the screen."},
                    "confidence": {"type": "number", "description": "Confidence level for image location (0.0 to 1.0).", "default": 0.9}
                },
                "required": ["action"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                    "screenshot_location": {"type": "string"},
                    "located_region": {"type": "array", "items": {"type": "number"}, "description": "[left, top, width, height] of located image or null."}
                }
            }
        )

    async def execute(self, inputs: ToolInput) -> ToolOutput:
        action = inputs.get("action")
        result: Dict[str, Any] = {"status": "error", "message": "Action not implemented or failed"}

        try:
            if action == "move_mouse_to":
                x = inputs.get("x")
                y = inputs.get("y")
                duration = inputs.get("duration", 0.5)
                if x is None or y is None:
                    return ToolOutput(data={"status": "error", "message": "x and y coordinates are required for move_mouse_to"})
                pyautogui.moveTo(x, y, duration=duration)
                result = {"status": "success", "message": f"Mouse moved to ({x}, {y})"}

            elif action == "click" or action == "double_click" or action == "right_click":
                x = inputs.get("x")
                y = inputs.get("y")
                button = inputs.get("button", "left")
                kwargs = {"button": button}
                if x is not None and y is not None:
                    kwargs["x"] = x
                    kwargs["y"] = y
                
                if action == "click":
                    pyautogui.click(**kwargs)
                    position_str = f"({kwargs["x"]}, {kwargs["y"]})" if "x" in kwargs else "current position"
                    result = {"status": "success", "message": f"{button.capitalize()} click at {position_str}"}
                elif action == "double_click":
                    pyautogui.doubleClick(**kwargs)
                    position_str = f"({kwargs["x"]}, {kwargs["y"]})" if "x" in kwargs else "current position"
                    result = {"status": "success", "message": f"{button.capitalize()} double click at {position_str}"}
                elif action == "right_click": # Ensure button is right for this specific action name
                    kwargs["button"] = "right"
                    pyautogui.click(**kwargs)
                    position_str = f"({kwargs["x"]}, {kwargs["y"]})" if "x" in kwargs else "current position"
                    result = {"status": "success", "message": f"Right click at {position_str}"}

            elif action == "drag_mouse_to":
                x = inputs.get("x")
                y = inputs.get("y")
                duration = inputs.get("duration", 0.5)
                button = inputs.get("button", "left")
                if x is None or y is None:
                    return ToolOutput(data={"status": "error", "message": "x and y coordinates are required for drag_mouse_to"})
                pyautogui.dragTo(x, y, duration=duration, button=button)
                result = {"status": "success", "message": f"Mouse dragged to ({x}, {y}) with {button} button"}

            elif action == "type_text":
                text_to_type = inputs.get("text_to_type")
                if text_to_type is None:
                    return ToolOutput(data={"status": "error", "message": "text_to_type is required for type_text action"})
                pyautogui.typewrite(text_to_type, interval=0.05) # Small interval for more human-like typing
                result = {"status": "success", "message": f"Typed text: {text_to_type}"}

            elif action == "press_key":
                keys_input = inputs.get("keys")
                if not keys_input or not isinstance(keys_input, list) or not keys_input[0]:
                    return ToolOutput(data={"status": "error", "message": "A non-empty list with at least one key is required for press_key action"})
                key_to_press = keys_input[0]
                pyautogui.press(key_to_press)
                result = {"status": "success", "message": f"Pressed key: {key_to_press}"}

            elif action == "hotkey":
                keys = inputs.get("keys")
                if not keys or not isinstance(keys, list) or len(keys) < 1:
                    return ToolOutput(data={"status": "error", "message": "A list of keys is required for hotkey action"})
                pyautogui.hotkey(*keys)
                result = {"status": "success", "message": f"Pressed hotkey: {', '.join(keys)}"}

            elif action == "screenshot":
                screenshot_path = inputs.get("screenshot_path")
                region = inputs.get("region")
                if not screenshot_path:
                    return ToolOutput(data={"status": "error", "message": "screenshot_path is required for screenshot action"})
                
                kwargs = {}
                if region and isinstance(region, list) and len(region) == 4:
                    kwargs["region"] = tuple(region)
                
                img = pyautogui.screenshot(**kwargs)
                img.save(screenshot_path)
                result = {"status": "success", "message": f"Screenshot saved to {screenshot_path}", "screenshot_location": screenshot_path}

            elif action == "locate_on_screen":
                image_to_locate = inputs.get("image_to_locate")
                confidence = inputs.get("confidence", 0.9)
                region_input = inputs.get("region")
                if not image_to_locate:
                    return ToolOutput(data={"status": "error", "message": "image_to_locate path is required"})
                
                kwargs = {"confidence": confidence}
                if region_input and isinstance(region_input, list) and len(region_input) == 4:
                    kwargs["region"] = tuple(region_input)
                
                try:
                    location = pyautogui.locateOnScreen(image_to_locate, **kwargs)
                    if location:
                        # Convert Box object to list [left, top, width, height]
                        located_region_list = [location.left, location.top, location.width, location.height]
                        result = {"status": "success", "message": f"Image found at {located_region_list}", "located_region": located_region_list}
                    else:
                        result = {"status": "success", "message": "Image not found on screen.", "located_region": None}
                except Exception as e: # pyautogui.ImageNotFoundException might not always be specific enough
                    result = {"status": "error", "message": f"Error during image location: {str(e)}. Ensure OpenCV is installed (pip install opencv-python) and the image path is correct.", "located_region": None}
            
            else:
                result["message"] = f"Unknown action: {action}"

        except Exception as e:
            error_message = f"Error during desktop automation action 	{action}	: {str(e)}"
            print(error_message)
            result["message"] = error_message
            result["status"] = "error"
        
        return ToolOutput(data=result)

# Note: For this tool to work reliably, especially for locate_on_screen,
# the environment needs a display server (e.g., Xvfb if running in a headless Linux environment)
# and Python bindings for screenshotting and image manipulation (Pillow, and opencv-python for locateOnScreen confidence).
# PyAutoGUI itself might pull some of these, but opencv-python is often needed explicitly for advanced image location.

