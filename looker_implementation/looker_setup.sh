#!/bin/bash
# Looker Setup Script for Aideon AI Lite
# This script automates the setup of Looker instance in GCP

# Set environment variables
export PROJECT_ID="aideon-ai-lite"
export REGION="us-central1"
export LOOKER_INSTANCE_NAME="aideon-looker"
export NETWORK="default"
export DB_CONNECTION_NAME="aideon-bigquery"

echo "Starting Looker setup for Aideon AI Lite..."

# 1. Create Looker instance in GCP
echo "Creating Looker instance in GCP..."
gcloud looker instances create $LOOKER_INSTANCE_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --network=$NETWORK \
  --oauth-client-id=${OAUTH_CLIENT_ID} \
  --oauth-client-secret=${OAUTH_CLIENT_SECRET}

# 2. Configure networking and security settings
echo "Configuring networking and security settings..."
gcloud looker instances update $LOOKER_INSTANCE_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --allowed-ip-ranges="0.0.0.0/0" \
  --enable-maintenance-window \
  --maintenance-window-day=SUNDAY \
  --maintenance-window-time=02:00 \
  --maintenance-window-duration=3h

# 3. Set up database connection to BigQuery
echo "Setting up BigQuery connection..."
gcloud looker connections create $DB_CONNECTION_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --instance=$LOOKER_INSTANCE_NAME \
  --database-type=bigquery \
  --host=$PROJECT_ID \
  --username=service-account \
  --password-secret=looker-bigquery-key

echo "Looker setup completed successfully!"
echo "Access your Looker instance at: https://$REGION-$PROJECT_ID.looker.app"
