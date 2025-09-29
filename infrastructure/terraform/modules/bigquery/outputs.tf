/**
 * IGDB Game Recommendation System - BigQuery Module Outputs
 */

output "dataset_id" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.igdb_games.dataset_id
}

output "dataset_location" {
  description = "BigQuery dataset location"
  value       = google_bigquery_dataset.igdb_games.location
}

output "raw_table_id" {
  description = "BigQuery raw games table ID"
  value       = google_bigquery_table.games_raw.table_id
}

output "games_table_id" {
  description = "BigQuery cleaned games table ID"
  value       = google_bigquery_table.games.table_id
}

output "relationships_table_id" {
  description = "BigQuery game relationships table ID"
  value       = google_bigquery_table.game_relationships.table_id
}

output "groups_table_id" {
  description = "BigQuery game groups table ID"
  value       = google_bigquery_table.game_groups.table_id
}

output "group_members_table_id" {
  description = "BigQuery game group members table ID"
  value       = google_bigquery_table.game_group_members.table_id
}

output "table_ids" {
  description = "Map of all BigQuery table IDs"
  value = {
    raw_games        = google_bigquery_table.games_raw.table_id
    games            = google_bigquery_table.games.table_id
    game_relationships = google_bigquery_table.game_relationships.table_id
    game_groups      = google_bigquery_table.game_groups.table_id
    game_group_members = google_bigquery_table.game_group_members.table_id
  }
}