#!/usr/bin/env python3
"""
Testa och visualisera rekommendationer från feature extraction.

Detta script låter dig testa rekommendationskvalitet manuellt genom att
söka efter spel och se rekommendationer.
"""

import json
import pandas as pd
import numpy as np
import os
import sys
import logging
from typing import Dict, Any, List, Optional
import argparse

# Lägg till feature_engineering till path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feature_engineering'))

from feature_extractor import FeatureExtractor
from similarity_search import SimilaritySearch

# Konfigurera loggning
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecommendationTester:
    """Testa rekommendationssystem interaktivt."""
    
    def __init__(self, games_data: List[Dict[str, Any]], 
                 text_weight: float = 0.6, 
                 max_text_features: int = 5000,
                 min_df: int = 5,
                 ngram_range: tuple = (1, 2)):
        """
        Initierar RecommendationTester.
        
        Args:
            games_data: Lista med speldata
            text_weight: Vikt för text-features
            max_text_features: Maximalt antal text-features
            min_df: Minimum document frequency
            ngram_range: N-gram range
        """
        self.games_data = games_data
        self.df = pd.DataFrame(games_data)
        
        logger.info("Extraherar features...")
        
        # Extrahera features
        extractor = FeatureExtractor(
            max_text_features=max_text_features,
            text_weight=text_weight
        )
        
        # Uppdatera TF-IDF vectorizer med våra parametrar
        from sklearn.feature_extraction.text import TfidfVectorizer
        extractor.tfidf = TfidfVectorizer(
            max_features=max_text_features,
            stop_words='english',
            min_df=min_df,
            ngram_range=ngram_range
        )
        
        self.features = extractor.extract_features(self.df)
        
        logger.info("Skapar similarity search index...")
        self.search = SimilaritySearch(self.features['combined_features'])
        
    def search_games(self, query: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Sök efter spel baserat på namn.
        
        Args:
            query: Sökfråga
            top_n: Antal resultat att returnera
            
        Returns:
            Lista med matchande spel
        """
        query_lower = query.lower()
        
        # Sök i både display_name och canonical_name
        matches = []
        for idx, row in self.df.iterrows():
            display_name = str(row.get('display_name', '')).lower()
            canonical_name = str(row.get('canonical_name', '')).lower()
            
            if query_lower in display_name or query_lower in canonical_name:
                matches.append({
                    'idx': idx,
                    'game_id': row['game_id'],
                    'display_name': row['display_name'],
                    'summary': row.get('summary', '')[:200] + '...' if len(str(row.get('summary', ''))) > 200 else row.get('summary', ''),
                    'quality_score': row.get('quality_score', 0),
                    'genres': row.get('genres', []),
                    'platforms': row.get('platforms', []),
                    'themes': row.get('themes', [])
                })
        
        # Sortera efter quality_score
        matches.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return matches[:top_n]
    
    def get_recommendations(self, game_id: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Hämta rekommendationer för ett spel.
        
        Args:
            game_id: ID för spelet
            top_n: Antal rekommendationer att returnera
            
        Returns:
            Lista med rekommendationer
        """
        if game_id not in self.features['reverse_mapping']:
            logger.warning("Spel med ID %s hittades inte", game_id)
            return []
        
        # Hämta index för spelet
        game_idx = self.features['reverse_mapping'][game_id]
        
        # Hämta rekommendationer
        recommendations_idx = self.search.find_similar(game_idx, top_n=top_n+1)
        
        # Konvertera till game data (skippa första som är samma spel)
        recommendations = []
        for idx, score in recommendations_idx[1:]:  # Skip first result (self)
            game_id_rec = self.features['id_mapping'][idx]
            game_data = self.df[self.df['game_id'] == game_id_rec].iloc[0]
            
            recommendations.append({
                'game_id': game_id_rec,
                'display_name': game_data['display_name'],
                'summary': game_data.get('summary', '')[:200] + '...' if len(str(game_data.get('summary', ''))) > 200 else game_data.get('summary', ''),
                'similarity_score': score,
                'quality_score': game_data.get('quality_score', 0),
                'genres': game_data.get('genres', []),
                'platforms': game_data.get('platforms', []),
                'themes': game_data.get('themes', [])
            })
        
        return recommendations
    
    def display_game(self, game: Dict[str, Any]) -> None:
        """
        Visa information om ett spel.
        
        Args:
            game: Speldata
        """
        print(f"\n{'='*80}")
        print(f"Spel: {game['display_name']}")
        print(f"ID: {game['game_id']}")
        if 'quality_score' in game:
            print(f"Quality Score: {game['quality_score']:.2f}")
        if 'similarity_score' in game:
            print(f"Similarity Score: {game['similarity_score']:.4f}")
        if game.get('genres'):
            print(f"Genres: {', '.join(game['genres'][:5])}")
        if game.get('platforms'):
            print(f"Platforms: {', '.join(game['platforms'][:5])}")
        if game.get('themes'):
            print(f"Themes: {', '.join(game['themes'][:5])}")
        if game.get('summary'):
            print(f"\nSummary: {game['summary']}")
        print(f"{'='*80}")
    
    def run_interactive(self):
        """Kör interaktiv testning."""
        print("\n" + "="*80)
        print("IGDB Game Recommendation Tester")
        print("="*80)
        print("\nKommandon:")
        print("  search <query>  - Sök efter spel")
        print("  rec <game_id>   - Hämta rekommendationer för ett spel")
        print("  show <game_id>  - Visa information om ett spel")
        print("  quit            - Avsluta")
        print("="*80)
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                
                if command == 'quit':
                    print("Avslutar...")
                    break
                
                elif command == 'search':
                    if len(parts) < 2:
                        print("Användning: search <query>")
                        continue
                    
                    query = parts[1]
                    results = self.search_games(query)
                    
                    if not results:
                        print(f"Inga spel hittades för '{query}'")
                        continue
                    
                    print(f"\nHittade {len(results)} spel:")
                    for i, game in enumerate(results, 1):
                        print(f"{i}. {game['display_name']} (ID: {game['game_id']}, Score: {game['quality_score']:.2f})")
                
                elif command == 'rec':
                    if len(parts) < 2:
                        print("Användning: rec <game_id>")
                        continue
                    
                    game_id = parts[1]
                    
                    # Visa vilket spel vi hämtar rekommendationer för
                    game_data = self.df[self.df['game_id'] == game_id]
                    if game_data.empty:
                        print(f"Spel med ID {game_id} hittades inte")
                        continue
                    
                    game = {
                        'game_id': game_id,
                        'display_name': game_data.iloc[0]['display_name'],
                        'summary': game_data.iloc[0].get('summary', ''),
                        'quality_score': game_data.iloc[0].get('quality_score', 0),
                        'genres': game_data.iloc[0].get('genres', []),
                        'platforms': game_data.iloc[0].get('platforms', []),
                        'themes': game_data.iloc[0].get('themes', [])
                    }
                    
                    self.display_game(game)
                    
                    # Hämta rekommendationer
                    recommendations = self.get_recommendations(game_id)
                    
                    if not recommendations:
                        print("Inga rekommendationer hittades")
                        continue
                    
                    print(f"\nTop 10 rekommendationer:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"\n{i}. {rec['display_name']} (ID: {rec['game_id']})")
                        print(f"   Similarity: {rec['similarity_score']:.4f}, Quality: {rec['quality_score']:.2f}")
                        if rec.get('genres'):
                            print(f"   Genres: {', '.join(rec['genres'][:3])}")
                        if rec.get('summary'):
                            print(f"   {rec['summary'][:150]}...")
                
                elif command == 'show':
                    if len(parts) < 2:
                        print("Användning: show <game_id>")
                        continue
                    
                    game_id = parts[1]
                    game_data = self.df[self.df['game_id'] == game_id]
                    
                    if game_data.empty:
                        print(f"Spel med ID {game_id} hittades inte")
                        continue
                    
                    game = {
                        'game_id': game_id,
                        'display_name': game_data.iloc[0]['display_name'],
                        'summary': game_data.iloc[0].get('summary', ''),
                        'quality_score': game_data.iloc[0].get('quality_score', 0),
                        'genres': game_data.iloc[0].get('genres', []),
                        'platforms': game_data.iloc[0].get('platforms', []),
                        'themes': game_data.iloc[0].get('themes', [])
                    }
                    
                    self.display_game(game)
                
                else:
                    print(f"Okänt kommando: {command}")
                    print("Använd 'search', 'rec', 'show' eller 'quit'")
                
            except KeyboardInterrupt:
                print("\nAvslutar...")
                break
            except Exception as e:
                logger.error("Fel: %s", str(e))
                print(f"Ett fel uppstod: {str(e)}")

def main():
    """Huvudfunktion för rekommendationstestning."""
    parser = argparse.ArgumentParser(description="Testa rekommendationssystem")
    parser.add_argument("--input", type=str, 
                       default="data/medium_dataset/games.json",
                       help="Sökväg till input dataset")
    parser.add_argument("--text-weight", type=float, default=0.6,
                       help="Vikt för text-features (0.0-1.0)")
    parser.add_argument("--max-text-features", type=int, default=5000,
                       help="Maximalt antal text-features")
    parser.add_argument("--min-df", type=int, default=5,
                       help="Minimum document frequency")
    
    args = parser.parse_args()
    
    # Ladda data
    logger.info("Laddar dataset från %s", args.input)
    with open(args.input, 'r', encoding='utf-8') as f:
        games_data = json.load(f)
    
    logger.info("Laddade %d spel", len(games_data))
    
    # Skapa tester
    tester = RecommendationTester(
        games_data,
        text_weight=args.text_weight,
        max_text_features=args.max_text_features,
        min_df=args.min_df
    )
    
    # Kör interaktiv testning
    tester.run_interactive()

if __name__ == "__main__":
    main()
