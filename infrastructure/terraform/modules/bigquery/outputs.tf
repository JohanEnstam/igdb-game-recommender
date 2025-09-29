/**
 * IGDB Game Recommendation System - BigQuery Module Outputs
 */

output "dataset_id" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.igdb_games.dataset_id
}

output "staging_table_id" {
  description = "BigQuery staging table ID"
  value       = google_bigquery_table.games_staging.table_id
}

output "production_table_id" {
  description = "BigQuery production table ID"
  value       = google_bigquery_table.games_production.table_id
}

output "dataset_location" {
  description = "BigQuery dataset location"
  value       = google_bigquery_dataset.igdb_games.location
}
