"""
Test script för IGDB Game Recommendation API.

Detta script testar API:et lokalt för att verifiera att ML-integrationen fungerar.
"""

import requests
import json
import time
import sys

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_search_games():
    """Test game search endpoint"""
    print("\nTesting game search...")
    try:
        response = requests.get(f"{BASE_URL}/games/search", params={"query": "zelda", "limit": 5})
        print(f"Search games: {response.status_code}")
        if response.status_code == 200:
            games = response.json()
            print(f"Found {len(games)} games")
            for game in games[:3]:
                print(f"  - {game['name']} (ID: {game['id']})")
            return games
        else:
            print(f"Search failed: {response.text}")
            return []
    except Exception as e:
        print(f"Search games failed: {e}")
        return []

def test_get_game(game_id):
    """Test get game by ID endpoint"""
    print(f"\nTesting get game {game_id}...")
    try:
        response = requests.get(f"{BASE_URL}/games/{game_id}")
        print(f"Get game: {response.status_code}")
        if response.status_code == 200:
            game = response.json()
            print(f"Game: {game['name']}")
            print(f"Summary: {game['summary'][:100]}...")
            return game
        else:
            print(f"Get game failed: {response.text}")
            return None
    except Exception as e:
        print(f"Get game failed: {e}")
        return None

def test_recommendations(game_id):
    """Test recommendations endpoint"""
    print(f"\nTesting recommendations for game {game_id}...")
    try:
        response = requests.get(f"{BASE_URL}/recommendations/{game_id}", params={"limit": 5})
        print(f"Recommendations: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            recommendations = result.get("recommended_games", [])
            print(f"Found {len(recommendations)} recommendations")
            for i, game in enumerate(recommendations):
                print(f"  {i+1}. {game['name']} (ID: {game['id']})")
            return recommendations
        else:
            print(f"Recommendations failed: {response.text}")
            return []
    except Exception as e:
        print(f"Recommendations failed: {e}")
        return []

def main():
    """Main test function"""
    print("IGDB Game Recommendation API Test")
    print("=" * 40)
    
    # Test health
    if not test_health():
        print("API is not running. Please start the API first.")
        sys.exit(1)
    
    # Test search games
    games = test_search_games()
    if not games:
        print("No games found. API might not be properly initialized.")
        sys.exit(1)
    
    # Test get game details
    test_game = games[0]
    game_details = test_get_game(test_game['id'])
    if not game_details:
        print("Failed to get game details.")
        sys.exit(1)
    
    # Test recommendations
    recommendations = test_recommendations(test_game['id'])
    if not recommendations:
        print("No recommendations found. ML model might not be loaded.")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("All tests passed! API is working correctly.")
    print(f"Tested with game: {test_game['name']} (ID: {test_game['id']})")
    print(f"Found {len(recommendations)} recommendations")

if __name__ == "__main__":
    main()
