#!/usr/bin/env python3
"""
Validera rekommendationskvalitet med manuell bedömning.

Detta script testar rekommendationer för populära spel och presenterar
resultaten för manuell bedömning av relevans.
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

class RecommendationValidator:
    """Validera rekommendationskvalitet med manuell bedömning."""
    
    def __init__(self, games_data: List[Dict[str, Any]], 
                 text_weight: float = 0.6, 
                 max_text_features: int = 5000,
                 min_df: int = 5,
                 ngram_range: tuple = (1, 2)):
        """
        Initierar RecommendationValidator.
        
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
    
    def display_game_info(self, game: pd.Series) -> None:
        """Visa information om ett spel."""
        print(f"\n{'='*80}")
        print(f"🎮 {game['display_name']}")
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
    
    def display_recommendation(self, rec: Dict[str, Any], index: int) -> None:
        """Visa en rekommendation."""
        print(f"\n{index}. {rec['display_name']}")
        print(f"   Similarity: {rec['similarity_score']:.4f} | Quality: {rec['quality_score']:.2f}")
        
        if rec.get('genres'):
            print(f"   Genres: {', '.join(rec['genres'][:3])}")
        
        if rec.get('summary'):
            summary = str(rec['summary'])
            if len(summary) > 200:
                summary = summary[:200] + '...'
            print(f"   {summary}")
    
    def validate_single_game(self, test_game: Dict[str, str]) -> Dict[str, Any]:
        """
        Validera rekommendationer för ett spel.
        
        Args:
            test_game: Dictionary med 'name' och 'category'
            
        Returns:
            Dictionary med valideringsresultat
        """
        print(f"\n{'#'*80}")
        print(f"TESTING: {test_game['name']} ({test_game['category']})")
        print(f"{'#'*80}")
        
        # Hitta spelet
        game = self.find_best_match(test_game['name'])
        if game is None:
            print(f"❌ Ingen matchning hittades för '{test_game['name']}'")
            return {
                'query': test_game['name'],
                'category': test_game['category'],
                'found': False,
                'recommendations': []
            }
        
        # Visa spelinfo
        self.display_game_info(game)
        
        # Hämta rekommendationer
        recommendations = self.get_recommendations(game['game_id'], top_n=10)
        
        if not recommendations:
            print("❌ Inga rekommendationer hittades")
            return {
                'query': test_game['name'],
                'category': test_game['category'],
                'found': True,
                'game_id': game['game_id'],
                'game_name': game['display_name'],
                'recommendations': []
            }
        
        print(f"\n📋 Top 10 rekommendationer:")
        print("-" * 80)
        
        # Visa rekommendationer
        for i, rec in enumerate(recommendations, 1):
            self.display_recommendation(rec, i)
        
        return {
            'query': test_game['name'],
            'category': test_game['category'],
            'found': True,
            'game_id': game['game_id'],
            'game_name': game['display_name'],
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
        print(f"\n{'='*80}")
        print("🔍 REKOMMENDATION VALIDATION")
        print(f"{'='*80}")
        print(f"Testar {len(self.test_games)} populära spel")
        print(f"Använder optimerade parametrar: text_weight=0.6, max_features=5000")
        print(f"{'='*80}")
        
        results = []
        games_to_test = self.test_games[:max_games] if max_games else self.test_games
        
        for i, test_game in enumerate(games_to_test, 1):
            print(f"\n[{i}/{len(games_to_test)}]")
            result = self.validate_single_game(test_game)
            results.append(result)
            
            # Pausa för manuell bedömning
            if i < len(games_to_test):
                input("\n⏸️  Tryck Enter för att fortsätta till nästa spel...")
        
        return results
    
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
    """Huvudfunktion för validering."""
    parser = argparse.ArgumentParser(description="Validera rekommendationskvalitet")
    parser.add_argument("--input", type=str, 
                       default="data/medium_dataset/games.json",
                       help="Sökväg till input dataset")
    parser.add_argument("--output", type=str, 
                       default="data/validation_results.json",
                       help="Sökväg till output resultat")
    parser.add_argument("--max-games", type=int,
                       help="Maximalt antal spel att testa")
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
    
    # Skapa validator
    validator = RecommendationValidator(
        games_data,
        text_weight=args.text_weight,
        max_text_features=args.max_text_features,
        min_df=args.min_df
    )
    
    # Kör validering
    results = validator.run_validation(max_games=args.max_games)
    
    # Spara resultat
    validator.save_results(results, args.output)
    
    print(f"\n✅ Validering klar! Resultat sparade till {args.output}")
    print(f"📊 Testade {len(results)} spel, hittade {len([r for r in results if r['found']])} spel")

if __name__ == "__main__":
    main()
