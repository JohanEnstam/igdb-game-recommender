/**
 * IGDB Game Recommendation System - Storage Module
 * 
 * This module sets up Cloud Storage buckets.
 */

# Bucket for raw IGDB data
resource "google_storage_bucket" "raw_data" {
  name          = "${var.raw_data_bucket_name}-${var.environment}"
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
  
  labels = var.labels
}

# Bucket for processed IGDB data
resource "google_storage_bucket" "processed_data" {
  name          = "${var.processed_data_bucket_name}-${var.environment}"
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
  
  labels = var.labels
}

# Bucket for ML model artifacts
resource "google_storage_bucket" "model_artifacts" {
  name          = "${var.model_artifacts_bucket_name}-${var.environment}"
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  labels = var.labels
}

# Bucket for Cloud Functions source code
resource "google_storage_bucket" "functions_source" {
  name          = "${var.functions_source_bucket_name}-${var.environment}"
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  labels = var.labels
}