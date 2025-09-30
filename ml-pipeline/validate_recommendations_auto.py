#!/usr/bin/env python3
"""
Automatisk validering av rekommendationskvalitet.

Detta script testar rekommendationer för populära spel och presenterar
alla resultat för manuell bedömning utan interaktiv input.
"""

import json
import pandas as pd
import numpy as np
import os
import sys
import logging
from typing import Dict, Any, List, Tuple
import argparse

# Lägg till feature_engineering till path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feature_engineering'))

from feature_extractor import FeatureExtractor
from similarity_search import SimilaritySearch

# Konfigurera loggning
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoRecommendationValidator:
    """Automatisk validering av rekommendationskvalitet."""
    
    def __init__(self, games_data: List[Dict[str, Any]], 
                 text_weight: float = 0.6, 
                 max_text_features: int = 5000,
                 min_df: int = 5,
                 ngram_range: tuple = (1, 2)):
        """
        Initierar AutoRecommendationValidator.
        
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
        self.search.id_mapping = self.features['id_mapping']
        self.search.reverse_mapping = self.features['reverse_mapping']
        self.search.build_index()
        
        # Definiera testspel
        self.test_games = [
            # AAA-spel
            {"name": "Witcher", "category": "AAA RPG"},
            {"name": "Dark Souls", "category": "AAA RPG"},
            {"name": "Skyrim", "category": "AAA RPG"},
            {"name": "Portal", "category": "AAA Puzzle"},
            {"name": "Half-Life", "category": "AAA FPS"},
            {"name": "Minecraft", "category": "AAA Sandbox"},
            {"name": "GTA", "category": "AAA Action"},
            {"name": "Zelda", "category": "AAA Adventure"},
            
            # Indie-spel
            {"name": "Hollow Knight", "category": "Indie Metroidvania"},
            {"name": "Celeste", "category": "Indie Platformer"},
            {"name": "Stardew Valley", "category": "Indie Farming"},
            {"name": "Undertale", "category": "Indie RPG"},
            {"name": "Cuphead", "category": "Indie Action"},
            {"name": "Ori", "category": "Indie Platformer"},
            
            # Olika genrer
            {"name": "Civilization", "category": "Strategy"},
            {"name": "SimCity", "category": "Simulation"},
            {"name": "FIFA", "category": "Sports"},
            {"name": "Call of Duty", "category": "FPS"},
            {"name": "World of Warcraft", "category": "MMORPG"},
            {"name": "League of Legends", "category": "MOBA"},
        ]
    
    def find_best_match(self, query: str) -> pd.Series:
        """
        Hitta bästa matchning för en sökfråga.
        
        Args:
            query: Sökfråga
            
        Returns:
            Bästa matchande spel
        """
        matches = self.df[self.df['display_name'].str.contains(query, case=False, na=False)]
        
        if len(matches) == 0:
            return None
        
        # Ta det första matchande spelet med högst quality score
        return matches.sort_values('quality_score', ascending=False).iloc[0]
    
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
            return []
        
        # Hämta rekommendationer
        game_idx = self.features['reverse_mapping'][game_id]
        recommendations_idx = self.search.find_similar(game_idx, top_n=top_n+1)
        
        # Konvertera till game data (skippa första som är samma spel)
        recommendations = []
        for idx, score in recommendations_idx[1:]:  # Skip first result (self)
            game_id_rec = self.features['id_mapping'][idx]
            game_data = self.df[self.df['game_id'] == game_id_rec].iloc[0]
            
            recommendations.append({
                'game_id': game_id_rec,
                'display_name': game_data['display_name'],
                'summary': game_data.get('summary', ''),
                'similarity_score': score,
                'quality_score': game_data.get('quality_score', 0),
                'genres': game_data.get('genres', []),
                'platforms': game_data.get('platforms', []),
                'themes': game_data.get('themes', [])
            })
        
        return recommendations
    
    def validate_single_game(self, test_game: Dict[str, str]) -> Dict[str, Any]:
        """
        Validera rekommendationer för ett spel.
        
        Args:
            test_game: Dictionary med 'name' och 'category'
            
        Returns:
            Dictionary med valideringsresultat
        """
        # Hitta spelet
        game = self.find_best_match(test_game['name'])
        if game is None:
            return {
                'query': test_game['name'],
                'category': test_game['category'],
                'found': False,
                'recommendations': []
            }
        
        # Hämta rekommendationer
        recommendations = self.get_recommendations(game['game_id'], top_n=10)
        
        return {
            'query': test_game['name'],
            'category': test_game['category'],
            'found': True,
            'game_id': game['game_id'],
            'game_name': game['display_name'],
            'game_quality_score': game.get('quality_score', 0),
            'game_genres': game.get('genres', []),
            'game_platforms': game.get('platforms', []),
            'game_themes': game.get('themes', []),
            'game_summary': game.get('summary', ''),
            'recommendations': recommendations
        }
    
    def run_validation(self, max_games: int = None) -> List[Dict[str, Any]]:
        """
        Kör validering för alla testspel.
        
        Args:
            max_games: Maximalt antal spel att testa (None för alla)
            
        Returns:
            Lista med valideringsresultat
        """
        logger.info("Startar automatisk validering...")
        
        results = []
        games_to_test = self.test_games[:max_games] if max_games else self.test_games
        
        for i, test_game in enumerate(games_to_test, 1):
            logger.info(f"Testar {i}/{len(games_to_test)}: {test_game['name']}")
            result = self.validate_single_game(test_game)
            results.append(result)
        
        return results
    
    def display_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Visa valideringsresultat för manuell bedömning.
        
        Args:
            results: Lista med valideringsresultat
        """
        print(f"\n{'='*100}")
        print("🔍 REKOMMENDATION VALIDATION RESULTS")
        print(f"{'='*100}")
        print(f"Testade {len(results)} populära spel")
        print(f"Använde optimerade parametrar: text_weight=0.6, max_features=5000")
        print(f"{'='*100}")
        
        found_games = [r for r in results if r['found']]
        print(f"\n📊 SAMMANFATTNING:")
        print(f"Total games tested: {len(results)}")
        print(f"Games found: {len(found_games)}")
        print(f"Success rate: {len(found_games)/len(results)*100:.1f}%")
        
        # Gruppera efter kategori
        categories = {}
        for result in found_games:
            cat = result['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        print(f"\n📋 RESULTAT PER KATEGORI:")
        print("-" * 50)
        
        for category, games in categories.items():
            print(f"\n🎯 {category} ({len(games)} spel):")
            print("-" * 30)
            
            for game_result in games:
                print(f"\n🎮 {game_result['game_name']}")
                print(f"   Query: '{game_result['query']}' | Quality: {game_result['game_quality_score']:.2f}")
                if game_result['game_genres']:
                    print(f"   Genres: {', '.join(game_result['game_genres'][:3])}")
                
                recommendations = game_result['recommendations']
                if recommendations:
                    print(f"   📋 Top 5 rekommendationer:")
                    for i, rec in enumerate(recommendations[:5], 1):
                        print(f"      {i}. {rec['display_name']} (Sim: {rec['similarity_score']:.3f}, Qual: {rec['quality_score']:.1f})")
                        if rec['genres']:
                            print(f"         Genres: {', '.join(rec['genres'][:2])}")
                else:
                    print("   ❌ Inga rekommendationer")
        
        # Visa spel som inte hittades
        not_found = [r for r in results if not r['found']]
        if not_found:
            print(f"\n❌ SPEL SOM INTE HITTADES ({len(not_found)}):")
            print("-" * 40)
            for result in not_found:
                print(f"   - {result['query']} ({result['category']})")
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Spara valideringsresultat.
        
        Args:
            results: Lista med valideringsresultat
            output_path: Sökväg att spara till
        """
        logger.info("Sparar valideringsresultat till %s", output_path)
        
        # Spara som JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Skapa sammanfattning
        summary_path = output_path.replace('.json', '_summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("REKOMMENDATION VALIDATION SUMMARY\n")
            f.write("="*50 + "\n\n")
            
            found_games = [r for r in results if r['found']]
            f.write(f"Total games tested: {len(results)}\n")
            f.write(f"Games found: {len(found_games)}\n")
            f.write(f"Success rate: {len(found_games)/len(results)*100:.1f}%\n\n")
            
            f.write("GAMES BY CATEGORY:\n")
            f.write("-" * 30 + "\n")
            categories = {}
            for result in found_games:
                cat = result['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(result['game_name'])
            
            for cat, games in categories.items():
                f.write(f"\n{cat}:\n")
                for game in games:
                    f.write(f"  - {game}\n")
        
        logger.info("Sparade även sammanfattning till %s", summary_path)

def main():
    """Huvudfunktion för automatisk validering."""
    parser = argparse.ArgumentParser(description="Automatisk validering av rekommendationskvalitet")
    parser.add_argument("--input", type=str, 
                       default="data/medium_dataset/games.json",
                       help="Sökväg till input dataset")
    parser.add_argument("--output", type=str, 
                       default="data/validation_results_auto.json",
                       help="Sökväg till output resultat")
    parser.add_argument("--max-games", type=int,
                       help="Maximalt antal spel att testa")
    parser.add_argument("--text-weight", type=float, default=0.6,
                       help="Vikt för text-features (0.0-1.0)")
    parser.add_argument("--max-text-features", type=int, default=5000,
                       help="Maximalt antal text-features")
    parser.add_argument("--min-df", type=int, default=5,
                       help="Minimum document frequency")
    parser.add_argument("--display", action="store_true",
                       help="Visa resultat i terminalen")
    
    args = parser.parse_args()
    
    # Ladda data
    logger.info("Laddar dataset från %s", args.input)
    with open(args.input, 'r', encoding='utf-8') as f:
        games_data = json.load(f)
    
    logger.info("Laddade %d spel", len(games_data))
    
    # Skapa validator
    validator = AutoRecommendationValidator(
        games_data,
        text_weight=args.text_weight,
        max_text_features=args.max_text_features,
        min_df=args.min_df
    )
    
    # Kör validering
    results = validator.run_validation(max_games=args.max_games)
    
    # Visa resultat om begärt
    if args.display:
        validator.display_results(results)
    
    # Spara resultat
    validator.save_results(results, args.output)
    
    print(f"\n✅ Validering klar! Resultat sparade till {args.output}")
    print(f"📊 Testade {len(results)} spel, hittade {len([r for r in results if r['found']])} spel")

if __name__ == "__main__":
    main()
