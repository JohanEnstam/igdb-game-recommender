"""
Cloud Function for running the IGDB data cleaning pipeline.

This function is triggered when a new raw data file is uploaded to Cloud Storage.
It processes the data using the data cleaning pipeline and saves the results to
the processed data bucket.
"""

import os
import json
import tempfile
import logging
from typing import Dict, Any
from datetime import datetime
from google.cloud import storage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
RAW_DATA_BUCKET = os.environ.get('RAW_DATA_BUCKET')
PROCESSED_DATA_BUCKET = os.environ.get('PROCESSED_DATA_BUCKET')

# Import data cleaning modules
import sys
sys.path.append('/tmp')

def download_processing_modules():
    """
    Downloads the processing modules from the processed data bucket.
    These modules are uploaded as part of the deployment process.
    """
    client = storage.Client()
    bucket = client.bucket(PROCESSED_DATA_BUCKET)
    
    module_files = [
        'name_processor.py',
        'game_grouper.py',
        'quality_scorer.py',
        'data_model.py',
        'utils.py',
        'etl_pipeline.py'
    ]
    
    for module_file in module_files:
        blob = bucket.blob(f'modules/{module_file}')
        blob.download_to_filename(f'/tmp/{module_file}')
        logger.info(f"Downloaded {module_file}")

def process_data(event, context):
    """
    Cloud Function entry point. Triggered by a new file in the raw data bucket.
    
    Args:
        event: The Cloud Functions event
        context: The Cloud Functions context
    """
    logger.info("Data cleaning pipeline function triggered")
    logger.info(f"Event: {event}")
    
    # Get the file that triggered the function
    file_name = event['name']
    
    # Only process JSON files
    if not file_name.endswith('.json'):
        logger.info(f"Ignoring non-JSON file: {file_name}")
        return
    
    # Download processing modules
    try:
        download_processing_modules()
        
        # Now we can import the modules
        from etl_pipeline import DataCleaningPipeline
        
        logger.info("Successfully imported processing modules")
    except Exception as e:
        logger.error(f"Error importing processing modules: {e}")
        raise
    
    # Create temporary directories for input and output
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Download the raw data file
        client = storage.Client()
        input_bucket = client.bucket(RAW_DATA_BUCKET)
        blob = input_bucket.blob(file_name)
        local_input_path = os.path.join(input_dir, os.path.basename(file_name))
        blob.download_to_filename(local_input_path)
        logger.info(f"Downloaded {file_name} to {local_input_path}")
        
        # Run the data cleaning pipeline
        try:
            pipeline = DataCleaningPipeline(input_dir, output_dir)
            pipeline.run()
            logger.info("Data cleaning pipeline completed successfully")
        except Exception as e:
            logger.error(f"Error running data cleaning pipeline: {e}")
            raise
        
        # Upload the processed data files to the processed data bucket
        output_bucket = client.bucket(PROCESSED_DATA_BUCKET)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for output_file in os.listdir(output_dir):
            source_path = os.path.join(output_dir, output_file)
            destination_blob_name = f"cleaned_data/{timestamp}/{output_file}"
            blob = output_bucket.blob(destination_blob_name)
            blob.upload_from_filename(source_path)
            logger.info(f"Uploaded {source_path} to {destination_blob_name}")
        
        # Create a metadata file with processing information
        metadata = {
            "source_file": file_name,
            "processed_at": timestamp,
            "environment": ENVIRONMENT,
            "status": "success"
        }
        
        metadata_blob = output_bucket.blob(f"cleaned_data/{timestamp}/metadata.json")
        metadata_blob.upload_from_string(json.dumps(metadata))
        logger.info(f"Uploaded metadata to cleaned_data/{timestamp}/metadata.json")
    
    logger.info("Data cleaning pipeline function completed")
    return "Data cleaning completed successfully"
