/**
 * ApexAgent Infrastructure as Code - Variables
 * 
 * This file defines all variables used in the Terraform configuration
 * for multi-cloud deployment of ApexAgent.
 */

# General variables
variable "environment" {
  description = "Environment name (e.g., dev, staging, production)"
  type        = string
  default     = "dev"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "apexagent.example.com"
}

variable "min_nodes" {
  description = "Minimum number of nodes in the cluster"
  type        = number
  default     = 2
}

variable "max_nodes" {
  description = "Maximum number of nodes in the cluster"
  type        = number
  default     = 10
}

# Provider enablement
variable "enable_aws" {
  description = "Enable AWS infrastructure deployment"
  type        = bool
  default     = true
}

variable "enable_gcp" {
  description = "Enable GCP infrastructure deployment"
  type        = bool
  default     = false
}

variable "enable_azure" {
  description = "Enable Azure infrastructure deployment"
  type        = bool
  default     = false
}

# AWS specific variables
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-west-2"
}

variable "aws_vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "aws_availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "aws_node_instance_type" {
  description = "EC2 instance type for EKS nodes"
  type        = string
  default     = "t3.medium"
}

variable "aws_certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS"
  type        = string
  default     = ""
}

# GCP specific variables
variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
  default     = ""
}

variable "gcp_region" {
  description = "GCP region to deploy resources"
  type        = string
  default     = "us-central1"
}

variable "gcp_zones" {
  description = "List of GCP zones to use"
  type        = list(string)
  default     = ["us-central1-a", "us-central1-b", "us-central1-c"]
}

variable "gcp_machine_type" {
  description = "GCP machine type for GKE nodes"
  type        = string
  default     = "e2-standard-2"
}

# Azure specific variables
variable "azure_location" {
  description = "Azure location to deploy resources"
  type        = string
  default     = "eastus"
}

variable "azure_kubernetes_version" {
  description = "Kubernetes version for AKS"
  type        = string
  default     = "1.25.5"
}

variable "azure_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_DS2_v2"
}

# Database variables
variable "db_engine" {
  description = "Database engine (postgres, mysql)"
  type        = string
  default     = "postgres"
}

variable "db_version" {
  description = "Database engine version"
  type        = string
  default     = "14"
}

variable "db_size" {
  description = "Database instance size"
  type        = string
  default     = "small"
}

# Redis variables
variable "redis_version" {
  description = "Redis version"
  type        = string
  default     = "6.2"
}

variable "redis_size" {
  description = "Redis instance size"
  type        = string
  default     = "small"
}

# Application variables
variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "replicas" {
  description = "Number of application replicas"
  type        = number
  default     = 3
}

variable "cpu_request" {
  description = "CPU request for application containers"
  type        = string
  default     = "100m"
}

variable "memory_request" {
  description = "Memory request for application containers"
  type        = string
  default     = "256Mi"
}

variable "cpu_limit" {
  description = "CPU limit for application containers"
  type        = string
  default     = "500m"
}

variable "memory_limit" {
  description = "Memory limit for application containers"
  type        = string
  default     = "512Mi"
}
