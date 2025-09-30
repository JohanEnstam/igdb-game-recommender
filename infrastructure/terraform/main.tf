/**
 * IGDB Game Recommendation System - Terraform Configuration
 * 
 * This file serves as the main entry point for Terraform configuration.
 * It sets up providers, backend, and includes all necessary modules.
 */

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.0"
    }
  }

  backend "gcs" {
    # Will be set from environment-specific tfvars
    bucket = "igdb-terraform-state"
    prefix = "terraform/state"
  }

  required_version = ">= 1.0.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Local variables for resource naming and tagging
locals {
  environment = var.environment
  labels = {
    environment = var.environment
    project     = "igdb-recommender"
    managed-by  = "terraform"
  }
}

# IAM Module - Sets up service accounts and permissions
module "iam" {
  source      = "./modules/iam"
  project_id  = var.project_id
  environment = local.environment
  labels      = local.labels
}

# Storage Module - Sets up GCS buckets
module "storage" {
  source      = "./modules/storage"
  project_id  = var.project_id
  environment = local.environment
  labels      = local.labels
  region      = var.region
}

# BigQuery Module - Sets up datasets and tables
module "bigquery" {
  source      = "./modules/bigquery"
  project_id  = var.project_id
  environment = local.environment
  labels      = local.labels
  region      = var.region
}

# Pub/Sub Module - Sets up topics and subscriptions
module "pubsub" {
  source      = "./modules/pubsub"
  project_id  = var.project_id
  environment = local.environment
  labels      = local.labels
}

# Cloud Functions Module - Sets up serverless functions
module "cloud_functions" {
  source                = "./modules/cloud_functions"
  project_id            = var.project_id
  environment           = local.environment
  labels                = local.labels
  region                = var.region
  service_account_email = module.iam.cloud_functions_service_account_email
  storage_bucket        = module.storage.functions_source_bucket
  raw_data_bucket       = module.storage.raw_data_bucket
  processed_data_bucket = module.storage.processed_data_bucket
  bigquery_dataset      = module.bigquery.dataset_id
  igdb_client_id        = var.igdb_client_id
  igdb_client_secret    = var.igdb_client_secret
  
  # Path to function source code zips
  data_cleaning_function_source_zip = var.data_cleaning_function_source_zip
  igdb_ingest_function_source_zip   = var.igdb_ingest_function_source_zip
  etl_processor_function_source_zip = var.etl_processor_function_source_zip
}

# Cloud SQL Module - Sets up PostgreSQL database
module "cloud_sql" {
  source        = "./modules/cloud_sql"
  project_id    = var.project_id
  environment   = local.environment
  labels        = local.labels
  region        = var.region
  instance_name = var.db_instance_name
}

# Vertex AI Module - Sets up ML infrastructure for batch pipelines
module "vertex_ai" {
  source                = "./modules/vertex_ai"
  project_id            = var.project_id
  environment           = local.environment
  labels                = local.labels
  region                = var.region
  service_account_email = module.iam.vertex_ai_service_account_email
  storage_bucket        = module.storage.model_artifacts_bucket
  bigquery_dataset      = module.bigquery.dataset_id
}

# Cloud Run Module - Sets up API service and batch jobs
module "cloud_run" {
  source                = "./modules/cloud_run"
  project_id            = var.project_id
  environment           = local.environment
  labels                = local.labels
  region                = var.region
  service_account_email = module.iam.cloud_run_service_account_email
  storage_bucket        = module.storage.model_artifacts_bucket
  bigquery_dataset      = module.bigquery.dataset_id
}

# Monitoring Module - Sets up logging, metrics, and alerting
module "monitoring" {
  source      = "./modules/monitoring"
  project_id  = var.project_id
  environment = local.environment
  labels      = local.labels
}