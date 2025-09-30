"""
Similarity search för IGDB Game Recommendation System.

Detta script implementerar similarity search för att hitta liknande spel baserat på features.
"""

import numpy as np
import faiss
import logging
from typing import Dict, List, Tuple, Any, Optional

# Konfigurera loggning
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimilaritySearch:
    """Implementerar similarity search för att hitta liknande spel."""
    
    def __init__(self, features: Dict[str, Any]):
        """
        Initierar SimilaritySearch.
        
        Args:
            features: Dictionary med features och metadata från FeatureExtractor
        """
        self.features = features
        self.combined_features = features['combined_features']
        self.id_mapping = features['id_mapping']
        self.reverse_mapping = features['reverse_mapping']
        self.index = None
        
    def build_index(self) -> None:
        """
        Bygger ett Faiss-index för snabb similarity search.
        """
        logger.info("Bygger Faiss-index...")
        
        # Konvertera sparse matrix till dense
        feature_matrix_dense = self.combined_features.toarray().astype('float32')
        
        # Skapa index
        d = feature_matrix_dense.shape[1]  # Dimensioner
        self.index = faiss.IndexFlatIP(d)  # Inner product = cosine similarity för normaliserade vektorer
        
        # Normalisera vektorer (för cosine similarity)
        faiss.normalize_L2(feature_matrix_dense)
        
        # Lägg till vektorer till index
        self.index.add(feature_matrix_dense)
        
        logger.info("Faiss-index byggt med %d vektorer", self.index.ntotal)
    
    def get_similar_games(self, game_id: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Hämtar liknande spel baserat på similarity search.
        
        Args:
            game_id: ID för spelet att hitta liknande spel för
            top_n: Antal rekommendationer att returnera
            
        Returns:
            Lista med dictionaries innehållande game_id och similarity_score
        """
        if self.index is None:
            self.build_index()
        
        if game_id not in self.reverse_mapping:
            logger.warning("Game ID %s finns inte i datasetet", game_id)
            return []
        
        # Hämta index för spelet
        game_idx = self.reverse_mapping[game_id]
        
        # Hämta feature vector för spelet
        query_vector = self.index.reconstruct(game_idx).reshape(1, -1)
        
        # Sök efter liknande spel
        distances, indices = self.index.search(query_vector, top_n + 1)
        
        # Konvertera till game_ids och scores (hoppa över första som är query-spelet)
        recommendations = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != game_idx:  # Exkludera query-spelet
                game_id = self.id_mapping[idx]
                similarity = float(distances[0][i])
                recommendations.append({
                    'game_id': game_id,
                    'similarity_score': similarity
                })
        
        return recommendations[:top_n]
    
    def get_similar_games_batch(self, game_ids: List[str], top_n: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Hämtar liknande spel för flera spel samtidigt.
        
        Args:
            game_ids: Lista med IDs för spelen att hitta liknande spel för
            top_n: Antal rekommendationer att returnera per spel
            
        Returns:
            Dictionary med game_id som nyckel och lista med rekommendationer som värde
        """
        if self.index is None:
            self.build_index()
        
        results = {}
        
        for game_id in game_ids:
            results[game_id] = self.get_similar_games(game_id, top_n)
        
        return results
    
    def benchmark_performance(self, num_queries: int = 100) -> Dict[str, float]:
        """
        Mät prestanda för rekommendationssystemet.
        
        Args:
            num_queries: Antal queries att köra
            
        Returns:
            Dictionary med prestandamått
        """
        import time
        import random
        
        if self.index is None:
            self.build_index()
        
        # Välj slumpmässiga spel för benchmark
        sample_game_ids = random.sample(list(self.reverse_mapping.keys()), min(num_queries, len(self.reverse_mapping)))
        
        # Mät query-tid
        start_time = time.time()
        for game_id in sample_game_ids:
            _ = self.get_similar_games(game_id, top_n=10)
        
        total_time = time.time() - start_time
        avg_time = total_time / len(sample_game_ids)
        qps = len(sample_game_ids) / total_time
        
        results = {
            'total_time': total_time,
            'avg_time': avg_time,
            'queries_per_second': qps,
            'num_queries': len(sample_game_ids)
        }
        
        logger.info("Benchmark resultat:")
        logger.info("- Total tid för %d queries: %.4f sekunder", len(sample_game_ids), total_time)
        logger.info("- Genomsnittlig query-tid: %.2f ms", avg_time * 1000)
        logger.info("- Queries per sekund: %.2f", qps)
        
        return results
    
    def save_index(self, output_path: str) -> None:
        """
        Sparar Faiss-index till disk.
        
        Args:
            output_path: Sökväg att spara index till
        """
        if self.index is None:
            self.build_index()
        
        faiss.write_index(self.index, output_path)
        logger.info("Sparade Faiss-index till %s", output_path)
    
    @classmethod
    def load_from_files(cls, features_path: str, index_path: Optional[str] = None) -> 'SimilaritySearch':
        """
        Laddar SimilaritySearch från sparade filer.
        
        Args:
            features_path: Sökväg till sparade features
            index_path: Sökväg till sparat Faiss-index (optional)
            
        Returns:
            SimilaritySearch-instans
        """
        from feature_extractor import FeatureExtractor
        
        # Ladda features
        features = FeatureExtractor.load_features(features_path)
        
        # Skapa SimilaritySearch
        similarity_search = cls(features)
        
        # Ladda index om det finns
        if index_path:
            similarity_search.index = faiss.read_index(index_path)
            logger.info("Laddade Faiss-index från %s", index_path)
        
        return similarity_search


if __name__ == "__main__":
    import argparse
    import os
    import pandas as pd
    
    parser = argparse.ArgumentParser(description="Kör similarity search på speldata")
    parser.add_argument("--features", type=str, required=True, help="Sökväg till sparade features")
    parser.add_argument("--index", type=str, help="Sökväg till sparat Faiss-index")
    parser.add_argument("--game-id", type=str, help="ID för spelet att hitta liknande spel för")
    parser.add_argument("--top-n", type=int, default=10, help="Antal rekommendationer att returnera")
    parser.add_argument("--benchmark", action="store_true", help="Kör prestandabenchmark")
    parser.add_argument("--save-index", type=str, help="Spara Faiss-index till sökväg")
    
    args = parser.parse_args()
    
    # Ladda similarity search
    similarity_search = SimilaritySearch.load_from_files(args.features, args.index)
    
    # Kör benchmark om det är specifierat
    if args.benchmark:
        similarity_search.benchmark_performance()
    
    # Spara index om det är specifierat
    if args.save_index:
        similarity_search.save_index(args.save_index)
    
    # Hämta rekommendationer om game_id är specifierat
    if args.game_id:
        # Ladda metadata för att visa spelnamn
        import pickle
        with open(os.path.join(args.features, 'features_metadata.pkl'), 'rb') as f:
            metadata = pickle.load(f)
        
        # Hämta rekommendationer
        recommendations = similarity_search.get_similar_games(args.game_id, args.top_n)
        
        # Visa rekommendationer
        print(f"\nTop {args.top_n} rekommendationer för spel {args.game_id}:")
        for i, rec in enumerate(recommendations):
            print(f"{i+1}. {rec['game_id']} (Score: {rec['similarity_score']:.4f})")
