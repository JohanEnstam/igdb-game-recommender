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

# Vertex AI Workbench for development and experimentation (optional)
resource "google_vertex_ai_workbench_instance" "ml_workbench" {
  count = var.environment == "dev" ? 1 : 0
  
  name     = "igdb-ml-workbench-${var.environment}"
  location = var.region
  project  = var.project_id

  gce_setup {
    machine_type = "e2-standard-4"
    
    boot_disk {
      disk_size_gb = 100
      disk_type    = "PD_STANDARD"
    }
    
    data_disks {
      disk_size_gb = 100
      disk_type    = "PD_STANDARD"
    }
  }

  labels = var.labels
}

# Vertex AI Pipeline for batch feature extraction (when needed)
resource "google_vertex_ai_pipeline" "feature_extraction_pipeline" {
  name     = "igdb-feature-extraction-pipeline-${var.environment}"
  location = var.region
  project  = var.project_id

  # Pipeline definition will be uploaded separately
  # This is a placeholder for the pipeline resource
  
  labels = var.labels
}

# Vertex AI Model Registry for versioning (optional, for future use)
resource "google_vertex_ai_model" "recommendation_model" {
  count = 0  # Disabled for now, can be enabled when needed
  
  name     = "igdb-recommendation-model-${var.environment}"
  location = var.region
  project  = var.project_id

  display_name = "IGDB Recommendation Model (${var.environment})"
  description  = "Content-based recommendation model for IGDB games"

  labels = var.labels
}

# Outputs
output "workbench_instance_name" {
  description = "Name of the Vertex AI Workbench instance (dev only)"
  value       = var.environment == "dev" ? google_vertex_ai_workbench_instance.ml_workbench[0].name : null
}

output "pipeline_name" {
  description = "Name of the Vertex AI pipeline"
  value       = google_vertex_ai_pipeline.feature_extraction_pipeline.name
}

output "status" {
  description = "Status of the Vertex AI module"
  value       = "Implemented for batch pipelines and development workbench"
}
