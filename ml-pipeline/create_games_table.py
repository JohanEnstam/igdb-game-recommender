#!/usr/bin/env python3
"""
Create BigQuery table that matches local data structure
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_bigquery_client():
    """Get BigQuery client"""
    return bigquery.Client()

def create_games_table_with_categories():
    """Create BigQuery table that matches local data structure"""
    # Get environment variables
    project_id = os.environ.get("PROJECT_ID", "igdb-pipeline-v3")
    bigquery_dataset = os.environ.get("BIGQUERY_DATASET", "igdb_games_dev")
    
    # Initialize BigQuery client
    bq_client = get_bigquery_client()
    
    # Define table reference
    table_ref = bq_client.dataset(bigquery_dataset).table("games_with_categories")
    
    # Check if table exists
    try:
        bq_client.get_table(table_ref)
        logger.info(f"Table {bigquery_dataset}.games_with_categories already exists")
        return
    except NotFound:
        logger.info(f"Creating table {bigquery_dataset}.games_with_categories")
    
    # Define schema that matches local data structure
    schema = [
        bigquery.SchemaField("game_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("canonical_name", "STRING"),
        bigquery.SchemaField("display_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("release_date", "TIMESTAMP"),
        bigquery.SchemaField("summary", "STRING"),
        bigquery.SchemaField("rating", "FLOAT"),
        bigquery.SchemaField("cover_url", "STRING"),
        bigquery.SchemaField("has_complete_data", "BOOLEAN"),
        bigquery.SchemaField("quality_score", "FLOAT"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        bigquery.SchemaField("genres", "STRING", mode="REPEATED"),
        bigquery.SchemaField("platforms", "STRING", mode="REPEATED"),
        bigquery.SchemaField("themes", "STRING", mode="REPEATED"),
        bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="REQUIRED")
    ]
    
    # Create table
    table = bigquery.Table(table_ref, schema=schema)
    table = bq_client.create_table(table)
    logger.info(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

def load_local_data_to_bigquery():
    """Load local data to BigQuery table"""
    # Get environment variables
    project_id = os.environ.get("PROJECT_ID", "igdb-pipeline-v3")
    bigquery_dataset = os.environ.get("BIGQUERY_DATASET", "igdb_games_dev")
    
    # Path to local data
    local_data_path = os.path.join(os.path.dirname(__file__), "..", "data", "medium_dataset", "games.json")
    
    if not os.path.exists(local_data_path):
        raise FileNotFoundError(f"Local data file not found: {local_data_path}")
    
    # Initialize BigQuery client
    bq_client = get_bigquery_client()
    
    # Create table if not exists
    create_games_table_with_categories()
    
    logger.info("Loading local data...")
    
    # Load and parse JSON data
    with open(local_data_path, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    logger.info(f"Loaded {len(games)} games from local file")
    
    # Transform data for BigQuery
    transformed_games = []
    ingestion_timestamp = datetime.utcnow()
    
    for game in games:
        # Handle NaN values in rating
        rating = game.get("rating")
        if rating is None or (isinstance(rating, float) and str(rating).lower() == 'nan'):
            rating = None
        
        # Handle NaN values in quality_score
        quality_score = game.get("quality_score")
        if quality_score is None or (isinstance(quality_score, float) and str(quality_score).lower() == 'nan'):
            quality_score = None
        
        # Parse release_date - keep as string for BigQuery
        release_date = game.get("release_date")
        if release_date:
            try:
                # Convert to ISO format string
                dt = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
                release_date = dt.isoformat()
            except:
                release_date = None
        
        # Parse created_at and updated_at - keep as strings
        created_at = game.get("created_at")
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at)
                created_at = dt.isoformat()
            except:
                created_at = None
        
        updated_at = game.get("updated_at")
        if updated_at:
            try:
                dt = datetime.fromisoformat(updated_at)
                updated_at = dt.isoformat()
            except:
                updated_at = None
        
        transformed_game = {
            "game_id": str(game.get("game_id", "")),
            "canonical_name": game.get("canonical_name", ""),
            "display_name": game.get("display_name", ""),
            "release_date": release_date,
            "summary": game.get("summary"),
            "rating": rating,
            "cover_url": game.get("cover_url"),
            "has_complete_data": game.get("has_complete_data", False),
            "quality_score": quality_score,
            "created_at": created_at,
            "updated_at": updated_at,
            "genres": game.get("genres", []),
            "platforms": game.get("platforms", []),
            "themes": game.get("themes", []),
            "ingestion_timestamp": ingestion_timestamp.isoformat()
        }
        transformed_games.append(transformed_game)
    
    # Load to BigQuery in batches
    table_ref = bq_client.dataset(bigquery_dataset).table("games_with_categories")
    table = bq_client.get_table(table_ref)
    
    batch_size = 1000
    total_inserted = 0
    
    for i in range(0, len(transformed_games), batch_size):
        batch = transformed_games[i:i + batch_size]
        errors = bq_client.insert_rows_json(table, batch)
        if errors:
            logger.error(f"Errors inserting batch {i//batch_size + 1}: {errors}")
            raise Exception(f"Failed to insert batch {i//batch_size + 1}")
        
        total_inserted += len(batch)
        logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} games (total: {total_inserted})")
    
    logger.info(f"Successfully loaded {total_inserted} games to {bigquery_dataset}.games_with_categories")

if __name__ == "__main__":
    load_local_data_to_bigquery()
