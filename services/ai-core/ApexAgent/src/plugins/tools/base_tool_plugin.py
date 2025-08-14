# src/plugins/tools/base_tool_plugin.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, TypedDict

class ToolInputSchema(TypedDict, total=False):
    # Base class for tool input schemas, can be inherited by specific tools
    # to define their expected parameters using Pydantic or similar if desired.
    pass

class ToolOutputSchema(TypedDict, total=False):
    # Base class for tool output schemas
    success: bool
    result: Any
    error: str

class ToolParameterInfo(TypedDict):
    name: str
    type: str # e.g., "string", "integer", "boolean", "file_path"
    description: str
    required: bool
    default: Any # Optional default value

class ToolInfo(TypedDict):
    name: str # Unique machine-readable name, e.g., "file_system_read_file"
    display_name: str # User-friendly name, e.g., "Read File"
    description: str # What the tool does
    category: str # e.g., "File System", "Shell", "Web Interaction", "Data Analysis"
    input_schema: Dict[str, ToolParameterInfo] # Describes expected parameters
    output_description: str # Describes what the tool returns

class BaseToolPlugin(ABC):
    @abstractmethod
    def get_tool_info(self) -> ToolInfo:
        """Returns metadata about the tool."""
        pass

    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> ToolOutputSchema:
        """Executes the tool with the given inputs.
           Inputs are validated against the input_schema defined in get_tool_info.
           Returns a dictionary conforming to ToolOutputSchema.
        """
        pass

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validates inputs against the schema. Can be overridden for complex validation."""
        tool_info = self.get_tool_info()
        input_schema = tool_info.get("input_schema", {})
        for param_name, param_info in input_schema.items():
            if param_info.get("required") and param_name not in inputs:
                # A more robust implementation would raise a specific error or return details
                print(f"Error: Missing required parameter \t{param_name} for tool {tool_info['name']}")
                return False
            # Basic type checking could be added here if not using Pydantic
        return True

