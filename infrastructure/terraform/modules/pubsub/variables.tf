/**
 * IGDB Game Recommendation System - Pub/Sub Module Variables
 */

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "labels" {
  description = "A map of labels to apply to resources"
  type        = map(string)
  default     = {}
}

variable "data_ingestion_topic_name" {
  description = "Name of the Pub/Sub topic for data ingestion events"
  type        = string
  default     = "igdb-data-ingestion"
}

variable "etl_processing_topic_name" {
  description = "Name of the Pub/Sub topic for ETL processing events"
  type        = string
  default     = "igdb-etl-processing"
}

variable "model_training_topic_name" {
  description = "Name of the Pub/Sub topic for model training events"
  type        = string
  default     = "igdb-model-training"
}
