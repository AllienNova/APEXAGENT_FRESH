#!/usr/bin/env python3
"""
Aideon AI Lite - Automated Sandbox-to-GitHub Sync System
Ensures all sandbox files are automatically tracked, organized, and committed to GitHub
"""

import os
import sys
import shutil
import subprocess
import time
import logging
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
import threading
import queue
import fnmatch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/complete_apexagent_sync/logs/sync_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SandboxSyncManager:
    """Comprehensive sandbox-to-GitHub synchronization system"""
    
    def __init__(self):
        # Core paths
        self.sandbox_root = Path("/home/ubuntu")
        self.git_repo = Path("/home/ubuntu/complete_apexagent_sync")
        self.logs_dir = self.git_repo / "logs"
        self.sync_config_file = self.git_repo / "sync_config.json"
        
        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        
        # File tracking
        self.tracked_files = set()
        self.file_hashes = {}
        self.sync_queue = queue.Queue()
        self.is_running = False
        
        # Configuration
        self.config = self.load_config()
        
        # Git configuration
        self.git_remote = "origin"
        self.git_branch = "together-ai-huggingface-integration"
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required but not set")
        
        logger.info("SandboxSyncManager initialized")
    
    def load_config(self) -> Dict:
        """Load sync configuration"""
        default_config = {
            "sync_interval": 30,  # seconds
            "auto_commit": True,
            "auto_push": True,
            "file_patterns": {
                "include": ["*.py", "*.md", "*.sh", "*.json", "*.yaml", "*.yml", "*.txt", "*.html", "*.css", "*.js"],
                "exclude": ["*.pyc", "*.log", "__pycache__", ".git", "node_modules", ".cache"]
            },
            "directory_mapping": {
                "*.py": "src/",
                "*.md": "docs/",
                "*.sh": "scripts/",
                "*.json": "config/",
                "*.yaml": "config/",
                "*.yml": "config/",
                "*.html": "frontend/",
                "*.css": "frontend/assets/",
                "*.js": "frontend/assets/"
            },
            "commit_message_templates": {
                "new_file": "feat: Add {filename} - {description}",
                "modified_file": "update: Modify {filename} - {description}",
                "multiple_files": "feat: Add/update {count} files - {description}",
                "automated": "chore: Automated sync - {timestamp}"
            }
        }
        
        if self.sync_config_file.exists():
            try:
                with open(self.sync_config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Save default config
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict):
        """Save sync configuration"""
        try:
            with open(self.sync_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in sync"""
        file_str = str(file_path)
        filename = file_path.name
        
        # Check exclude patterns first
        for pattern in self.config["file_patterns"]["exclude"]:
            if fnmatch.fnmatch(filename, pattern) or pattern in file_str:
                return False
        
        # Check include patterns
        for pattern in self.config["file_patterns"]["include"]:
            if fnmatch.fnmatch(filename, pattern):
                return True
        
        return False
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def get_target_directory(self, file_path: Path) -> Path:
        """Determine target directory in git repository"""
        filename = file_path.name
        
        # Check directory mapping
        for pattern, target_dir in self.config["directory_mapping"].items():
            if fnmatch.fnmatch(filename, pattern):
                return self.git_repo / target_dir
        
        # Default to docs directory
        return self.git_repo / "docs"
    
    def scan_sandbox_files(self) -> List[Path]:
        """Scan sandbox for files to sync"""
        files_to_sync = []
        
        try:
            # Scan sandbox root (excluding git repositories)
            for item in self.sandbox_root.iterdir():
                if item.is_file() and self.should_include_file(item):
                    files_to_sync.append(item)
                elif item.is_dir() and not item.name.startswith('.') and item.name != 'complete_apexagent_sync':
                    # Scan subdirectories (limited depth)
                    for subitem in item.rglob('*'):
                        if subitem.is_file() and self.should_include_file(subitem):
                            files_to_sync.append(subitem)
        
        except Exception as e:
            logger.error(f"Error scanning sandbox files: {e}")
        
        return files_to_sync
    
    def copy_file_to_repo(self, source_path: Path, target_dir: Path) -> bool:
        """Copy file to git repository with organization"""
        try:
            # Ensure target directory exists
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine target file path
            target_path = target_dir / source_path.name
            
            # Handle conflicts (append timestamp if file exists)
            if target_path.exists():
                source_hash = self.get_file_hash(source_path)
                target_hash = self.get_file_hash(target_path)
                
                if source_hash == target_hash:
                    logger.info(f"File {source_path.name} already exists with same content")
                    return True
                else:
                    # Create backup of existing file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = target_dir / f"{source_path.stem}_{timestamp}{source_path.suffix}"
                    shutil.copy2(target_path, backup_path)
                    logger.info(f"Created backup: {backup_path}")
            
            # Copy file
            shutil.copy2(source_path, target_path)
            logger.info(f"Copied {source_path} -> {target_path}")
            
            # Update tracking
            self.tracked_files.add(str(target_path))
            self.file_hashes[str(target_path)] = self.get_file_hash(target_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Error copying {source_path} to {target_dir}: {e}")
            return False
    
    def emergency_file_recovery(self) -> int:
        """Emergency recovery of all orphaned files"""
        logger.info("Starting emergency file recovery...")
        
        files_to_sync = self.scan_sandbox_files()
        recovered_count = 0
        
        for file_path in files_to_sync:
            try:
                target_dir = self.get_target_directory(file_path)
                if self.copy_file_to_repo(file_path, target_dir):
                    recovered_count += 1
            except Exception as e:
                logger.error(f"Error recovering {file_path}: {e}")
        
        logger.info(f"Emergency recovery completed: {recovered_count} files recovered")
        return recovered_count
    
    def setup_git_repository(self):
        """Setup git repository configuration"""
        try:
            os.chdir(self.git_repo)
            
            # Configure git user
            subprocess.run(["git", "config", "user.name", "Manus AI"], check=True)
            subprocess.run(["git", "config", "user.email", "manus@aideon.ai"], check=True)
            
            # Configure remote with token
            remote_url = f"https://AllienNova:{self.github_token}@github.com/AllienNova/APEXAGENT_FRESH.git"
            subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
            
            logger.info("Git repository configured successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git configuration error: {e}")
        except Exception as e:
            logger.error(f"Error setting up git repository: {e}")
    
    def generate_commit_message(self, files: List[str]) -> str:
        """Generate intelligent commit message"""
        if not files:
            return "chore: Automated sync - no changes"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if len(files) == 1:
            filename = Path(files[0]).name
            if filename.endswith('.md'):
                description = "documentation update"
            elif filename.endswith('.py'):
                description = "code implementation"
            elif filename.endswith('.sh'):
                description = "script automation"
            else:
                description = "file update"
            
            return self.config["commit_message_templates"]["new_file"].format(
                filename=filename, description=description
            )
        else:
            return self.config["commit_message_templates"]["multiple_files"].format(
                count=len(files), description=f"automated sync at {timestamp}"
            )
    
    def commit_and_push_changes(self) -> bool:
        """Commit and push changes to GitHub"""
        try:
            os.chdir(self.git_repo)
            
            # Check for changes
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                logger.info("No changes to commit")
                return True
            
            # Add all changes
            subprocess.run(["git", "add", "."], check=True)
            
            # Get list of changed files
            result = subprocess.run(["git", "diff", "--cached", "--name-only"], 
                                  capture_output=True, text=True, check=True)
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Generate commit message
            commit_message = self.generate_commit_message(changed_files)
            
            # Commit changes
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            logger.info(f"Committed changes: {commit_message}")
            
            # Push to GitHub
            if self.config["auto_push"]:
                subprocess.run(["git", "push", "origin", self.git_branch], check=True)
                logger.info(f"Pushed changes to GitHub ({self.git_branch})")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error committing and pushing changes: {e}")
            return False
    
    def continuous_sync(self):
        """Continuous file monitoring and sync"""
        logger.info("Starting continuous sync monitoring...")
        
        while self.is_running:
            try:
                # Scan for new files
                files_to_sync = self.scan_sandbox_files()
                sync_count = 0
                
                for file_path in files_to_sync:
                    file_str = str(file_path)
                    current_hash = self.get_file_hash(file_path)
                    
                    # Check if file is new or modified
                    if (file_str not in self.tracked_files or 
                        self.file_hashes.get(file_str) != current_hash):
                        
                        target_dir = self.get_target_directory(file_path)
                        if self.copy_file_to_repo(file_path, target_dir):
                            sync_count += 1
                
                # Commit and push if changes were made
                if sync_count > 0:
                    logger.info(f"Synced {sync_count} files")
                    if self.config["auto_commit"]:
                        self.commit_and_push_changes()
                
                # Wait for next sync cycle
                time.sleep(self.config["sync_interval"])
                
            except Exception as e:
                logger.error(f"Error in continuous sync: {e}")
                time.sleep(10)  # Wait before retrying
    
    def start_sync_daemon(self):
        """Start sync daemon in background thread"""
        if self.is_running:
            logger.warning("Sync daemon already running")
            return
        
        self.is_running = True
        sync_thread = threading.Thread(target=self.continuous_sync, daemon=True)
        sync_thread.start()
        logger.info("Sync daemon started")
    
    def stop_sync_daemon(self):
        """Stop sync daemon"""
        self.is_running = False
        logger.info("Sync daemon stopped")
    
    def verify_github_sync(self) -> Dict:
        """Verify that all files are properly synced to GitHub"""
        try:
            os.chdir(self.git_repo)
            
            # Get remote repository status
            subprocess.run(["git", "fetch", "origin"], check=True)
            
            # Check if local is ahead of remote
            result = subprocess.run(["git", "rev-list", "--count", f"origin/{self.git_branch}..HEAD"], 
                                  capture_output=True, text=True, check=True)
            commits_ahead = int(result.stdout.strip())
            
            # Check if local is behind remote
            result = subprocess.run(["git", "rev-list", "--count", f"HEAD..origin/{self.git_branch}"], 
                                  capture_output=True, text=True, check=True)
            commits_behind = int(result.stdout.strip())
            
            # Get file count in repository
            result = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True)
            repo_files = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
            # Get sandbox file count
            sandbox_files = len(self.scan_sandbox_files())
            
            verification_result = {
                "sync_status": "synced" if commits_ahead == 0 else "needs_push",
                "commits_ahead": commits_ahead,
                "commits_behind": commits_behind,
                "repo_file_count": repo_files,
                "sandbox_file_count": sandbox_files,
                "sync_percentage": min(100, (repo_files / max(sandbox_files, 1)) * 100),
                "last_check": datetime.now().isoformat()
            }
            
            logger.info(f"GitHub sync verification: {verification_result}")
            return verification_result
            
        except Exception as e:
            logger.error(f"Error verifying GitHub sync: {e}")
            return {"error": str(e)}
    
    def create_sync_report(self) -> str:
        """Create comprehensive sync status report"""
        report_lines = [
            "# Sandbox-to-GitHub Sync Report",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Sync Status"
        ]
        
        # Get verification results
        verification = self.verify_github_sync()
        
        if "error" not in verification:
            report_lines.extend([
                f"- **Sync Status:** {verification['sync_status']}",
                f"- **Commits Ahead:** {verification['commits_ahead']}",
                f"- **Commits Behind:** {verification['commits_behind']}",
                f"- **Repository Files:** {verification['repo_file_count']}",
                f"- **Sandbox Files:** {verification['sandbox_file_count']}",
                f"- **Sync Percentage:** {verification['sync_percentage']:.1f}%",
                ""
            ])
        
        # Add tracked files summary
        report_lines.extend([
            "## Tracked Files",
            f"- **Total Tracked:** {len(self.tracked_files)}",
            f"- **File Hashes:** {len(self.file_hashes)}",
            ""
        ])
        
        # Add configuration
        report_lines.extend([
            "## Configuration",
            f"- **Sync Interval:** {self.config['sync_interval']} seconds",
            f"- **Auto Commit:** {self.config['auto_commit']}",
            f"- **Auto Push:** {self.config['auto_push']}",
            f"- **Git Branch:** {self.git_branch}",
            ""
        ])
        
        return "\n".join(report_lines)

def main():
    """Main entry point for sync system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aideon AI Lite Sandbox Sync System")
    parser.add_argument("--emergency-recovery", action="store_true", 
                       help="Perform emergency file recovery")
    parser.add_argument("--start-daemon", action="store_true", 
                       help="Start continuous sync daemon")
    parser.add_argument("--verify", action="store_true", 
                       help="Verify GitHub sync status")
    parser.add_argument("--report", action="store_true", 
                       help="Generate sync status report")
    parser.add_argument("--setup-git", action="store_true", 
                       help="Setup git repository configuration")
    
    args = parser.parse_args()
    
    # Create sync manager
    sync_manager = SandboxSyncManager()
    
    if args.setup_git:
        sync_manager.setup_git_repository()
    
    if args.emergency_recovery:
        recovered = sync_manager.emergency_file_recovery()
        print(f"Emergency recovery completed: {recovered} files recovered")
        
        # Commit recovered files
        if recovered > 0:
            sync_manager.commit_and_push_changes()
    
    if args.verify:
        verification = sync_manager.verify_github_sync()
        print(json.dumps(verification, indent=2))
    
    if args.report:
        report = sync_manager.create_sync_report()
        print(report)
        
        # Save report to file
        report_file = sync_manager.git_repo / "docs" / "sync_status_report.md"
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")
    
    if args.start_daemon:
        sync_manager.start_sync_daemon()
        try:
            print("Sync daemon running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sync_manager.stop_sync_daemon()
            print("\nSync daemon stopped")
    
    if not any(vars(args).values()):
        print("No action specified. Use --help for options.")
        print("Quick start: python automated_sync_system.py --emergency-recovery")

if __name__ == "__main__":
    main()

