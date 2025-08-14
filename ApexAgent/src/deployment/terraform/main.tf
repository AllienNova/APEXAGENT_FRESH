/**
 * ApexAgent Infrastructure as Code - Main Terraform Configuration
 * 
 * This module provides a multi-cloud deployment infrastructure for ApexAgent
 * with support for AWS, GCP, and Azure cloud providers.
 */

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
  
  backend "s3" {
    # Will be configured via backend-config during initialization
    # terraform init -backend-config=backend-${environment}.hcl
  }
}

# Provider configuration will be loaded from environment variables or provider-specific config files
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "ApexAgent"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}

# Kubernetes provider will be configured after cluster creation
provider "kubernetes" {
  # Configuration will be injected by the module outputs
}

provider "helm" {
  # Configuration will be injected by the module outputs
}

# Load modules based on enabled providers
module "aws_infrastructure" {
  source = "./modules/aws"
  count  = var.enable_aws ? 1 : 0
  
  environment         = var.environment
  vpc_cidr            = var.aws_vpc_cidr
  availability_zones  = var.aws_availability_zones
  cluster_name        = "apexagent-${var.environment}"
  node_instance_type  = var.aws_node_instance_type
  min_nodes           = var.min_nodes
  max_nodes           = var.max_nodes
  domain_name         = var.domain_name
  certificate_arn     = var.aws_certificate_arn
}

module "gcp_infrastructure" {
  source = "./modules/gcp"
  count  = var.enable_gcp ? 1 : 0
  
  environment        = var.environment
  project_id         = var.gcp_project_id
  region             = var.gcp_region
  zones              = var.gcp_zones
  cluster_name       = "apexagent-${var.environment}"
  machine_type       = var.gcp_machine_type
  min_nodes          = var.min_nodes
  max_nodes          = var.max_nodes
  domain_name        = var.domain_name
}

module "azure_infrastructure" {
  source = "./modules/azure"
  count  = var.enable_azure ? 1 : 0
  
  environment        = var.environment
  location           = var.azure_location
  resource_group     = "apexagent-${var.environment}"
  kubernetes_version = var.azure_kubernetes_version
  vm_size            = var.azure_vm_size
  min_node_count     = var.min_nodes
  max_node_count     = var.max_nodes
  domain_name        = var.domain_name
}

# Common monitoring and observability stack
module "monitoring" {
  source = "./modules/monitoring"
  
  environment = var.environment
  
  # Conditionally use the appropriate cluster based on enabled providers
  cluster_endpoint = coalesce(
    var.enable_aws ? module.aws_infrastructure[0].cluster_endpoint : "",
    var.enable_gcp ? module.gcp_infrastructure[0].cluster_endpoint : "",
    var.enable_azure ? module.azure_infrastructure[0].cluster_endpoint : ""
  )
  
  depends_on = [
    module.aws_infrastructure,
    module.gcp_infrastructure,
    module.azure_infrastructure
  ]
}

# Common database module
module "database" {
  source = "./modules/database"
  
  environment = var.environment
  engine      = var.db_engine
  version     = var.db_version
  size        = var.db_size
  
  # Use appropriate VPC/subnet based on enabled providers
  vpc_id = var.enable_aws ? module.aws_infrastructure[0].vpc_id : null
  
  depends_on = [
    module.aws_infrastructure,
    module.gcp_infrastructure,
    module.azure_infrastructure
  ]
}

# Common Redis module
module "redis" {
  source = "./modules/redis"
  
  environment = var.environment
  version     = var.redis_version
  size        = var.redis_size
  
  depends_on = [
    module.aws_infrastructure,
    module.gcp_infrastructure,
    module.azure_infrastructure
  ]
}

# Application deployment module
module "application" {
  source = "./modules/application"
  
  environment     = var.environment
  image_tag       = var.image_tag
  replicas        = var.replicas
  cpu_request     = var.cpu_request
  memory_request  = var.memory_request
  cpu_limit       = var.cpu_limit
  memory_limit    = var.memory_limit
  
  # Database and Redis connection information
  database_url    = module.database.connection_string
  redis_url       = module.redis.connection_string
  
  depends_on = [
    module.database,
    module.redis,
    module.monitoring
  ]
}

# Outputs
output "aws_cluster_name" {
  value = var.enable_aws ? module.aws_infrastructure[0].cluster_name : null
}

output "gcp_cluster_name" {
  value = var.enable_gcp ? module.gcp_infrastructure[0].cluster_name : null
}

output "azure_cluster_name" {
  value = var.enable_azure ? module.azure_infrastructure[0].cluster_name : null
}

output "application_url" {
  value = "https://${var.domain_name}"
}

output "monitoring_url" {
  value = module.monitoring.grafana_url
}
