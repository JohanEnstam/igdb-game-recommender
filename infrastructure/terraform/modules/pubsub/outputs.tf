/**
 * IGDB Game Recommendation System - Pub/Sub Module Outputs
 */

output "data_ingestion_topic_id" {
  description = "Pub/Sub topic ID for data ingestion events"
  value       = google_pubsub_topic.data_ingestion.id
}

output "etl_processing_topic_id" {
  description = "Pub/Sub topic ID for ETL processing events"
  value       = google_pubsub_topic.etl_processing.id
}

output "model_training_topic_id" {
  description = "Pub/Sub topic ID for model training events"
  value       = google_pubsub_topic.model_training.id
}

output "data_ingestion_subscription_id" {
  description = "Pub/Sub subscription ID for data ingestion events"
  value       = google_pubsub_subscription.data_ingestion_sub.id
}

output "etl_processing_subscription_id" {
  description = "Pub/Sub subscription ID for ETL processing events"
  value       = google_pubsub_subscription.etl_processing_sub.id
}

output "model_training_subscription_id" {
  description = "Pub/Sub subscription ID for model training events"
  value       = google_pubsub_subscription.model_training_sub.id
}