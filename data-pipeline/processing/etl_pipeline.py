"""
ETL-pipeline för datarensning.

Denna modul innehåller klasser och funktioner för att extrahera, transformera
och ladda IGDB-speldata med datarensning.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

import name_processor
import game_grouper
import quality_scorer
import data_model
import utils

# Import specific functions
extract_canonical_name = name_processor.extract_canonical_name
extract_series_name = name_processor.extract_series_name
GameGrouper = game_grouper.GameGrouper
calculate_quality_score = quality_scorer.calculate_quality_score
select_representative_game = quality_scorer.select_representative_game
Game = data_model.Game
GameRelationship = data_model.GameRelationship
GameGroup = data_model.GameGroup
GameGroupMember = data_model.GameGroupMember
convert_to_bigquery_schema = data_model.convert_to_bigquery_schema
setup_logger = utils.setup_logger
load_games_from_directory = utils.load_games_from_directory
save_to_json = utils.save_to_json


class DataCleaningPipeline:
    """Pipeline för datarensning av IGDB-speldata."""
    
    def __init__(self, input_dir: str, output_dir: str, log_level: int = logging.INFO):
        """
        Initiera datarensningspipelinen.
        
        Args:
            input_dir: Katalog med rådata från IGDB
            output_dir: Katalog där rensad data ska sparas
            log_level: Loggnivå
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.logger = setup_logger("data_cleaning_pipeline", log_level)
        
        # Skapa output-katalog om den inte finns
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initiera datastrukturer
        self.raw_games = []
        self.cleaned_games = []
        self.game_relationships = []
        self.game_groups = []
        self.group_members = []
    
    def extract(self) -> None:
        """Extrahera rådata från input-katalogen."""
        self.logger.info(f"Extraherar data från {self.input_dir}")
        
        if not self.input_dir.exists():
            self.logger.error(f"Input-katalog {self.input_dir} finns inte")
            sys.exit(1)
        
        # Ladda alla spel från JSON-filer
        self.raw_games = load_games_from_directory(self.input_dir)
        
        self.logger.info(f"Laddade {len(self.raw_games)} spel från {self.input_dir}")
    
    def transform(self) -> None:
        """Transformera rådata till rensad data."""
        self.logger.info("Transformerar data")
        
        if not self.raw_games:
            self.logger.error("Inga spel att transformera")
            sys.exit(1)
        
        # Steg 1: Extrahera kanoniska namn
        self.logger.info("Extraherar kanoniska namn")
        games_with_canonical_names = []
        
        for game in self.raw_games:
            if "name" not in game or not game["name"]:
                continue
                
            canonical_name = extract_canonical_name(game["name"])
            quality_score = calculate_quality_score(game)
            
            games_with_canonical_names.append({
                "game": game,
                "canonical_name": canonical_name,
                "quality_score": quality_score
            })
        
        # Steg 2: Gruppera spel
        self.logger.info("Grupperar spel")
        grouper = GameGrouper()
        grouper.process_games([item["game"] for item in games_with_canonical_names])
        
        # Steg 3: Skapa datamodell
        self.logger.info("Skapar datamodell")
        
        # Skapa Game-objekt
        for item in games_with_canonical_names:
            game = Game.from_igdb_game(
                item["game"],
                item["canonical_name"],
                item["quality_score"]
            )
            self.cleaned_games.append(game)
        
        # Skapa relationer
        raw_relationships = grouper.get_game_relationships()
        for rel in raw_relationships:
            relationship = GameRelationship(
                source_game_id=rel["source_game_id"],
                target_game_id=rel["target_game_id"],
                relationship_type=rel["relationship_type"],
                confidence_score=rel["confidence_score"]
            )
            self.game_relationships.append(relationship)
        
        # Skapa grupper och medlemskap
        raw_groups = grouper.get_game_groups()
        raw_members = grouper.get_group_members()
        
        # Skapa unika grupp-ID:n
        group_ids = {}
        
        for group in raw_groups:
            group_obj = GameGroup(
                group_id=group["group_id"],
                group_type=group["group_type"],
                canonical_name=group["canonical_name"],
                representative_game_id=group["representative_game_id"],
                game_count=group["game_count"]
            )
            self.game_groups.append(group_obj)
            group_ids[group["canonical_name"]] = group["group_id"]
        
        for member in raw_members:
            member_obj = GameGroupMember(
                group_id=member["group_id"],
                game_id=member["game_id"],
                is_primary=member["is_primary"]
            )
            self.group_members.append(member_obj)
        
        self.logger.info(f"Transformering klar: {len(self.cleaned_games)} spel, "
                        f"{len(self.game_relationships)} relationer, "
                        f"{len(self.game_groups)} grupper, "
                        f"{len(self.group_members)} gruppmedlemmar")
    
    def load(self) -> None:
        """Ladda rensad data till output-katalogen."""
        self.logger.info(f"Sparar rensad data till {self.output_dir}")
        
        # Konvertera till BigQuery-schema
        bq_data = convert_to_bigquery_schema(
            self.cleaned_games,
            self.game_relationships,
            self.game_groups,
            self.group_members
        )
        
        # Spara varje tabell som en separat JSON-fil
        for table_name, rows in bq_data.items():
            file_path = self.output_dir / f"{table_name}.json"
            save_to_json(rows, file_path)
            self.logger.info(f"Sparade {len(rows)} rader till {file_path}")
    
    def run(self) -> None:
        """Kör hela ETL-pipelinen."""
        self.logger.info("Startar datarensningspipeline")
        
        start_time = datetime.now()
        
        self.extract()
        self.transform()
        self.load()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.logger.info(f"Datarensningspipeline slutförd på {duration:.1f} sekunder")


def main():
    """Huvudfunktion för att köra datarensningspipelinen från kommandoraden."""
    import argparse
    import os
    
    # Kontrollera om virtuell miljö är aktiverad
    if not os.environ.get("VIRTUAL_ENV"):
        print("VARNING: Virtuell miljö är inte aktiverad!")
        print("Aktivera virtuell miljö med: source ./activate.sh")
        print("Avbryter...")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="Rensa IGDB-speldata")
    parser.add_argument("--input", type=str, required=True, help="Katalog med rådata")
    parser.add_argument("--output", type=str, required=True, help="Katalog för rensad data")
    parser.add_argument("--log-level", type=str, default="INFO", help="Loggnivå")
    
    args = parser.parse_args()
    
    # Konvertera loggnivå från sträng till konstant
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    
    # Skapa och kör pipeline
    pipeline = DataCleaningPipeline(args.input, args.output, log_level)
    pipeline.run()


if __name__ == "__main__":
    main()
