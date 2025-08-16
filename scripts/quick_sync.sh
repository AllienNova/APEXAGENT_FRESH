#!/bin/bash
# Quick Sync Script - Emergency file recovery and GitHub sync
# Usage: ./quick_sync.sh

set -e  # Exit on any error

echo "🚀 Aideon AI Lite - Quick Sync System"
echo "======================================"

# Change to repository directory
cd /home/ubuntu/complete_apexagent_sync

# Setup git configuration
echo "📋 Setting up Git configuration..."
python3 automated_sync_system.py --setup-git

# Perform emergency file recovery
echo "🔄 Performing emergency file recovery..."
python3 automated_sync_system.py --emergency-recovery

# Verify sync status
echo "✅ Verifying GitHub sync status..."
python3 automated_sync_system.py --verify

# Generate sync report
echo "📊 Generating sync status report..."
python3 automated_sync_system.py --report

echo ""
echo "🎉 Quick sync completed successfully!"
echo "📁 All sandbox files have been recovered and committed to GitHub"
echo "🔗 Repository: https://github.com/AllienNova/APEXAGENT_FRESH"
echo ""
echo "To start continuous monitoring:"
echo "  python3 automated_sync_system.py --start-daemon"

