/**
 * IGDB Game Recommendation System - IAM Module
 * 
 * This module sets up service accounts and IAM permissions.
 */

# Create service account for Cloud Functions
resource "google_service_account" "cloud_functions" {
  account_id   = "igdb-cloud-functions-${var.environment}"
  display_name = "IGDB Cloud Functions Service Account (${var.environment})"
  description  = "Service account for Cloud Functions in the IGDB Game Recommendation System"
  project      = var.project_id
}

# Create service account for Cloud Run
resource "google_service_account" "cloud_run" {
  account_id   = "igdb-cloud-run-${var.environment}"
  display_name = "IGDB Cloud Run Service Account (${var.environment})"
  description  = "Service account for Cloud Run in the IGDB Game Recommendation System"
  project      = var.project_id
}

# Create service account for Vertex AI
resource "google_service_account" "vertex_ai" {
  account_id   = "igdb-vertex-ai-${var.environment}"
  display_name = "IGDB Vertex AI Service Account (${var.environment})"
  description  = "Service account for Vertex AI in the IGDB Game Recommendation System"
  project      = var.project_id
}

# Grant BigQuery Data Editor role to Cloud Functions service account
resource "google_project_iam_member" "cloud_functions_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.cloud_functions.email}"
}

# Grant Storage Object Admin role to Cloud Functions service account
resource "google_project_iam_member" "cloud_functions_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.cloud_functions.email}"
}

# Grant Pub/Sub Publisher role to Cloud Functions service account
resource "google_project_iam_member" "cloud_functions_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.cloud_functions.email}"
}

# Grant BigQuery Data Viewer role to Cloud Run service account
resource "google_project_iam_member" "cloud_run_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Grant Cloud SQL Client role to Cloud Run service account
resource "google_project_iam_member" "cloud_run_cloudsql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Grant Vertex AI User role to Cloud Run service account
resource "google_project_iam_member" "cloud_run_vertexai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Grant BigQuery Data Editor role to Vertex AI service account
resource "google_project_iam_member" "vertex_ai_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.vertex_ai.email}"
}

# Grant Storage Object Admin role to Vertex AI service account
resource "google_project_iam_member" "vertex_ai_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.vertex_ai.email}"
}
