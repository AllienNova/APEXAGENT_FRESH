#!/bin/bash
# ApexAgent Onboarding Script
# This script guides new developers through the onboarding process

set -e

# Print colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_step() {
  echo -e "${BLUE}[STEP]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Welcome message
clear
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Welcome to ApexAgent Onboarding Guide  ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo
echo -e "This interactive script will guide you through the process of setting up your development environment and getting familiar with the ApexAgent project."
echo

# Check if user wants to proceed
read -p "Press Enter to begin the onboarding process, or Ctrl+C to exit..."

# Step 1: Environment setup
log_step "Step 1: Setting up your development environment"
echo
log_info "Checking for required dependencies..."

# Check for dependencies
dependencies=("git" "docker" "docker-compose" "node" "npm")
missing_deps=()

for dep in "${dependencies[@]}"; do
  if ! command -v $dep &> /dev/null; then
    missing_deps+=($dep)
    log_error "$dep is not installed."
  else
    log_info "$dep is installed ✓"
  fi
done

if [ ${#missing_deps[@]} -ne 0 ]; then
  echo
  log_error "Please install the missing dependencies and run this script again."
  echo
  log_info "Installation guides:"
  [ $(echo "${missing_deps[@]}" | grep -c "git") -ne 0 ] && echo "  - Git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git"
  [ $(echo "${missing_deps[@]}" | grep -c "docker") -ne 0 ] && echo "  - Docker: https://docs.docker.com/get-docker/"
  [ $(echo "${missing_deps[@]}" | grep -c "docker-compose") -ne 0 ] && echo "  - Docker Compose: https://docs.docker.com/compose/install/"
  [ $(echo "${missing_deps[@]}" | grep -c "node") -ne 0 ] && echo "  - Node.js: https://nodejs.org/en/download/"
  exit 1
fi

echo
log_info "All dependencies are installed! ✓"
echo

# Step 2: Clone repository
log_step "Step 2: Cloning the repository"
echo

if [ -d "ApexAgent" ]; then
  log_warn "ApexAgent directory already exists."
  read -p "Do you want to use the existing directory? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Nn]$ ]]; then
    read -p "Do you want to delete the existing directory and clone again? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      log_info "Removing existing directory..."
      rm -rf ApexAgent
      log_info "Cloning repository..."
      git clone https://github.com/AllienNova/ApexAgent.git
    else
      log_info "Using existing directory."
    fi
  else
    log_info "Using existing directory."
  fi
else
  log_info "Cloning repository..."
  git clone https://github.com/AllienNova/ApexAgent.git
fi

# Change to project directory
cd ApexAgent

echo
log_info "Repository is ready! ✓"
echo

# Step 3: Run setup script
log_step "Step 3: Setting up development environment"
echo

log_info "Running development environment setup script..."
chmod +x src/devex/local_env/setup.sh
./src/devex/local_env/setup.sh

echo
log_info "Development environment is set up! ✓"
echo

# Step 4: IDE setup
log_step "Step 4: Setting up your IDE"
echo

log_info "Recommended IDE: Visual Studio Code"
log_info "Recommended extensions:"
echo "  - ESLint"
echo "  - Prettier"
echo "  - Docker"
echo "  - Jest"
echo "  - GitLens"

if command -v code &> /dev/null; then
  read -p "Do you want to install recommended VS Code extensions? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Installing recommended VS Code extensions..."
    code --install-extension dbaeumer.vscode-eslint
    code --install-extension esbenp.prettier-vscode
    code --install-extension ms-azuretools.vscode-docker
    code --install-extension orta.vscode-jest
    code --install-extension eamodio.gitlens
    log_info "Extensions installed! ✓"
  fi
else
  log_info "VS Code not found. Please install the recommended extensions manually."
fi

echo
log_info "IDE setup complete! ✓"
echo

# Step 5: Project tour
log_step "Step 5: Project tour"
echo

log_info "ApexAgent Project Structure:"
echo "  - /src - Source code"
echo "    - /core - Core framework components"
echo "    - /domain - Domain models and business logic"
echo "    - /api - API endpoints"
echo "    - /infrastructure - External systems integration"
echo "    - /ui - User interface components"
echo "    - /devex - Developer experience tools"
echo "  - /tests - Test suite"
echo "  - /docs - Documentation"
echo "  - /example_plugins - Example plugin implementations"
echo

log_info "Key documentation to review:"
echo "  - src/devex/documentation/code_architecture.md - System architecture"
echo "  - src/devex/documentation/development_workflow.md - Development workflow"
echo "  - docs/plugin_system_architecture.md - Plugin system"
echo

read -p "Press Enter to open the code architecture documentation..."
if command -v code &> /dev/null; then
  code src/devex/documentation/code_architecture.md
else
  # Use a fallback method to display the file
  if command -v less &> /dev/null; then
    less src/devex/documentation/code_architecture.md
  else
    cat src/devex/documentation/code_architecture.md | more
  fi
fi

echo
log_info "Project tour complete! ✓"
echo

# Step 6: First task
log_step "Step 6: Your first task"
echo

log_info "Let's complete a simple task to get familiar with the codebase."
echo

log_info "Task: Create a simple 'Hello World' component"
echo "  1. Use the dev.sh script to generate a component:"
echo "     ./dev.sh generate component HelloWorld"
echo "  2. Modify the component to display 'Hello, ApexAgent!'"
echo "  3. Run the tests to ensure everything works:"
echo "     ./dev.sh test"
echo

read -p "Press Enter when you're ready to try this task..."

# Check if dev.sh exists and is executable
if [ -f "./dev.sh" ] && [ -x "./dev.sh" ]; then
  log_info "Running: ./dev.sh generate component HelloWorld"
  ./dev.sh generate component HelloWorld
  
  log_info "Now open and edit the component at: src/components/HelloWorld/HelloWorld.js"
  log_info "When you're done, run: ./dev.sh test"
else
  log_warn "dev.sh script not found or not executable. Please complete the task manually."
fi

echo
log_info "First task guidance complete! ✓"
echo

# Step 7: Resources and contacts
log_step "Step 7: Resources and contacts"
echo

log_info "Additional resources:"
echo "  - GitHub repository: https://github.com/AllienNova/ApexAgent"
echo "  - Documentation: /docs directory"
echo "  - Issue tracker: https://github.com/AllienNova/ApexAgent/issues"
echo

log_info "Key contacts:"
echo "  - Technical Lead: tech.lead@example.com"
echo "  - Project Manager: project.manager@example.com"
echo "  - Team chat: #apexagent-dev channel"
echo

# Step 8: Completion
log_step "Step 8: Onboarding complete!"
echo

log_info "Congratulations! You've completed the initial onboarding process."
log_info "Here's what you should do next:"
echo "  1. Review the architecture documentation"
echo "  2. Complete your first task"
echo "  3. Join the team standup (10:00 AM daily)"
echo "  4. Schedule a 1:1 with your mentor"
echo

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Welcome to the ApexAgent team!         ${NC}"
echo -e "${GREEN}=========================================${NC}"
