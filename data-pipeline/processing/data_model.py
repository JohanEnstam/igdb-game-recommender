"""
Modul för att definiera datamodellen för spel och spelrelationer.

Denna modul innehåller klasser och funktioner för att representera
spel, spelrelationer och spelgrupper i en strukturerad datamodell.
"""

from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class Game:
    """Representerar ett spel i den rensade datamodellen."""
    
    game_id: str
    canonical_name: str
    display_name: str
    release_date: Optional[datetime] = None
    summary: Optional[str] = None
    rating: Optional[float] = None
    cover_url: Optional[str] = None
    has_complete_data: bool = False
    quality_score: float = 0.0
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    @classmethod
    def from_igdb_game(cls, game: Dict[str, Any], canonical_name: str, quality_score: float) -> 'Game':
        """
        Skapa ett Game-objekt från IGDB-speldata.
        
        Args:
            game: IGDB-speldata
            canonical_name: Det kanoniska namnet för spelet
            quality_score: Kvalitetspoäng för spelet
            
        Returns:
            Ett Game-objekt
        """
        release_date = None
        if game.get("first_release_date"):
            release_date = datetime.fromtimestamp(game["first_release_date"])
            
        cover_url = None
        if game.get("cover") and game["cover"].get("url"):
            cover_url = game["cover"]["url"]
            
        return cls(
            game_id=str(game["id"]),
            canonical_name=canonical_name,
            display_name=game["name"],
            release_date=release_date,
            summary=game.get("summary"),
            rating=game.get("rating"),
            cover_url=cover_url,
            has_complete_data=bool(game.get("summary") and cover_url),
            quality_score=quality_score
        )


@dataclass
class GameRelationship:
    """Representerar en relation mellan två spel."""
    
    source_game_id: str
    target_game_id: str
    relationship_type: str  # "duplicate_of", "version_of", "sequel_to", "in_series", "dlc_for", etc.
    confidence_score: float
    created_at: datetime = datetime.now()


@dataclass
class GameGroup:
    """Representerar en grupp av relaterade spel."""
    
    group_id: str
    group_type: str  # "version_group", "series", "franchise"
    canonical_name: str
    representative_game_id: str
    game_count: int
    created_at: datetime = datetime.now()
    
    @classmethod
    def create_version_group(cls, canonical_name: str, representative_game_id: str, game_count: int) -> 'GameGroup':
        """
        Skapa en versionsgrupp.
        
        Args:
            canonical_name: Det kanoniska namnet för gruppen
            representative_game_id: ID för det representativa spelet
            game_count: Antal spel i gruppen
            
        Returns:
            Ett GameGroup-objekt
        """
        return cls(
            group_id=str(uuid.uuid4()),
            group_type="version_group",
            canonical_name=canonical_name,
            representative_game_id=representative_game_id,
            game_count=game_count
        )
    
    @classmethod
    def create_series_group(cls, series_name: str, representative_game_id: str, game_count: int) -> 'GameGroup':
        """
        Skapa en seriegrupp.
        
        Args:
            series_name: Namnet på spelserien
            representative_game_id: ID för det representativa spelet
            game_count: Antal spel i gruppen
            
        Returns:
            Ett GameGroup-objekt
        """
        return cls(
            group_id=str(uuid.uuid4()),
            group_type="series",
            canonical_name=series_name,
            representative_game_id=representative_game_id,
            game_count=game_count
        )


@dataclass
class GameGroupMember:
    """Representerar ett spels medlemskap i en grupp."""
    
    group_id: str
    game_id: str
    is_primary: bool
    created_at: datetime = datetime.now()


def convert_to_bigquery_schema(games: List[Game], relationships: List[GameRelationship], 
                              groups: List[GameGroup], members: List[GameGroupMember]) -> Dict[str, List[Dict]]:
    """
    Konvertera datamodellen till BigQuery-schema.
    
    Args:
        games: Lista med Game-objekt
        relationships: Lista med GameRelationship-objekt
        groups: Lista med GameGroup-objekt
        members: Lista med GameGroupMember-objekt
        
    Returns:
        Dictionary med tabellnamn och rader för BigQuery
    """
    bq_data = {
        "games": [],
        "game_relationships": [],
        "game_groups": [],
        "game_group_members": []
    }
    
    # Konvertera spel
    for game in games:
        bq_data["games"].append({
            "game_id": game.game_id,
            "canonical_name": game.canonical_name,
            "display_name": game.display_name,
            "release_date": game.release_date.isoformat() if game.release_date else None,
            "summary": game.summary,
            "rating": game.rating,
            "cover_url": game.cover_url,
            "has_complete_data": game.has_complete_data,
            "quality_score": game.quality_score,
            "created_at": game.created_at.isoformat(),
            "updated_at": game.updated_at.isoformat()
        })
    
    # Konvertera relationer
    for rel in relationships:
        bq_data["game_relationships"].append({
            "source_game_id": rel.source_game_id,
            "target_game_id": rel.target_game_id,
            "relationship_type": rel.relationship_type,
            "confidence_score": rel.confidence_score,
            "created_at": rel.created_at.isoformat()
        })
    
    # Konvertera grupper
    for group in groups:
        bq_data["game_groups"].append({
            "group_id": group.group_id,
            "group_type": group.group_type,
            "canonical_name": group.canonical_name,
            "representative_game_id": group.representative_game_id,
            "game_count": group.game_count,
            "created_at": group.created_at.isoformat()
        })
    
    # Konvertera gruppmedlemmar
    for member in members:
        bq_data["game_group_members"].append({
            "group_id": member.group_id,
            "game_id": member.game_id,
            "is_primary": member.is_primary,
            "created_at": member.created_at.isoformat()
        })
    
    return bq_data
