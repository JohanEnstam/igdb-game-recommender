/**
 * IGDB Game Recommendation System - Cloud Run Module
 * 
 * This module sets up Cloud Run services.
 * Currently a placeholder for future API components.
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

variable "service_account_email" {
  description = "Service account email for Cloud Run"
  type        = string
}

# This is a placeholder module for future Cloud Run resources
# Will be implemented in the web app phase

output "status" {
  description = "Status of the Cloud Run module"
  value       = "Placeholder module - will be implemented in the web app phase"
}
