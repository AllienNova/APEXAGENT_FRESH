"""
Enhanced Tools and Automation API Endpoints
Provides comprehensive access to restored internal tools and automation capabilities
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime
import asyncio

# Import restored tool components
from services.ai_core.ApexAgent.src.plugins.tools.internal.desktop_automation_tool import DesktopAutomationTool
from services.ai_core.ApexAgent.src.plugins.tools.internal.file_system_reader_tool import FileSystemReaderTool
from services.ai_core.ApexAgent.src.plugins.tools.internal.file_system_writer_tool import FileSystemWriterTool
from services.ai_core.ApexAgent.src.plugins.tools.internal.shell_executor_tool import ShellExecutorTool
from services.ai_core.ApexAgent.src.plugins.tools.internal.web_automation_tool import WebAutomationTool
from services.ai_core.ApexAgent.src.plugins.tools.internal.web_browser_tool import WebBrowserTool

router = APIRouter(prefix="/api/v1/tools/enhanced", tags=["Enhanced Tools & Automation"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize tools
tools = {
    "desktop_automation": DesktopAutomationTool(),
    "file_system_reader": FileSystemReaderTool(),
    "file_system_writer": FileSystemWriterTool(),
    "shell_executor": ShellExecutorTool(),
    "web_automation": WebAutomationTool(),
    "web_browser": WebBrowserTool()
}

# Pydantic models
class DesktopAutomationRequest(BaseModel):
    action: str = Field(..., description="Desktop action to perform")
    target: Optional[str] = Field(None, description="Target application or window")
    coordinates: Optional[Dict[str, int]] = Field(None, description="X, Y coordinates")
    text_input: Optional[str] = Field(None, description="Text to input")
    screenshot: bool = Field(False, description="Take screenshot after action")
    wait_time: Optional[float] = Field(None, description="Wait time in seconds")

class FileSystemRequest(BaseModel):
    operation: str = Field(..., description="File operation (read, write, list, delete)")
    path: str = Field(..., description="File or directory path")
    content: Optional[str] = Field(None, description="Content to write")
    encoding: Optional[str] = Field("utf-8", description="File encoding")
    recursive: bool = Field(False, description="Recursive operation for directories")
    filters: Optional[List[str]] = Field(None, description="File filters")

class ShellExecutionRequest(BaseModel):
    command: str = Field(..., description="Shell command to execute")
    working_directory: Optional[str] = Field(None, description="Working directory")
    environment_vars: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    timeout: Optional[int] = Field(30, description="Timeout in seconds")
    capture_output: bool = Field(True, description="Capture command output")
    shell: bool = Field(True, description="Execute through shell")

class WebAutomationRequest(BaseModel):
    action: str = Field(..., description="Web automation action")
    url: Optional[str] = Field(None, description="Target URL")
    selector: Optional[str] = Field(None, description="CSS selector")
    text_input: Optional[str] = Field(None, description="Text to input")
    wait_for: Optional[str] = Field(None, description="Element to wait for")
    screenshot: bool = Field(False, description="Take screenshot")
    headless: bool = Field(True, description="Run in headless mode")

class WorkflowRequest(BaseModel):
    name: str = Field(..., description="Workflow name")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps")
    parallel_execution: bool = Field(False, description="Execute steps in parallel")
    error_handling: str = Field("stop", description="Error handling strategy")
    timeout: Optional[int] = Field(None, description="Overall workflow timeout")

# Desktop automation endpoints
@router.post("/desktop/automate")
async def desktop_automation(
    request: DesktopAutomationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Perform desktop automation actions
    """
    try:
        desktop_tool = tools["desktop_automation"]
        
        # Execute desktop automation
        result = await desktop_tool.execute_action(
            action=request.action,
            target=request.target,
            coordinates=request.coordinates,
            text_input=request.text_input,
            wait_time=request.wait_time
        )
        
        response_data = {
            "status": "success",
            "action": request.action,
            "result": {
                "success": result.success,
                "message": result.message,
                "execution_time": result.execution_time,
                "target_found": result.target_found
            }
        }
        
        # Add screenshot if requested
        if request.screenshot and result.success:
            screenshot = await desktop_tool.take_screenshot()
            response_data["screenshot"] = {
                "data": screenshot.base64_data,
                "timestamp": screenshot.timestamp,
                "dimensions": screenshot.dimensions
            }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Desktop automation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Desktop automation failed: {str(e)}"
        )

@router.get("/desktop/screenshot")
async def take_screenshot(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Take a screenshot of the desktop
    """
    try:
        desktop_tool = tools["desktop_automation"]
        screenshot = await desktop_tool.take_screenshot()
        
        return {
            "status": "success",
            "screenshot": {
                "data": screenshot.base64_data,
                "timestamp": screenshot.timestamp,
                "dimensions": screenshot.dimensions,
                "file_size": screenshot.file_size
            }
        }
        
    except Exception as e:
        logger.error(f"Screenshot error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Screenshot failed: {str(e)}"
        )

# File system endpoints
@router.post("/filesystem/operate")
async def file_system_operation(
    request: FileSystemRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Perform file system operations
    """
    try:
        if request.operation == "read":
            tool = tools["file_system_reader"]
            result = await tool.read_file(
                path=request.path,
                encoding=request.encoding
            )
            
            return {
                "status": "success",
                "operation": "read",
                "result": {
                    "content": result.content,
                    "file_size": result.file_size,
                    "last_modified": result.last_modified,
                    "encoding": result.encoding
                }
            }
            
        elif request.operation == "write":
            tool = tools["file_system_writer"]
            result = await tool.write_file(
                path=request.path,
                content=request.content,
                encoding=request.encoding
            )
            
            return {
                "status": "success",
                "operation": "write",
                "result": {
                    "bytes_written": result.bytes_written,
                    "file_created": result.file_created,
                    "backup_created": result.backup_created
                }
            }
            
        elif request.operation == "list":
            tool = tools["file_system_reader"]
            result = await tool.list_directory(
                path=request.path,
                recursive=request.recursive,
                filters=request.filters
            )
            
            return {
                "status": "success",
                "operation": "list",
                "result": {
                    "items": result.items,
                    "total_files": result.total_files,
                    "total_directories": result.total_directories,
                    "total_size": result.total_size
                }
            }
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported operation: {request.operation}"
            )
        
    except Exception as e:
        logger.error(f"File system operation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File system operation failed: {str(e)}"
        )

@router.post("/filesystem/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = Field(..., description="Target file path"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Upload a file to the file system
    """
    try:
        tool = tools["file_system_writer"]
        
        # Read uploaded file content
        content = await file.read()
        
        # Write file to specified path
        result = await tool.write_file(
            path=path,
            content=content,
            encoding="binary"
        )
        
        return {
            "status": "success",
            "operation": "upload",
            "file_info": {
                "original_name": file.filename,
                "target_path": path,
                "size": len(content),
                "content_type": file.content_type
            },
            "result": {
                "bytes_written": result.bytes_written,
                "file_created": result.file_created
            }
        }
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

# Shell execution endpoints
@router.post("/shell/execute")
async def execute_shell_command(
    request: ShellExecutionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute shell commands with enhanced features
    """
    try:
        shell_tool = tools["shell_executor"]
        
        # Execute command
        result = await shell_tool.execute_command(
            command=request.command,
            working_directory=request.working_directory,
            environment_vars=request.environment_vars,
            timeout=request.timeout,
            capture_output=request.capture_output,
            shell=request.shell
        )
        
        return {
            "status": "success",
            "command": request.command,
            "result": {
                "return_code": result.return_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": result.execution_time,
                "timed_out": result.timed_out,
                "working_directory": result.working_directory
            }
        }
        
    except Exception as e:
        logger.error(f"Shell execution error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Shell execution failed: {str(e)}"
        )

@router.get("/shell/environment")
async def get_shell_environment(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get current shell environment information
    """
    try:
        shell_tool = tools["shell_executor"]
        env_info = await shell_tool.get_environment_info()
        
        return {
            "status": "success",
            "environment": {
                "shell": env_info.shell,
                "platform": env_info.platform,
                "working_directory": env_info.working_directory,
                "user": env_info.user,
                "environment_variables": env_info.environment_variables,
                "path": env_info.path
            }
        }
        
    except Exception as e:
        logger.error(f"Environment info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get environment info: {str(e)}"
        )

# Web automation endpoints
@router.post("/web/automate")
async def web_automation(
    request: WebAutomationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Perform web automation actions
    """
    try:
        web_tool = tools["web_automation"]
        
        # Execute web automation
        result = await web_tool.execute_action(
            action=request.action,
            url=request.url,
            selector=request.selector,
            text_input=request.text_input,
            wait_for=request.wait_for,
            headless=request.headless
        )
        
        response_data = {
            "status": "success",
            "action": request.action,
            "result": {
                "success": result.success,
                "message": result.message,
                "execution_time": result.execution_time,
                "page_title": result.page_title,
                "current_url": result.current_url
            }
        }
        
        # Add screenshot if requested
        if request.screenshot and result.success:
            screenshot = await web_tool.take_screenshot()
            response_data["screenshot"] = {
                "data": screenshot.base64_data,
                "timestamp": screenshot.timestamp
            }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Web automation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web automation failed: {str(e)}"
        )

@router.post("/web/browse")
async def web_browse(
    url: str,
    extract_text: bool = True,
    take_screenshot: bool = False,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Browse a web page and extract information
    """
    try:
        browser_tool = tools["web_browser"]
        
        # Browse the page
        result = await browser_tool.browse_page(
            url=url,
            extract_text=extract_text,
            take_screenshot=take_screenshot
        )
        
        response_data = {
            "status": "success",
            "url": url,
            "page_info": {
                "title": result.title,
                "description": result.description,
                "keywords": result.keywords,
                "load_time": result.load_time
            }
        }
        
        if extract_text:
            response_data["content"] = {
                "text": result.text_content,
                "links": result.links,
                "images": result.images,
                "forms": result.forms
            }
        
        if take_screenshot:
            response_data["screenshot"] = {
                "data": result.screenshot.base64_data,
                "timestamp": result.screenshot.timestamp
            }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Web browsing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web browsing failed: {str(e)}"
        )

# Workflow automation endpoints
@router.post("/workflow/execute")
async def execute_workflow(
    request: WorkflowRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute a complex workflow with multiple tools
    """
    try:
        workflow_results = []
        start_time = datetime.utcnow()
        
        if request.parallel_execution:
            # Execute steps in parallel
            tasks = []
            for step in request.steps:
                task = asyncio.create_task(execute_workflow_step(step))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    workflow_results.append({
                        "step": i + 1,
                        "status": "error",
                        "error": str(result)
                    })
                else:
                    workflow_results.append({
                        "step": i + 1,
                        "status": "success",
                        "result": result
                    })
        else:
            # Execute steps sequentially
            for i, step in enumerate(request.steps):
                try:
                    result = await execute_workflow_step(step)
                    workflow_results.append({
                        "step": i + 1,
                        "status": "success",
                        "result": result
                    })
                except Exception as step_error:
                    workflow_results.append({
                        "step": i + 1,
                        "status": "error",
                        "error": str(step_error)
                    })
                    
                    if request.error_handling == "stop":
                        break
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        # Calculate success rate
        successful_steps = len([r for r in workflow_results if r["status"] == "success"])
        success_rate = successful_steps / len(request.steps) if request.steps else 0
        
        return {
            "status": "completed",
            "workflow_name": request.name,
            "execution_summary": {
                "total_steps": len(request.steps),
                "successful_steps": successful_steps,
                "failed_steps": len(request.steps) - successful_steps,
                "success_rate": success_rate,
                "execution_time": execution_time
            },
            "step_results": workflow_results,
            "parallel_execution": request.parallel_execution
        }
        
    except Exception as e:
        logger.error(f"Workflow execution error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )

async def execute_workflow_step(step: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single workflow step
    """
    tool_name = step.get("tool")
    action = step.get("action")
    parameters = step.get("parameters", {})
    
    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    tool = tools[tool_name]
    
    # Execute the tool action
    if hasattr(tool, action):
        method = getattr(tool, action)
        return await method(**parameters)
    else:
        raise ValueError(f"Tool {tool_name} doesn't support action: {action}")

@router.get("/tools/available")
async def get_available_tools(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get list of available tools and their capabilities
    """
    try:
        tool_info = []
        
        for tool_name, tool in tools.items():
            capabilities = await tool.get_capabilities()
            status = await tool.get_status()
            
            tool_info.append({
                "name": tool_name,
                "display_name": tool.display_name,
                "description": tool.description,
                "status": status.status,
                "capabilities": capabilities.supported_actions,
                "requirements": capabilities.requirements,
                "limitations": capabilities.limitations,
                "last_used": status.last_used
            })
        
        return {
            "status": "success",
            "tools": tool_info,
            "total_tools": len(tool_info),
            "active_tools": len([t for t in tool_info if t["status"] == "active"])
        }
        
    except Exception as e:
        logger.error(f"Get tools error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tool information: {str(e)}"
        )

@router.get("/system/health")
async def tools_system_health(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get health status of enhanced tools system
    """
    try:
        health_data = {}
        overall_health = "healthy"
        
        for tool_name, tool in tools.items():
            try:
                health = await tool.get_health_status()
                health_data[tool_name] = {
                    "status": health.status,
                    "last_check": health.last_check,
                    "error_count": health.error_count,
                    "performance": health.performance_metrics
                }
                
                if health.status != "healthy":
                    overall_health = "degraded"
                    
            except Exception as tool_error:
                health_data[tool_name] = {
                    "status": "error",
                    "error": str(tool_error)
                }
                overall_health = "degraded"
        
        return {
            "status": "success",
            "overall_health": overall_health,
            "tools": health_data,
            "system_info": {
                "total_tools": len(tools),
                "healthy_tools": len([h for h in health_data.values() if h.get("status") == "healthy"]),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Tools system health check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )

