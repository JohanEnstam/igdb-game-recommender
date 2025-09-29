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

# Create table schemas
locals {
  # Schema for raw/staging data
  raw_game_schema = [
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
  
  # Schema for cleaned games table
  cleaned_games_schema = [
    {
      name = "game_id",
      type = "STRING",
      mode = "REQUIRED",
      description = "Unique identifier for the game (from IGDB)"
    },
    {
      name = "canonical_name",
      type = "STRING",
      mode = "REQUIRED",
      description = "Normalized name without version markers"
    },
    {
      name = "display_name",
      type = "STRING",
      mode = "REQUIRED",
      description = "Original name for display"
    },
    {
      name = "release_date",
      type = "TIMESTAMP",
      mode = "NULLABLE",
      description = "Game release date"
    },
    {
      name = "summary",
      type = "STRING",
      mode = "NULLABLE",
      description = "Game summary"
    },
    {
      name = "rating",
      type = "FLOAT",
      mode = "NULLABLE",
      description = "Average user rating"
    },
    {
      name = "cover_url",
      type = "STRING",
      mode = "NULLABLE",
      description = "URL to game cover image"
    },
    {
      name = "has_complete_data",
      type = "BOOLEAN",
      mode = "REQUIRED",
      description = "Whether the game has complete data"
    },
    {
      name = "quality_score",
      type = "FLOAT",
      mode = "REQUIRED",
      description = "Calculated score based on data quality (0-100)"
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
  
  # Schema for game relationships table
  game_relationships_schema = [
    {
      name = "source_game_id",
      type = "STRING",
      mode = "REQUIRED",
      description = "ID of the source game"
    },
    {
      name = "target_game_id",
      type = "STRING",
      mode = "REQUIRED",
      description = "ID of the target game"
    },
    {
      name = "relationship_type",
      type = "STRING",
      mode = "REQUIRED",
      description = "Type of relationship (duplicate_of, version_of, sequel_to)"
    },
    {
      name = "confidence_score",
      type = "FLOAT",
      mode = "REQUIRED",
      description = "Confidence score for the relationship"
    },
    {
      name = "created_at",
      type = "TIMESTAMP",
      mode = "REQUIRED",
      description = "Record creation timestamp"
    }
  ]
  
  # Schema for game groups table
  game_groups_schema = [
    {
      name = "group_id",
      type = "STRING",
      mode = "REQUIRED",
      description = "Unique identifier for the group"
    },
    {
      name = "group_type",
      type = "STRING",
      mode = "REQUIRED",
      description = "Type of group (version_group, series)"
    },
    {
      name = "canonical_name",
      type = "STRING",
      mode = "REQUIRED",
      description = "Canonical name for the group"
    },
    {
      name = "representative_game_id",
      type = "STRING",
      mode = "REQUIRED",
      description = "ID of the representative game for the group"
    },
    {
      name = "game_count",
      type = "INTEGER",
      mode = "REQUIRED",
      description = "Number of games in the group"
    },
    {
      name = "created_at",
      type = "TIMESTAMP",
      mode = "REQUIRED",
      description = "Record creation timestamp"
    }
  ]
  
  # Schema for game group members table
  game_group_members_schema = [
    {
      name = "group_id",
      type = "STRING",
      mode = "REQUIRED",
      description = "ID of the group"
    },
    {
      name = "game_id",
      type = "STRING",
      mode = "REQUIRED",
      description = "ID of the game"
    },
    {
      name = "is_primary",
      type = "BOOLEAN",
      mode = "REQUIRED",
      description = "Whether this is the primary game in the group"
    },
    {
      name = "created_at",
      type = "TIMESTAMP",
      mode = "REQUIRED",
      description = "Record creation timestamp"
    }
  ]
}

# Create raw data staging table
resource "google_bigquery_table" "games_raw" {
  dataset_id = google_bigquery_dataset.igdb_games.dataset_id
  table_id   = "games_raw"
  
  description = "Raw staging table for IGDB game data"
  
  schema = jsonencode(local.raw_game_schema)
  
  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }
  
  labels = var.labels
}

# Create cleaned games table
resource "google_bigquery_table" "games" {
  dataset_id = google_bigquery_dataset.igdb_games.dataset_id
  table_id   = "games"
  
  description = "Cleaned games table with canonical names and quality scores"
  
  schema = jsonencode(local.cleaned_games_schema)
  
  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }
  
  clustering = ["canonical_name"]
  
  labels = var.labels
}

# Create game relationships table
resource "google_bigquery_table" "game_relationships" {
  dataset_id = google_bigquery_dataset.igdb_games.dataset_id
  table_id   = "game_relationships"
  
  description = "Game relationships table defining connections between games"
  
  schema = jsonencode(local.game_relationships_schema)
  
  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }
  
  clustering = ["source_game_id", "relationship_type"]
  
  labels = var.labels
}

# Create game groups table
resource "google_bigquery_table" "game_groups" {
  dataset_id = google_bigquery_dataset.igdb_games.dataset_id
  table_id   = "game_groups"
  
  description = "Game groups table for versions and series"
  
  schema = jsonencode(local.game_groups_schema)
  
  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }
  
  clustering = ["group_type", "canonical_name"]
  
  labels = var.labels
}

# Create game group members table
resource "google_bigquery_table" "game_group_members" {
  dataset_id = google_bigquery_dataset.igdb_games.dataset_id
  table_id   = "game_group_members"
  
  description = "Game group members mapping table"
  
  schema = jsonencode(local.game_group_members_schema)
  
  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }
  
  clustering = ["group_id"]
  
  labels = var.labels
}