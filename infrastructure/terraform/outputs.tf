/**
 * IGDB Game Recommendation System - Terraform Outputs
 * 
 * This file defines outputs that are useful for scripts, CI/CD, and documentation.
 */

# IAM outputs
output "cloud_functions_service_account_email" {
  description = "Email of the service account used by Cloud Functions"
  value       = module.iam.cloud_functions_service_account_email
}

output "cloud_run_service_account_email" {
  description = "Email of the service account used by Cloud Run"
  value       = module.iam.cloud_run_service_account_email
}

# Storage outputs
output "raw_data_bucket" {
  description = "Bucket for raw IGDB data"
  value       = module.storage.raw_data_bucket
}

output "processed_data_bucket" {
  description = "Bucket for processed IGDB data"
  value       = module.storage.processed_data_bucket
}

output "model_artifacts_bucket" {
  description = "Bucket for ML model artifacts"
  value       = module.storage.model_artifacts_bucket
}

output "functions_source_bucket" {
  description = "Bucket for Cloud Functions source code"
  value       = module.storage.functions_source_bucket
}

# BigQuery outputs
output "bigquery_dataset_id" {
  description = "BigQuery dataset ID"
  value       = module.bigquery.dataset_id
}

output "bigquery_raw_table_id" {
  description = "BigQuery raw games table ID"
  value       = module.bigquery.raw_table_id
}

output "bigquery_games_table_id" {
  description = "BigQuery cleaned games table ID"
  value       = module.bigquery.games_table_id
}

output "bigquery_relationships_table_id" {
  description = "BigQuery game relationships table ID"
  value       = module.bigquery.relationships_table_id
}

output "bigquery_groups_table_id" {
  description = "BigQuery game groups table ID"
  value       = module.bigquery.groups_table_id
}

# Pub/Sub outputs
output "data_ingestion_topic_id" {
  description = "Pub/Sub topic ID for data ingestion events"
  value       = module.pubsub.data_ingestion_topic_id
}

output "etl_processing_topic_id" {
  description = "Pub/Sub topic ID for ETL processing events"
  value       = module.pubsub.etl_processing_topic_id
}

output "model_training_topic_id" {
  description = "Pub/Sub topic ID for model training events"
  value       = module.pubsub.model_training_topic_id
}

# Cloud SQL outputs
output "cloud_sql_status" {
  description = "Status of the Cloud SQL module"
  value       = module.cloud_sql.status
}

# Cloud Run outputs
output "cloud_run_status" {
  description = "Status of the Cloud Run module"
  value       = module.cloud_run.status
}

# Vertex AI outputs
output "vertex_ai_status" {
  description = "Status of the Vertex AI module"
  value       = module.vertex_ai.status
}

# Monitoring outputs
output "monitoring_status" {
  description = "Status of the monitoring module"
  value       = module.monitoring.status
}

# Cloud Functions outputs
output "data_cleaning_function_name" {
  description = "Name of the data cleaning Cloud Function"
  value       = module.cloud_functions.data_cleaning_function_name
}

output "igdb_ingest_function_name" {
  description = "Name of the IGDB API ingest Cloud Function"
  value       = module.cloud_functions.igdb_ingest_function_name
}

output "etl_processor_function_name" {
  description = "Name of the ETL processor Cloud Function"
  value       = module.cloud_functions.etl_processor_function_name
}

output "igdb_ingest_function_url" {
  description = "URL for the IGDB API ingest Cloud Function"
  value       = module.cloud_functions.igdb_ingest_function_url
}