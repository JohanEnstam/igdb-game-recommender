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
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set
from collections import Counter, defaultdict

import pandas as pd
import numpy as np
from difflib import SequenceMatcher

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

def find_similar_games(games: List[Dict[str, Any]], output_dir: Path) -> Dict[str, Any]:
    """
    Identifiera potentiella dubbletter och olika versioner av samma spel
    
    Metoder som används:
    1. Exakt namnmatchning (identiska namn)
    2. Ordbaserad likhetsmätning (Jaccard-likhet)
    3. Identifiering av versioner/utgåvor (DLC, GOTY, etc.)
    4. Identifiering av spel i samma serie
    """
    logger.info("Analyserar potentiella dubbletter och spelserier...")
    
    # Skapa en dictionary med namn som nyckel för snabbare sökning
    name_to_games = defaultdict(list)
    for game in games:
        if "name" in game and game["name"]:
            name_to_games[game["name"].lower()].append(game)
    
    # Hitta exakta dubbletter (samma namn)
    exact_duplicates = {name: games_list for name, games_list in name_to_games.items() if len(games_list) > 1}
    
    # Hitta potentiella versioner/utgåvor av samma spel
    # Regex-mönster för att identifiera vanliga versionsmarkörer
    version_patterns = [
        r"(deluxe|premium|gold|complete|definitive|enhanced|remastered|hd|special|collector'?s?|goty|game of the year)",
        r"(edition|version|collection|bundle)",
        r"(dlc|expansion|season pass|content pack)",
        r"(remake|reboot|remaster)",
        r"(\d{4}|\d{2}|\d)$",  # Årtal eller versionsnummer i slutet
        r"(vol\.?\s*\d+|volume\s*\d+)",
        r"(chapter|episode|part)\s*\d+"
    ]
    
    combined_pattern = re.compile("|".join(version_patterns), re.IGNORECASE)
    
    # Gruppera spel efter basnamn (utan versionsindikatorer)
    base_name_to_games = defaultdict(list)
    for name, game_list in name_to_games.items():
        # Försök identifiera basnamnet genom att ta bort versionsindikatorer
        base_name = re.sub(combined_pattern, "", name).strip()
        # Ta bort eventuella kolon, bindestreck och andra separatorer i slutet
        base_name = re.sub(r"[:;-–—_\s]+$", "", base_name).strip()
        
        if base_name and base_name != name:  # Om vi faktiskt tog bort något
            for game in game_list:
                base_name_to_games[base_name].append(game)
    
    # Filtrera för att bara behålla basnamn med flera spel
    version_groups = {name: games_list for name, games_list in base_name_to_games.items() 
                     if len(games_list) > 1 and len(name) > 3}  # Ignorera för korta basnamn
    
    # Hitta spel i samma serie (t.ex. "Final Fantasy I", "Final Fantasy II")
    series_patterns = [
        r"(.+)\s+\d+$",  # Namn följt av nummer i slutet
        r"(.+)\s+[ivx]+$",  # Namn följt av romerska siffror
        r"(.+):\s*.+$",  # Namn följt av kolon och undertitel
    ]
    
    series_to_games = defaultdict(list)
    for game in games:
        if "name" not in game or not game["name"]:
            continue
            
        name = game["name"]
        for pattern in series_patterns:
            match = re.match(pattern, name, re.IGNORECASE)
            if match:
                series_name = match.group(1).strip()
                if len(series_name) > 3:  # Ignorera för korta serienamn
                    series_to_games[series_name.lower()].append(game)
                break
    
    # Filtrera för att bara behålla serier med flera spel
    series_groups = {name: games_list for name, games_list in series_to_games.items() 
                    if len(games_list) > 1}
    
    # Hitta liknande namn med en mer effektiv metod
    # Vi använder en ordbaserad approach istället för full fuzzy matching
    # Detta är betydligt snabbare än SequenceMatcher för stora datamängder
    logger.info("Analyserar liknande namn med ordbaserad metod (mycket snabbare än full fuzzy matching)...")
    
    # Begränsa till ett rimligt urval för analys
    sample_size = min(1000, len(games))  # Kraftigt reducerad sampelstorlek
    
    # Skapa en ordbok där nycklarna är ord och värdena är spel som innehåller dessa ord
    word_to_games = defaultdict(set)
    
    # Använd ett urval av spel för ordbaserad analys
    sample_games = games[:sample_size] if len(games) > sample_size else games
    
    # Förbehandla spelnamn och bygg ordindexet
    game_words = {}
    
    for game in sample_games:
        if "name" not in game or not game["name"]:
            continue
            
        name = game["name"].lower()
        # Ta bort specialtecken och dela upp i ord
        words = re.findall(r'\w+', name)
        # Filtrera bort mycket korta ord och vanliga ord
        words = [w for w in words if len(w) > 2]
        
        if words:
            game_words[game["id"]] = words
            for word in words:
                word_to_games[word].add(game["id"])
    
    # Hitta spel med överlappande ord
    fuzzy_matches = []
    processed_pairs = set()
    
    # Gå igenom varje spel och hitta andra spel med överlappande ord
    for game_id, words in game_words.items():
        # Hitta alla spel som delar minst ett ord med detta spel
        candidate_games = set()
        for word in words:
            candidate_games.update(word_to_games[word])
        
        # Ta bort det aktuella spelet
        candidate_games.discard(game_id)
        
        # För varje kandidatspel, beräkna Jaccard-likheten
        game1 = next(g for g in sample_games if g["id"] == game_id)
        
        for candidate_id in candidate_games:
            # Hoppa över om vi redan har behandlat detta par
            pair_id = tuple(sorted([game_id, candidate_id]))
            if pair_id in processed_pairs:
                continue
                
            processed_pairs.add(pair_id)
            
            # Hitta kandidatspelet
            game2 = next(g for g in sample_games if g["id"] == candidate_id)
            
            # Beräkna Jaccard-likhet (storlek av snittet / storlek av unionen)
            words2 = game_words[candidate_id]
            intersection = set(words) & set(words2)
            union = set(words) | set(words2)
            
            if not union:
                continue
                
            similarity = len(intersection) / len(union)
            
            # Använd en lägre tröskel eftersom Jaccard-likhet tenderar att ge lägre värden än SequenceMatcher
            if similarity >= 0.5:  # Justerad tröskel för Jaccard-likhet
                fuzzy_matches.append({
                    "game1_id": game1["id"],
                    "game1_name": game1["name"],
                    "game2_id": game2["id"],
                    "game2_name": game2["name"],
                    "similarity": similarity
                })
    
    # Sortera fuzzy matches efter likhet
    fuzzy_matches.sort(key=lambda x: x["similarity"], reverse=True)
    
    # Sammanställ resultat
    duplicate_stats = {
        "exact_duplicates_count": len(exact_duplicates),
        "version_groups_count": len(version_groups),
        "series_groups_count": len(series_groups),
        "fuzzy_matches_count": len(fuzzy_matches)
    }
    
    # Spara resultat till filer
    with open(output_dir / "duplicate_stats.json", "w", encoding="utf-8") as f:
        json.dump(duplicate_stats, f, ensure_ascii=False, indent=2)
    
    # Spara exempel på exakta dubbletter
    exact_duplicates_sample = {}
    for name, game_list in list(exact_duplicates.items())[:100]:  # Begränsa till 100 exempel
        exact_duplicates_sample[name] = [
            {"id": g["id"], "name": g["name"], "first_release_date": g.get("first_release_date")} 
            for g in game_list
        ]
    
    with open(output_dir / "exact_duplicates_sample.json", "w", encoding="utf-8") as f:
        json.dump(exact_duplicates_sample, f, ensure_ascii=False, indent=2)
    
    # Spara exempel på versionsgrupper
    version_groups_sample = {}
    for base_name, game_list in list(version_groups.items())[:100]:  # Begränsa till 100 exempel
        version_groups_sample[base_name] = [
            {"id": g["id"], "name": g["name"], "first_release_date": g.get("first_release_date")} 
            for g in game_list
        ]
    
    with open(output_dir / "version_groups_sample.json", "w", encoding="utf-8") as f:
        json.dump(version_groups_sample, f, ensure_ascii=False, indent=2)
    
    # Spara exempel på spelserier
    series_groups_sample = {}
    for series_name, game_list in list(series_groups.items())[:100]:  # Begränsa till 100 exempel
        series_groups_sample[series_name] = [
            {"id": g["id"], "name": g["name"], "first_release_date": g.get("first_release_date")} 
            for g in game_list
        ]
    
    with open(output_dir / "series_groups_sample.json", "w", encoding="utf-8") as f:
        json.dump(series_groups_sample, f, ensure_ascii=False, indent=2)
    
    # Spara fuzzy matches
    with open(output_dir / "fuzzy_matches.json", "w", encoding="utf-8") as f:
        json.dump(fuzzy_matches[:500], f, ensure_ascii=False, indent=2)  # Begränsa till 500 exempel
    
    # Logga resultat
    logger.info(f"Hittade {duplicate_stats['exact_duplicates_count']} spel med exakt samma namn")
    logger.info(f"Hittade {duplicate_stats['version_groups_count']} potentiella versionsgrupper")
    logger.info(f"Hittade {duplicate_stats['series_groups_count']} potentiella spelserier")
    logger.info(f"Hittade {duplicate_stats['fuzzy_matches_count']} par av spel med liknande namn")
    
    return duplicate_stats

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
    
    # Analysera dubbletter och liknande spel
    logger.info("Startar analys av dubbletter och liknande spel (detta kan ta några minuter)...")
    start_time = pd.Timestamp.now()
    duplicate_stats = find_similar_games(games, output_dir)
    end_time = pd.Timestamp.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Dubblett-analys slutförd på {duration:.1f} sekunder")
    
    # Uppdatera grundläggande statistik med dubblett-information
    with open(output_dir / "basic_stats.json", "r", encoding="utf-8") as f:
        basic_stats = json.load(f)
    
    basic_stats.update(duplicate_stats)
    basic_stats["duplicate_analysis_time_seconds"] = duration
    
    with open(output_dir / "basic_stats.json", "w", encoding="utf-8") as f:
        json.dump(basic_stats, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
