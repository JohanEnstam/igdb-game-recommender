#!/usr/bin/env python3
"""
Skapa ett mellanstort dataset med alla nödvändiga features.

Detta script skapar ett dataset med 10,000-50,000 spel för snabba iterationer
under utveckling och optimering av rekommendationssystemet.
"""

import json
import pandas as pd
import numpy as np
import os
import logging
import glob
from typing import List, Dict, Any
import argparse

# Konfigurera loggning
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_full_dataset_with_features(cleaned_data_path: str, raw_data_dir: str) -> List[Dict[str, Any]]:
    """
    Ladda hela datasetet med kategoriska features från rådata.
    
    Args:
        cleaned_data_path: Sökväg till games.json (cleaned data)
        raw_data_dir: Katalog med rådata batch-filer
        
    Returns:
        Lista med alla spel med kategoriska features
    """
    logger.info("Laddar rensad data från %s", cleaned_data_path)
    
    with open(cleaned_data_path, 'r', encoding='utf-8') as f:
        cleaned_games = json.load(f)
    
    logger.info("Laddade %d rensade spel", len(cleaned_games))
    
    # Läs in rådata för att få kategoriska features
    logger.info("Läser in rådata från %s", raw_data_dir)
    raw_games = []
    batch_files = glob.glob(os.path.join(raw_data_dir, "games_batch_*.json"))
    
    logger.info("Hitlade %d batch-filer", len(batch_files))
    
    for file_path in batch_files:
        with open(file_path, "r") as f:
            batch = json.load(f)
            raw_games.extend(batch)
    
    logger.info("Laddade %d spel från rådata", len(raw_games))
    
    # Skapa lookup dict för rådata
    raw_games_dict = {str(game['id']): game for game in raw_games}
    
    # Slå ihop rensad data med rådata
    merged_games = []
    for game in cleaned_games:
        game_id = game['game_id']
        if game_id in raw_games_dict:
            raw_game = raw_games_dict[game_id]
            
            # Extrahera namn från kategoriska features
            def extract_names(items):
                if isinstance(items, list) and len(items) > 0 and isinstance(items[0], dict):
                    return [item.get('name', '') for item in items if isinstance(item, dict) and 'name' in item]
                return []
            
            # Lägg till kategoriska features
            game_copy = game.copy()
            game_copy['genres'] = extract_names(raw_game.get('genres', []))
            game_copy['platforms'] = extract_names(raw_game.get('platforms', []))
            game_copy['themes'] = extract_names(raw_game.get('themes', []))
            
            merged_games.append(game_copy)
        else:
            # Lägg till tom lista om rådata saknas
            game_copy = game.copy()
            game_copy['genres'] = []
            game_copy['platforms'] = []
            game_copy['themes'] = []
            merged_games.append(game_copy)
    
    logger.info("Slog ihop %d spel med rådata", len(merged_games))
    return merged_games

def create_stratified_sample(games: List[Dict[str, Any]], target_size: int = 25000) -> List[Dict[str, Any]]:
    """
    Skapa en stratifierad urval av spel baserat på quality_score.
    
    Args:
        games: Lista med alla spel
        target_size: Målstorlek för urvalet
        
    Returns:
        Stratifierat urval av spel
    """
    logger.info("Skapar stratifierat urval med %d spel", target_size)
    
    # Konvertera till DataFrame för enklare hantering
    df = pd.DataFrame(games)
    
    # Sortera efter quality_score
    df = df.sort_values('quality_score', ascending=False).reset_index(drop=True)
    
    # Skapa kvalitetskategorier baserat på percentiler
    try:
        df['quality_category'] = pd.qcut(
            df['quality_score'], 
            q=5, 
            labels=['very_low', 'low', 'medium', 'high', 'very_high'],
            duplicates='drop'
        )
    except ValueError:
        # Fallback om qcut misslyckas (t.ex. för få unika värden)
        df['quality_category'] = pd.cut(
            df['quality_score'], 
            bins=5, 
            labels=['very_low', 'low', 'medium', 'high', 'very_high'],
            duplicates='drop'
        )
    
    # Beräkna antal spel per kategori
    category_counts = df['quality_category'].value_counts()
    logger.info("Kvalitetskategorier: %s", dict(category_counts))
    
    # Stratifierat urval - proportionellt från varje kategori
    sampled_games = []
    for category in df['quality_category'].unique():
        if pd.isna(category):
            continue
            
        category_games = df[df['quality_category'] == category]
        category_size = int(target_size * len(category_games) / len(df))
        
        # Ta minst 100 spel per kategori, max alla i kategorin
        category_size = max(100, min(category_size, len(category_games)))
        
        # Slumpmässigt urval inom kategorin
        sampled_category = category_games.sample(n=category_size, random_state=42)
        sampled_games.append(sampled_category)
        
        logger.info("Kategori %s: %d spel (från %d totalt)", 
                   category, category_size, len(category_games))
    
    # Kombinera alla kategorier
    result_df = pd.concat(sampled_games, ignore_index=True)
    
    # Om vi har för många spel, ta de bästa
    if len(result_df) > target_size:
        result_df = result_df.head(target_size)
    
    # Ta bort temporary category column
    if 'quality_category' in result_df.columns:
        result_df = result_df.drop(columns=['quality_category'])
    
    # Konvertera tillbaka till lista av dictionaries
    result_games = result_df.to_dict('records')
    
    logger.info("Skapade stratifierat urval med %d spel", len(result_games))
    return result_games

def save_dataset(games: List[Dict[str, Any]], output_path: str) -> None:
    """
    Spara dataset till JSON-fil.
    
    Args:
        games: Lista med spel
        output_path: Sökväg att spara till
    """
    logger.info("Sparar dataset till %s", output_path)
    
    # Skapa output-katalog om den inte finns
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Spara som JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)
    
    logger.info("Sparade %d spel till %s", len(games), output_path)

def analyze_dataset(games: List[Dict[str, Any]]) -> None:
    """
    Analysera dataset och visa statistik.
    
    Args:
        games: Lista med spel
    """
    logger.info("Analyserar dataset...")
    
    df = pd.DataFrame(games)
    
    # Grundläggande statistik
    logger.info("Dataset statistik:")
    logger.info("- Total antal spel: %d", len(df))
    logger.info("- Spel med summary: %d", df['summary'].notna().sum())
    logger.info("- Spel med cover_url: %d", df['cover_url'].notna().sum())
    
    # Quality score statistik
    if 'quality_score' in df.columns:
        logger.info("- Quality score - Min: %.2f, Max: %.2f, Medel: %.2f", 
                   df['quality_score'].min(), 
                   df['quality_score'].max(), 
                   df['quality_score'].mean())
    
    # Kategoriska features statistik
    if 'genres' in df.columns:
        genre_counts = df['genres'].apply(len)
        logger.info("- Spel med genres: %d (medel: %.1f per spel)", 
                   (genre_counts > 0).sum(), genre_counts.mean())
    
    if 'platforms' in df.columns:
        platform_counts = df['platforms'].apply(len)
        logger.info("- Spel med platforms: %d (medel: %.1f per spel)", 
                   (platform_counts > 0).sum(), platform_counts.mean())
    
    if 'themes' in df.columns:
        theme_counts = df['themes'].apply(len)
        logger.info("- Spel med themes: %d (medel: %.1f per spel)", 
                   (theme_counts > 0).sum(), theme_counts.mean())
    
    # Summary längd statistik
    summary_lengths = df['summary'].str.len().dropna()
    if len(summary_lengths) > 0:
        logger.info("- Summary längd - Min: %d, Max: %d, Medel: %.1f", 
                   summary_lengths.min(), 
                   summary_lengths.max(), 
                   summary_lengths.mean())

def main():
    """Huvudfunktion för att skapa mellanstort dataset."""
    parser = argparse.ArgumentParser(description="Skapa mellanstort dataset för optimering")
    parser.add_argument("--cleaned-data", type=str, 
                       default="data-pipeline/processing/cleaned_data/games.json",
                       help="Sökväg till rensad data")
    parser.add_argument("--raw-data-dir", type=str, 
                       default="data-pipeline/ingestion/data",
                       help="Katalog med rådata batch-filer")
    parser.add_argument("--output", type=str, 
                       default="data/medium_dataset/games.json",
                       help="Sökväg till output dataset")
    parser.add_argument("--size", type=int, default=25000,
                       help="Storlek på dataset (default: 25000)")
    
    args = parser.parse_args()
    
    # Ladda hela datasetet med kategoriska features
    games = load_full_dataset_with_features(args.cleaned_data, args.raw_data_dir)
    
    # Skapa stratifierat urval
    sampled_games = create_stratified_sample(games, args.size)
    
    # Analysera dataset
    analyze_dataset(sampled_games)
    
    # Spara dataset
    save_dataset(sampled_games, args.output)
    
    logger.info("Klar! Dataset skapat med %d spel", len(sampled_games))

if __name__ == "__main__":
    main()
