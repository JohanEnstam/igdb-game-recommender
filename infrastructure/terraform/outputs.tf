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

output "bigquery_staging_table_id" {
  description = "BigQuery staging table ID"
  value       = module.bigquery.staging_table_id
}

output "bigquery_production_table_id" {
  description = "BigQuery production table ID"
  value       = module.bigquery.production_table_id
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
output "db_instance_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = module.cloud_sql.instance_connection_name
}

output "db_instance_ip" {
  description = "Cloud SQL instance IP address"
  value       = module.cloud_sql.instance_ip_address
}

# Cloud Run outputs
output "api_service_url" {
  description = "URL of the Cloud Run API service"
  value       = module.cloud_run.service_url
}

# Vertex AI outputs
output "model_endpoint_id" {
  description = "ID of the Vertex AI model endpoint"
  value       = module.vertex_ai.endpoint_id
}

# Monitoring outputs
output "dashboard_url" {
  description = "URL of the monitoring dashboard"
  value       = module.monitoring.dashboard_url
}
