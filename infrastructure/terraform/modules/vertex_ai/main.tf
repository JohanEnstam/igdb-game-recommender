/**
 * IGDB Game Recommendation System - Vertex AI Module
 * 
 * This module sets up Vertex AI resources for batch pipelines only.
 * Focuses on cost-effective batch processing without constant costs.
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

variable "service_account_email" {
  description = "Service account email for Vertex AI"
  type        = string
}

variable "storage_bucket" {
  description = "Cloud Storage bucket for model artifacts"
  type        = string
}

variable "bigquery_dataset" {
  description = "BigQuery dataset for training data"
  type        = string
}

# Enable Vertex AI API for future use
resource "google_project_service" "vertex_ai_api" {
  project = var.project_id
  service = "aiplatform.googleapis.com"
  
  disable_on_destroy = false
}

# Vertex AI Workbench for development and experimentation (optional)
# Note: google_notebooks_instance is deprecated, using Vertex AI Workbench instead
# For now, we'll skip the workbench to focus on the main pipeline

# Outputs
output "status" {
  description = "Status of the Vertex AI module"
  value       = "Simplified for Cloud Run + batch jobs architecture"
}
