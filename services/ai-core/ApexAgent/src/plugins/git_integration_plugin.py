# src/plugins/git_integration_plugin.py
import asyncio
import logging
import os
from typing import Dict, List, Any, Optional

import git # GitPython library

from .base_enhanced_plugin import BaseEnhancedPlugin
from src.core.plugin_exceptions import PluginExecutionError, InvalidInputError, ExternalServiceError

logger = logging.getLogger(__name__)

class GitIntegrationPlugin(BaseEnhancedPlugin):
    def __init__(self, api_key_manager=None):
        super().__init__(api_key_manager=api_key_manager)
        self.plugin_name = "GitIntegrationPlugin"
        logger.info(f"{self.plugin_name} initialized.")

    async def _get_repo(self, local_path: str) -> git.Repo:
        """Helper to get a GitPython Repo object or raise error."""
        if not os.path.isdir(local_path):
            raise InvalidInputError(errors=f"Local path 	"{local_path}	" is not a valid directory.")
        try:
            repo = git.Repo(local_path)
            return repo
        except git.InvalidGitRepositoryError:
            raise InvalidInputError(errors=f"Path 	"{local_path}	" is not a valid Git repository.")
        except Exception as e:
            logger.error(f"Error accessing repository at {local_path}: {e}")
            raise PluginExecutionError(action_name="_get_repo", plugin_name=self.plugin_name, original_exception=e)

    async def clone_repository(self, repository_url: str, local_path: str) -> Dict[str, Any]:
        logger.info(f"Cloning repository from {repository_url} to {local_path}")
        if os.path.exists(local_path) and os.listdir(local_path):
            raise InvalidInputError(errors=f"Local path 	"{local_path}	" already exists and is not empty.")
        try:
            # GitPython clone is synchronous, run in executor for async compatibility
            loop = asyncio.get_event_loop()
            repo = await loop.run_in_executor(None, git.Repo.clone_from, repository_url, local_path)
            logger.info(f"Repository cloned successfully to {repo.working_dir}")
            return {"status": "success", "message": "Repository cloned successfully.", "repo_path": repo.working_dir}
        except git.GitCommandError as e:
            logger.error(f"Git command error during clone: {e}")
            raise ExternalServiceError(service_name="git_clone", error_details=str(e), status_code_from_service=e.status)
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            raise PluginExecutionError(action_name="clone_repository", plugin_name=self.plugin_name, original_exception=e)

    async def get_status(self, local_path: str) -> Dict[str, Any]:
        repo = await self._get_repo(local_path)
        try:
            status_text = await asyncio.to_thread(repo.git.status)
            is_dirty = repo.is_dirty()
            current_branch = repo.active_branch.name
            untracked_files = repo.untracked_files
            return {
                "status_text": status_text,
                "is_dirty": is_dirty,
                "current_branch": current_branch,
                "untracked_files": untracked_files
            }
        except Exception as e:
            logger.error(f"Error getting status for {local_path}: {e}")
            raise PluginExecutionError(action_name="get_status", plugin_name=self.plugin_name, original_exception=e)

    async def add_files(self, local_path: str, files: List[str]) -> Dict[str, Any]:
        repo = await self._get_repo(local_path)
        if not files:
            raise InvalidInputError(errors="File list cannot be empty for add_files action.")
        try:
            await asyncio.to_thread(repo.git.add, *files)
            return {"status": "success", "message": f"Files {files} added to staging area."}
        except git.GitCommandError as e:
            logger.error(f"Git command error during add: {e}")
            raise ExternalServiceError(service_name="git_add", error_details=str(e), status_code_from_service=e.status)
        except Exception as e:
            logger.error(f"Error adding files in {local_path}: {e}")
            raise PluginExecutionError(action_name="add_files", plugin_name=self.plugin_name, original_exception=e)

    async def commit_changes(self, local_path: str, message: str) -> Dict[str, Any]:
        repo = await self._get_repo(local_path)
        if not message.strip():
            raise InvalidInputError(errors="Commit message cannot be empty.")
        try:
            commit = await asyncio.to_thread(repo.index.commit, message)
            return {"status": "success", "message": "Changes committed.", "commit_sha": commit.hexsha}
        except git.GitCommandError as e:
            logger.error(f"Git command error during commit: {e}")
            raise ExternalServiceError(service_name="git_commit", error_details=str(e), status_code_from_service=e.status)
        except Exception as e:
            logger.error(f"Error committing changes in {local_path}: {e}")
            raise PluginExecutionError(action_name="commit_changes", plugin_name=self.plugin_name, original_exception=e)

    async def push_changes(self, local_path: str, remote_name: Optional[str] = "origin", branch_name: Optional[str] = None) -> Dict[str, Any]:
        repo = await self._get_repo(local_path)
        actual_branch = branch_name if branch_name else repo.active_branch.name
        try:
            remote = repo.remote(name=remote_name)
            push_info_list = await asyncio.to_thread(remote.push, actual_branch)
            # Check push_info for errors
            for info in push_info_list:
                if info.flags & (git.PushInfo.ERROR | git.PushInfo.REJECTED | git.PushInfo.REMOTE_REJECTED | git.PushInfo.REMOTE_FAILURE):
                    logger.error(f"Push failed for branch {actual_branch} to remote {remote_name}: {info.summary}")
                    raise ExternalServiceError(service_name="git_push", error_details=info.summary, message=f"Push failed: {info.summary}")
            return {"status": "success", "message": f"Changes pushed to {remote_name}/{actual_branch}."}
        except git.GitCommandError as e:
            logger.error(f"Git command error during push: {e}")
            raise ExternalServiceError(service_name="git_push", error_details=str(e), status_code_from_service=e.status)
        except Exception as e:
            logger.error(f"Error pushing changes from {local_path}: {e}")
            raise PluginExecutionError(action_name="push_changes", plugin_name=self.plugin_name, original_exception=e)

    async def pull_changes(self, local_path: str, remote_name: Optional[str] = "origin", branch_name: Optional[str] = None) -> Dict[str, Any]:
        repo = await self._get_repo(local_path)
        actual_branch = branch_name if branch_name else repo.active_branch.name
        try:
            remote = repo.remote(name=remote_name)
            await asyncio.to_thread(remote.pull, actual_branch)
            return {"status": "success", "message": f"Changes pulled from {remote_name}/{actual_branch}."}
        except git.GitCommandError as e:
            logger.error(f"Git command error during pull: {e}")
            raise ExternalServiceError(service_name="git_pull", error_details=str(e), status_code_from_service=e.status)
        except Exception as e:
            logger.error(f"Error pulling changes for {local_path}: {e}")
            raise PluginExecutionError(action_name="pull_changes", plugin_name=self.plugin_name, original_exception=e)

    async def create_branch(self, local_path: str, branch_name: str, checkout: Optional[bool] = False) -> Dict[str, Any]:
        repo = await self._get_repo(local_path)
        if not branch_name.strip():
            raise InvalidInputError(errors="Branch name cannot be empty.")
        try:
            new_branch = await asyncio.to_thread(repo.create_head, branch_name)
            message = f"Branch 	"{branch_name}	" created."
            if checkout:
                await asyncio.to_thread(new_branch.checkout)
                message += " And checked out."
            return {"status": "success", "message": message}
        except git.GitCommandError as e:
            logger.error(f"Git command error during create_branch: {e}")
            # Check if branch already exists
            if "already exists" in str(e).lower():
                 raise InvalidInputError(errors=f"Branch 	"{branch_name}	" already exists.")
            raise ExternalServiceError(service_name="git_create_branch", error_details=str(e), status_code_from_service=e.status)
        except Exception as e:
            logger.error(f"Error creating branch 	"{branch_name}	" in {local_path}: {e}")
            raise PluginExecutionError(action_name="create_branch", plugin_name=self.plugin_name, original_exception=e)

    async def checkout_branch(self, local_path: str, branch_name: str) -> Dict[str, Any]:
        repo = await self._get_repo(local_path)
        if not branch_name.strip():
            raise InvalidInputError(errors="Branch name cannot be empty.")
        try:
            await asyncio.to_thread(repo.git.checkout, branch_name)
            return {"status": "success", "message": f"Checked out branch 	"{branch_name}	"."}
        except git.GitCommandError as e:
            logger.error(f"Git command error during checkout: {e}")
            # Check if branch does not exist
            if "did not match any file(s) known to git" in str(e).lower() or "is not a commit and a branch" in str(e).lower() :
                 raise InvalidInputError(errors=f"Branch 	"{branch_name}	" not found.")
            raise ExternalServiceError(service_name="git_checkout", error_details=str(e), status_code_from_service=e.status)
        except Exception as e:
            logger.error(f"Error checking out branch 	"{branch_name}	" in {local_path}: {e}")
            raise PluginExecutionError(action_name="checkout_branch", plugin_name=self.plugin_name, original_exception=e)

    async def list_branches(self, local_path: str) -> Dict[str, Any]:
        repo = await self._get_repo(local_path)
        try:
            branches = [head.name for head in repo.heads]
            return {"status": "success", "branches": branches}
        except Exception as e:
            logger.error(f"Error listing branches for {local_path}: {e}")
            raise PluginExecutionError(action_name="list_branches", plugin_name=self.plugin_name, original_exception=e)

# To make this plugin discoverable by the PluginManager, ensure:
# 1. It inherits from BaseEnhancedPlugin (or a compatible base).
# 2. A corresponding _metadata.json file exists in the same directory.
# 3. The entry_point in metadata matches "git_integration_plugin.GitIntegrationPlugin".
# 4. The GitPython library is listed in dependencies in metadata and installed in the environment.

