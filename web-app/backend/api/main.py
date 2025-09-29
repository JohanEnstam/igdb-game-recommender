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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
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
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
):
    """
    Search for games by name.
    """
    try:
        # Mock data for now
        mock_games = [
            {
                "id": 1,
                "name": "The Legend of Zelda: Breath of the Wild",
                "summary": "Step into a world of discovery, exploration, and adventure in The Legend of Zelda: Breath of the Wild.",
                "rating": 9.2,
                "first_release_date": "2017-03-03",
                "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co3p2d.jpg",
            },
            {
                "id": 2,
                "name": "The Witcher 3: Wild Hunt",
                "summary": "The Witcher 3: Wild Hunt is an action role-playing game set in an open world environment.",
                "rating": 9.3,
                "first_release_date": "2015-05-19",
                "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1wyy.jpg",
            },
            {
                "id": 3,
                "name": "Red Dead Redemption 2",
                "summary": "Red Dead Redemption 2 is an epic tale of life in America's unforgiving heartland.",
                "rating": 9.4,
                "first_release_date": "2018-10-26",
                "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1q9f.jpg",
            },
        ]
        
        # Filter mock data based on query
        filtered_games = [
            game for game in mock_games 
            if query.lower() in game["name"].lower()
        ][:limit]
        
        return filtered_games
    except Exception as e:
        logger.error(f"Error searching games: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get game by ID endpoint
@app.get("/games/{game_id}", response_model=GameDetail)
async def get_game(game_id: int):
    """
    Get detailed information about a specific game.
    """
    try:
        # Mock data for now
        mock_games = {
            1: {
                "id": 1,
                "name": "The Legend of Zelda: Breath of the Wild",
                "summary": "Step into a world of discovery, exploration, and adventure in The Legend of Zelda: Breath of the Wild.",
                "storyline": "Forget everything you know about The Legend of Zelda games. Step into a world of discovery, exploration, and adventure in The Legend of Zelda: Breath of the Wild, a boundary-breaking new game in the acclaimed series.",
                "rating": 9.2,
                "rating_count": 1234,
                "aggregated_rating": 9.5,
                "aggregated_rating_count": 123,
                "first_release_date": "2017-03-03",
                "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co3p2d.jpg",
                "genres": [
                    {"id": 12, "name": "Adventure"},
                    {"id": 31, "name": "RPG"},
                ],
                "platforms": [
                    {"id": 41, "name": "Nintendo Switch"},
                    {"id": 47, "name": "Wii U"},
                ],
                "themes": [
                    {"id": 1, "name": "Fantasy"},
                    {"id": 39, "name": "Open World"},
                ],
            },
            2: {
                "id": 2,
                "name": "The Witcher 3: Wild Hunt",
                "summary": "The Witcher 3: Wild Hunt is an action role-playing game set in an open world environment.",
                "storyline": "The Witcher 3: Wild Hunt is a story-driven, next-generation open world role-playing game set in a visually stunning fantasy universe full of meaningful choices and impactful consequences.",
                "rating": 9.3,
                "rating_count": 2345,
                "aggregated_rating": 9.4,
                "aggregated_rating_count": 234,
                "first_release_date": "2015-05-19",
                "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1wyy.jpg",
                "genres": [
                    {"id": 12, "name": "Adventure"},
                    {"id": 31, "name": "RPG"},
                ],
                "platforms": [
                    {"id": 6, "name": "PC"},
                    {"id": 48, "name": "PlayStation 4"},
                    {"id": 49, "name": "Xbox One"},
                ],
                "themes": [
                    {"id": 1, "name": "Fantasy"},
                    {"id": 39, "name": "Open World"},
                ],
            },
            3: {
                "id": 3,
                "name": "Red Dead Redemption 2",
                "summary": "Red Dead Redemption 2 is an epic tale of life in America's unforgiving heartland.",
                "storyline": "America, 1899. The end of the wild west era has begun as lawmen hunt down the last remaining outlaw gangs. Those who will not surrender or succumb are killed.",
                "rating": 9.4,
                "rating_count": 3456,
                "aggregated_rating": 9.6,
                "aggregated_rating_count": 345,
                "first_release_date": "2018-10-26",
                "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1q9f.jpg",
                "genres": [
                    {"id": 12, "name": "Adventure"},
                    {"id": 31, "name": "RPG"},
                    {"id": 5, "name": "Shooter"},
                ],
                "platforms": [
                    {"id": 6, "name": "PC"},
                    {"id": 48, "name": "PlayStation 4"},
                    {"id": 49, "name": "Xbox One"},
                ],
                "themes": [
                    {"id": 39, "name": "Open World"},
                    {"id": 28, "name": "Western"},
                ],
            },
        }
        
        if game_id not in mock_games:
            raise HTTPException(status_code=404, detail="Game not found")
        
        return mock_games[game_id]
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
        # Mock data for now
        mock_games = {
            1: [  # Recommendations for Zelda: BOTW
                {
                    "id": 2,
                    "name": "The Witcher 3: Wild Hunt",
                    "summary": "The Witcher 3: Wild Hunt is an action role-playing game set in an open world environment.",
                    "rating": 9.3,
                    "first_release_date": "2015-05-19",
                    "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1wyy.jpg",
                },
                {
                    "id": 3,
                    "name": "Red Dead Redemption 2",
                    "summary": "Red Dead Redemption 2 is an epic tale of life in America's unforgiving heartland.",
                    "rating": 9.4,
                    "first_release_date": "2018-10-26",
                    "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1q9f.jpg",
                },
                {
                    "id": 4,
                    "name": "Horizon Zero Dawn",
                    "summary": "Horizon Zero Dawn is an action role-playing game set in a post-apocalyptic world.",
                    "rating": 9.0,
                    "first_release_date": "2017-02-28",
                    "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1izx.jpg",
                },
            ],
            2: [  # Recommendations for The Witcher 3
                {
                    "id": 1,
                    "name": "The Legend of Zelda: Breath of the Wild",
                    "summary": "Step into a world of discovery, exploration, and adventure in The Legend of Zelda: Breath of the Wild.",
                    "rating": 9.2,
                    "first_release_date": "2017-03-03",
                    "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co3p2d.jpg",
                },
                {
                    "id": 3,
                    "name": "Red Dead Redemption 2",
                    "summary": "Red Dead Redemption 2 is an epic tale of life in America's unforgiving heartland.",
                    "rating": 9.4,
                    "first_release_date": "2018-10-26",
                    "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1q9f.jpg",
                },
                {
                    "id": 5,
                    "name": "God of War",
                    "summary": "God of War is an action-adventure game developed by Santa Monica Studio and published by Sony Interactive Entertainment.",
                    "rating": 9.3,
                    "first_release_date": "2018-04-20",
                    "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1tmu.jpg",
                },
            ],
            3: [  # Recommendations for Red Dead Redemption 2
                {
                    "id": 2,
                    "name": "The Witcher 3: Wild Hunt",
                    "summary": "The Witcher 3: Wild Hunt is an action role-playing game set in an open world environment.",
                    "rating": 9.3,
                    "first_release_date": "2015-05-19",
                    "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1wyy.jpg",
                },
                {
                    "id": 6,
                    "name": "Grand Theft Auto V",
                    "summary": "Grand Theft Auto V is an action-adventure game set in an open world environment.",
                    "rating": 9.1,
                    "first_release_date": "2013-09-17",
                    "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1nt4.jpg",
                },
                {
                    "id": 7,
                    "name": "Assassin's Creed Odyssey",
                    "summary": "Assassin's Creed Odyssey is an action role-playing game set in ancient Greece.",
                    "rating": 8.8,
                    "first_release_date": "2018-10-05",
                    "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1zkt.jpg",
                },
            ],
        }
        
        if game_id not in mock_games:
            return {"game_id": game_id, "recommended_games": []}
        
        return {
            "game_id": game_id,
            "recommended_games": mock_games[game_id][:limit],
        }
    except Exception as e:
        logger.error(f"Error getting recommendations for game {game_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
