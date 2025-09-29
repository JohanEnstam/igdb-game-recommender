/**
 * IGDB Game Recommendation System - Storage Module Outputs
 */

output "raw_data_bucket" {
  description = "Bucket for raw IGDB data"
  value       = google_storage_bucket.raw_data.name
}

output "processed_data_bucket" {
  description = "Bucket for processed IGDB data"
  value       = google_storage_bucket.processed_data.name
}

output "model_artifacts_bucket" {
  description = "Bucket for ML model artifacts"
  value       = google_storage_bucket.model_artifacts.name
}

output "functions_source_bucket" {
  description = "Bucket for Cloud Functions source code"
  value       = google_storage_bucket.functions_source.name
}

output "bucket_urls" {
  description = "Map of bucket URLs"
  value = {
    raw_data = "gs://${google_storage_bucket.raw_data.name}"
    processed_data = "gs://${google_storage_bucket.processed_data.name}"
    model_artifacts = "gs://${google_storage_bucket.model_artifacts.name}"
    functions_source = "gs://${google_storage_bucket.functions_source.name}"
  }
}