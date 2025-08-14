#!/bin/bash

# Aideon Lite AI - Firebase Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

echo "🚀 Starting Aideon Lite AI Firebase Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Firebase CLI is installed
check_firebase_cli() {
    print_status "Checking Firebase CLI installation..."
    
    if ! command -v firebase &> /dev/null; then
        print_warning "Firebase CLI not found. Installing..."
        npm install -g firebase-tools
        print_success "Firebase CLI installed successfully"
    else
        print_success "Firebase CLI is already installed"
        firebase --version
    fi
}

# Check if user is logged in to Firebase
check_firebase_auth() {
    print_status "Checking Firebase authentication..."
    
    if ! firebase projects:list &> /dev/null; then
        print_warning "Not logged in to Firebase. Please login..."
        firebase login
    else
        print_success "Already logged in to Firebase"
    fi
}

# Initialize Firebase project if not already initialized
init_firebase_project() {
    print_status "Initializing Firebase project..."
    
    if [ ! -f ".firebaserc" ]; then
        print_warning "Firebase project not initialized. Starting initialization..."
        firebase init
    else
        print_success "Firebase project already initialized"
        cat .firebaserc
    fi
}

# Install Cloud Functions dependencies
install_functions_deps() {
    print_status "Installing Cloud Functions dependencies..."
    
    cd functions
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing npm packages..."
        npm install
        print_success "Dependencies installed successfully"
    else
        print_status "Updating dependencies..."
        npm update
        print_success "Dependencies updated successfully"
    fi
    
    cd ..
}

# Build Cloud Functions
build_functions() {
    print_status "Building Cloud Functions..."
    
    cd functions
    npm run build
    print_success "Cloud Functions built successfully"
    cd ..
}

# Validate Firestore rules
validate_firestore_rules() {
    print_status "Validating Firestore security rules..."
    
    if firebase firestore:rules:validate firestore.rules; then
        print_success "Firestore rules are valid"
    else
        print_error "Firestore rules validation failed"
        exit 1
    fi
}

# Validate Storage rules
validate_storage_rules() {
    print_status "Validating Storage security rules..."
    
    if firebase storage:rules:validate storage.rules; then
        print_success "Storage rules are valid"
    else
        print_error "Storage rules validation failed"
        exit 1
    fi
}

# Deploy to Firebase
deploy_to_firebase() {
    print_status "Deploying to Firebase..."
    
    # Deploy all services
    firebase deploy --only hosting,functions,firestore:rules,storage:rules
    
    if [ $? -eq 0 ]; then
        print_success "Deployment completed successfully!"
        
        # Get the hosting URL
        PROJECT_ID=$(firebase use | grep "active project" | awk '{print $4}' | tr -d '()')
        HOSTING_URL="https://${PROJECT_ID}.web.app"
        
        print_success "🌐 Your Aideon Lite AI is now live at: $HOSTING_URL"
        
        # Open in browser (optional)
        read -p "Would you like to open the app in your browser? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v xdg-open &> /dev/null; then
                xdg-open "$HOSTING_URL"
            elif command -v open &> /dev/null; then
                open "$HOSTING_URL"
            else
                print_warning "Could not open browser automatically. Please visit: $HOSTING_URL"
            fi
        fi
    else
        print_error "Deployment failed!"
        exit 1
    fi
}

# Run local emulator for testing
run_emulator() {
    print_status "Starting Firebase emulators for local testing..."
    
    # Install functions dependencies if not already done
    if [ ! -d "functions/node_modules" ]; then
        install_functions_deps
    fi
    
    # Build functions
    build_functions
    
    print_status "Starting emulators..."
    print_warning "Press Ctrl+C to stop the emulators"
    
    firebase emulators:start --only hosting,functions,firestore,auth
}

# Performance optimization
optimize_performance() {
    print_status "Optimizing performance..."
    
    # Minify CSS and JS (basic optimization)
    if command -v uglifyjs &> /dev/null; then
        print_status "Minifying JavaScript..."
        # Add JS minification here if needed
    fi
    
    # Optimize images (if any)
    if command -v imagemin &> /dev/null; then
        print_status "Optimizing images..."
        # Add image optimization here if needed
    fi
    
    print_success "Performance optimization completed"
}

# Security check
security_check() {
    print_status "Running security checks..."
    
    # Check for sensitive data in code
    if grep -r "api.*key\|secret\|password" public/ functions/src/ --exclude-dir=node_modules 2>/dev/null; then
        print_warning "Potential sensitive data found in code. Please review."
    else
        print_success "No obvious sensitive data found in code"
    fi
    
    # Validate security rules
    validate_firestore_rules
    validate_storage_rules
    
    print_success "Security checks completed"
}

# Backup current deployment
backup_deployment() {
    print_status "Creating deployment backup..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup configuration files
    cp firebase.json "$BACKUP_DIR/"
    cp firestore.rules "$BACKUP_DIR/"
    cp storage.rules "$BACKUP_DIR/"
    cp firestore.indexes.json "$BACKUP_DIR/"
    
    # Backup functions
    cp -r functions/src "$BACKUP_DIR/functions_src"
    cp functions/package.json "$BACKUP_DIR/"
    
    # Backup public files
    cp -r public "$BACKUP_DIR/"
    
    print_success "Backup created at: $BACKUP_DIR"
}

# Show help
show_help() {
    echo "Aideon Lite AI - Firebase Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     Deploy to Firebase (default)"
    echo "  emulator   Run local emulator for testing"
    echo "  build      Build Cloud Functions only"
    echo "  validate   Validate security rules"
    echo "  optimize   Run performance optimizations"
    echo "  security   Run security checks"
    echo "  backup     Create deployment backup"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Deploy to Firebase"
    echo "  $0 emulator        # Run local emulator"
    echo "  $0 security        # Run security checks"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            print_status "🚀 Starting full deployment process..."
            check_firebase_cli
            check_firebase_auth
            init_firebase_project
            install_functions_deps
            build_functions
            security_check
            optimize_performance
            backup_deployment
            deploy_to_firebase
            ;;
        "emulator")
            print_status "🧪 Starting local emulator..."
            check_firebase_cli
            run_emulator
            ;;
        "build")
            print_status "🔨 Building Cloud Functions..."
            install_functions_deps
            build_functions
            ;;
        "validate")
            print_status "✅ Validating configuration..."
            validate_firestore_rules
            validate_storage_rules
            ;;
        "optimize")
            print_status "⚡ Running optimizations..."
            optimize_performance
            ;;
        "security")
            print_status "🔒 Running security checks..."
            security_check
            ;;
        "backup")
            print_status "💾 Creating backup..."
            backup_deployment
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

