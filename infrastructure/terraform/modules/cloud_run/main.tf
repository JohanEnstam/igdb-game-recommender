/**
 * IGDB Game Recommendation System - Cloud Run Module
 * 
 * This module sets up Cloud Run services for API serving and batch jobs.
 * Focuses on cost-effective, serverless architecture with scale-to-zero capability.
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
  description = "Service account email for Cloud Run"
  type        = string
}

variable "storage_bucket" {
  description = "Cloud Storage bucket for features and models"
  type        = string
}

variable "bigquery_dataset" {
  description = "BigQuery dataset for game data"
  type        = string
}

# Cloud Run service for recommendation API
resource "google_cloud_run_v2_service" "recommendation_api" {
  name     = "igdb-recommendation-api-${var.environment}"
  location = var.region
  project  = var.project_id

  template {
    service_account = var.service_account_email
    
    containers {
      image = "gcr.io/${var.project_id}/igdb-recommendation-api:latest"
      
      ports {
        container_port = 8000
      }
      
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      
      env {
        name  = "STORAGE_BUCKET"
        value = var.storage_bucket
      }
      
      env {
        name  = "BIGQUERY_DATASET"
        value = var.bigquery_dataset
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  labels = var.labels
}

# Cloud Run job for feature extraction (batch processing)
resource "google_cloud_run_v2_job" "feature_extraction" {
  name     = "igdb-feature-extraction-${var.environment}"
  location = var.region
  project  = var.project_id

  template {
    template {
      service_account = var.service_account_email
      
      containers {
        image = "gcr.io/${var.project_id}/igdb-feature-extraction:latest"
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        env {
          name  = "STORAGE_BUCKET"
          value = var.storage_bucket
        }
        
        env {
          name  = "BIGQUERY_DATASET"
          value = var.bigquery_dataset
        }
        
        resources {
          limits = {
            cpu    = "4"
            memory = "8Gi"
          }
        }
      }
      
      timeout = "3600s"  # 1 hour timeout for feature extraction
    }
  }

  labels = var.labels
}

# IAM policy for Cloud Run service (public access for API)
resource "google_cloud_run_service_iam_policy" "recommendation_api_public" {
  location = google_cloud_run_v2_service.recommendation_api.location
  project  = google_cloud_run_v2_service.recommendation_api.project
  service  = google_cloud_run_v2_service.recommendation_api.name

  policy_data = data.google_iam_policy.public.policy_data
}

data "google_iam_policy" "public" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

# Outputs
output "recommendation_api_url" {
  description = "URL of the recommendation API service"
  value       = google_cloud_run_v2_service.recommendation_api.uri
}

output "feature_extraction_job_name" {
  description = "Name of the feature extraction job"
  value       = google_cloud_run_v2_job.feature_extraction.name
}

output "status" {
  description = "Status of the Cloud Run module"
  value       = "Implemented with API service and batch job"
}
