#!/usr/bin/env python3
"""
Demo av rekommendationssystem.

Detta script visar exempel på rekommendationer för några populära spel.
"""

import json
import pandas as pd
import numpy as np
import os
import sys
import logging
from typing import Dict, Any, List
import argparse

# Lägg till feature_engineering till path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feature_engineering'))

from feature_extractor import FeatureExtractor
from similarity_search import SimilaritySearch

# Konfigurera loggning
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def display_game(game: pd.Series) -> None:
    """Visa information om ett spel."""
    print(f"\n{'='*80}")
    print(f"Spel: {game['display_name']}")
    print(f"ID: {game['game_id']}")
    print(f"Quality Score: {game.get('quality_score', 0):.2f}")
    if game.get('genres'):
        print(f"Genres: {', '.join(game['genres'][:5])}")
    if game.get('platforms'):
        print(f"Platforms: {', '.join(game['platforms'][:5])}")
    if game.get('themes'):
        print(f"Themes: {', '.join(game['themes'][:5])}")
    if game.get('summary'):
        summary = str(game['summary'])
        if len(summary) > 300:
            summary = summary[:300] + '...'
        print(f"\nSummary: {summary}")
    print(f"{'='*80}")

def get_recommendations_demo(df: pd.DataFrame, features: Dict[str, Any], 
                            game_name_query: str, top_n: int = 10) -> None:
    """Visa rekommendationer för ett spel baserat på namnfråga."""
    
    # Sök efter spelet
    matches = df[df['display_name'].str.contains(game_name_query, case=False, na=False)]
    
    if len(matches) == 0:
        print(f"\nInget spel hittades för '{game_name_query}'")
        return
    
    # Ta det första matchande spelet med högst quality score
    game = matches.sort_values('quality_score', ascending=False).iloc[0]
    game_id = game['game_id']
    
    # Visa spelinfo
    display_game(game)
    
    # Hämta rekommendationer
    if game_id not in features['reverse_mapping']:
        print(f"\nSpel {game_id} finns inte i feature index")
        return
    
    # Skapa similarity search
    search = SimilaritySearch(features['combined_features'])
    search.id_mapping = features['id_mapping']
    search.reverse_mapping = features['reverse_mapping']
    search.build_index()
    
    # Hämta rekommendationer
    game_idx = features['reverse_mapping'][game_id]
    recommendations_idx = search.find_similar(game_idx, top_n=top_n+1)
    
    print(f"\nTop {top_n} rekommendationer:")
    print("-" * 80)
    
    for i, (idx, score) in enumerate(recommendations_idx[1:], 1):  # Skip first (self)
        rec_game_id = features['id_mapping'][idx]
        rec_game = df[df['game_id'] == rec_game_id].iloc[0]
        
        print(f"\n{i}. {rec_game['display_name']}")
        print(f"   Similarity: {score:.4f}, Quality: {rec_game.get('quality_score', 0):.2f}")
        if rec_game.get('genres'):
            print(f"   Genres: {', '.join(rec_game['genres'][:3])}")
        if rec_game.get('summary'):
            summary = str(rec_game['summary'])
            if len(summary) > 150:
                summary = summary[:150] + '...'
            print(f"   {summary}")

def main():
    """Huvudfunktion för demo."""
    parser = argparse.ArgumentParser(description="Demo av rekommendationssystem")
    parser.add_argument("--input", type=str, 
                       default="data/medium_dataset/games.json",
                       help="Sökväg till input dataset")
    parser.add_argument("--text-weight", type=float, default=0.6,
                       help="Vikt för text-features (0.0-1.0)")
    parser.add_argument("--max-text-features", type=int, default=5000,
                       help="Maximalt antal text-features")
    parser.add_argument("--min-df", type=int, default=5,
                       help="Minimum document frequency")
    parser.add_argument("--game", type=str,
                       help="Spelnamn att söka rekommendationer för")
    
    args = parser.parse_args()
    
    # Ladda data
    logger.info("Laddar dataset från %s", args.input)
    with open(args.input, 'r', encoding='utf-8') as f:
        games_data = json.load(f)
    
    logger.info("Laddade %d spel", len(games_data))
    
    df = pd.DataFrame(games_data)
    
    # Extrahera features
    logger.info("Extraherar features...")
    extractor = FeatureExtractor(
        max_text_features=args.max_text_features,
        text_weight=args.text_weight
    )
    
    # Uppdatera TF-IDF vectorizer
    from sklearn.feature_extraction.text import TfidfVectorizer
    extractor.tfidf = TfidfVectorizer(
        max_features=args.max_text_features,
        stop_words='english',
        min_df=args.min_df,
        ngram_range=(1, 2)
    )
    
    features = extractor.extract_features(df)
    logger.info("Feature extraction klar!")
    
    # Visa demo rekommendationer
    print("\n" + "="*80)
    print("IGDB Game Recommendation System - Demo")
    print("="*80)
    
    # Om ett spel angavs, visa rekommendationer för det
    if args.game:
        get_recommendations_demo(df, features, args.game, top_n=10)
    else:
        # Visa exempel med några populära spel
        example_games = [
            "Witcher",
            "Portal",
            "Zelda",
            "Dark Souls",
            "Minecraft"
        ]
        
        for game_name in example_games:
            try:
                get_recommendations_demo(df, features, game_name, top_n=5)
                print("\n")
            except Exception as e:
                logger.error("Fel vid rekommendation för %s: %s", game_name, str(e))
                continue

if __name__ == "__main__":
    main()
