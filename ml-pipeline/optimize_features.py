#!/usr/bin/env python3
"""
Optimera feature extraction på mellanstort dataset.

Detta script testar olika parametrar och approacher för feature extraction
för att hitta den bästa konfigurationen för rekommendationssystemet.
"""

import json
import pandas as pd
import numpy as np
import os
import logging
import time
from typing import Dict, Any, List, Tuple
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack, save_npz, load_npz
import pickle
# import matplotlib.pyplot as plt
# import seaborn as sns

# Konfigurera loggning
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureOptimizer:
    """Optimera feature extraction parametrar."""
    
    def __init__(self, games_data: List[Dict[str, Any]]):
        """
        Initierar FeatureOptimizer.
        
        Args:
            games_data: Lista med speldata
        """
        self.games_data = games_data
        self.df = pd.DataFrame(games_data)
        self.results = []
        
    def extract_features_with_params(self, 
                                   max_text_features: int = 5000,
                                   text_weight: float = 0.7,
                                   min_df: int = 5,
                                   ngram_range: Tuple[int, int] = (1, 2),
                                   stop_words: str = 'english') -> Dict[str, Any]:
        """
        Extrahera features med specificerade parametrar.
        
        Args:
            max_text_features: Maximalt antal text-features
            text_weight: Vikt för text-features
            min_df: Minimum document frequency för TF-IDF
            ngram_range: N-gram range för TF-IDF
            stop_words: Stop words för TF-IDF
            
        Returns:
            Dictionary med features och metadata
        """
        logger.info("Extraherar features med parametrar: max_text_features=%d, text_weight=%.2f, min_df=%d, ngram_range=%s", 
                   max_text_features, text_weight, min_df, ngram_range)
        
        start_time = time.time()
        
        # Förbered data
        df = self.df.copy()
        df['summary_clean'] = df['summary'].fillna('')
        
        # Filtrera bort spel utan summary
        df_with_summary = df[df['summary_clean'] != ''].copy()
        
        if len(df_with_summary) == 0:
            logger.warning("Inga spel med summary hittades")
            return None
        
        # Text features
        tfidf = TfidfVectorizer(
            max_features=max_text_features,
            stop_words=stop_words,
            min_df=min_df,
            ngram_range=ngram_range
        )
        
        try:
            text_features = tfidf.fit_transform(df_with_summary['summary_clean'])
        except ValueError as e:
            logger.error("Fel vid TF-IDF extraktion: %s", str(e))
            return None
        
        # Categoriska features
        mlb_genres = MultiLabelBinarizer()
        mlb_platforms = MultiLabelBinarizer()
        mlb_themes = MultiLabelBinarizer()
        
        # Förbered kategoriska data
        genres = df_with_summary['genres'].apply(lambda x: [] if not isinstance(x, list) else x)
        platforms = df_with_summary['platforms'].apply(lambda x: [] if not isinstance(x, list) else x)
        themes = df_with_summary['themes'].apply(lambda x: [] if not isinstance(x, list) else x)
        
        try:
            genres_features = mlb_genres.fit_transform(genres)
            platforms_features = mlb_platforms.fit_transform(platforms)
            themes_features = mlb_themes.fit_transform(themes)
        except ValueError as e:
            logger.error("Fel vid kategorisk feature extraktion: %s", str(e))
            return None
        
        # Konvertera till sparse matrices om de inte redan är det
        from scipy.sparse import csr_matrix
        if not isinstance(genres_features, csr_matrix):
            genres_features = csr_matrix(genres_features)
        if not isinstance(platforms_features, csr_matrix):
            platforms_features = csr_matrix(platforms_features)
        if not isinstance(themes_features, csr_matrix):
            themes_features = csr_matrix(themes_features)
        
        # Kombinera kategoriska features
        categorical_features = hstack([genres_features, platforms_features, themes_features])
        
        # Normalisera och kombinera features
        from sklearn.preprocessing import normalize
        text_features_norm = normalize(text_features)
        categorical_features_norm = normalize(categorical_features)
        
        combined_features = hstack([
            text_features_norm * text_weight,
            categorical_features_norm * (1.0 - text_weight)
        ])
        
        # Skapa ID-mapping
        id_mapping = dict(enumerate(df_with_summary['game_id']))
        reverse_mapping = {v: k for k, v in id_mapping.items()}
        
        extraction_time = time.time() - start_time
        
        return {
            'text_features': text_features,
            'categorical_features': categorical_features,
            'combined_features': combined_features,
            'id_mapping': id_mapping,
            'reverse_mapping': reverse_mapping,
            'tfidf': tfidf,
            'mlb_genres': mlb_genres,
            'mlb_platforms': mlb_platforms,
            'mlb_themes': mlb_themes,
            'extraction_time': extraction_time,
            'num_games': len(df_with_summary),
            'text_features_count': text_features.shape[1],
            'categorical_features_count': categorical_features.shape[1],
            'combined_features_count': combined_features.shape[1]
        }
    
    def test_recommendations(self, features: Dict[str, Any], num_tests: int = 10) -> Dict[str, float]:
        """
        Testa rekommendationskvalitet med manuell bedömning.
        
        Args:
            features: Dictionary med features
            num_tests: Antal test att köra
            
        Returns:
            Dictionary med prestandamätningar
        """
        logger.info("Testar rekommendationskvalitet med %d test", num_tests)
        
        if features is None:
            return {'error': 'Inga features att testa'}
        
        start_time = time.time()
        
        # Välj slumpmässiga spel för test
        test_game_ids = np.random.choice(
            list(features['reverse_mapping'].keys()), 
            size=min(num_tests, len(features['reverse_mapping'])), 
            replace=False
        )
        
        total_similarity = 0
        successful_queries = 0
        
        for game_id in test_game_ids:
            try:
                # Hämta rekommendationer
                recommendations = self.get_recommendations(
                    game_id, features, top_n=5
                )
                
                if recommendations:
                    # Beräkna genomsnittlig similarity
                    avg_similarity = np.mean([rec['similarity_score'] for rec in recommendations])
                    total_similarity += avg_similarity
                    successful_queries += 1
                    
            except Exception as e:
                logger.warning("Fel vid rekommendation för game_id %s: %s", game_id, str(e))
                continue
        
        query_time = time.time() - start_time
        
        if successful_queries == 0:
            return {'error': 'Inga lyckade rekommendationer'}
        
        return {
            'avg_similarity': total_similarity / successful_queries,
            'successful_queries': successful_queries,
            'total_queries': len(test_game_ids),
            'query_time': query_time,
            'avg_query_time': query_time / successful_queries
        }
    
    def get_recommendations(self, game_id: str, features: Dict[str, Any], top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Hämta rekommendationer för ett spel.
        
        Args:
            game_id: ID för spelet
            features: Dictionary med features
            top_n: Antal rekommendationer att returnera
            
        Returns:
            Lista med rekommendationer
        """
        if game_id not in features['reverse_mapping']:
            return []
        
        game_idx = features['reverse_mapping'][game_id]
        game_features = features['combined_features'][game_idx:game_idx+1]
        
        # Beräkna similarity
        similarities = cosine_similarity(game_features, features['combined_features'])[0]
        
        # Hämta top similar games
        similar_indices = np.argsort(similarities)[::-1][1:top_n+1]  # Skip the first one (self)
        
        # Konvertera till game_ids och scores
        recommendations = [
            {
                'game_id': features['id_mapping'][idx],
                'similarity_score': float(similarities[idx])
            }
            for idx in similar_indices
        ]
        
        return recommendations
    
    def run_optimization(self, 
                        text_weights: List[float] = [0.5, 0.6, 0.7, 0.8, 0.9],
                        max_text_features_list: List[int] = [3000, 5000, 7000, 10000],
                        min_df_list: List[int] = [3, 5, 10],
                        ngram_ranges: List[Tuple[int, int]] = [(1, 1), (1, 2), (2, 2)]) -> List[Dict[str, Any]]:
        """
        Kör optimering med olika parametrar.
        
        Args:
            text_weights: Lista med text-weights att testa
            max_text_features_list: Lista med max_text_features att testa
            min_df_list: Lista med min_df att testa
            ngram_ranges: Lista med ngram_ranges att testa
            
        Returns:
            Lista med resultat
        """
        logger.info("Startar optimering med %d parameterkombinationer", 
                   len(text_weights) * len(max_text_features_list) * len(min_df_list) * len(ngram_ranges))
        
        results = []
        total_combinations = len(text_weights) * len(max_text_features_list) * len(min_df_list) * len(ngram_ranges)
        current_combination = 0
        
        for text_weight in text_weights:
            for max_text_features in max_text_features_list:
                for min_df in min_df_list:
                    for ngram_range in ngram_ranges:
                        current_combination += 1
                        logger.info("Testar kombination %d/%d: text_weight=%.2f, max_text_features=%d, min_df=%d, ngram_range=%s", 
                                   current_combination, total_combinations, text_weight, max_text_features, min_df, ngram_range)
                        
                        try:
                            # Extrahera features
                            features = self.extract_features_with_params(
                                max_text_features=max_text_features,
                                text_weight=text_weight,
                                min_df=min_df,
                                ngram_range=ngram_range
                            )
                            
                            if features is None:
                                logger.warning("Misslyckades att extrahera features för kombination %d", current_combination)
                                continue
                            
                            # Testa rekommendationskvalitet
                            performance = self.test_recommendations(features, num_tests=5)
                            
                            # Spara resultat
                            result = {
                                'text_weight': text_weight,
                                'max_text_features': max_text_features,
                                'min_df': min_df,
                                'ngram_range': ngram_range,
                                'extraction_time': features['extraction_time'],
                                'num_games': features['num_games'],
                                'text_features_count': features['text_features_count'],
                                'categorical_features_count': features['categorical_features_count'],
                                'combined_features_count': features['combined_features_count'],
                                **performance
                            }
                            
                            results.append(result)
                            
                            logger.info("Resultat: avg_similarity=%.4f, extraction_time=%.2fs, features_count=%d", 
                                       result.get('avg_similarity', 0), 
                                       result['extraction_time'], 
                                       result['combined_features_count'])
                            
                        except Exception as e:
                            logger.error("Fel vid optimering för kombination %d: %s", current_combination, str(e))
                            continue
        
        self.results = results
        return results
    
    def save_results(self, output_path: str) -> None:
        """
        Spara optimeringsresultat.
        
        Args:
            output_path: Sökväg att spara till
        """
        logger.info("Sparar optimeringsresultat till %s", output_path)
        
        # Spara som JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Spara som CSV för enkel analys
        if self.results:
            df_results = pd.DataFrame(self.results)
            csv_path = output_path.replace('.json', '.csv')
            df_results.to_csv(csv_path, index=False)
            logger.info("Sparade även som CSV: %s", csv_path)
    
    def analyze_results(self) -> Dict[str, Any]:
        """
        Analysera optimeringsresultat.
        
        Returns:
            Dictionary med analys
        """
        if not self.results:
            return {'error': 'Inga resultat att analysera'}
        
        df_results = pd.DataFrame(self.results)
        
        # Filtrera bort felaktiga resultat
        df_results = df_results[df_results['avg_similarity'].notna()]
        
        if len(df_results) == 0:
            return {'error': 'Inga giltiga resultat att analysera'}
        
        # Hitta bästa resultat
        best_result = df_results.loc[df_results['avg_similarity'].idxmax()]
        
        # Analysera parametrar
        analysis = {
            'total_combinations_tested': len(df_results),
            'best_avg_similarity': best_result['avg_similarity'],
            'best_parameters': {
                'text_weight': best_result['text_weight'],
                'max_text_features': best_result['max_text_features'],
                'min_df': best_result['min_df'],
                'ngram_range': best_result['ngram_range']
            },
            'best_extraction_time': best_result['extraction_time'],
            'best_features_count': best_result['combined_features_count'],
            'similarity_stats': {
                'mean': df_results['avg_similarity'].mean(),
                'std': df_results['avg_similarity'].std(),
                'min': df_results['avg_similarity'].min(),
                'max': df_results['avg_similarity'].max()
            },
            'extraction_time_stats': {
                'mean': df_results['extraction_time'].mean(),
                'std': df_results['extraction_time'].std(),
                'min': df_results['extraction_time'].min(),
                'max': df_results['extraction_time'].max()
            }
        }
        
        return analysis

def main():
    """Huvudfunktion för feature optimering."""
    parser = argparse.ArgumentParser(description="Optimera feature extraction")
    parser.add_argument("--input", type=str, 
                       default="data/medium_dataset/games.json",
                       help="Sökväg till input dataset")
    parser.add_argument("--output", type=str, 
                       default="data/optimization_results.json",
                       help="Sökväg till output resultat")
    parser.add_argument("--quick", action="store_true",
                       help="Kör snabb optimering med färre parametrar")
    
    args = parser.parse_args()
    
    # Ladda data
    logger.info("Laddar dataset från %s", args.input)
    with open(args.input, 'r', encoding='utf-8') as f:
        games_data = json.load(f)
    
    logger.info("Laddade %d spel", len(games_data))
    
    # Skapa optimizer
    optimizer = FeatureOptimizer(games_data)
    
    # Definiera parametrar för optimering
    if args.quick:
        # Snabb optimering
        text_weights = [0.6, 0.7, 0.8]
        max_text_features_list = [3000, 5000]
        min_df_list = [5]
        ngram_ranges = [(1, 2)]
    else:
        # Full optimering
        text_weights = [0.5, 0.6, 0.7, 0.8, 0.9]
        max_text_features_list = [3000, 5000, 7000, 10000]
        min_df_list = [3, 5, 10]
        ngram_ranges = [(1, 1), (1, 2), (2, 2)]
    
    # Kör optimering
    results = optimizer.run_optimization(
        text_weights=text_weights,
        max_text_features_list=max_text_features_list,
        min_df_list=min_df_list,
        ngram_ranges=ngram_ranges
    )
    
    # Spara resultat
    optimizer.save_results(args.output)
    
    # Analysera resultat
    analysis = optimizer.analyze_results()
    
    logger.info("Optimering klar!")
    
    if 'error' in analysis:
        logger.error("Analys misslyckades: %s", analysis['error'])
    else:
        logger.info("Bästa resultat:")
        logger.info("- Avg similarity: %.4f", analysis['best_avg_similarity'])
        logger.info("- Text weight: %.2f", analysis['best_parameters']['text_weight'])
        logger.info("- Max text features: %d", analysis['best_parameters']['max_text_features'])
        logger.info("- Min df: %d", analysis['best_parameters']['min_df'])
        logger.info("- N-gram range: %s", analysis['best_parameters']['ngram_range'])
        logger.info("- Extraction time: %.2fs", analysis['best_extraction_time'])
        logger.info("- Features count: %d", analysis['best_features_count'])

if __name__ == "__main__":
    main()
