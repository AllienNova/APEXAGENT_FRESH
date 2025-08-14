# src/plugins/code_analysis_plugin.py
import asyncio
import logging
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional

from .base_enhanced_plugin import BaseEnhancedPlugin
from src.core.plugin_exceptions import PluginExecutionError, InvalidInputError, ExternalServiceError

# Attempt to import radon for complexity analysis, but don't make it a hard crash if not found initially
# The dependency check in PluginManager should handle this.
try:
    from radon.complexity import cc_visit
    from radon.metrics import h_visit
    from radon.raw import analyze as raw_analyze
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False
    # logger.warning("Radon library not found. Code complexity analysis will be unavailable.")

logger = logging.getLogger(__name__)

class CodeAnalysisPlugin(BaseEnhancedPlugin):
    def __init__(self, api_key_manager=None):
        super().__init__(api_key_manager=api_key_manager)
        self.plugin_name = "CodeAnalysisPlugin"
        if not RADON_AVAILABLE:
            logger.warning(f"{self.plugin_name}: Radon library not found. Code complexity analysis will be unavailable.")
        logger.info(f"{self.plugin_name} initialized.")

    async def _run_command(self, command: list[str]) -> tuple[str, str, int]:
        """Helper to run shell commands asynchronously."""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode(), process.returncode

    async def lint_code(self, code_content: str, linter: str, language: Optional[str] = "python") -> Dict[str, Any]:
        logger.info(f"Linting code with {linter} for language {language}")
        if not code_content.strip():
            raise InvalidInputError(errors="Code content cannot be empty for linting.")

        report = ""
        issues_found = 0
        status = "error"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=f".{language}") as tmp_file:
            tmp_file.write(code_content)
            tmp_file_path = tmp_file.name

        try:
            if linter.lower() == "flake8" and language.lower() == "python":
                cmd = ["flake8", tmp_file_path]
                stdout, stderr, returncode = await self._run_command(cmd)
                report = stdout + stderr
                issues_found = len(stdout.strip().split('\n')) if stdout.strip() else 0
                status = "success" if returncode == 0 or (returncode !=0 and stdout) else "error" # Flake8 exits >0 if issues
            elif linter.lower() == "pylint" and language.lower() == "python":
                # Pylint has various exit codes, we'll consider it a success if it runs
                cmd = ["pylint", "--output-format=text", tmp_file_path]
                stdout, stderr, returncode = await self._run_command(cmd)
                report = stdout + stderr
                # A bit simplistic for pylint issue counting, but good for a start
                if "Your code has been rated at" in stdout:
                    status = "success"
                    # Try to count lines that look like issues
                    issues_found = sum(1 for line in stdout.split('\n') if line and (line.startswith("E:") or line.startswith("W:") or line.startswith("C:") or line.startswith("R:")))
                else:
                    status = "error"
            else:
                raise InvalidInputError(errors=f"Linter '{linter}' for language '{language}' is not supported or language mismatch.")
            
            return {"status": status, "issues_found": issues_found, "report": report.strip(), "linter_used": linter}
        except FileNotFoundError as e:
            logger.error(f"Linter command not found for {linter}: {e}")
            raise ExternalServiceError(service_name=linter, error_details=f"{linter} executable not found. Please ensure it's installed and in PATH.")
        except Exception as e:
            logger.error(f"Error during linting with {linter}: {e}")
            raise PluginExecutionError(action_name="lint_code", plugin_name=self.plugin_name, original_exception=e)
        finally:
            os.remove(tmp_file_path)

    async def format_code(self, code_content: str, formatter: str, language: Optional[str] = "python") -> Dict[str, Any]:
        logger.info(f"Formatting code with {formatter} for language {language}")
        if not code_content.strip():
            raise InvalidInputError(errors="Code content cannot be empty for formatting.")

        formatted_code = ""
        errors = None

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=f".{language}") as tmp_file:
            tmp_file.write(code_content)
            tmp_file_path = tmp_file.name
        
        try:
            if formatter.lower() == "black" and language.lower() == "python":
                cmd = ["black", "--quiet", tmp_file_path]
                stdout, stderr, returncode = await self._run_command(cmd)
                if returncode == 0:
                    with open(tmp_file_path, "r") as f:
                        formatted_code = f.read()
                    status = "success"
                else:
                    status = "error"
                    errors = stderr or stdout # Black often puts errors on stdout for non-critical issues
            elif formatter.lower() == "autopep8" and language.lower() == "python":
                cmd = ["autopep8", "--in-place", tmp_file_path]
                stdout, stderr, returncode = await self._run_command(cmd)
                if returncode == 0:
                    with open(tmp_file_path, "r") as f:
                        formatted_code = f.read()
                    status = "success"
                else:
                    status = "error"
                    errors = stderr or stdout
            # Add prettier for JS/TS/etc. later if needed
            else:
                raise InvalidInputError(errors=f"Formatter '{formatter}' for language '{language}' is not supported or language mismatch.")
            
            result = {"status": status, "formatter_used": formatter}
            if formatted_code:
                result["formatted_code"] = formatted_code
            if errors:
                result["errors"] = errors.strip()
            return result
        except FileNotFoundError as e:
            logger.error(f"Formatter command not found for {formatter}: {e}")
            raise ExternalServiceError(service_name=formatter, error_details=f"{formatter} executable not found. Please ensure it's installed and in PATH.")
        except Exception as e:
            logger.error(f"Error during formatting with {formatter}: {e}")
            raise PluginExecutionError(action_name="format_code", plugin_name=self.plugin_name, original_exception=e)
        finally:
            os.remove(tmp_file_path)

    async def analyze_complexity(self, code_content: str) -> Dict[str, Any]:
        logger.info("Analyzing code complexity")
        if not RADON_AVAILABLE:
            raise PluginExecutionError(action_name="analyze_complexity", plugin_name=self.plugin_name, message="Radon library is not installed. Complexity analysis is unavailable.")
        if not code_content.strip():
            raise InvalidInputError(errors="Code content cannot be empty for complexity analysis.")

        try:
            # Radon functions are synchronous, run in executor
            loop = asyncio.get_event_loop()
            cc_results = await loop.run_in_executor(None, cc_visit, code_content)
            # mi_results = mi_visit(code_content, multi=True) # Maintainability Index - can add later
            raw_metrics = await loop.run_in_executor(None, raw_analyze, code_content)
            
            complexity_report = {
                "cyclomatic_complexity": [],
                "raw_metrics": {
                    "loc": raw_metrics.loc, # Lines of Code
                    "lloc": raw_metrics.lloc, # Logical Lines of Code
                    "sloc": raw_metrics.sloc, # Source Lines of Code (excluding comments and blank lines)
                    "comments": raw_metrics.comments,
                    "multi": raw_metrics.multi, # Multi-line strings (docstrings)
                    "blank": raw_metrics.blank,
                    "single_comments": raw_metrics.single_comments
                }
            }
            for item in cc_results:
                complexity_report["cyclomatic_complexity"].append({
                    "type": item.type,
                    "name": item.name,
                    "lineno": item.lineno,
                    "col_offset": item.col_offset,
                    "complexity": item.complexity,
                    "rank": item.rank()
                })
            
            return {"status": "success", "complexity_report": complexity_report, "message": "Complexity analysis complete."}
        except Exception as e:
            logger.error(f"Error during complexity analysis: {e}")
            raise PluginExecutionError(action_name="analyze_complexity", plugin_name=self.plugin_name, original_exception=e)

# Ensure:
# 1. Inherits BaseEnhancedPlugin.
# 2. _metadata.json exists.
# 3. entry_point matches.
# 4. Dependencies (flake8, pylint, black, autopep8, radon) are in metadata and environment.

