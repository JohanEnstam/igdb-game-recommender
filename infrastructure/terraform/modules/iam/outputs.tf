/**
 * IGDB Game Recommendation System - IAM Module Outputs
 */

output "cloud_functions_service_account_email" {
  description = "Email of the service account used by Cloud Functions"
  value       = google_service_account.cloud_functions.email
}

output "cloud_run_service_account_email" {
  description = "Email of the service account used by Cloud Run"
  value       = google_service_account.cloud_run.email
}

output "vertex_ai_service_account_email" {
  description = "Email of the service account used by Vertex AI"
  value       = google_service_account.vertex_ai.email
}