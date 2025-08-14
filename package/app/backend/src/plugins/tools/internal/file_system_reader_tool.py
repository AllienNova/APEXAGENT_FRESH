# src/plugins/tools/internal/file_system_tool.py
import os
from typing import Dict, Any
from src.plugins.tools.base_tool_plugin import BaseToolPlugin, ToolInfo, ToolOutputSchema, ToolParameterInfo

class FileSystemReaderTool(BaseToolPlugin):
    def get_tool_info(self) -> ToolInfo:
        return {
            "name": "file_system_read_file",
            "display_name": "Read File",
            "description": "Reads the content of a specified text file from the local file system.",
            "category": "File System",
            "input_schema": {
                "path": {
                    "name": "path",
                    "type": "string",
                    "description": "The absolute path to the file to be read.",
                    "required": True,
                    "default": None
                }
            },
            "output_description": "Returns the content of the file as a string, or an error message."
        }

    async def execute(self, inputs: Dict[str, Any]) -> ToolOutputSchema:
        if not self.validate_inputs(inputs):
            return {
                "success": False,
                "result": None,
                "error": "Invalid inputs provided. Missing required parameter: path."
            }
        
        file_path = inputs.get("path")
        if not isinstance(file_path, str):
             return {
                "success": False,
                "result": None,
                "error": "Invalid input type for path. Expected a string."
            }

        try:
            # Security consideration: In a real agent, validate the path to prevent access to sensitive files.
            # For this example, we assume the agent has legitimate reasons to access the given path.
            if not os.path.isabs(file_path):
                return {
                    "success": False,
                    "result": None,
                    "error": f"File path must be absolute. Received: {file_path}"
                }
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "result": None,
                    "error": f"File not found at path: {file_path}"
                }
            if not os.path.isfile(file_path):
                return {
                    "success": False,
                    "result": None,
                    "error": f"Path is not a file: {file_path}"
                }
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "success": True,
                "result": content,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": f"Failed to read file 	{file_path}: {str(e)}"
            }

# To make this discoverable by the PluginManager, ensure it is in a directory scanned by it.
# For example, if PluginManager scans subdirectories of `src/plugins/tools/internal`,
# this file could be `src/plugins/tools/internal/fs_tools/plugin.py` and expose FileSystemReaderTool.
# Or, if single files are scanned, it could be `src/plugins/tools/internal/file_system_reader_tool.py`.

