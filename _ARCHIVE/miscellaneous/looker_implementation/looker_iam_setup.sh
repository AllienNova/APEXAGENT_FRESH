#!/bin/bash
# Looker IAM Configuration Script for Aideon AI Lite
# This script sets up the necessary IAM roles and permissions for Looker

# Set environment variables
export PROJECT_ID="aideon-ai-lite"
export LOOKER_SA="looker-service-account@${PROJECT_ID}.iam.gserviceaccount.com"
export BIGQUERY_DATASET="aideon_analytics"

echo "Setting up IAM roles for Looker integration..."

# 1. Create service account for Looker
echo "Creating Looker service account..."
gcloud iam service-accounts create looker-service-account \
  --project=$PROJECT_ID \
  --display-name="Looker Service Account"

# 2. Assign BigQuery roles to the service account
echo "Assigning BigQuery roles..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${LOOKER_SA}" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${LOOKER_SA}" \
  --role="roles/bigquery.jobUser"

# 3. Grant dataset-specific permissions
echo "Granting dataset-specific permissions..."
bq add-iam-policy-binding \
  --member="serviceAccount:${LOOKER_SA}" \
  --role="roles/bigquery.dataViewer" \
  $BIGQUERY_DATASET

# 4. Create and download service account key
echo "Creating service account key..."
gcloud iam service-accounts keys create looker-sa-key.json \
  --iam-account=${LOOKER_SA}

# 5. Store key in Secret Manager
echo "Storing key in Secret Manager..."
gcloud secrets create looker-bigquery-key \
  --project=$PROJECT_ID \
  --replication-policy="automatic" \
  --data-file=looker-sa-key.json

# 6. Clean up local key file
echo "Cleaning up local key file..."
rm looker-sa-key.json

echo "IAM configuration completed successfully!"
