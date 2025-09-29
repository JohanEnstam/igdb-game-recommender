"""
Modul för att gruppera spel baserat på olika kriterier.

Denna modul innehåller funktioner för att identifiera och gruppera spel
som är dubbletter, olika versioner av samma spel, eller tillhör samma serie.
"""

import re
from typing import Dict, List, Set, Tuple, Any, DefaultDict
from collections import defaultdict
import uuid

import name_processor

# Import specific functions
extract_canonical_name = name_processor.extract_canonical_name
extract_series_name = name_processor.extract_series_name
is_likely_same_game = name_processor.is_likely_same_game


class GameGrouper:
    """Klass för att gruppera spel baserat på olika kriterier."""
    
    def __init__(self):
        """Initiera GameGrouper."""
        self.exact_duplicates = defaultdict(list)  # Spel med exakt samma namn
        self.version_groups = defaultdict(list)    # Olika versioner av samma spel
        self.series_groups = defaultdict(list)     # Spel i samma serie
        
    def process_games(self, games: List[Dict[str, Any]]) -> None:
        """
        Bearbeta en lista med spel och gruppera dem.
        
        Args:
            games: Lista med spel att gruppera
        """
        # Skapa en dictionary med namn som nyckel för snabbare sökning
        name_to_games = defaultdict(list)
        for game in games:
            if "name" in game and game["name"]:
                name_to_games[game["name"].lower()].append(game)
        
        # Hitta exakta dubbletter (samma namn)
        self.exact_duplicates = {name: games_list for name, games_list in name_to_games.items() 
                               if len(games_list) > 1}
        
        # Hitta potentiella versioner/utgåvor av samma spel
        base_name_to_games = defaultdict(list)
        for game in games:
            if "name" not in game or not game["name"]:
                continue
                
            # Extrahera basnamnet genom att ta bort versionsindikatorer
            base_name = extract_canonical_name(game["name"])
            
            if base_name and base_name != game["name"].lower() and len(base_name) > 3:
                base_name_to_games[base_name].append(game)
        
        # Filtrera för att bara behålla basnamn med flera spel
        self.version_groups = {name: games_list for name, games_list in base_name_to_games.items() 
                             if len(games_list) > 1}
        
        # Hitta spel i samma serie
        series_to_games = defaultdict(list)
        for game in games:
            if "name" not in game or not game["name"]:
                continue
                
            series_name = extract_series_name(game["name"])
            if series_name:
                series_to_games[series_name].append(game)
        
        # Filtrera för att bara behålla serier med flera spel
        self.series_groups = {name: games_list for name, games_list in series_to_games.items() 
                            if len(games_list) > 1}
    
    def get_game_relationships(self) -> List[Dict[str, Any]]:
        """
        Generera relationsinformation mellan spel baserat på grupperingen.
        
        Returns:
            Lista med relationer mellan spel
        """
        relationships = []
        
        # Hantera exakta dubbletter
        for name, games in self.exact_duplicates.items():
            if len(games) <= 1:
                continue
                
            # Välj det första spelet som referens
            reference_game = games[0]
            
            for game in games[1:]:
                relationships.append({
                    "source_game_id": game["id"],
                    "target_game_id": reference_game["id"],
                    "relationship_type": "duplicate_of",
                    "confidence_score": 1.0
                })
        
        # Hantera versionsgrupper
        for base_name, games in self.version_groups.items():
            if len(games) <= 1:
                continue
                
            # Sortera spel efter utgivningsdatum om tillgängligt
            sorted_games = sorted(
                games, 
                key=lambda g: g.get("first_release_date", 0),
                reverse=False  # Äldsta först
            )
            
            # Välj det äldsta spelet som referens
            reference_game = sorted_games[0]
            
            for game in sorted_games[1:]:
                relationships.append({
                    "source_game_id": game["id"],
                    "target_game_id": reference_game["id"],
                    "relationship_type": "version_of",
                    "confidence_score": 0.9
                })
        
        # Hantera spelserier
        for series_name, games in self.series_groups.items():
            if len(games) <= 1:
                continue
                
            # Sortera spel efter utgivningsdatum om tillgängligt
            sorted_games = sorted(
                games, 
                key=lambda g: g.get("first_release_date", 0),
                reverse=False  # Äldsta först
            )
            
            # Skapa relationer mellan spel i serien
            for i in range(len(sorted_games) - 1):
                current_game = sorted_games[i]
                next_game = sorted_games[i + 1]
                
                relationships.append({
                    "source_game_id": next_game["id"],
                    "target_game_id": current_game["id"],
                    "relationship_type": "sequel_to",
                    "confidence_score": 0.8
                })
        
        return relationships
    
    def get_game_groups(self) -> List[Dict[str, Any]]:
        """
        Generera gruppinformation för spel baserat på grupperingen.
        
        Returns:
            Lista med spelgrupper
        """
        groups = []
        
        # Skapa grupper för versioner
        for base_name, games in self.version_groups.items():
            if len(games) <= 1:
                continue
                
            group_id = str(uuid.uuid4())
            groups.append({
                "group_id": group_id,
                "group_type": "version_group",
                "canonical_name": base_name,
                "representative_game_id": games[0]["id"],  # Använd första spelet som representant
                "game_count": len(games)
            })
        
        # Skapa grupper för spelserier
        for series_name, games in self.series_groups.items():
            if len(games) <= 1:
                continue
                
            group_id = str(uuid.uuid4())
            groups.append({
                "group_id": group_id,
                "group_type": "series",
                "canonical_name": series_name,
                "representative_game_id": games[0]["id"],  # Använd första spelet som representant
                "game_count": len(games)
            })
        
        return groups
    
    def get_group_members(self) -> List[Dict[str, Any]]:
        """
        Generera medlemsinformation för spelgrupper.
        
        Returns:
            Lista med gruppmedlemskap för spel
        """
        members = []
        
        # Skapa gruppmedlemskap för versioner
        for base_name, games in self.version_groups.items():
            if len(games) <= 1:
                continue
                
            group_id = str(uuid.uuid4())  # Samma som i get_game_groups
            
            for i, game in enumerate(games):
                members.append({
                    "group_id": group_id,
                    "game_id": game["id"],
                    "is_primary": i == 0  # Första spelet är primärt
                })
        
        # Skapa gruppmedlemskap för spelserier
        for series_name, games in self.series_groups.items():
            if len(games) <= 1:
                continue
                
            group_id = str(uuid.uuid4())  # Samma som i get_game_groups
            
            for i, game in enumerate(games):
                members.append({
                    "group_id": group_id,
                    "game_id": game["id"],
                    "is_primary": i == 0  # Första spelet är primärt
                })
        
        return members
