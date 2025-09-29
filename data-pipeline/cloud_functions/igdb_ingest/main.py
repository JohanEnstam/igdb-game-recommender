"""
Cloud Function for fetching data from the IGDB API.

This function fetches game data from the IGDB API and stores it in Cloud Storage.
It can be triggered via HTTP or scheduled via Cloud Scheduler.
"""

import os
import json
import tempfile
import logging
import time
import requests
from typing import Dict, List, Any
from datetime import datetime
from google.cloud import storage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
RAW_DATA_BUCKET = os.environ.get('RAW_DATA_BUCKET')
IGDB_CLIENT_ID = os.environ.get('IGDB_CLIENT_ID')
IGDB_CLIENT_SECRET = os.environ.get('IGDB_CLIENT_SECRET')

# IGDB API constants
IGDB_AUTH_URL = "https://id.twitch.tv/oauth2/token"
IGDB_API_URL = "https://api.igdb.com/v4"
BATCH_SIZE = 500  # Number of games to fetch per request
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

class IGDBClient:
    """Client for interacting with the IGDB API."""
    
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the IGDB client.
        
        Args:
            client_id: IGDB API client ID
            client_secret: IGDB API client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = 0
    
    def get_access_token(self) -> str:
        """
        Get an access token for the IGDB API.
        
        Returns:
            Access token
        """
        now = time.time()
        
        # Check if token is still valid
        if self.access_token and now < self.token_expires_at:
            return self.access_token
        
        # Get a new token
        auth_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(IGDB_AUTH_URL, data=auth_data)
            response.raise_for_status()
            data = response.json()
            logger.info("Successfully obtained access token")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            logger.error(f"Response content: {response.content if 'response' in locals() else 'No response'}")
            raise
        self.access_token = data['access_token']
        self.token_expires_at = now + data['expires_in'] - 60  # Subtract 60 seconds for safety
        
        return self.access_token
    
    def fetch_games(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch games from the IGDB API.
        
        Args:
            offset: Offset for pagination
            limit: Number of games to fetch
            
        Returns:
            List of games
        """
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.get_access_token()}'
        }
        
        # Define the fields to fetch
        fields = [
            "id", "name", "summary", "storyline", "first_release_date",
            "rating", "rating_count", "aggregated_rating", "aggregated_rating_count",
            "genres.id", "genres.name", "platforms.id", "platforms.name",
            "themes.id", "themes.name", "cover.url"
        ]
        
        # Build the query
        query = f"""
        fields {','.join(fields)};
        limit {limit};
        offset {offset};
        where version_parent = null;
        sort id asc;
        """
        
        # Make the request with retries
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(f"{IGDB_API_URL}/games", headers=headers, data=query)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"Request failed, retrying in {RETRY_DELAY} seconds: {e}")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Request failed after {MAX_RETRIES} attempts: {e}")
                    raise
    
    def fetch_all_games(self, max_games: int = None) -> List[Dict[str, Any]]:
        """
        Fetch all games from the IGDB API.
        
        Args:
            max_games: Maximum number of games to fetch (None for all)
            
        Returns:
            List of games
        """
        all_games = []
        offset = 0
        
        while True:
            # Check if we've reached the maximum
            if max_games and offset >= max_games:
                break
            
            # Adjust batch size if needed
            current_batch_size = min(BATCH_SIZE, max_games - offset) if max_games else BATCH_SIZE
            
            # Fetch a batch of games
            logger.info(f"Fetching games {offset} to {offset + current_batch_size}")
            games = self.fetch_games(offset, current_batch_size)
            
            # Check if we got any games
            if not games:
                break
            
            all_games.extend(games)
            offset += len(games)
            
            # Check if we got fewer games than requested (end of data)
            if len(games) < current_batch_size:
                break
            
            # Sleep to avoid rate limiting
            time.sleep(0.25)
        
        return all_games

def fetch_igdb_data(request):
    """
    Cloud Function entry point. Fetches data from the IGDB API and stores it in Cloud Storage.
    
    Args:
        request: HTTP request
        
    Returns:
        HTTP response
    """
    # Parse request parameters
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    # Get parameters
    max_games = None
    if request_json and 'max_games' in request_json:
        max_games = int(request_json['max_games'])
    elif request_args and 'max_games' in request_args:
        max_games = int(request_args['max_games'])
    
    # Initialize the IGDB client
    client = IGDBClient(IGDB_CLIENT_ID, IGDB_CLIENT_SECRET)
    
    # Fetch the games
    try:
        logger.info(f"Fetching games from IGDB API (max_games={max_games})")
        games = client.fetch_all_games(max_games)
        logger.info(f"Fetched {len(games)} games")
    except Exception as e:
        logger.error(f"Error fetching games: {e}")
        return {"success": False, "error": str(e)}, 500
    
    # Store the games in Cloud Storage
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(games, temp_file)
            temp_file_path = temp_file.name
        
        # Upload to Cloud Storage
        client = storage.Client()
        bucket = client.bucket(RAW_DATA_BUCKET)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob = bucket.blob(f"raw_data/igdb_games_{timestamp}.json")
        blob.upload_from_filename(temp_file_path)
        
        # Clean up
        os.unlink(temp_file_path)
        
        logger.info(f"Uploaded games to gs://{RAW_DATA_BUCKET}/raw_data/igdb_games_{timestamp}.json")
    except Exception as e:
        logger.error(f"Error storing games: {e}")
        return {"success": False, "error": str(e)}, 500
    
    # Return success
    return {
        "success": True,
        "games_fetched": len(games),
        "storage_path": f"gs://{RAW_DATA_BUCKET}/raw_data/igdb_games_{timestamp}.json"
    }
