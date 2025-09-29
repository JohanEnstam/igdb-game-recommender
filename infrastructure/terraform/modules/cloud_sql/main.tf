/**
 * IGDB Game Recommendation System - Cloud SQL Module
 * 
 * This module sets up Cloud SQL instances.
 * Currently a placeholder for future database components.
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

variable "instance_name" {
  description = "Name of the Cloud SQL instance"
  type        = string
  default     = "igdb-postgres"
}

# This is a placeholder module for future Cloud SQL resources
# Will be implemented in the database phase

output "status" {
  description = "Status of the Cloud SQL module"
  value       = "Placeholder module - will be implemented in the database phase"
}