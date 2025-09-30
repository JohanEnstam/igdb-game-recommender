#!/usr/bin/env python3
"""
ETL Pipeline for IGDB Data Ingestion
Cloud Run Job version that loads data directly to BigQuery
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any
from google.cloud import bigquery
from google.cloud import storage
from google.cloud.exceptions import NotFound

# Add ingestion path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ingestion'))
from igdb_client import IGDBClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fields to fetch from IGDB API
FIELDS = [
    "id",
    "name",
    "summary",
    "storyline",
    "genres.name",
    "platforms.name",
    "themes.name",
    "game_modes.name",
    "player_perspectives.name",
    "age_ratings.rating",
    "release_dates.date",
    "screenshots.url",
    "videos.video_id",
    "cover.url",
    "websites.url",
    "involved_companies.company.name",
    "game_engines.name",
    "franchises.name",
    "collections.name",
    "rating",
    "rating_count",
    "aggregated_rating",
    "aggregated_rating_count",
    "total_rating",
    "total_rating_count",
    "hypes",
    "popularity",
    "follows",
    "created_at",
    "updated_at"
]

def get_bigquery_client():
    """Get BigQuery client"""
    return bigquery.Client()

def get_storage_client():
    """Get Cloud Storage client"""
    return storage.Client()

def create_bigquery_table_if_not_exists(client: bigquery.Client, dataset_id: str, table_id: str):
    """Create BigQuery table if it doesn't exist"""
    table_ref = client.dataset(dataset_id).table(table_id)
    
    try:
        client.get_table(table_ref)
        logger.info(f"Table {dataset_id}.{table_id} already exists")
        return
    except NotFound:
        logger.info(f"Creating table {dataset_id}.{table_id}")
    
    # Define schema
    schema = [
        bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("summary", "STRING"),
        bigquery.SchemaField("storyline", "STRING"),
        bigquery.SchemaField("genres", "STRING", mode="REPEATED"),
        bigquery.SchemaField("platforms", "STRING", mode="REPEATED"),
        bigquery.SchemaField("themes", "STRING", mode="REPEATED"),
        bigquery.SchemaField("game_modes", "STRING", mode="REPEATED"),
        bigquery.SchemaField("player_perspectives", "STRING", mode="REPEATED"),
        bigquery.SchemaField("age_ratings", "STRING", mode="REPEATED"),
        bigquery.SchemaField("release_dates", "STRING", mode="REPEATED"),
        bigquery.SchemaField("screenshots", "STRING", mode="REPEATED"),
        bigquery.SchemaField("videos", "STRING", mode="REPEATED"),
        bigquery.SchemaField("cover", "STRING"),
        bigquery.SchemaField("websites", "STRING", mode="REPEATED"),
        bigquery.SchemaField("involved_companies", "STRING", mode="REPEATED"),
        bigquery.SchemaField("game_engines", "STRING", mode="REPEATED"),
        bigquery.SchemaField("franchises", "STRING", mode="REPEATED"),
        bigquery.SchemaField("collections", "STRING", mode="REPEATED"),
        bigquery.SchemaField("rating", "FLOAT"),
        bigquery.SchemaField("rating_count", "INTEGER"),
        bigquery.SchemaField("aggregated_rating", "FLOAT"),
        bigquery.SchemaField("aggregated_rating_count", "INTEGER"),
        bigquery.SchemaField("total_rating", "FLOAT"),
        bigquery.SchemaField("total_rating_count", "INTEGER"),
        bigquery.SchemaField("hypes", "INTEGER"),
        bigquery.SchemaField("popularity", "FLOAT"),
        bigquery.SchemaField("follows", "INTEGER"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="REQUIRED")
    ]
    
    table = bigquery.Table(table_ref, schema=schema)
    table = client.create_table(table)
    logger.info(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

def transform_game_data(games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform game data for BigQuery"""
    transformed_games = []
    ingestion_timestamp = datetime.utcnow()
    
    for game in games:
        transformed_game = {
            "id": game.get("id"),
            "name": game.get("name"),
            "summary": game.get("summary"),
            "storyline": game.get("storyline"),
            "genres": [str(g) for g in game.get("genres", [])],
            "platforms": [str(p) for p in game.get("platforms", [])],
            "themes": [str(t) for t in game.get("themes", [])],
            "game_modes": [str(gm) for gm in game.get("game_modes", [])],
            "player_perspectives": [str(pp) for pp in game.get("player_perspectives", [])],
            "age_ratings": [str(ar) for ar in game.get("age_ratings", [])],
            "release_dates": [str(rd) for rd in game.get("release_dates", [])],
            "screenshots": [str(s) for s in game.get("screenshots", [])],
            "videos": [str(v) for v in game.get("videos", [])],
            "cover": str(game.get("cover", "")),
            "websites": [str(w) for w in game.get("websites", [])],
            "involved_companies": [str(ic) for ic in game.get("involved_companies", [])],
            "game_engines": [str(ge) for ge in game.get("game_engines", [])],
            "franchises": [str(f) for f in game.get("franchises", [])],
            "collections": [str(c) for c in game.get("collections", [])],
            "rating": game.get("rating"),
            "rating_count": game.get("rating_count"),
            "aggregated_rating": game.get("aggregated_rating"),
            "aggregated_rating_count": game.get("aggregated_rating_count"),
            "total_rating": game.get("total_rating"),
            "total_rating_count": game.get("total_rating_count"),
            "hypes": game.get("hypes"),
            "popularity": game.get("popularity"),
            "follows": game.get("follows"),
            "created_at": game.get("created_at"),
            "updated_at": game.get("updated_at"),
            "ingestion_timestamp": ingestion_timestamp
        }
        transformed_games.append(transformed_game)
    
    return transformed_games

def load_to_bigquery(client: bigquery.Client, dataset_id: str, table_id: str, games: List[Dict[str, Any]]):
    """Load games data to BigQuery"""
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)
    
    # Transform data
    transformed_games = transform_game_data(games)
    
    # Insert data
    errors = client.insert_rows_json(table, transformed_games)
    if errors:
        logger.error(f"Errors inserting rows: {errors}")
        raise Exception(f"Failed to insert {len(errors)} rows")
    
    logger.info(f"Successfully loaded {len(transformed_games)} games to {dataset_id}.{table_id}")

def save_to_storage(storage_client: storage.Client, bucket_name: str, games: List[Dict[str, Any]], filename: str):
    """Save games data to Cloud Storage as backup"""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"raw_data/{filename}")
    
    # Convert to JSON
    json_data = json.dumps(games, ensure_ascii=False, indent=2)
    
    # Upload
    blob.upload_from_string(json_data, content_type='application/json')
    logger.info(f"Saved {len(games)} games to gs://{bucket_name}/raw_data/{filename}")

def fetch_and_load_games():
    """Main function to fetch games from IGDB and load to BigQuery"""
    # Get environment variables
    project_id = os.environ.get("PROJECT_ID")
    environment = os.environ.get("ENVIRONMENT", "dev")
    raw_data_bucket = os.environ.get("RAW_DATA_BUCKET")
    bigquery_dataset = os.environ.get("BIGQUERY_DATASET")
    igdb_client_id = os.environ.get("IGDB_CLIENT_ID")
    igdb_client_secret = os.environ.get("IGDB_CLIENT_SECRET")
    
    if not all([project_id, raw_data_bucket, bigquery_dataset, igdb_client_id, igdb_client_secret]):
        raise ValueError("Missing required environment variables")
    
    # Initialize clients
    bq_client = get_bigquery_client()
    storage_client = get_storage_client()
    
    # Create table if not exists
    create_bigquery_table_if_not_exists(bq_client, bigquery_dataset, "games_raw")
    
    # Initialize IGDB client
    igdb_client = IGDBClient(
        client_id=igdb_client_id,
        client_secret=igdb_client_secret,
        rate_limit=4,  # 4 requests per second
        batch_size=500
    )
    
    logger.info("Starting ETL pipeline...")
    start_time = time.time()
    
    try:
        # Fetch all games
        all_games = []
        offset = 0
        batch_size = 500
        
        while True:
            logger.info(f"Fetching games {offset} to {offset + batch_size}")
            
            # Fetch batch
            games = igdb_client.get_games(
                fields=FIELDS,
                limit=batch_size,
                offset=offset
            )
            
            if not games:
                break
            
            all_games.extend(games)
            offset += batch_size
            
            # Load to BigQuery in batches
            if len(all_games) >= 1000:  # Load every 1000 games
                load_to_bigquery(bq_client, bigquery_dataset, "games_raw", all_games)
                
                # Save to storage as backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"games_batch_{offset}_{timestamp}.json"
                save_to_storage(storage_client, raw_data_bucket, all_games, filename)
                
                all_games = []  # Clear batch
            
            # Rate limiting
            time.sleep(0.25)  # 4 requests per second
        
        # Load remaining games
        if all_games:
            load_to_bigquery(bq_client, bigquery_dataset, "games_raw", all_games)
            
            # Save to storage as backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"games_final_{timestamp}.json"
            save_to_storage(storage_client, raw_data_bucket, all_games, filename)
        
        # Calculate statistics
        end_time = time.time()
        total_time = end_time - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        logger.info(f"ETL pipeline completed successfully!")
        logger.info(f"Total time: {minutes} minutes and {seconds} seconds")
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        raise

if __name__ == "__main__":
    fetch_and_load_games()
