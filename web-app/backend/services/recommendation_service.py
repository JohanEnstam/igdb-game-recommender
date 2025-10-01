"""
Recommendation service för IGDB Game Recommendation System.

Denna service hanterar laddning av features från Cloud Storage och similarity search.
"""

import os
import logging
import tempfile
from typing import Dict, List, Any, Optional
import numpy as np
from scipy.sparse import load_npz
import pickle
import faiss
from google.cloud import storage, bigquery

logger = logging.getLogger(__name__)

class RecommendationService:
    """Service för att hantera rekommendationer med ML-modeller."""
    
    def __init__(self):
        self.features = None
        self.similarity_index = None
        self.bigquery_client = None
        self.storage_client = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initierar service genom att ladda features och bygga index."""
        if self._initialized:
            return
            
        try:
            logger.info("Initierar RecommendationService...")
            
            # Initiera klienter
            self.bigquery_client = bigquery.Client()
            self.storage_client = storage.Client()
            
            # Ladda features från Cloud Storage
            self._load_features_from_gcs()
            
            # Bygg similarity index
            self._build_similarity_index()
            
            self._initialized = True
            logger.info("RecommendationService initierad framgångsrikt")
            
        except Exception as e:
            logger.error(f"Fel vid initiering av RecommendationService: {e}")
            raise
    
    def _load_features_from_gcs(self) -> None:
        """Laddar features från Cloud Storage."""
        try:
            bucket_name = os.environ.get("FEATURES_BUCKET", "igdb-model-artifacts-dev")
            bucket = self.storage_client.bucket(bucket_name)
            
            # Skapa temporär katalog för nedladdning
            with tempfile.TemporaryDirectory() as temp_dir:
                # Ladda ned filer
                files_to_download = [
                    'text_features.npz',
                    'categorical_features.npz',
                    'combined_features.npz',
                    'features_metadata.pkl'
                ]
                
                for filename in files_to_download:
                    blob_name = f"features/{filename}"
                    blob = bucket.blob(blob_name)
                    local_path = os.path.join(temp_dir, filename)
                    blob.download_to_filename(local_path)
                    logger.info(f"Laddade ned {filename} från Cloud Storage")
                
                # Ladda features
                self.features = self._load_features_from_local(temp_dir)
                
        except Exception as e:
            logger.error(f"Fel vid laddning av features från Cloud Storage: {e}")
            raise
    
    def _load_features_from_local(self, features_dir: str) -> Dict[str, Any]:
        """Laddar features från lokal katalog."""
        # Ladda sparse matrices
        text_features = load_npz(os.path.join(features_dir, 'text_features.npz'))
        categorical_features = load_npz(os.path.join(features_dir, 'categorical_features.npz'))
        combined_features = load_npz(os.path.join(features_dir, 'combined_features.npz'))
        
        # Ladda metadata
        with open(os.path.join(features_dir, 'features_metadata.pkl'), 'rb') as f:
            metadata = pickle.load(f)
        
        features = {
            'text_features': text_features,
            'categorical_features': categorical_features,
            'combined_features': combined_features,
            **metadata
        }
        
        logger.info(f"Laddade features med {combined_features.shape[0]} spel och {combined_features.shape[1]} features")
        return features
    
    def _build_similarity_index(self) -> None:
        """Bygger Faiss-index för similarity search."""
        try:
            logger.info("Bygger Faiss-index...")
            
            # Konvertera sparse matrix till dense
            feature_matrix_dense = self.features['combined_features'].toarray().astype('float32')
            
            # Skapa index
            d = feature_matrix_dense.shape[1]  # Dimensioner
            self.similarity_index = faiss.IndexFlatIP(d)  # Inner product = cosine similarity för normaliserade vektorer
            
            # Normalisera vektorer (för cosine similarity)
            faiss.normalize_L2(feature_matrix_dense)
            
            # Lägg till vektorer till index
            self.similarity_index.add(feature_matrix_dense)
            
            logger.info(f"Faiss-index byggt med {self.similarity_index.ntotal} vektorer")
            
        except Exception as e:
            logger.error(f"Fel vid byggande av Faiss-index: {e}")
            raise
    
    def get_similar_games(self, game_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Hämtar liknande spel baserat på similarity search.
        
        Args:
            game_id: ID för spelet att hitta liknande spel för
            limit: Antal rekommendationer att returnera
            
        Returns:
            Lista med dictionaries innehållande game_id och similarity_score
        """
        if not self._initialized:
            self.initialize()
        
        try:
            # Kontrollera att game_id finns i datasetet
            reverse_mapping = self.features['reverse_mapping']
            if game_id not in reverse_mapping:
                logger.warning(f"Game ID {game_id} finns inte i datasetet")
                return []
            
            # Hämta index för spelet
            game_idx = reverse_mapping[game_id]
            
            # Hämta feature vector för spelet
            query_vector = self.similarity_index.reconstruct(game_idx).reshape(1, -1)
            
            # Sök efter liknande spel
            distances, indices = self.similarity_index.search(query_vector, limit + 1)
            
            # Konvertera till game_ids och scores (hoppa över första som är query-spelet)
            recommendations = []
            id_mapping = self.features['id_mapping']
            
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx != game_idx:  # Exkludera query-spelet
                    game_id_rec = id_mapping[idx]
                    similarity = float(distances[0][i])
                    recommendations.append({
                        'game_id': game_id_rec,
                        'similarity_score': similarity
                    })
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Fel vid hämtning av liknande spel för {game_id}: {e}")
            return []
    
    def get_game_details(self, game_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Hämtar spelinformation från BigQuery.
        
        Args:
            game_ids: Lista med game IDs att hämta information för
            
        Returns:
            Lista med spelinformation
        """
        if not self._initialized:
            self.initialize()
        
        try:
            # Skapa SQL-query
            game_ids_str = "', '".join(game_ids)
            query = f"""
            SELECT
                g.game_id,
                g.canonical_name,
                g.display_name,
                g.summary,
                g.quality_score,
                g.genres,
                g.platforms,
                g.themes,
                g.rating,
                g.cover_url
            FROM
                `igdb-pipeline-v3.igdb_games_dev.games_with_categories` AS g
            WHERE
                g.game_id IN ('{game_ids_str}')
            ORDER BY
                g.quality_score DESC
            """
            
            logger.info(f"Hämtar spelinformation för {len(game_ids)} spel från BigQuery")
            df = self.bigquery_client.query(query).to_dataframe()
            
            # Konvertera till lista med dictionaries
            games = []
            for _, row in df.iterrows():
                # Hantera numpy arrays och None-värden säkert
                def safe_get(value, default=None):
                    if value is None or (hasattr(value, '__len__') and len(value) == 0):
                        return default
                    if hasattr(value, 'tolist'):  # numpy array
                        return value.tolist()
                    # Hantera NaN och inf värden för JSON serialization
                    if isinstance(value, (int, float)) and (np.isnan(value) or np.isinf(value)):
                        return default
                    return value
                
                game = {
                    'id': int(row['game_id']),
                    'name': row['display_name'] or row['canonical_name'],
                    'summary': safe_get(row['summary'], ''),
                    'rating': safe_get(row['rating']),
                    'first_release_date': None,  # Not available in current schema
                    'cover_url': safe_get(row['cover_url']),
                    'genres': safe_get(row['genres'], []),
                    'platforms': safe_get(row['platforms'], []),
                    'themes': safe_get(row['themes'], [])
                }
                games.append(game)
            
            return games
            
        except Exception as e:
            logger.error(f"Fel vid hämtning av spelinformation: {e}")
            return []
    
    def search_games(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Söker efter spel i BigQuery.
        
        Args:
            query: Sökterm
            limit: Maximalt antal resultat
            
        Returns:
            Lista med spel som matchar söktermen
        """
        if not self._initialized:
            self.initialize()
        
        try:
            # Skapa SQL-query för sökning
            search_query = f"""
            SELECT
                g.game_id,
                g.canonical_name,
                g.display_name,
                g.summary,
                g.quality_score,
                g.genres,
                g.platforms,
                g.themes,
                g.rating,
                g.cover_url
            FROM
                `igdb-pipeline-v3.igdb_games_dev.games_with_categories` AS g
            WHERE
                LOWER(g.display_name) LIKE LOWER('%{query}%')
                OR LOWER(g.canonical_name) LIKE LOWER('%{query}%')
                OR LOWER(g.summary) LIKE LOWER('%{query}%')
            ORDER BY
                g.quality_score DESC
            LIMIT {limit}
            """
            
            logger.info(f"Söker efter spel med query: {query}")
            df = self.bigquery_client.query(search_query).to_dataframe()
            
            # Konvertera till lista med dictionaries
            games = []
            for _, row in df.iterrows():
                # Hantera numpy arrays och None-värden säkert
                def safe_get(value, default=None):
                    if value is None or (hasattr(value, '__len__') and len(value) == 0):
                        return default
                    if hasattr(value, 'tolist'):  # numpy array
                        return value.tolist()
                    # Hantera NaN och inf värden för JSON serialization
                    if isinstance(value, (int, float)) and (np.isnan(value) or np.isinf(value)):
                        return default
                    return value
                
                game = {
                    'id': int(row['game_id']),
                    'name': row['display_name'] or row['canonical_name'],
                    'summary': safe_get(row['summary'], ''),
                    'rating': safe_get(row['rating']),
                    'first_release_date': None,  # Not available in current schema
                    'cover_url': safe_get(row['cover_url']),
                    'genres': safe_get(row['genres'], []),
                    'platforms': safe_get(row['platforms'], []),
                    'themes': safe_get(row['themes'], [])
                }
                games.append(game)
            
            return games
            
        except Exception as e:
            logger.error(f"Fel vid sökning av spel: {e}")
            return []

# Global service instance
recommendation_service = RecommendationService()
