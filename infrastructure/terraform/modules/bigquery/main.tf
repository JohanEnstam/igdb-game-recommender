/**
 * IGDB Game Recommendation System - BigQuery Module
 * 
 * This module sets up BigQuery datasets and tables.
 */

# Create BigQuery dataset
resource "google_bigquery_dataset" "igdb_games" {
  dataset_id                  = "${var.bigquery_dataset_id}_${var.environment}"
  friendly_name               = "IGDB Games Dataset (${var.environment})"
  description                 = "Dataset for IGDB game data and recommendations"
  location                    = var.bigquery_location
  default_table_expiration_ms = null
  
  labels = var.labels
  
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }
  
  access {
    role          = "READER"
    special_group = "projectReaders"
  }
  
  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }
}

# Create staging table schema
locals {
  game_schema = [
    {
      name = "id",
      type = "INTEGER",
      mode = "REQUIRED",
      description = "IGDB game ID"
    },
    {
      name = "name",
      type = "STRING",
      mode = "REQUIRED",
      description = "Game title"
    },
    {
      name = "summary",
      type = "STRING",
      mode = "NULLABLE",
      description = "Game summary"
    },
    {
      name = "storyline",
      type = "STRING",
      mode = "NULLABLE",
      description = "Game storyline"
    },
    {
      name = "first_release_date",
      type = "TIMESTAMP",
      mode = "NULLABLE",
      description = "First release date"
    },
    {
      name = "rating",
      type = "FLOAT",
      mode = "NULLABLE",
      description = "Average rating"
    },
    {
      name = "rating_count",
      type = "INTEGER",
      mode = "NULLABLE",
      description = "Number of ratings"
    },
    {
      name = "aggregated_rating",
      type = "FLOAT",
      mode = "NULLABLE",
      description = "Aggregated critic rating"
    },
    {
      name = "aggregated_rating_count",
      type = "INTEGER",
      mode = "NULLABLE",
      description = "Number of critic ratings"
    },
    {
      name = "genres",
      type = "RECORD",
      mode = "REPEATED",
      description = "Game genres",
      fields = [
        {
          name = "id",
          type = "INTEGER",
          mode = "REQUIRED",
          description = "Genre ID"
        },
        {
          name = "name",
          type = "STRING",
          mode = "REQUIRED",
          description = "Genre name"
        }
      ]
    },
    {
      name = "platforms",
      type = "RECORD",
      mode = "REPEATED",
      description = "Game platforms",
      fields = [
        {
          name = "id",
          type = "INTEGER",
          mode = "REQUIRED",
          description = "Platform ID"
        },
        {
          name = "name",
          type = "STRING",
          mode = "REQUIRED",
          description = "Platform name"
        }
      ]
    },
    {
      name = "themes",
      type = "RECORD",
      mode = "REPEATED",
      description = "Game themes",
      fields = [
        {
          name = "id",
          type = "INTEGER",
          mode = "REQUIRED",
          description = "Theme ID"
        },
        {
          name = "name",
          type = "STRING",
          mode = "REQUIRED",
          description = "Theme name"
        }
      ]
    },
    {
      name = "cover_url",
      type = "STRING",
      mode = "NULLABLE",
      description = "Game cover image URL"
    },
    {
      name = "created_at",
      type = "TIMESTAMP",
      mode = "REQUIRED",
      description = "Record creation timestamp"
    },
    {
      name = "updated_at",
      type = "TIMESTAMP",
      mode = "REQUIRED",
      description = "Record update timestamp"
    }
  ]
}

# Create staging table
resource "google_bigquery_table" "games_staging" {
  dataset_id = google_bigquery_dataset.igdb_games.dataset_id
  table_id   = "games_staging"
  
  description = "Staging table for IGDB game data"
  
  schema = jsonencode(local.game_schema)
  
  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }
  
  labels = var.labels
}

# Create production table
resource "google_bigquery_table" "games_production" {
  dataset_id = google_bigquery_dataset.igdb_games.dataset_id
  table_id   = "games_production"
  
  description = "Production table for IGDB game data"
  
  schema = jsonencode(local.game_schema)
  
  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }
  
  labels = var.labels
}
