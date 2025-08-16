#!/bin/bash

# ApexAgent Sync System - Environment Setup Script
# This script helps set up the environment for secure GitHub authentication

set -e

echo "🔧 ApexAgent Sync System - Environment Setup"
echo "============================================="

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
    source .env
else
    echo "⚠️  .env file not found"
    echo "📝 Creating .env file from template..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "📝 Please edit .env file and add your GitHub Personal Access Token"
        echo ""
        echo "To get a GitHub PAT:"
        echo "1. Go to https://github.com/settings/tokens"
        echo "2. Click 'Generate new token (classic)'"
        echo "3. Select 'repo' scope for full repository access"
        echo "4. Copy the token and paste it in .env file"
        echo ""
        read -p "Press Enter after you've updated the .env file..."
    else
        echo "❌ .env.example file not found"
        exit 1
    fi
fi

# Validate environment variables
echo "🔍 Validating environment configuration..."

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN not set in environment"
    echo "Please set GITHUB_TOKEN in your .env file"
    exit 1
fi

if [[ "$GITHUB_TOKEN" == "your_github_personal_access_token_here" ]]; then
    echo "❌ GITHUB_TOKEN still contains placeholder value"
    echo "Please update GITHUB_TOKEN in your .env file with your actual token"
    exit 1
fi

# Test GitHub authentication
echo "🔐 Testing GitHub authentication..."
if curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user > /dev/null; then
    echo "✅ GitHub authentication successful"
    
    # Get user info
    USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
    USERNAME=$(echo $USER_INFO | python3 -c "import sys, json; print(json.load(sys.stdin)['login'])")
    echo "👤 Authenticated as: $USERNAME"
else
    echo "❌ GitHub authentication failed"
    echo "Please check your GITHUB_TOKEN in the .env file"
    exit 1
fi

# Test repository access
echo "📁 Testing repository access..."
REPO_URL="https://api.github.com/repos/${GITHUB_REPOSITORY:-AllienNova/APEXAGENT_FRESH}"
if curl -s -H "Authorization: token $GITHUB_TOKEN" "$REPO_URL" > /dev/null; then
    echo "✅ Repository access confirmed"
else
    echo "❌ Repository access failed"
    echo "Please check repository permissions for your token"
    exit 1
fi

# Set up Git configuration
echo "⚙️  Configuring Git..."
git config user.name "Manus AI"
git config user.email "manus@aideon.ai"

# Update remote URL with token
REPO_NAME="${GITHUB_REPOSITORY:-AllienNova/APEXAGENT_FRESH}"
git remote set-url origin "https://$USERNAME:$GITHUB_TOKEN@github.com/$REPO_NAME.git"

echo ""
echo "🎉 Environment setup complete!"
echo "✅ GitHub authentication configured"
echo "✅ Repository access verified"
echo "✅ Git configuration updated"
echo ""
echo "You can now run the sync system:"
echo "  python3 selective_sync_system.py --sync"
echo "  python3 automated_sync_system.py"
echo ""

