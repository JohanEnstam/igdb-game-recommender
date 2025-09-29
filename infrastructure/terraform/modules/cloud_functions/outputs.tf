/**
 * IGDB Game Recommendation System - Cloud Functions Module Outputs
 */

output "data_cleaning_function_name" {
  description = "Name of the data cleaning Cloud Function"
  value       = google_cloudfunctions_function.data_cleaning_pipeline.name
}

output "igdb_ingest_function_name" {
  description = "Name of the IGDB API ingest Cloud Function"
  value       = google_cloudfunctions_function.igdb_api_ingest.name
}

output "etl_processor_function_name" {
  description = "Name of the ETL processor Cloud Function"
  value       = google_cloudfunctions_function.etl_processor.name
}

output "igdb_ingest_function_url" {
  description = "URL for the IGDB API ingest Cloud Function"
  value       = google_cloudfunctions_function.igdb_api_ingest.https_trigger_url
}

output "function_details" {
  description = "Map of function details"
  value = {
    data_cleaning = {
      name = google_cloudfunctions_function.data_cleaning_pipeline.name
      trigger_type = "Storage"
      trigger_resource = var.raw_data_bucket
    }
    igdb_ingest = {
      name = google_cloudfunctions_function.igdb_api_ingest.name
      trigger_type = "HTTP"
      url = google_cloudfunctions_function.igdb_api_ingest.https_trigger_url
    }
    etl_processor = {
      name = google_cloudfunctions_function.etl_processor.name
      trigger_type = "Storage"
      trigger_resource = var.processed_data_bucket
    }
  }
}