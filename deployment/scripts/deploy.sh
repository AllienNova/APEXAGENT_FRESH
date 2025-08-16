#!/bin/bash
# ApexAgent Deployment Script
echo "Starting ApexAgent deployment..."
cd "$(dirname "$0")/../.."
echo "Building frontend..."
cd core/frontend && npm install && npm run build
echo "Setting up backend..."
cd ../backend && pip install -r requirements.txt
echo "Deployment completed successfully!"
