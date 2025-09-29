/**
 * IGDB Game Recommendation System - Storage Module Outputs
 */

output "raw_data_bucket" {
  description = "Bucket for raw IGDB data"
  value       = google_storage_bucket.raw_data.name
}

output "model_artifacts_bucket" {
  description = "Bucket for ML model artifacts"
  value       = google_storage_bucket.model_artifacts.name
}

output "functions_source_bucket" {
  description = "Bucket for Cloud Functions source code"
  value       = google_storage_bucket.functions_source.name
}
