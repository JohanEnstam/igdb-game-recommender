/**
 * IGDB Game Recommendation System - Cloud Functions Module Variables
 */

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "europe-west1"
}

variable "labels" {
  description = "A map of labels to apply to resources"
  type        = map(string)
  default     = {}
}

variable "storage_bucket" {
  description = "GCS bucket for Cloud Functions source code"
  type        = string
}

variable "raw_data_bucket" {
  description = "GCS bucket for raw IGDB data"
  type        = string
}

variable "processed_data_bucket" {
  description = "GCS bucket for processed IGDB data"
  type        = string
}

variable "bigquery_dataset" {
  description = "BigQuery dataset ID"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for Cloud Functions"
  type        = string
}

variable "data_cleaning_function_source_zip" {
  description = "Path to the zipped source code for the data cleaning function"
  type        = string
  default     = "../data-pipeline/cloud_functions/data_cleaning_pipeline.zip"
}

variable "igdb_ingest_function_source_zip" {
  description = "Path to the zipped source code for the IGDB API ingest function"
  type        = string
  default     = "../data-pipeline/cloud_functions/igdb_ingest.zip"
}

variable "etl_processor_function_source_zip" {
  description = "Path to the zipped source code for the ETL processor function"
  type        = string
  default     = "../data-pipeline/cloud_functions/etl_processor.zip"
}

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