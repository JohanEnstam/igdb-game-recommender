"""
Modul för att beräkna kvalitetspoäng för spel.

Denna modul innehåller funktioner för att beräkna kvalitetspoäng för spel
baserat på tillgängliga metadata och attribut.
"""

from typing import Dict, Any, List, Set


def calculate_quality_score(game: Dict[str, Any]) -> float:
    """
    Beräkna en kvalitetspoäng för ett spel baserat på tillgängliga metadata.
    
    Args:
        game: En dictionary med speldata
        
    Returns:
        En kvalitetspoäng mellan 0 och 100
    """
    score = 0
    weights = {
        "has_name": 1.0,
        "has_summary": 0.8,
        "has_cover": 0.7,
        "has_release_date": 0.6,
        "has_rating": 0.5,
        "has_genres": 0.4,
        "has_platforms": 0.3,
        "has_themes": 0.2
    }
    
    if game.get("name"):
        score += weights["has_name"]
    if game.get("summary"):
        score += weights["has_summary"]
    if game.get("cover"):
        score += weights["has_cover"]
    if game.get("first_release_date"):
        score += weights["has_release_date"]
    if game.get("rating"):
        score += weights["has_rating"]
    if game.get("genres"):
        score += weights["has_genres"]
    if game.get("platforms"):
        score += weights["has_platforms"]
    if game.get("themes"):
        score += weights["has_themes"]
    
    # Normalisera till 0-100
    max_possible = sum(weights.values())
    normalized_score = (score / max_possible) * 100
    
    return normalized_score


def has_complete_data(game: Dict[str, Any]) -> bool:
    """
    Avgör om ett spel har tillräckligt komplett data för att användas i rekommendationer.
    
    Args:
        game: En dictionary med speldata
        
    Returns:
        True om spelet har tillräckligt komplett data, annars False
    """
    # Krav för att ett spel ska anses ha komplett data
    required_fields = ["name", "summary", "cover"]
    optional_fields = ["first_release_date", "rating", "genres", "platforms"]
    
    # Kontrollera att alla obligatoriska fält finns
    for field in required_fields:
        if not game.get(field):
            return False
    
    # Kontrollera att minst 2 av de valfria fälten finns
    optional_count = sum(1 for field in optional_fields if game.get(field))
    
    return optional_count >= 2


def select_representative_game(games: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Välj det mest representativa spelet från en grupp av liknande spel.
    
    Args:
        games: En lista med spel som anses vara samma eller liknande
        
    Returns:
        Det spel som har bäst kvalitet och mest komplett data
    """
    if not games:
        raise ValueError("Kan inte välja representativt spel från en tom lista")
    
    if len(games) == 1:
        return games[0]
    
    # Beräkna kvalitetspoäng för varje spel
    games_with_scores = [(game, calculate_quality_score(game)) for game in games]
    
    # Sortera efter kvalitetspoäng (högst först)
    sorted_games = sorted(games_with_scores, key=lambda x: x[1], reverse=True)
    
    return sorted_games[0][0]
