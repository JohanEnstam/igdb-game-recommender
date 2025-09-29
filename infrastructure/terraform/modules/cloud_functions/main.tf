/**
 * IGDB Game Recommendation System - Cloud Functions Module
 * 
 * This module sets up Cloud Functions for data processing.
 */

# Cloud Function for data cleaning pipeline
resource "google_cloudfunctions_function" "data_cleaning_pipeline" {
  name        = "data-cleaning-pipeline-${var.environment}"
  description = "Function to run the data cleaning pipeline on IGDB game data"
  runtime     = "python39"

  available_memory_mb   = 2048
  source_archive_bucket = var.storage_bucket
  source_archive_object = google_storage_bucket_object.data_cleaning_function_zip.name
  timeout               = 540  # 9 minutes
  entry_point           = "process_data"
  
  environment_variables = {
    PROJECT_ID = var.project_id
    ENVIRONMENT = var.environment
    RAW_DATA_BUCKET = var.raw_data_bucket
    PROCESSED_DATA_BUCKET = var.processed_data_bucket
    BIGQUERY_DATASET = var.bigquery_dataset
  }

  event_trigger {
    event_type = "google.storage.object.finalize"
    resource   = var.raw_data_bucket
  }

  labels = var.labels
  service_account_email = var.service_account_email
}

# Cloud Function for IGDB API data ingestion
resource "google_cloudfunctions_function" "igdb_api_ingest" {
  name        = "igdb-api-ingest-${var.environment}"
  description = "Function to fetch data from IGDB API"
  runtime     = "python39"

  available_memory_mb   = 1024
  source_archive_bucket = var.storage_bucket
  source_archive_object = google_storage_bucket_object.igdb_ingest_function_zip.name
  timeout               = 540  # 9 minutes
  entry_point           = "fetch_igdb_data"
  
  environment_variables = {
    PROJECT_ID = var.project_id
    ENVIRONMENT = var.environment
    RAW_DATA_BUCKET = var.raw_data_bucket
    IGDB_CLIENT_ID = var.igdb_client_id
    IGDB_CLIENT_SECRET = var.igdb_client_secret
  }

  # This function will be triggered by Pub/Sub or Cloud Scheduler
  trigger_http = true

  labels = var.labels
  service_account_email = var.service_account_email
}

# Cloud Function for ETL processing
resource "google_cloudfunctions_function" "etl_processor" {
  name        = "etl-processor-${var.environment}"
  description = "Function to load processed data into BigQuery"
  runtime     = "python39"

  available_memory_mb   = 1024
  source_archive_bucket = var.storage_bucket
  source_archive_object = google_storage_bucket_object.etl_processor_function_zip.name
  timeout               = 540  # 9 minutes
  entry_point           = "load_to_bigquery"
  
  environment_variables = {
    PROJECT_ID = var.project_id
    ENVIRONMENT = var.environment
    PROCESSED_DATA_BUCKET = var.processed_data_bucket
    BIGQUERY_DATASET = var.bigquery_dataset
  }

  event_trigger {
    event_type = "google.storage.object.finalize"
    resource   = var.processed_data_bucket
  }

  labels = var.labels
  service_account_email = var.service_account_email
}

# Zip files for Cloud Functions
resource "google_storage_bucket_object" "data_cleaning_function_zip" {
  name   = "functions/data_cleaning_pipeline_${formatdate("YYYYMMDDhhmmss", timestamp())}.zip"
  bucket = var.storage_bucket
  source = var.data_cleaning_function_source_zip

  # This will change when the file changes
  content_type = "application/zip"
}

resource "google_storage_bucket_object" "igdb_ingest_function_zip" {
  name   = "functions/igdb_ingest_${formatdate("YYYYMMDDhhmmss", timestamp())}.zip"
  bucket = var.storage_bucket
  source = var.igdb_ingest_function_source_zip

  # This will change when the file changes
  content_type = "application/zip"
}

resource "google_storage_bucket_object" "etl_processor_function_zip" {
  name   = "functions/etl_processor_${formatdate("YYYYMMDDhhmmss", timestamp())}.zip"
  bucket = var.storage_bucket
  source = var.etl_processor_function_source_zip

  # This will change when the file changes
  content_type = "application/zip"
}