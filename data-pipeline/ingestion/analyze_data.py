#!/usr/bin/env python3
"""
IGDB Data Analysis Script

Detta skript analyserar data som hämtats från IGDB API för att ge insikter
om datakvalitet, struktur och statistik.

Användning:
    python analyze_data.py --input INPUT_DIR

Exempel:
    python analyze_data.py --input ./data
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter

import pandas as pd
import numpy as np

# Helper function för att konvertera NumPy-typer till Python-standardtyper
def convert_to_serializable(obj):
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parsa kommandoradsargument"""
    parser = argparse.ArgumentParser(description="Analysera IGDB speldata")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Katalog där data är sparad"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./analysis",
        help="Katalog där analysresultat ska sparas (default: ./analysis)"
    )
    return parser.parse_args()

def load_games(input_dir: Path) -> List[Dict[str, Any]]:
    """Ladda alla spel från JSON-filer"""
    games = []
    batch_files = sorted([f for f in input_dir.glob("games_batch_*.json")])
    
    if not batch_files:
        logger.error(f"Inga batch-filer hittades i {input_dir}")
        sys.exit(1)
    
    for batch_file in batch_files:
        logger.info(f"Laddar {batch_file}")
        with open(batch_file, "r", encoding="utf-8") as f:
            batch_games = json.load(f)
            games.extend(batch_games)
    
    logger.info(f"Laddade totalt {len(games)} spel")
    return games

def analyze_games(games: List[Dict[str, Any]], output_dir: Path) -> None:
    """Analysera speldata och generera statistik"""
    # Skapa output-katalog om den inte finns
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Konvertera till DataFrame för enklare analys
    df = pd.DataFrame(games)
    
    # Grundläggande statistik
    stats = {
        "total_games": len(games),
        "games_with_rating": df["rating"].notna().sum(),
        "games_with_summary": df["summary"].notna().sum(),
        "games_with_cover": df["cover"].notna().sum(),
        "games_with_release_date": df["first_release_date"].notna().sum(),
        "games_with_genres": sum(1 for g in games if g.get("genres")),
        "games_with_platforms": sum(1 for g in games if g.get("platforms")),
        "games_with_themes": sum(1 for g in games if g.get("themes")),
    }
    
    # Spara grundläggande statistik
    with open(output_dir / "basic_stats.json", "w", encoding="utf-8") as f:
        json.dump({k: convert_to_serializable(v) for k, v in stats.items()}, f, ensure_ascii=False, indent=2)
    
    # Analysera saknade värden
    missing_values = df.isna().sum().to_dict()
    with open(output_dir / "missing_values.json", "w", encoding="utf-8") as f:
        json.dump({k: convert_to_serializable(v) for k, v in missing_values.items()}, f, ensure_ascii=False, indent=2)
    
    # Analysera release years
    if "first_release_date" in df.columns:
        # Konvertera UNIX timestamp till år
        df["release_year"] = pd.to_datetime(df["first_release_date"], unit="s").dt.year
        year_counts = df["release_year"].value_counts().sort_index().to_dict()
        with open(output_dir / "release_years.json", "w", encoding="utf-8") as f:
            json.dump({convert_to_serializable(k): convert_to_serializable(v) for k, v in year_counts.items()}, f, ensure_ascii=False, indent=2)
    
    # Analysera genres
    genres = []
    for game in games:
        if game.get("genres"):
            for genre in game["genres"]:
                genres.append(genre.get("name", "Unknown"))
    
    genre_counts = Counter(genres)
    with open(output_dir / "genre_counts.json", "w", encoding="utf-8") as f:
        json.dump(dict(genre_counts.most_common()), f, ensure_ascii=False, indent=2)
    
    # Analysera platforms
    platforms = []
    for game in games:
        if game.get("platforms"):
            for platform in game["platforms"]:
                platforms.append(platform.get("name", "Unknown"))
    
    platform_counts = Counter(platforms)
    with open(output_dir / "platform_counts.json", "w", encoding="utf-8") as f:
        json.dump(dict(platform_counts.most_common()), f, ensure_ascii=False, indent=2)
    
    # Analysera themes
    themes = []
    for game in games:
        if game.get("themes"):
            for theme in game["themes"]:
                themes.append(theme.get("name", "Unknown"))
    
    theme_counts = Counter(themes)
    with open(output_dir / "theme_counts.json", "w", encoding="utf-8") as f:
        json.dump(dict(theme_counts.most_common()), f, ensure_ascii=False, indent=2)
    
    # Analysera ratings
    if "rating" in df.columns:
        rating_stats = df["rating"].describe().to_dict()
        with open(output_dir / "rating_stats.json", "w", encoding="utf-8") as f:
            json.dump({k: convert_to_serializable(v) for k, v in rating_stats.items()}, f, ensure_ascii=False, indent=2)
    
    # Generera exempel på speldata för BigQuery schema
    sample_games = games[:10] if len(games) >= 10 else games
    with open(output_dir / "sample_games.json", "w", encoding="utf-8") as f:
        json.dump(sample_games, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Analys klar! Resultat sparade i {output_dir}")
    
    # Skriv ut några intressanta statistikpunkter
    logger.info(f"Totalt antal spel: {stats['total_games']}")
    logger.info(f"Spel med betyg: {stats['games_with_rating']} ({stats['games_with_rating']/stats['total_games']*100:.1f}%)")
    logger.info(f"Spel med sammanfattning: {stats['games_with_summary']} ({stats['games_with_summary']/stats['total_games']*100:.1f}%)")
    logger.info(f"Spel med omslagsbild: {stats['games_with_cover']} ({stats['games_with_cover']/stats['total_games']*100:.1f}%)")
    logger.info(f"Spel med utgivningsdatum: {stats['games_with_release_date']} ({stats['games_with_release_date']/stats['total_games']*100:.1f}%)")
    logger.info(f"Antal unika genrer: {len(genre_counts)}")
    logger.info(f"Antal unika plattformar: {len(platform_counts)}")
    logger.info(f"Antal unika teman: {len(theme_counts)}")

def main():
    """Huvudfunktion"""
    args = parse_arguments()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists():
        logger.error(f"Input-katalog {input_dir} finns inte")
        sys.exit(1)
    
    # Ladda alla spel
    games = load_games(input_dir)
    
    # Analysera speldata
    analyze_games(games, output_dir)

if __name__ == "__main__":
    main()
