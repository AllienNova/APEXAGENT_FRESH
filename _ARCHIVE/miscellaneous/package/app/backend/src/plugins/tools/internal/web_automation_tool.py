# src/plugins/tools/internal/web_automation_tool.py
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from playwright.async_api import async_playwright, Page, Browser, Error as PlaywrightException

from src.plugins.tools.base_tool_plugin import BaseToolPlugin, ToolInfo, ToolInputSchema as ToolInput, ToolOutputSchema as ToolOutput

# Keep track of the browser instance to reuse it
_browser_instance: Optional[Browser] = None
_playwright_instance: Optional[async_playwright] = None

async def get_browser_page() -> Tuple[Optional[Page], Optional[str]]:
    """Ensures a browser is running and returns a new page. Manages a single browser instance."""
    global _browser_instance, _playwright_instance
    try:
        if _playwright_instance is None:
            _playwright_instance = await async_playwright().start()
        
        if _browser_instance is None or not _browser_instance.is_connected():
            print("Starting new browser instance for web automation...")
            _browser_instance = await _playwright_instance.chromium.launch(headless=True) # Run headless for automation
            _browser_instance.on("disconnected", lambda: setattr(_browser_instance, "_is_disconnected_flag", True))
            setattr(_browser_instance, "_is_disconnected_flag", False)
            print("Browser instance started.")

        if getattr(_browser_instance, "_is_disconnected_flag", True):
            # Attempt to relaunch if disconnected flag is set
            print("Browser was disconnected, attempting to relaunch...")
            _browser_instance = await _playwright_instance.chromium.launch(headless=True)
            _browser_instance.on("disconnected", lambda: setattr(_browser_instance, "_is_disconnected_flag", True))
            setattr(_browser_instance, "_is_disconnected_flag", False)
            print("Browser relaunched.")

        page = await _browser_instance.new_page()
        return page, None
    except PlaywrightException as e:
        error_message = f"Playwright Error (get_browser_page): {str(e)}"
        print(error_message)
        # Attempt to close and clean up if error occurs during setup
        if _browser_instance and _browser_instance.is_connected():
            await _browser_instance.close()
        _browser_instance = None
        if _playwright_instance:
            await _playwright_instance.stop()
        _playwright_instance = None
        return None, error_message
    except Exception as e:
        error_message = f"Unexpected error in get_browser_page: {str(e)}"
        print(error_message)
        return None, error_message

async def close_browser_resources():
    """Closes the browser and playwright resources if they are active."""
    global _browser_instance, _playwright_instance
    if _browser_instance and _browser_instance.is_connected():
        print("Closing browser instance...")
        await _browser_instance.close()
        _browser_instance = None
        print("Browser instance closed.")
    if _playwright_instance:
        print("Stopping Playwright...")
        await _playwright_instance.stop()
        _playwright_instance = None
        print("Playwright stopped.")

class WebAutomationTool(BaseToolPlugin):
    def get_tool_info(self) -> ToolInfo:
        return ToolInfo(
            name="web_automation_agent",
            description="A tool for automating web browser interactions like navigation, clicking, typing, and extracting content.",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["navigate", "click", "type", "get_content", "fill_form"]},
                    "url": {"type": "string", "description": "URL to navigate to (for navigate action)."},
                    "selector": {"type": "string", "description": "CSS selector for the element to interact with (for click, type, fill_form actions)."},
                    "text_to_type": {"type": "string", "description": "Text to type into an element (for type action)."},
                    "form_data": {"type": "object", "description": "A dictionary of selector:value pairs for filling a form (for fill_form action)."},
                    "wait_for_navigation": {"type": "boolean", "description": "Whether to wait for navigation after an action (e.g., click). Defaults to True for clicks.", "default": True}
                },
                "required": ["action"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "page_title": {"type": "string"},
                    "current_url": {"type": "string"},
                    "content": {"type": "string", "description": "Extracted text content from the page or element."},
                    "error": {"type": "string"}
                }
            }
        )

    async def execute(self, inputs: ToolInput) -> ToolOutput:
        action = inputs.get("action")
        page: Optional[Page] = None
        error_message: Optional[str] = None
        result: Dict[str, Any] = {"status": "error", "content": None, "error": "Action not implemented or failed"}

        try:
            page, error_message = await get_browser_page()
            if error_message or not page:
                return ToolOutput(data={"status": "error", "error": error_message or "Failed to get browser page"})

            if action == "navigate":
                url = inputs.get("url")
                if not url:
                    return ToolOutput(data={"status": "error", "error": "URL is required for navigate action"})
                print(f"Navigating to: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                result["status"] = "success"
                result["page_title"] = await page.title()
                result["current_url"] = page.url
                print(f"Navigation successful to {page.url}")

            elif action == "click":
                selector = inputs.get("selector")
                if not selector:
                    return ToolOutput(data={"status": "error", "error": "Selector is required for click action"})
                print(f"Attempting to click element with selector: {selector}")
                element = page.locator(selector).first # Ensure we target one element
                await element.click(timeout=30000)
                # Optional: wait for navigation if expected
                if inputs.get("wait_for_navigation", True):
                    try:
                        await page.wait_for_load_state("domcontentloaded", timeout=30000) # Wait for potential navigation
                        print("Load state after click achieved.")
                    except PlaywrightException as e:
                        print(f"Timeout or error waiting for navigation after click: {str(e)}. Proceeding...")
                
                result["status"] = "success"
                result["page_title"] = await page.title()
                result["current_url"] = page.url
                print(f"Click successful on {selector}")

            elif action == "type":
                selector = inputs.get("selector")
                text_to_type = inputs.get("text_to_type")
                if not selector or text_to_type is None: # text_to_type can be empty string
                    return ToolOutput(data={"status": "error", "error": "Selector and text_to_type are required for type action"})
                print(f"Attempting to type into element with selector: {selector}")
                element = page.locator(selector).first
                await element.fill(text_to_type, timeout=30000) # fill clears existing content and types
                result["status"] = "success"
                result["page_title"] = await page.title()
                result["current_url"] = page.url
                print(f"Typing successful into {selector}")

            elif action == "get_content":
                selector = inputs.get("selector") # Optional: get content of specific element
                if selector:
                    print(f"Getting content from element with selector: {selector}")
                    element = page.locator(selector).first
                    content = await element.inner_text(timeout=30000)
                else:
                    print("Getting content from entire page")
                    content = await page.content() # Gets full HTML, consider page.inner_text("body") for just text
                result["status"] = "success"
                result["content"] = content
                result["page_title"] = await page.title()
                result["current_url"] = page.url
                print("Get content successful.")

            elif action == "fill_form":
                form_data = inputs.get("form_data")
                if not isinstance(form_data, dict) or not form_data:
                    return ToolOutput(data={"status": "error", "error": "form_data (object with selector:value pairs) is required for fill_form action"})
                
                print(f"Attempting to fill form with data: {form_data}")
                for selector, value_to_fill in form_data.items():
                    print(f"Filling selector 	{selector}	 with value: 	{value_to_fill}")
                    element = page.locator(selector).first
                    await element.fill(str(value_to_fill), timeout=30000)
                result["status"] = "success"
                result["page_title"] = await page.title()
                result["current_url"] = page.url
                print("Form fill successful.")
            
            else:
                result["error"] = f"Unknown action: {action}"

        except PlaywrightException as e:
            error_message = f"Playwright Error ({action}): {str(e)}"
            print(error_message)
            result["error"] = error_message
            result["status"] = "error"
        except Exception as e:
            error_message = f"Unexpected error during web automation action 	{action}	: {str(e)}"
            print(error_message)
            result["error"] = error_message
            result["status"] = "error"
        finally:
            if page:
                try:
                    # Don_t close the page here if we want to reuse the browser instance for subsequent actions.
                    # The browser instance is managed globally by get_browser_page and close_browser_resources.
                    # However, if a specific action implies the end of a sequence, page.close() might be considered.
                    # For now, we keep the page open, relying on a higher-level mechanism or explicit close action if needed.
                    pass 
                except Exception as e:
                    print(f"Error trying to close page (or not closing): {e}")
        
        return ToolOutput(data=result)

# It might be useful to have a separate tool or agent lifecycle method to explicitly close the browser 
# when the agent is shutting down or after a long period of inactivity.
# For now, this is a basic implementation.

# To ensure cleanup on agent shutdown (conceptual):
# async def on_agent_shutdown():
# await close_browser_resources()

