"""
IGDB Game Recommendation System - Backend API

This module implements the FastAPI application for the IGDB Game Recommendation System.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
import sys

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
from recommendation_service import recommendation_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG") != "True" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IGDB Game Recommendation API",
    description="API for game recommendations based on IGDB data",
    version="0.1.0",
)

# Initialize recommendation service on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the recommendation service on startup"""
    try:
        logger.info("Initializing recommendation service...")
        recommendation_service.initialize()
        logger.info("Recommendation service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize recommendation service: {e}")
        # Don't raise - let the app start but recommendations will fail gracefully

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://igdb-recommendation-frontend-dev-5wxthq523q-ew.a.run.app",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class GameBase(BaseModel):
    id: int
    name: str
    summary: Optional[str] = None
    rating: Optional[float] = None
    first_release_date: Optional[str] = None
    cover_url: Optional[str] = None

class GameDetail(GameBase):
    storyline: Optional[str] = None
    rating_count: Optional[int] = None
    aggregated_rating: Optional[float] = None
    aggregated_rating_count: Optional[int] = None
    genres: Optional[List[Dict[str, Any]]] = None
    platforms: Optional[List[Dict[str, Any]]] = None
    themes: Optional[List[Dict[str, Any]]] = None

class RecommendationResponse(BaseModel):
    game_id: int
    recommended_games: List[GameBase]

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the IGDB Game Recommendation API"}

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

# Search games endpoint
@app.get("/games/search", response_model=List[GameBase])
async def search_games(
    query: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(3, ge=1, le=50, description="Maximum number of results"),
):
    """
    Search for games by name.
    """
    try:
        logger.info(f"Searching for games with query: '{query}', limit: {limit}")
        
        # Use recommendation service to search games
        games = recommendation_service.search_games(query, limit)
        
        if not games:
            logger.info(f"No games found for query: '{query}'")
            return []
        
        # Convert to GameBase format
        result_games = []
        for game in games:
            result_games.append({
                "id": game["id"],
                "name": game["name"],
                "summary": game["summary"],
                "rating": game["rating"],
                "first_release_date": game["first_release_date"],
                "cover_url": game["cover_url"]
            })
        
        logger.info(f"Found {len(result_games)} games for query: '{query}'")
        return result_games
    except Exception as e:
        logger.error(f"Error searching games for query '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search games: {str(e)}")

# Get game by ID endpoint
@app.get("/games/{game_id}", response_model=GameDetail)
async def get_game(game_id: int):
    """
    Get detailed information about a specific game.
    """
    try:
        # Use recommendation service to get game details
        games = recommendation_service.get_game_details([str(game_id)])
        
        if not games:
            raise HTTPException(status_code=404, detail="Game not found")
        
        game = games[0]
        
        # Convert to GameDetail format
        game_detail = {
            "id": game["id"],
            "name": game["name"],
            "summary": game["summary"],
            "storyline": game["summary"],  # Use summary as storyline for now
            "rating": game["rating"],
            "rating_count": None,  # Not available in current data
            "aggregated_rating": game["rating"],
            "aggregated_rating_count": None,  # Not available in current data
            "first_release_date": game["first_release_date"],
            "cover_url": game["cover_url"],
            "genres": [{"id": i, "name": genre} for i, genre in enumerate(game["genres"])],
            "platforms": [{"id": i, "name": platform} for i, platform in enumerate(game["platforms"])],
            "themes": [{"id": i, "name": theme} for i, theme in enumerate(game["themes"])]
        }
        
        return game_detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting game {game_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get recommendations endpoint
@app.get("/recommendations/{game_id}", response_model=RecommendationResponse)
async def get_recommendations(
    game_id: int,
    limit: int = Query(5, ge=1, le=20, description="Maximum number of recommendations"),
):
    """
    Get game recommendations based on a specific game.
    """
    try:
        # Get similar games using ML model
        similar_games = recommendation_service.get_similar_games(str(game_id), limit)
        
        if not similar_games:
            return {"game_id": game_id, "recommended_games": []}
        
        # Get game IDs from recommendations
        recommended_game_ids = [rec["game_id"] for rec in similar_games]
        
        # Get detailed game information
        games_details = recommendation_service.get_game_details(recommended_game_ids)
        
        # Convert to GameBase format
        recommended_games = []
        for game in games_details:
            recommended_games.append({
                "id": game["id"],
                "name": game["name"],
                "summary": game["summary"],
                "rating": game["rating"],
                "first_release_date": game["first_release_date"],
                "cover_url": game["cover_url"]
            })
        
        return {
            "game_id": game_id,
            "recommended_games": recommended_games,
        }
    except Exception as e:
        logger.error(f"Error getting recommendations for game {game_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
