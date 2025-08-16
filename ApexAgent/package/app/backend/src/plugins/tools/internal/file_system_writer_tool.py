# src/plugins/tools/internal/file_system_writer_tool.py
import os
from typing import Dict, Any
from src.plugins.tools.base_tool_plugin import BaseToolPlugin, ToolInfo, ToolOutputSchema, ToolParameterInfo

class FileSystemWriterTool(BaseToolPlugin):
    def get_tool_info(self) -> ToolInfo:
        return {
            "name": "file_system_write_file",
            "display_name": "Write File",
            "description": "Writes or appends content to a specified text file on the local file system.",
            "category": "File System",
            "input_schema": {
                "path": {
                    "name": "path",
                    "type": "string",
                    "description": "The absolute path to the file to be written.",
                    "required": True,
                    "default": None
                },
                "content": {
                    "name": "content",
                    "type": "string",
                    "description": "The text content to write to the file.",
                    "required": True,
                    "default": None
                },
                "append": {
                    "name": "append",
                    "type": "boolean",
                    "description": "If true, appends content to the file. If false (default), overwrites the file.",
                    "required": False,
                    "default": False
                }
            },
            "output_description": "Returns a success status or an error message."
        }

    async def execute(self, inputs: Dict[str, Any]) -> ToolOutputSchema:
        if not self.validate_inputs(inputs):
            # More specific error based on which validation failed would be better
            return {
                "success": False,
                "result": None,
                "error": "Invalid inputs provided. Missing required parameters or incorrect types."
            }
        
        file_path = inputs.get("path")
        content = inputs.get("content")
        append_mode = inputs.get("append", False)

        if not isinstance(file_path, str) or not isinstance(content, str) or not isinstance(append_mode, bool):
            return {
                "success": False,
                "result": None,
                "error": "Invalid input types for path, content, or append mode."
            }

        try:
            # Security consideration: Validate path to prevent writing to unintended locations.
            if not os.path.isabs(file_path):
                return {
                    "success": False,
                    "result": None,
                    "error": f"File path must be absolute. Received: {file_path}"
                }
            
            # Ensure the directory exists, create if not (optional, based on desired behavior)
            dir_name = os.path.dirname(file_path)
            if not os.path.exists(dir_name):
                try:
                    os.makedirs(dir_name, exist_ok=True)
                except Exception as e:
                    return {
                        "success": False,
                        "result": None,
                        "error": f"Failed to create directory {dir_name}: {str(e)}"
                    }
            
            mode = "a" if append_mode else "w"
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(content)
            
            return {
                "success": True,
                "result": f"Successfully wrote to file: {file_path}",
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": f"Failed to write to file {file_path}: {str(e)}"
            }


