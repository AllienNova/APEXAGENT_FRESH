# src/plugins/tools/internal/web_browser_tool.py
import asyncio
from typing import Dict, Any
# In a real scenario, you would use a proper HTTP client library like httpx or aiohttp
# For simplicity, this example might be very basic or use a synchronous library in an async wrapper.
# For a real implementation, ensure non-blocking I/O.
import httpx # Added httpx to dependencies

from src.plugins.tools.base_tool_plugin import BaseToolPlugin, ToolInfo, ToolOutputSchema, ToolParameterInfo

class WebBrowserTool(BaseToolPlugin):
    def get_tool_info(self) -> ToolInfo:
        return {
            "name": "web_browser_fetch_content",
            "display_name": "Fetch Web Content",
            "description": "Fetches the HTML content of a given URL.",
            "category": "Web Interaction",
            "input_schema": {
                "url": {
                    "name": "url",
                    "type": "string",
                    "description": "The URL to fetch content from.",
                    "required": True,
                    "default": None
                },
                "timeout": {
                    "name": "timeout",
                    "type": "integer",
                    "description": "Maximum time in seconds to wait for the request.",
                    "required": False,
                    "default": 30 # Default timeout of 30 seconds
                }
            },
            "output_description": "Returns the HTML content of the page as a string, or an error message."
        }

    async def execute(self, inputs: Dict[str, Any]) -> ToolOutputSchema:
        if not self.validate_inputs(inputs):
            return {
                "success": False,
                "result": None,
                "error": "Invalid inputs provided. Missing required parameter: url."
            }
        
        url = inputs.get("url")
        timeout = inputs.get("timeout", 30)

        if not isinstance(url, str):
            return {
                "success": False,
                "result": None,
                "error": "Invalid input type for url. Expected a string."
            }
        if not (url.startswith("http://") or url.startswith("https://")):
            return {
                "success": False,
                "result": None,
                "error": "Invalid URL format. Must start with http:// or https://"
            }
        if not isinstance(timeout, int) or timeout <= 0:
            return {
                "success": False,
                "result": None,
                "error": "Invalid input type or value for timeout. Expected a positive integer."
            }

        try:
            async with httpx.AsyncClient(timeout=float(timeout), follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status() # Raises an HTTPStatusError for 4xx/5xx responses
                content = response.text
            return {
                "success": True,
                "result": content,
                "error": None
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "result": None,
                "error": f"Request to {url} timed out after {timeout} seconds."
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "result": None,
                "error": f"Failed to fetch content from {url}: Request error - {str(e)}"
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "result": None,
                "error": f"Failed to fetch content from {url}: HTTP error {e.response.status_code} - {e.response.reason_phrase}"
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": f"Failed to fetch content from {url}: An unexpected error occurred - {str(e)}"
            }


