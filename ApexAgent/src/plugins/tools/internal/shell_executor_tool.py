# src/plugins/tools/internal/shell_executor_tool.py
import asyncio
import subprocess
from typing import Dict, Any
from src.plugins.tools.base_tool_plugin import BaseToolPlugin, ToolInfo, ToolOutputSchema, ToolParameterInfo

class ShellExecutorTool(BaseToolPlugin):
    def get_tool_info(self) -> ToolInfo:
        return {
            "name": "shell_command_executor",
            "display_name": "Execute Shell Command",
            "description": "Executes a shell command in the agent's environment and returns its output.",
            "category": "Shell",
            "input_schema": {
                "command": {
                    "name": "command",
                    "type": "string",
                    "description": "The shell command to execute.",
                    "required": True,
                    "default": None
                },
                "timeout": {
                    "name": "timeout",
                    "type": "integer",
                    "description": "Maximum time in seconds to wait for the command to complete.",
                    "required": False,
                    "default": 60 # Default timeout of 60 seconds
                }
            },
            "output_description": "Returns a dictionary containing stdout, stderr, and return code, or an error message."
        }

    async def execute(self, inputs: Dict[str, Any]) -> ToolOutputSchema:
        if not self.validate_inputs(inputs):
            return {
                "success": False,
                "result": None,
                "error": "Invalid inputs provided. Missing required parameter: command."
            }
        
        command = inputs.get("command")
        timeout = inputs.get("timeout", 60)

        if not isinstance(command, str):
            return {
                "success": False,
                "result": None,
                "error": "Invalid input type for command. Expected a string."
            }
        if not isinstance(timeout, int) or timeout <= 0:
            return {
                "success": False,
                "result": None,
                "error": "Invalid input type or value for timeout. Expected a positive integer."
            }

        try:
            # Security Warning: Executing arbitrary shell commands is highly dangerous.
            # In a real-world agent, this tool would need extreme caution, sandboxing,
            # and/or strict validation of allowed commands.
            # For this example, we proceed with the understanding that the agent environment is controlled.
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            return_code = process.returncode

            return {
                "success": True,
                "result": {
                    "stdout": stdout.decode(errors="ignore"),
                    "stderr": stderr.decode(errors="ignore"),
                    "return_code": return_code
                },
                "error": None
            }
        except asyncio.TimeoutError:
            # Ensure the process is killed if it times out
            if process and process.returncode is None:
                try:
                    process.kill()
                    await process.wait() # Ensure kill is processed
                except ProcessLookupError:
                    pass # Process might have already exited
                except Exception as e_kill:
                    print(f"Error trying to kill timed-out process for command 	{command}: {e_kill}")
            return {
                "success": False,
                "result": None,
                "error": f"Command 	{command} timed out after {timeout} seconds."
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": f"Failed to execute command 	{command}: {str(e)}"
            }


