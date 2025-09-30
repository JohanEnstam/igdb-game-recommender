#!/usr/bin/env python3
"""
Skapa ett mellanstort dataset för optimering av feature extraction.

Detta script skapar ett dataset med 10,000-50,000 spel för snabba iterationer
under utveckling och optimering av rekommendationssystemet.
"""

import json
import pandas as pd
import numpy as np
import os
import logging
from typing import List, Dict, Any
import argparse

# Konfigurera loggning
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_full_dataset(cleaned_data_path: str) -> List[Dict[str, Any]]:
    """
    Ladda hela datasetet från cleaned_data.
    
    Args:
        cleaned_data_path: Sökväg till games.json
        
    Returns:
        Lista med alla spel
    """
    logger.info("Laddar hela datasetet från %s", cleaned_data_path)
    
    with open(cleaned_data_path, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    logger.info("Laddade %d spel", len(games))
    return games

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
    
    # Konvertera tillbaka till lista av dictionaries
    result_games = result_df.to_dict('records')
    
    logger.info("Skapade stratifierat urval med %d spel", len(result_games))
    return result_games

def create_quality_based_sample(games: List[Dict[str, Any]], target_size: int = 25000) -> List[Dict[str, Any]]:
    """
    Skapa urval baserat på quality_score (de bästa spelen).
    
    Args:
        games: Lista med alla spel
        target_size: Målstorlek för urvalet
        
    Returns:
        Urval av de bästa spelen
    """
    logger.info("Skapar quality-baserat urval med %d spel", target_size)
    
    # Sortera efter quality_score (högst först)
    sorted_games = sorted(games, key=lambda x: x.get('quality_score', 0), reverse=True)
    
    # Ta de bästa spelen
    result_games = sorted_games[:target_size]
    
    logger.info("Skapade quality-baserat urval med %d spel", len(result_games))
    logger.info("Quality score range: %.2f - %.2f", 
               result_games[-1].get('quality_score', 0),
               result_games[0].get('quality_score', 0))
    
    return result_games

def create_diverse_sample(games: List[Dict[str, Any]], target_size: int = 25000) -> List[Dict[str, Any]]:
    """
    Skapa ett diversifierat urval som fångar olika typer av spel.
    
    Args:
        games: Lista med alla spel
        target_size: Målstorlek för urvalet
        
    Returns:
        Diversifierat urval av spel
    """
    logger.info("Skapar diversifierat urval med %d spel", target_size)
    
    # Konvertera till DataFrame
    df = pd.DataFrame(games)
    
    # Filtrera bort spel utan summary
    df = df[df['summary'].notna() & (df['summary'] != '')]
    
    # Sortera efter quality_score
    df = df.sort_values('quality_score', ascending=False).reset_index(drop=True)
    
    # Ta de bästa 50% för diversifiering
    top_half = df.head(len(df) // 2)
    
    # Skapa diversifierat urval
    sampled_games = []
    
    # Ta varje 10:e spel för diversifiering
    step = max(1, len(top_half) // (target_size // 2))
    for i in range(0, len(top_half), step):
        if len(sampled_games) >= target_size:
            break
        sampled_games.append(top_half.iloc[i].to_dict())
    
    # Fyll på med de bästa spelen om vi behöver fler
    if len(sampled_games) < target_size:
        remaining = target_size - len(sampled_games)
        for i in range(remaining):
            if i < len(top_half):
                sampled_games.append(top_half.iloc[i].to_dict())
    
    logger.info("Skapade diversifierat urval med %d spel", len(sampled_games))
    return sampled_games

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
    
    # Release date statistik
    if 'release_date' in df.columns:
        release_dates = df['release_date'].dropna()
        if len(release_dates) > 0:
            logger.info("- Spel med release_date: %d", len(release_dates))
    
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
    parser.add_argument("--input", type=str, 
                       default="../data-pipeline/processing/cleaned_data/games.json",
                       help="Sökväg till input dataset")
    parser.add_argument("--output", type=str, 
                       default="../data/medium_dataset/games.json",
                       help="Sökväg till output dataset")
    parser.add_argument("--size", type=int, default=25000,
                       help="Storlek på dataset (default: 25000)")
    parser.add_argument("--method", type=str, default="stratified",
                       choices=["stratified", "quality", "diverse"],
                       help="Metod för urval (default: stratified)")
    
    args = parser.parse_args()
    
    # Ladda hela datasetet
    games = load_full_dataset(args.input)
    
    # Skapa urval baserat på vald metod
    if args.method == "stratified":
        sampled_games = create_stratified_sample(games, args.size)
    elif args.method == "quality":
        sampled_games = create_quality_based_sample(games, args.size)
    elif args.method == "diverse":
        sampled_games = create_diverse_sample(games, args.size)
    else:
        raise ValueError(f"Okänd metod: {args.method}")
    
    # Analysera dataset
    analyze_dataset(sampled_games)
    
    # Spara dataset
    save_dataset(sampled_games, args.output)
    
    logger.info("Klar! Dataset skapat med %d spel", len(sampled_games))

if __name__ == "__main__":
    main()
