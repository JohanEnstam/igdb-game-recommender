/**
 * Cloud Functions Terraform Module
 * 
 * Detta är en modul för att hantera Cloud Functions i GCP.
 */

variable "project_id" {
  description = "GCP-projektets ID"
  type        = string
}

variable "environment" {
  description = "Miljö (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "GCP-region för Cloud Functions"
  type        = string
  default     = "europe-west1"
}

variable "service_account_email" {
  description = "Service account email för Cloud Functions"
  type        = string
}

variable "storage_bucket" {
  description = "GCS bucket för Cloud Functions källkod"
  type        = string
}

variable "pubsub_topic_id" {
  description = "Pub/Sub topic ID för att trigga funktioner"
  type        = string
  default     = ""
}

variable "functions" {
  description = "Lista över Cloud Functions att skapa"
  type = list(object({
    name        = string
    description = string
    runtime     = string
    entry_point = string
    source_dir  = string
    trigger_http = bool
    pubsub_topic = optional(string)
    timeout_seconds = optional(number)
    memory_mb = optional(number)
    environment_variables = optional(map(string))
  }))
  default = []
}

variable "labels" {
  description = "Labels att applicera på alla resurser"
  type        = map(string)
  default     = {}
}

# Placeholder för Cloud Functions-resurser
# Kommer att implementeras senare när vi börjar skapa faktiska funktioner

output "function_urls" {
  description = "URLs för HTTP-triggade Cloud Functions"
  value       = {}
}