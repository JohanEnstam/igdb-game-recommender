"""
Cloud Function for loading processed IGDB data into BigQuery.

This function is triggered when new processed data files are uploaded to Cloud Storage.
It loads the data into BigQuery tables.
"""

import os
import json
import logging
import tempfile
from typing import Dict, List, Any
from google.cloud import storage
from google.cloud import bigquery

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
PROCESSED_DATA_BUCKET = os.environ.get('PROCESSED_DATA_BUCKET')
BIGQUERY_DATASET = os.environ.get('BIGQUERY_DATASET')

# BigQuery table names
TABLE_NAMES = {
    'games.json': 'games',
    'game_relationships.json': 'game_relationships',
    'game_groups.json': 'game_groups',
    'game_group_members.json': 'game_group_members'
}

def load_to_bigquery(event, context):
    """
    Cloud Function entry point. Triggered by a new file in the processed data bucket.
    
    Args:
        event: The Cloud Functions event
        context: The Cloud Functions context
    """
    logger.info("ETL processor function triggered")
    logger.info(f"Event: {event}")
    
    # Get the file that triggered the function
    file_name = event['name']
    
    # Only process files in the cleaned_data directory
    if not file_name.startswith('cleaned_data/'):
        logger.info(f"Ignoring file not in cleaned_data directory: {file_name}")
        return
    
    # Only process JSON files
    if not file_name.endswith('.json'):
        logger.info(f"Ignoring non-JSON file: {file_name}")
        return
    
    # Skip metadata files
    if file_name.endswith('metadata.json'):
        logger.info(f"Ignoring metadata file: {file_name}")
        return
    
    # Get the base file name
    base_file_name = os.path.basename(file_name)
    
    # Check if this is a file we know how to process
    if base_file_name not in TABLE_NAMES:
        logger.info(f"Ignoring unknown file: {base_file_name}")
        return
    
    # Get the table name
    table_name = TABLE_NAMES[base_file_name]
    
    # Load the data into BigQuery
    try:
        # Create a BigQuery client
        bq_client = bigquery.Client()
        
        # Create a reference to the destination table
        table_ref = f"{PROJECT_ID}.{BIGQUERY_DATASET}.{table_name}"
        
        # Create a storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(PROCESSED_DATA_BUCKET)
        blob = bucket.blob(file_name)
        
        # Download the file content
        content = blob.download_as_string()
        
        # Parse the JSON array
        json_array = json.loads(content)
        
        # Create a temporary file with newline-delimited JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            for item in json_array:
                temp_file.write(json.dumps(item) + '\n')
            temp_file_path = temp_file.name
        
        # Configure the load job
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=[
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
            ]
        )
        
        # Load the data into BigQuery
        with open(temp_file_path, 'rb') as source_file:
            load_job = bq_client.load_table_from_file(
                source_file,
                table_ref,
                job_config=job_config
            )
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        # Wait for the job to complete
        load_job.result()
        
        # Get the destination table
        table = bq_client.get_table(table_ref)
        
        logger.info(f"Loaded {len(json_array)} rows into {table_ref}")
    except Exception as e:
        logger.error(f"Error loading data into BigQuery: {e}")
        raise
    
    logger.info("ETL processor function completed")
    return f"Loaded {file_name} into BigQuery table {table_name}"
