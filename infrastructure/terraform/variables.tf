/**
 * IGDB Game Recommendation System - Terraform Variables
 * 
 * This file defines all variables used across the Terraform configuration.
 */

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "The GCP zone for zonal resources"
  type        = string
  default     = "europe-west1-b"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

# BigQuery variables
variable "bigquery_dataset_id" {
  description = "The BigQuery dataset ID"
  type        = string
  default     = "igdb_games"
}

variable "bigquery_location" {
  description = "The BigQuery dataset location"
  type        = string
  default     = "EU"
}

# Storage variables
variable "raw_data_bucket_name" {
  description = "Name of the bucket for raw IGDB data"
  type        = string
  default     = "igdb-raw-data"
}

variable "processed_data_bucket_name" {
  description = "Name of the bucket for processed IGDB data"
  type        = string
  default     = "igdb-processed-data"
}

variable "model_artifacts_bucket_name" {
  description = "Name of the bucket for ML model artifacts"
  type        = string
  default     = "igdb-model-artifacts"
}

variable "functions_source_bucket_name" {
  description = "Name of the bucket for Cloud Functions source code"
  type        = string
  default     = "igdb-functions-source"
}

# Pub/Sub variables
variable "data_ingestion_topic_name" {
  description = "Name of the Pub/Sub topic for data ingestion events"
  type        = string
  default     = "igdb-data-ingestion"
}

variable "etl_processing_topic_name" {
  description = "Name of the Pub/Sub topic for ETL processing events"
  type        = string
  default     = "igdb-etl-processing"
}

variable "model_training_topic_name" {
  description = "Name of the Pub/Sub topic for model training events"
  type        = string
  default     = "igdb-model-training"
}

# Cloud SQL variables
variable "db_instance_name" {
  description = "Name of the Cloud SQL instance"
  type        = string
  default     = "igdb-postgres"
}

variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "igdb_games"
}

variable "db_user" {
  description = "Database user"
  type        = string
  default     = "igdb_app"
}

# Cloud Run variables
variable "api_service_name" {
  description = "Name of the Cloud Run API service"
  type        = string
  default     = "igdb-api"
}

variable "api_container_port" {
  description = "Port the API container listens on"
  type        = number
  default     = 8000
}

# Vertex AI variables
variable "model_display_name" {
  description = "Display name for the ML model"
  type        = string
  default     = "igdb-recommendation-model"
}

# Monitoring variables
variable "alert_notification_email" {
  description = "Email address for alert notifications"
  type        = string
  default     = "admin@example.com"
}

# IGDB API variables
variable "igdb_client_id" {
  description = "IGDB API Client ID"
  type        = string
  sensitive   = true
}

variable "igdb_client_secret" {
  description = "IGDB API Client Secret"
  type        = string
  sensitive   = true
}

# Cloud Functions source code paths
variable "data_cleaning_function_source_zip" {
  description = "Path to the zipped source code for the data cleaning function"
  type        = string
  default     = "../data-pipeline/data_cleaning_pipeline.zip"
}

variable "igdb_ingest_function_source_zip" {
  description = "Path to the zipped source code for the IGDB API ingest function"
  type        = string
  default     = "../data-pipeline/igdb_ingest.zip"
}

variable "etl_processor_function_source_zip" {
  description = "Path to the zipped source code for the ETL processor function"
  type        = string
  default     = "../data-pipeline/etl_processor.zip"
}