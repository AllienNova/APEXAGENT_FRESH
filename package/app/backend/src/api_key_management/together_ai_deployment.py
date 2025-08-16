"""
Deployment automation scripts and CI/CD configuration for Together AI integration.

This module implements deployment automation scripts and CI/CD configuration
for Together AI integration, ensuring smooth deployment and updates.
"""

import os
import sys
import logging
import subprocess
import json
import time
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class TogetherAIDeploymentAutomation:
    """
    Deployment automation for Together AI integration.
    
    This class handles deployment automation for Together AI integration,
    including CI/CD configuration and deployment scripts.
    """
    
    def __init__(self, config_dir: str = "/etc/aideon/deployment"):
        """
        Initialize the deployment automation.
        
        Args:
            config_dir: Configuration directory
        """
        self.config_dir = config_dir
        self.deployment_config = self._load_deployment_config()
    
    def _load_deployment_config(self) -> Dict[str, Any]:
        """
        Load deployment configuration.
        
        Returns:
            Deployment configuration
        """
        config_path = os.path.join(self.config_dir, "together_ai_deployment.json")
        
        # Create default config if not exists
        if not os.path.exists(config_path):
            default_config = {
                "version": "1.0.0",
                "environments": {
                    "development": {
                        "api_url": "https://dev-api.aideon.ai",
                        "feature_flags": {
                            "together_ai_integration": True,
                            "together_ai_free_tier": True
                        }
                    },
                    "staging": {
                        "api_url": "https://staging-api.aideon.ai",
                        "feature_flags": {
                            "together_ai_integration": True,
                            "together_ai_free_tier": True
                        }
                    },
                    "production": {
                        "api_url": "https://api.aideon.ai",
                        "feature_flags": {
                            "together_ai_integration": False,
                            "together_ai_free_tier": False
                        }
                    }
                },
                "deployment_steps": [
                    "validate_code",
                    "run_tests",
                    "build_package",
                    "deploy_to_environment",
                    "run_smoke_tests",
                    "update_feature_flags"
                ]
            }
            
            # Create directory if not exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Write default config
            with open(config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
        
        # Load existing config
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading deployment config: {str(e)}")
            return {}
    
    def save_deployment_config(self) -> bool:
        """
        Save deployment configuration.
        
        Returns:
            True if successful, False otherwise
        """
        config_path = os.path.join(self.config_dir, "together_ai_deployment.json")
        
        try:
            # Create directory if not exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Write config
            with open(config_path, "w") as f:
                json.dump(self.deployment_config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving deployment config: {str(e)}")
            return False
    
    def update_environment_config(
        self,
        environment: str,
        config_updates: Dict[str, Any]
    ) -> bool:
        """
        Update environment configuration.
        
        Args:
            environment: Environment name
            config_updates: Configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        if environment not in self.deployment_config.get("environments", {}):
            logger.error(f"Environment {environment} not found in deployment config")
            return False
        
        try:
            # Update environment config
            self.deployment_config["environments"][environment].update(config_updates)
            
            # Save config
            return self.save_deployment_config()
        except Exception as e:
            logger.error(f"Error updating environment config: {str(e)}")
            return False
    
    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """
        Get environment configuration.
        
        Args:
            environment: Environment name
            
        Returns:
            Environment configuration
        """
        return self.deployment_config.get("environments", {}).get(environment, {})
    
    def validate_code(self, code_dir: str) -> bool:
        """
        Validate code before deployment.
        
        Args:
            code_dir: Code directory
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Run linting
            lint_result = subprocess.run(
                ["flake8", "src/plugins/llm_providers/internal/together_ai_provider.py", "src/api_key_management/together_ai_*.py"],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            
            if lint_result.returncode != 0:
                logger.error(f"Linting failed: {lint_result.stdout}\n{lint_result.stderr}")
                return False
            
            # Run type checking
            mypy_result = subprocess.run(
                ["mypy", "src/plugins/llm_providers/internal/together_ai_provider.py", "src/api_key_management/together_ai_*.py"],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            
            if mypy_result.returncode != 0:
                logger.error(f"Type checking failed: {mypy_result.stdout}\n{mypy_result.stderr}")
                return False
            
            # Run security checks
            bandit_result = subprocess.run(
                ["bandit", "-r", "src/plugins/llm_providers/internal/together_ai_provider.py", "src/api_key_management/together_ai_*.py"],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            
            if bandit_result.returncode != 0:
                logger.error(f"Security checks failed: {bandit_result.stdout}\n{bandit_result.stderr}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating code: {str(e)}")
            return False
    
    def run_tests(self, code_dir: str) -> bool:
        """
        Run tests before deployment.
        
        Args:
            code_dir: Code directory
            
        Returns:
            True if tests pass, False otherwise
        """
        try:
            # Run unit tests
            test_result = subprocess.run(
                ["python", "-m", "unittest", "tests/test_together_ai_integration.py"],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            
            if test_result.returncode != 0:
                logger.error(f"Tests failed: {test_result.stdout}\n{test_result.stderr}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            return False
    
    def build_package(self, code_dir: str, output_dir: str) -> Optional[str]:
        """
        Build deployment package.
        
        Args:
            code_dir: Code directory
            output_dir: Output directory
            
        Returns:
            Path to built package, or None if build fails
        """
        try:
            # Create output directory if not exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Get version
            version = self.deployment_config.get("version", "1.0.0")
            
            # Build package
            package_name = f"together_ai_integration-{version}.zip"
            package_path = os.path.join(output_dir, package_name)
            
            # Create zip file
            zip_result = subprocess.run(
                [
                    "zip", "-r", package_path,
                    "src/plugins/llm_providers/internal/together_ai_provider.py",
                    "src/api_key_management/together_ai_*.py",
                    "src/api/together_ai_endpoints.py",
                    "tests/test_together_ai_integration.py"
                ],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            
            if zip_result.returncode != 0:
                logger.error(f"Package build failed: {zip_result.stdout}\n{zip_result.stderr}")
                return None
            
            return package_path
        except Exception as e:
            logger.error(f"Error building package: {str(e)}")
            return None
    
    def deploy_to_environment(
        self,
        package_path: str,
        environment: str,
        dry_run: bool = False
    ) -> bool:
        """
        Deploy package to environment.
        
        Args:
            package_path: Path to deployment package
            environment: Environment name
            dry_run: Whether to perform a dry run
            
        Returns:
            True if deployment succeeds, False otherwise
        """
        try:
            # Get environment config
            env_config = self.get_environment_config(environment)
            if not env_config:
                logger.error(f"Environment {environment} not found in deployment config")
                return False
            
            # Get API URL
            api_url = env_config.get("api_url")
            if not api_url:
                logger.error(f"API URL not found for environment {environment}")
                return False
            
            # Log deployment
            logger.info(f"Deploying {package_path} to {environment} ({api_url})")
            
            if dry_run:
                logger.info("Dry run, skipping actual deployment")
                return True
            
            # Deploy package
            deploy_result = subprocess.run(
                [
                    "curl", "-X", "POST",
                    "-H", "Content-Type: multipart/form-data",
                    "-F", f"package=@{package_path}",
                    "-F", f"environment={environment}",
                    f"{api_url}/admin/deploy"
                ],
                capture_output=True,
                text=True
            )
            
            if deploy_result.returncode != 0:
                logger.error(f"Deployment failed: {deploy_result.stdout}\n{deploy_result.stderr}")
                return False
            
            # Parse response
            try:
                response = json.loads(deploy_result.stdout)
                if response.get("status") != "success":
                    logger.error(f"Deployment failed: {response.get('message')}")
                    return False
            except Exception as e:
                logger.error(f"Error parsing deployment response: {str(e)}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error deploying to environment: {str(e)}")
            return False
    
    def run_smoke_tests(self, environment: str) -> bool:
        """
        Run smoke tests after deployment.
        
        Args:
            environment: Environment name
            
        Returns:
            True if smoke tests pass, False otherwise
        """
        try:
            # Get environment config
            env_config = self.get_environment_config(environment)
            if not env_config:
                logger.error(f"Environment {environment} not found in deployment config")
                return False
            
            # Get API URL
            api_url = env_config.get("api_url")
            if not api_url:
                logger.error(f"API URL not found for environment {environment}")
                return False
            
            # Run smoke tests
            smoke_tests = [
                # Check API endpoints
                f"curl -s {api_url}/api/v1/together/models",
                # Check health endpoint
                f"curl -s {api_url}/health"
            ]
            
            for test_cmd in smoke_tests:
                test_result = subprocess.run(
                    test_cmd.split(),
                    capture_output=True,
                    text=True
                )
                
                if test_result.returncode != 0:
                    logger.error(f"Smoke test failed: {test_cmd}\n{test_result.stdout}\n{test_result.stderr}")
                    return False
                
                # Parse response
                try:
                    response = json.loads(test_result.stdout)
                    if "error" in response:
                        logger.error(f"Smoke test failed: {test_cmd}\n{response}")
                        return False
                except Exception as e:
                    logger.error(f"Error parsing smoke test response: {str(e)}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error running smoke tests: {str(e)}")
            return False
    
    def update_feature_flags(self, environment: str) -> bool:
        """
        Update feature flags after deployment.
        
        Args:
            environment: Environment name
            
        Returns:
            True if update succeeds, False otherwise
        """
        try:
            # Get environment config
            env_config = self.get_environment_config(environment)
            if not env_config:
                logger.error(f"Environment {environment} not found in deployment config")
                return False
            
            # Get API URL
            api_url = env_config.get("api_url")
            if not api_url:
                logger.error(f"API URL not found for environment {environment}")
                return False
            
            # Get feature flags
            feature_flags = env_config.get("feature_flags", {})
            
            # Update feature flags
            for flag_name, flag_value in feature_flags.items():
                update_result = subprocess.run(
                    [
                        "curl", "-X", "POST",
                        "-H", "Content-Type: application/json",
                        "-d", json.dumps({"value": flag_value}),
                        f"{api_url}/admin/feature-flags/{flag_name}"
                    ],
                    capture_output=True,
                    text=True
                )
                
                if update_result.returncode != 0:
                    logger.error(f"Feature flag update failed: {flag_name}\n{update_result.stdout}\n{update_result.stderr}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error updating feature flags: {str(e)}")
            return False
    
    def deploy(
        self,
        code_dir: str,
        environment: str,
        dry_run: bool = False
    ) -> bool:
        """
        Deploy Together AI integration to environment.
        
        Args:
            code_dir: Code directory
            environment: Environment name
            dry_run: Whether to perform a dry run
            
        Returns:
            True if deployment succeeds, False otherwise
        """
        try:
            # Get deployment steps
            deployment_steps = self.deployment_config.get("deployment_steps", [])
            
            # Validate code
            if "validate_code" in deployment_steps:
                logger.info("Validating code...")
                if not self.validate_code(code_dir):
                    logger.error("Code validation failed")
                    return False
            
            # Run tests
            if "run_tests" in deployment_steps:
                logger.info("Running tests...")
                if not self.run_tests(code_dir):
                    logger.error("Tests failed")
                    return False
            
            # Build package
            if "build_package" in deployment_steps:
                logger.info("Building package...")
                package_path = self.build_package(code_dir, "/tmp/aideon_deployment")
                if not package_path:
                    logger.error("Package build failed")
                    return False
            
            # Deploy to environment
            if "deploy_to_environment" in deployment_steps:
                logger.info(f"Deploying to {environment}...")
                if not self.deploy_to_environment(package_path, environment, dry_run):
                    logger.error("Deployment failed")
                    return False
            
            # Run smoke tests
            if "run_smoke_tests" in deployment_steps and not dry_run:
                logger.info("Running smoke tests...")
                if not self.run_smoke_tests(environment):
                    logger.error("Smoke tests failed")
                    return False
            
            # Update feature flags
            if "update_feature_flags" in deployment_steps and not dry_run:
                logger.info("Updating feature flags...")
                if not self.update_feature_flags(environment):
                    logger.error("Feature flag update failed")
                    return False
            
            logger.info(f"Deployment to {environment} completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error during deployment: {str(e)}")
            return False


# CI/CD configuration
def generate_github_actions_workflow(output_path: str) -> bool:
    """
    Generate GitHub Actions workflow configuration.
    
    Args:
        output_path: Output path for workflow file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        workflow = """name: Together AI Integration CI/CD

on:
  push:
    branches: [ main ]
    paths:
      - 'src/plugins/llm_providers/internal/together_ai_provider.py'
      - 'src/api_key_management/together_ai_*.py'
      - 'src/api/together_ai_endpoints.py'
      - 'tests/test_together_ai_integration.py'
  pull_request:
    branches: [ main ]
    paths:
      - 'src/plugins/llm_providers/internal/together_ai_provider.py'
      - 'src/api_key_management/together_ai_*.py'
      - 'src/api/together_ai_endpoints.py'
      - 'tests/test_together_ai_integration.py'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'development'
        type: choice
        options:
          - development
          - staging
          - production

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flake8 mypy bandit
          pip install -r requirements.txt
      - name: Lint with flake8
        run: |
          flake8 src/plugins/llm_providers/internal/together_ai_provider.py src/api_key_management/together_ai_*.py src/api/together_ai_endpoints.py
      - name: Type check with mypy
        run: |
          mypy src/plugins/llm_providers/internal/together_ai_provider.py src/api_key_management/together_ai_*.py src/api/together_ai_endpoints.py
      - name: Security check with bandit
        run: |
          bandit -r src/plugins/llm_providers/internal/together_ai_provider.py src/api_key_management/together_ai_*.py src/api/together_ai_endpoints.py

  test:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m unittest tests/test_together_ai_integration.py

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Build package
        run: |
          mkdir -p dist
          zip -r dist/together_ai_integration.zip src/plugins/llm_providers/internal/together_ai_provider.py src/api_key_management/together_ai_*.py src/api/together_ai_endpoints.py tests/test_together_ai_integration.py
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: together-ai-integration
          path: dist/together_ai_integration.zip

  deploy-development:
    needs: build
    if: github.event_name == 'push' || (github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'development')
    runs-on: ubuntu-latest
    environment: development
    steps:
      - uses: actions/download-artifact@v3
        with:
          name: together-ai-integration
          path: dist
      - name: Deploy to development
        env:
          API_URL: ${{ secrets.DEV_API_URL }}
          API_KEY: ${{ secrets.DEV_API_KEY }}
        run: |
          curl -X POST \\
            -H "Authorization: Bearer $API_KEY" \\
            -H "Content-Type: multipart/form-data" \\
            -F "package=@dist/together_ai_integration.zip" \\
            -F "environment=development" \\
            $API_URL/admin/deploy
      - name: Run smoke tests
        env:
          API_URL: ${{ secrets.DEV_API_URL }}
          API_KEY: ${{ secrets.DEV_API_KEY }}
        run: |
          curl -s -H "Authorization: Bearer $API_KEY" $API_URL/api/v1/together/models
          curl -s $API_URL/health

  deploy-staging:
    needs: deploy-development
    if: github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'staging'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/download-artifact@v3
        with:
          name: together-ai-integration
          path: dist
      - name: Deploy to staging
        env:
          API_URL: ${{ secrets.STAGING_API_URL }}
          API_KEY: ${{ secrets.STAGING_API_KEY }}
        run: |
          curl -X POST \\
            -H "Authorization: Bearer $API_KEY" \\
            -H "Content-Type: multipart/form-data" \\
            -F "package=@dist/together_ai_integration.zip" \\
            -F "environment=staging" \\
            $API_URL/admin/deploy
      - name: Run smoke tests
        env:
          API_URL: ${{ secrets.STAGING_API_URL }}
          API_KEY: ${{ secrets.STAGING_API_KEY }}
        run: |
          curl -s -H "Authorization: Bearer $API_KEY" $API_URL/api/v1/together/models
          curl -s $API_URL/health

  deploy-production:
    needs: deploy-staging
    if: github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'production'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/download-artifact@v3
        with:
          name: together-ai-integration
          path: dist
      - name: Deploy to production
        env:
          API_URL: ${{ secrets.PROD_API_URL }}
          API_KEY: ${{ secrets.PROD_API_KEY }}
        run: |
          curl -X POST \\
            -H "Authorization: Bearer $API_KEY" \\
            -H "Content-Type: multipart/form-data" \\
            -F "package=@dist/together_ai_integration.zip" \\
            -F "environment=production" \\
            $API_URL/admin/deploy
      - name: Run smoke tests
        env:
          API_URL: ${{ secrets.PROD_API_URL }}
          API_KEY: ${{ secrets.PROD_API_KEY }}
        run: |
          curl -s -H "Authorization: Bearer $API_KEY" $API_URL/api/v1/together/models
          curl -s $API_URL/health
"""
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write workflow file
        with open(output_path, "w") as f:
            f.write(workflow)
        
        return True
    except Exception as e:
        logger.error(f"Error generating GitHub Actions workflow: {str(e)}")
        return False


def generate_deployment_script(output_path: str) -> bool:
    """
    Generate deployment script.
    
    Args:
        output_path: Output path for script file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        script = """#!/bin/bash
# Together AI Integration Deployment Script

set -e

# Default values
ENVIRONMENT="development"
DRY_RUN=false
CODE_DIR="$(pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -e|--environment)
            ENVIRONMENT="$2"
            shift
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -c|--code-dir)
            CODE_DIR="$2"
            shift
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -e, --environment <env>  Deployment environment (default: development)"
            echo "  -d, --dry-run            Perform a dry run without actual deployment"
            echo "  -c, --code-dir <dir>     Code directory (default: current directory)"
            echo "  -h, --help               Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Deploying Together AI integration to $ENVIRONMENT environment"
echo "Code directory: $CODE_DIR"
if [ "$DRY_RUN" = true ]; then
    echo "Dry run: no actual deployment will be performed"
fi

# Validate environment
if [ "$ENVIRONMENT" != "development" ] && [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "Error: Invalid environment. Must be one of: development, staging, production"
    exit 1
fi

# Check if code directory exists
if [ ! -d "$CODE_DIR" ]; then
    echo "Error: Code directory does not exist: $CODE_DIR"
    exit 1
fi

# Validate code
echo "Validating code..."
if ! flake8 "$CODE_DIR/src/plugins/llm_providers/internal/together_ai_provider.py" "$CODE_DIR/src/api_key_management/together_ai_"*.py "$CODE_DIR/src/api/together_ai_endpoints.py"; then
    echo "Error: Code validation failed"
    exit 1
fi

# Run tests
echo "Running tests..."
if ! python -m unittest "$CODE_DIR/tests/test_together_ai_integration.py"; then
    echo "Error: Tests failed"
    exit 1
fi

# Build package
echo "Building package..."
PACKAGE_DIR="/tmp/aideon_deployment"
mkdir -p "$PACKAGE_DIR"
PACKAGE_PATH="$PACKAGE_DIR/together_ai_integration.zip"
if ! zip -r "$PACKAGE_PATH" "$CODE_DIR/src/plugins/llm_providers/internal/together_ai_provider.py" "$CODE_DIR/src/api_key_management/together_ai_"*.py "$CODE_DIR/src/api/together_ai_endpoints.py" "$CODE_DIR/tests/test_together_ai_integration.py"; then
    echo "Error: Package build failed"
    exit 1
fi

# Get API URL and key
case "$ENVIRONMENT" in
    development)
        API_URL="${DEV_API_URL:-https://dev-api.aideon.ai}"
        API_KEY="${DEV_API_KEY}"
        ;;
    staging)
        API_URL="${STAGING_API_URL:-https://staging-api.aideon.ai}"
        API_KEY="${STAGING_API_KEY}"
        ;;
    production)
        API_URL="${PROD_API_URL:-https://api.aideon.ai}"
        API_KEY="${PROD_API_KEY}"
        ;;
esac

if [ -z "$API_KEY" ]; then
    echo "Error: API key not set for $ENVIRONMENT environment"
    echo "Please set ${ENVIRONMENT^^}_API_KEY environment variable"
    exit 1
fi

# Deploy to environment
echo "Deploying to $ENVIRONMENT..."
if [ "$DRY_RUN" = false ]; then
    if ! curl -X POST \\
        -H "Authorization: Bearer $API_KEY" \\
        -H "Content-Type: multipart/form-data" \\
        -F "package=@$PACKAGE_PATH" \\
        -F "environment=$ENVIRONMENT" \\
        "$API_URL/admin/deploy"; then
        echo "Error: Deployment failed"
        exit 1
    fi
    
    # Run smoke tests
    echo "Running smoke tests..."
    if ! curl -s -H "Authorization: Bearer $API_KEY" "$API_URL/api/v1/together/models" | grep -q "models"; then
        echo "Error: Smoke tests failed"
        exit 1
    fi
    
    if ! curl -s "$API_URL/health" | grep -q "status"; then
        echo "Error: Health check failed"
        exit 1
    fi
    
    echo "Deployment completed successfully"
else
    echo "Dry run completed successfully"
fi
"""
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write script file
        with open(output_path, "w") as f:
            f.write(script)
        
        # Make script executable
        os.chmod(output_path, 0o755)
        
        return True
    except Exception as e:
        logger.error(f"Error generating deployment script: {str(e)}")
        return False


# Create deployment automation
def create_deployment_automation(code_dir: str) -> bool:
    """
    Create deployment automation for Together AI integration.
    
    Args:
        code_dir: Code directory
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create GitHub Actions workflow
        workflow_path = os.path.join(code_dir, ".github/workflows/together_ai_integration.yml")
        if not generate_github_actions_workflow(workflow_path):
            logger.error("Failed to generate GitHub Actions workflow")
            return False
        
        # Create deployment script
        script_path = os.path.join(code_dir, "scripts/deploy_together_ai.sh")
        if not generate_deployment_script(script_path):
            logger.error("Failed to generate deployment script")
            return False
        
        # Create deployment automation instance
        deployment_automation = TogetherAIDeploymentAutomation()
        
        # Update deployment config
        deployment_automation.update_environment_config(
            "development",
            {
                "feature_flags": {
                    "together_ai_integration": True,
                    "together_ai_free_tier": True
                }
            }
        )
        
        return True
    except Exception as e:
        logger.error(f"Error creating deployment automation: {str(e)}")
        return False
