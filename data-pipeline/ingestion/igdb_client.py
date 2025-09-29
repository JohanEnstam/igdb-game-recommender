"""
IGDB API Client

This module implements a client for the IGDB API with proper rate limiting.
It handles authentication, request formatting, and pagination.

Rate Limit: 4 requests/second
Batch Size: 500 games per request
"""

import os
import time
import requests
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IGDBClient:
    """
    Client for interacting with the IGDB API with proper rate limiting.
    """
    
    BASE_URL = "https://api.igdb.com/v4"
    AUTH_URL = "https://id.twitch.tv/oauth2/token"
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        rate_limit: float = 4.0,  # 4 requests per second
        batch_size: int = 500
    ):
        """
        Initialize the IGDB API client.
        
        Args:
            client_id: IGDB/Twitch Client ID
            client_secret: IGDB/Twitch Client Secret
            rate_limit: Maximum requests per second (default: 4.0)
            batch_size: Number of games to fetch per request (default: 500)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.rate_limit = rate_limit
        self.batch_size = batch_size
        self.access_token = None
        self.token_expiry = None
        self.last_request_time = 0
        
        # Authenticate on initialization
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with the IGDB API and get an access token.
        """
        logger.info("Authenticating with IGDB API")
        
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(self.AUTH_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data['access_token']
            expires_in = data['expires_in']
            
            # Set token expiry time (subtract 1 hour for safety margin)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 3600)
            
            logger.info(f"Authentication successful, token expires at {self.token_expiry}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def _check_token(self) -> None:
        """
        Check if the access token is still valid and refresh if needed.
        """
        if not self.access_token or datetime.now() >= self.token_expiry:
            logger.info("Access token expired or missing, refreshing")
            self._authenticate()
    
    def _rate_limit(self) -> None:
        """
        Apply rate limiting to ensure we don't exceed the API limits.
        """
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        # Calculate minimum time between requests
        min_interval = 1.0 / self.rate_limit
        
        # If we need to wait to respect rate limit
        if elapsed < min_interval:
            sleep_time = min_interval - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.4f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(
        self,
        endpoint: str,
        body: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the IGDB API with rate limiting.
        
        Args:
            endpoint: API endpoint to call
            body: Request body in IGDB's query format
            params: Optional query parameters
            
        Returns:
            JSON response from the API
        """
        self._check_token()
        self._rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'text/plain'
        }
        
        try:
            response = requests.post(url, data=body, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Too Many Requests
                logger.warning("Rate limit exceeded, retrying after delay")
                time.sleep(5)  # Wait 5 seconds before retrying
                return self._make_request(endpoint, body, params)
            else:
                logger.error(f"HTTP error: {e}")
                raise
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get_games(
        self,
        fields: List[str],
        limit: int = None,
        offset: int = 0,
        filters: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get games from the IGDB API.
        
        Args:
            fields: List of fields to retrieve
            limit: Maximum number of games to retrieve (default: batch_size)
            offset: Offset for pagination
            filters: Additional filters in IGDB query format
            
        Returns:
            List of game data dictionaries
        """
        if limit is None:
            limit = self.batch_size
        
        # Construct the query
        query_parts = [
            f"fields {','.join(fields)};",
            f"limit {min(limit, self.batch_size)};"
        ]
        
        if offset > 0:
            query_parts.append(f"offset {offset};")
            
        if filters:
            query_parts.append(filters)
            
        query = " ".join(query_parts)
        
        logger.info(f"Fetching games with offset {offset}, limit {min(limit, self.batch_size)}")
        return self._make_request("games", query)
    
    def get_all_games(
        self,
        fields: List[str],
        filters: Optional[str] = None,
        max_games: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all games from the IGDB API with pagination.
        
        Args:
            fields: List of fields to retrieve
            filters: Additional filters in IGDB query format
            max_games: Maximum number of games to retrieve (default: all)
            
        Returns:
            List of all game data dictionaries
        """
        all_games = []
        offset = 0
        
        while True:
            # Calculate how many games to fetch in this batch
            if max_games:
                remaining = max_games - len(all_games)
                if remaining <= 0:
                    break
                batch_limit = min(remaining, self.batch_size)
            else:
                batch_limit = self.batch_size
            
            # Fetch a batch of games
            games = self.get_games(fields, batch_limit, offset, filters)
            
            # If no more games, break
            if not games:
                break
                
            all_games.extend(games)
            logger.info(f"Fetched {len(games)} games, total: {len(all_games)}")
            
            # If fewer games returned than requested, we've reached the end
            if len(games) < batch_limit:
                break
                
            # Update offset for next batch
            offset += len(games)
            
            # If we've reached the maximum number of games, break
            if max_games and len(all_games) >= max_games:
                break
        
        return all_games
    
    def get_game_by_id(self, game_id: int, fields: List[str]) -> Optional[Dict[str, Any]]:
        """
        Get a specific game by ID.
        
        Args:
            game_id: IGDB game ID
            fields: List of fields to retrieve
            
        Returns:
            Game data dictionary or None if not found
        """
        query = f"fields {','.join(fields)}; where id = {game_id};"
        result = self._make_request("games", query)
        
        return result[0] if result else None
    
    def search_games(
        self,
        search_term: str,
        fields: List[str],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for games by name.
        
        Args:
            search_term: Text to search for
            fields: List of fields to retrieve
            limit: Maximum number of results to return
            
        Returns:
            List of matching game data dictionaries
        """
        query = f"fields {','.join(fields)}; search \"{search_term}\"; limit {limit};"
        return self._make_request("games", query)


if __name__ == "__main__":
    # Example usage
    client_id = os.environ.get("IGDB_CLIENT_ID")
    client_secret = os.environ.get("IGDB_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Error: IGDB_CLIENT_ID and IGDB_CLIENT_SECRET environment variables must be set")
        exit(1)
    
    client = IGDBClient(client_id, client_secret)
    
    # Example: Search for a game
    fields = ["id", "name", "summary", "rating", "first_release_date", "cover.url"]
    results = client.search_games("The Legend of Zelda", fields)
    
    for game in results:
        print(f"ID: {game.get('id')}")
        print(f"Name: {game.get('name')}")
        print(f"Rating: {game.get('rating', 'N/A')}")
        print(f"Summary: {game.get('summary', 'N/A')[:100]}...")
        print("-" * 50)
