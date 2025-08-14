-- LookML Model for Aideon AI Lite Analytics
-- This file defines the core LookML model structure for Aideon analytics data

connection: "aideon-bigquery"

# Include all views in the views/ folder
include: "/views/*.view.lkml"

# Define the explores (entry points for queries)
explore: user_activity {
  label: "User Activity Analysis"
  description: "Analyze user interactions, session data, and feature usage"
  
  join: users {
    type: left_outer
    sql_on: ${user_activity.user_id} = ${users.id} ;;
    relationship: many_to_one
  }
  
  join: features {
    type: left_outer
    sql_on: ${user_activity.feature_id} = ${features.id} ;;
    relationship: many_to_one
  }
  
  join: sessions {
    type: left_outer
    sql_on: ${user_activity.session_id} = ${sessions.id} ;;
    relationship: many_to_one
  }
}

explore: model_performance {
  label: "AI Model Performance"
  description: "Analyze performance metrics for different AI models"
  
  join: models {
    type: left_outer
    sql_on: ${model_performance.model_id} = ${models.id} ;;
    relationship: many_to_one
  }
  
  join: providers {
    type: left_outer
    sql_on: ${models.provider_id} = ${providers.id} ;;
    relationship: many_to_one
  }
}

explore: system_metrics {
  label: "System Performance"
  description: "Analyze system performance, resource usage, and errors"
  
  join: error_logs {
    type: left_outer
    sql_on: ${system_metrics.id} = ${error_logs.system_metric_id} ;;
    relationship: one_to_many
  }
}

explore: business_metrics {
  label: "Business Metrics"
  description: "Analyze business KPIs, subscription data, and revenue metrics"
  
  join: subscriptions {
    type: left_outer
    sql_on: ${business_metrics.subscription_id} = ${subscriptions.id} ;;
    relationship: many_to_one
  }
  
  join: users {
    type: left_outer
    sql_on: ${subscriptions.user_id} = ${users.id} ;;
    relationship: many_to_one
  }
}
