#!/usr/bin/env python3
"""
Proof of Concept för IGDB Game Recommendation System.

Detta script kör en proof of concept för rekommendationssystemet med en mindre delmängd av data.
"""

import os
import pandas as pd
import logging
import argparse
from feature_engineering.feature_extractor import FeatureExtractor, load_games_from_bigquery
from feature_engineering.similarity_search import SimilaritySearch

# Konfigurera loggning
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_proof_of_concept(
    limit: int = 1000,
    output_dir: str = "data/features",
    text_weight: float = 0.7,
    max_text_features: int = 5000,
    top_n: int = 10,
    sample_games: int = 5
):
    """
    Kör proof of concept för rekommendationssystemet.
    
    Args:
        limit: Antal spel att ladda
        output_dir: Katalog att spara features i
        text_weight: Vikt för text-features (0.0-1.0)
        max_text_features: Maximalt antal text-features
        top_n: Antal rekommendationer att visa per spel
        sample_games: Antal exempelspel att visa rekommendationer för
    """
    # Skapa output-katalog om den inte finns
    os.makedirs(output_dir, exist_ok=True)
    
    # Ladda data
    logger.info("Laddar %d spel från BigQuery...", limit)
    games_df = load_games_from_bigquery(limit)
    
    # Extrahera features
    logger.info("Extraherar features...")
    extractor = FeatureExtractor(
        max_text_features=max_text_features,
        text_weight=text_weight
    )
    features = extractor.extract_features(games_df)
    
    # Spara features
    logger.info("Sparar features...")
    extractor.save_features(features, output_dir)
    
    # Skapa similarity search
    logger.info("Skapar similarity search...")
    similarity_search = SimilaritySearch(features)
    similarity_search.build_index()
    
    # Spara index
    similarity_search.save_index(os.path.join(output_dir, "faiss_index.bin"))
    
    # Kör benchmark
    logger.info("Kör prestandabenchmark...")
    benchmark_results = similarity_search.benchmark_performance(num_queries=100)
    
    # Visa rekommendationer för några exempelspel
    logger.info("Visar rekommendationer för %d exempelspel...", sample_games)
    
    # Välj några spel med högst kvalitetspoäng
    sample_game_ids = games_df.sort_values('quality_score', ascending=False).head(sample_games)['game_id'].tolist()
    
    for game_id in sample_game_ids:
        game_name = games_df[games_df['game_id'] == game_id]['display_name'].iloc[0]
        
        print(f"\n{'='*80}")
        print(f"Rekommendationer för: {game_name} (ID: {game_id})")
        print(f"{'='*80}")
        
        recommendations = similarity_search.get_similar_games(game_id, top_n)
        
        for i, rec in enumerate(recommendations):
            rec_id = rec['game_id']
            rec_name = games_df[games_df['game_id'] == rec_id]['display_name'].iloc[0]
            rec_score = rec['similarity_score']
            
            print(f"{i+1}. {rec_name} (Score: {rec_score:.4f})")
            
            # Visa några detaljer för att bedöma rekommendationskvalitet
            rec_genres = games_df[games_df['game_id'] == rec_id]['genres'].iloc[0]
            rec_platforms = games_df[games_df['game_id'] == rec_id]['platforms'].iloc[0]
            
            print(f"   Genres: {rec_genres}")
            print(f"   Platforms: {rec_platforms}")
            print(f"   ID: {rec_id}")
    
    # Sammanfatta resultat
    print(f"\n{'='*80}")
    print("Proof of Concept - Sammanfattning")
    print(f"{'='*80}")
    print(f"Antal spel: {len(games_df)}")
    print(f"Text features: {features['text_features'].shape[1]}")
    print(f"Kategoriska features: {features['categorical_features'].shape[1]}")
    print(f"Kombinerade features: {features['combined_features'].shape[1]}")
    print(f"Text weight: {text_weight}")
    print(f"Genomsnittlig query-tid: {benchmark_results['avg_time']*1000:.2f} ms")
    print(f"Queries per sekund: {benchmark_results['queries_per_second']:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kör proof of concept för rekommendationssystemet")
    parser.add_argument("--limit", type=int, default=1000, help="Antal spel att ladda")
    parser.add_argument("--output", type=str, default="data/features", help="Katalog att spara features i")
    parser.add_argument("--text-weight", type=float, default=0.7, help="Vikt för text-features (0.0-1.0)")
    parser.add_argument("--max-text-features", type=int, default=5000, help="Maximalt antal text-features")
    parser.add_argument("--top-n", type=int, default=10, help="Antal rekommendationer att visa per spel")
    parser.add_argument("--sample-games", type=int, default=5, help="Antal exempelspel att visa rekommendationer för")
    
    args = parser.parse_args()
    
    run_proof_of_concept(
        limit=args.limit,
        output_dir=args.output,
        text_weight=args.text_weight,
        max_text_features=args.max_text_features,
        top_n=args.top_n,
        sample_games=args.sample_games
    )
