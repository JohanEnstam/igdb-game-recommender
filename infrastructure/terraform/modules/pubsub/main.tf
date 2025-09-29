/**
 * IGDB Game Recommendation System - Pub/Sub Module
 * 
 * This module sets up Pub/Sub topics and subscriptions.
 */

# Create data ingestion topic
resource "google_pubsub_topic" "data_ingestion" {
  name    = "${var.data_ingestion_topic_name}-${var.environment}"
  project = var.project_id
  
  labels = var.labels
  
  message_retention_duration = "86600s"  # 24 hours + 10 minutes
}

# Create ETL processing topic
resource "google_pubsub_topic" "etl_processing" {
  name    = "${var.etl_processing_topic_name}-${var.environment}"
  project = var.project_id
  
  labels = var.labels
  
  message_retention_duration = "86600s"  # 24 hours + 10 minutes
}

# Create model training topic
resource "google_pubsub_topic" "model_training" {
  name    = "${var.model_training_topic_name}-${var.environment}"
  project = var.project_id
  
  labels = var.labels
  
  message_retention_duration = "86600s"  # 24 hours + 10 minutes
}

# Create subscription for data ingestion topic
resource "google_pubsub_subscription" "data_ingestion_sub" {
  name    = "${var.data_ingestion_topic_name}-sub-${var.environment}"
  topic   = google_pubsub_topic.data_ingestion.name
  project = var.project_id
  
  labels = var.labels
  
  ack_deadline_seconds = 60
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  
  expiration_policy {
    ttl = "2592000s"  # 30 days
  }
}

# Create subscription for ETL processing topic
resource "google_pubsub_subscription" "etl_processing_sub" {
  name    = "${var.etl_processing_topic_name}-sub-${var.environment}"
  topic   = google_pubsub_topic.etl_processing.name
  project = var.project_id
  
  labels = var.labels
  
  ack_deadline_seconds = 60
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  
  expiration_policy {
    ttl = "2592000s"  # 30 days
  }
}

# Create subscription for model training topic
resource "google_pubsub_subscription" "model_training_sub" {
  name    = "${var.model_training_topic_name}-sub-${var.environment}"
  topic   = google_pubsub_topic.model_training.name
  project = var.project_id
  
  labels = var.labels
  
  ack_deadline_seconds = 60
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  
  expiration_policy {
    ttl = "2592000s"  # 30 days
  }
}
