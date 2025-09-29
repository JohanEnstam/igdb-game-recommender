/**
 * IGDB Game Recommendation System - BigQuery Module Variables
 */

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
}

variable "labels" {
  description = "A map of labels to apply to resources"
  type        = map(string)
  default     = {}
}

variable "bigquery_dataset_id" {
  description = "The BigQuery dataset ID"
  type        = string
  default     = "igdb_games"
}

variable "bigquery_location" {
  description = "The BigQuery dataset location"
  type        = string
  default     = "EU"
}
