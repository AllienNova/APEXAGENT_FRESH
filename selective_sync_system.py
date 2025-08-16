#!/usr/bin/env python3
"""
Aideon AI Lite - Selective Sandbox-to-GitHub Sync System
Focuses on important project files and avoids system/library files
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SelectiveSyncManager:
    """Selective sync focusing on important project files only"""
    
    def __init__(self):
        self.sandbox_root = Path("/home/ubuntu")
        self.git_repo = Path("/home/ubuntu/complete_apexagent_sync")
        
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required but not set")
        self.git_branch = "together-ai-huggingface-integration"
        
        # Important file patterns (only sync these)
        self.important_patterns = {
            "*.md": "docs/",
            "*REPORT*.md": "docs/reports/",
            "*ANALYSIS*.md": "docs/analysis/",
            "*IMPLEMENTATION*.md": "docs/implementation/",
            "*STATUS*.md": "docs/status/",
            "*CHECKLIST*.md": "docs/checklists/",
            "*.py": "src/",
            "*.sh": "scripts/",
            "*.json": "config/",
            "*.yaml": "config/",
            "*.yml": "config/",
            "*.txt": "docs/",
            "requirements.txt": "",
            "README.md": "",
            "LICENSE": "",
            "CHANGELOG.md": "",
            ".gitignore": ""
        }
        
        # Exclude patterns (never sync these)
        self.exclude_patterns = [
            "*.pyc", "*.pyo", "*.pyd", "__pycache__",
            ".git", ".cache", ".nvm", "node_modules",
            "venv", "env", ".env", "*.log",
            "*.tmp", "*.temp", "*.bak", "*.backup",
            ".DS_Store", "Thumbs.db",
            "site-packages", "lib/python*",
            "*.egg-info", "build", "dist"
        ]
        
        # Important directories to scan
        self.scan_directories = [
            self.sandbox_root,  # Root level files only
            # Don't scan subdirectories to avoid library files
        ]
    
    def should_sync_file(self, file_path: Path) -> bool:
        """Check if file should be synced based on selective criteria"""
        file_str = str(file_path)
        filename = file_path.name
        
        # Check exclude patterns first
        for pattern in self.exclude_patterns:
            if pattern in file_str or filename.startswith('.'):
                return False
        
        # Check if it's in a library/system directory
        if any(x in file_str for x in ['site-packages', 'lib/python', 'venv/', 'env/', '.cache']):
            return False
        
        # Check important patterns
        for pattern in self.important_patterns.keys():
            if filename == pattern or filename.endswith(pattern.replace('*', '')):
                return True
        
        # Special cases for important files
        important_keywords = [
            'AIDEON', 'APEX', 'IMPLEMENTATION', 'REPORT', 'ANALYSIS',
            'STATUS', 'CHECKLIST', 'DEPLOYMENT', 'SYNC', 'TOGETHER',
            'HUGGINGFACE', 'CLAUDE', 'COMPREHENSIVE'
        ]
        
        for keyword in important_keywords:
            if keyword in filename.upper():
                return True
        
        return False
    
    def get_target_directory(self, file_path: Path) -> Path:
        """Get target directory for file in git repository"""
        filename = file_path.name
        
        # Check specific patterns
        for pattern, target_dir in self.important_patterns.items():
            if filename == pattern or filename.endswith(pattern.replace('*', '')):
                if target_dir:
                    return self.git_repo / target_dir
                else:
                    return self.git_repo
        
        # Default based on file type
        if filename.endswith('.md'):
            if any(x in filename.upper() for x in ['REPORT', 'ANALYSIS']):
                return self.git_repo / "docs" / "reports"
            elif any(x in filename.upper() for x in ['STATUS', 'CHECKLIST']):
                return self.git_repo / "docs" / "status"
            else:
                return self.git_repo / "docs"
        elif filename.endswith('.py'):
            return self.git_repo / "src"
        elif filename.endswith('.sh'):
            return self.git_repo / "scripts"
        else:
            return self.git_repo / "docs"
    
    def scan_important_files(self) -> List[Path]:
        """Scan for important files only"""
        important_files = []
        
        # Scan root directory for important files
        for item in self.sandbox_root.iterdir():
            if item.is_file() and self.should_sync_file(item):
                important_files.append(item)
        
        logger.info(f"Found {len(important_files)} important files to sync")
        return important_files
    
    def copy_file_safely(self, source_path: Path, target_dir: Path) -> bool:
        """Copy file with conflict resolution"""
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / source_path.name
            
            # If file exists, create backup
            if target_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = target_dir / f"{source_path.stem}_backup_{timestamp}{source_path.suffix}"
                shutil.copy2(target_path, backup_path)
                logger.info(f"Created backup: {backup_path.name}")
            
            # Copy file
            shutil.copy2(source_path, target_path)
            logger.info(f"Synced: {source_path.name} -> {target_dir.name}/")
            return True
            
        except Exception as e:
            logger.error(f"Error copying {source_path.name}: {e}")
            return False
    
    def setup_git_repository(self):
        """Setup git repository"""
        try:
            os.chdir(self.git_repo)
            
            # Configure git
            subprocess.run(["git", "config", "user.name", "Manus AI"], check=True)
            subprocess.run(["git", "config", "user.email", "manus@aideon.ai"], check=True)
            
            # Configure remote
            remote_url = f"https://AllienNova:{self.github_token}@github.com/AllienNova/APEXAGENT_FRESH.git"
            subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
            
            logger.info("Git repository configured")
            return True
            
        except Exception as e:
            logger.error(f"Git setup error: {e}")
            return False
    
    def commit_and_push(self, message: str = None) -> bool:
        """Commit and push changes"""
        try:
            os.chdir(self.git_repo)
            
            # Check for changes
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                logger.info("No changes to commit")
                return True
            
            # Add changes
            subprocess.run(["git", "add", "."], check=True)
            
            # Generate commit message
            if not message:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"feat: Selective sync of important project files - {timestamp}"
            
            # Commit
            subprocess.run(["git", "commit", "-m", message], check=True)
            logger.info(f"Committed: {message}")
            
            # Push
            subprocess.run(["git", "push", "origin", self.git_branch], check=True)
            logger.info(f"Pushed to GitHub ({self.git_branch})")
            
            return True
            
        except Exception as e:
            logger.error(f"Git commit/push error: {e}")
            return False
    
    def selective_sync(self) -> Dict:
        """Perform selective sync of important files"""
        logger.info("Starting selective sync of important files...")
        
        # Setup git
        if not self.setup_git_repository():
            return {"error": "Git setup failed"}
        
        # Scan for important files
        important_files = self.scan_important_files()
        
        if not important_files:
            logger.info("No important files found to sync")
            return {"synced_files": 0, "status": "no_files"}
        
        # Sync files
        synced_count = 0
        synced_files = []
        
        for file_path in important_files:
            target_dir = self.get_target_directory(file_path)
            if self.copy_file_safely(file_path, target_dir):
                synced_count += 1
                synced_files.append(file_path.name)
        
        # Commit and push
        if synced_count > 0:
            commit_message = f"feat: Sync {synced_count} important project files"
            if self.commit_and_push(commit_message):
                logger.info(f"Successfully synced {synced_count} files to GitHub")
            else:
                logger.error("Failed to commit/push changes")
        
        return {
            "synced_files": synced_count,
            "total_found": len(important_files),
            "files": synced_files,
            "status": "success" if synced_count > 0 else "no_changes"
        }
    
    def create_sync_summary(self) -> str:
        """Create sync summary report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        summary = f"""# Selective Sync Summary Report

**Generated:** {timestamp}
**Repository:** https://github.com/AllienNova/APEXAGENT_FRESH
**Branch:** {self.git_branch}

## Sync Strategy

This selective sync focuses on important project files only:

### ✅ Files Synced:
- Documentation files (*.md)
- Implementation reports
- Status reports and checklists
- Python source files (*.py)
- Scripts (*.sh)
- Configuration files (*.json, *.yaml)
- Project root files (README, LICENSE, etc.)

### ❌ Files Excluded:
- System/library files (site-packages, venv, etc.)
- Cache files (.cache, __pycache__, etc.)
- Temporary files (*.tmp, *.log, etc.)
- Binary files and build artifacts

## Benefits

1. **Clean Repository** - Only important project files
2. **Fast Sync** - Avoids thousands of unnecessary files
3. **Focused Development** - Easy to find and manage project files
4. **Deployment Ready** - Contains only what's needed for deployment

## Usage

```bash
# Run selective sync
python3 selective_sync_system.py --sync

# Setup git only
python3 selective_sync_system.py --setup-git

# Generate report
python3 selective_sync_system.py --report
```
"""
        return summary

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Selective Sandbox Sync System")
    parser.add_argument("--sync", action="store_true", help="Perform selective sync")
    parser.add_argument("--setup-git", action="store_true", help="Setup git repository")
    parser.add_argument("--report", action="store_true", help="Generate sync report")
    
    args = parser.parse_args()
    
    sync_manager = SelectiveSyncManager()
    
    if args.setup_git:
        if sync_manager.setup_git_repository():
            print("✅ Git repository configured successfully")
        else:
            print("❌ Git setup failed")
    
    if args.sync:
        result = sync_manager.selective_sync()
        if "error" in result:
            print(f"❌ Sync failed: {result['error']}")
        else:
            print(f"✅ Selective sync completed:")
            print(f"   - Files synced: {result['synced_files']}")
            print(f"   - Total found: {result['total_found']}")
            print(f"   - Status: {result['status']}")
            if result['files']:
                print("   - Synced files:")
                for file in result['files'][:10]:  # Show first 10
                    print(f"     • {file}")
                if len(result['files']) > 10:
                    print(f"     ... and {len(result['files']) - 10} more")
    
    if args.report:
        report = sync_manager.create_sync_summary()
        print(report)
        
        # Save report
        report_file = sync_manager.git_repo / "docs" / "selective_sync_report.md"
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_file}")
    
    if not any(vars(args).values()):
        print("Selective Sandbox Sync System")
        print("Usage: python3 selective_sync_system.py --sync")
        print("       python3 selective_sync_system.py --setup-git")
        print("       python3 selective_sync_system.py --report")

if __name__ == "__main__":
    main()

