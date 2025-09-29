/**
 * Cloud SQL Terraform Module
 * 
 * Detta är en modul för att hantera Cloud SQL (PostgreSQL) i GCP.
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
  description = "GCP-region för Cloud SQL"
  type        = string
  default     = "europe-west1"
}

variable "instance_name" {
  description = "Namn på Cloud SQL-instansen"
  type        = string
}

variable "database_version" {
  description = "Databasversion för PostgreSQL"
  type        = string
  default     = "POSTGRES_14"
}

variable "tier" {
  description = "Maskintyp för Cloud SQL-instansen"
  type        = string
  default     = "db-f1-micro"
}

variable "disk_size" {
  description = "Diskstorlek i GB"
  type        = number
  default     = 10
}

variable "databases" {
  description = "Lista över databaser att skapa"
  type        = list(string)
  default     = ["games"]
}

variable "users" {
  description = "Lista över användare att skapa"
  type = list(object({
    name     = string
    password = string
  }))
  default = []
}

variable "labels" {
  description = "Labels att applicera på alla resurser"
  type        = map(string)
  default     = {}
}

# Placeholder för Cloud SQL-resurser
# Kommer att implementeras senare när vi börjar skapa faktiska databaser

output "instance_connection_name" {
  description = "Connection name för Cloud SQL-instansen"
  value       = ""
}

output "instance_ip_address" {
  description = "IP-adress för Cloud SQL-instansen"
  value       = ""
}