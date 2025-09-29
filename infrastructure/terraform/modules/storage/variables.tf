/**
 * IGDB Game Recommendation System - Storage Module Variables
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
}

variable "labels" {
  description = "A map of labels to apply to resources"
  type        = map(string)
  default     = {}
}

variable "raw_data_bucket_name" {
  description = "Name of the bucket for raw IGDB data"
  type        = string
  default     = "igdb-raw-data"
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
