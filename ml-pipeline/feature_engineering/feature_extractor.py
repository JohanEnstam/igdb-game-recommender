"""
Feature extraction för IGDB Game Recommendation System.

Detta script extraherar features från speldata för användning i rekommendationssystemet.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from scipy.sparse import hstack, save_npz, load_npz
import pickle
import os
import logging
from typing import Dict, Any, Tuple, List, Optional

# Konfigurera loggning
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureExtractor:
    """Extraherar features från speldata för rekommendationssystemet."""
    
    def __init__(self, max_text_features: int = 5000, text_weight: float = 0.7):
        """
        Initierar FeatureExtractor.
        
        Args:
            max_text_features: Maximalt antal text-features att extrahera
            text_weight: Vikt för text-features relativt kategoriska features (0.0-1.0)
        """
        self.max_text_features = max_text_features
        self.text_weight = text_weight
        self.tfidf = TfidfVectorizer(
            max_features=max_text_features,
            stop_words='english',
            min_df=5,
            ngram_range=(1, 2)
        )
        self.mlb_genres = MultiLabelBinarizer()
        self.mlb_platforms = MultiLabelBinarizer()
        self.mlb_themes = MultiLabelBinarizer()
        self.id_mapping = {}
        self.reverse_mapping = {}
        
    def extract_text_features(self, games_df: pd.DataFrame) -> Tuple[Any, TfidfVectorizer]:
        """
        Extraherar text-features från spelsammanfattningar med TF-IDF.
        
        Args:
            games_df: DataFrame med speldata, måste innehålla 'summary' kolumn
            
        Returns:
            Sparse matrix med TF-IDF features och TF-IDF vektoriseraren
        """
        logger.info("Extraherar text-features från %d spel", len(games_df))
        
        # Hantera saknade värden
        games_df['summary_clean'] = games_df['summary'].fillna('')
        
        # Transformera text till TF-IDF features
        text_features = self.tfidf.fit_transform(games_df['summary_clean'])
        
        logger.info("Extraherade %d text-features", text_features.shape[1])
        return text_features
    
    def extract_categorical_features(self, games_df: pd.DataFrame) -> Any:
        """
        Extraherar kategoriska features med one-hot encoding.
        
        Args:
            games_df: DataFrame med speldata, måste innehålla 'genres', 'platforms', 'themes'
            
        Returns:
            Sparse matrix med one-hot encoded features
        """
        logger.info("Extraherar kategoriska features från %d spel", len(games_df))
        
        # Förbehandla listor
        genres = games_df['genres'].fillna('').apply(lambda x: [] if x == '' else x)
        platforms = games_df['platforms'].fillna('').apply(lambda x: [] if x == '' else x)
        themes = games_df['themes'].fillna('').apply(lambda x: [] if x == '' else x)
        
        # One-hot encoding
        genres_features = self.mlb_genres.fit_transform(genres)
        platforms_features = self.mlb_platforms.fit_transform(platforms)
        themes_features = self.mlb_themes.fit_transform(themes)
        
        # Kombinera alla kategoriska features
        categorical_features = hstack([
            genres_features,
            platforms_features,
            themes_features
        ])
        
        logger.info("Extraherade %d kategoriska features", categorical_features.shape[1])
        return categorical_features
    
    def combine_features(self, text_features: Any, categorical_features: Any) -> Any:
        """
        Kombinerar text- och kategoriska features med viktning.
        
        Args:
            text_features: Sparse matrix med TF-IDF features
            categorical_features: Sparse matrix med kategoriska features
            
        Returns:
            Sparse matrix med kombinerade features
        """
        from sklearn.preprocessing import normalize
        
        logger.info("Kombinerar features med text_weight=%.2f", self.text_weight)
        
        # Normalisera features
        text_features_norm = normalize(text_features)
        categorical_features_norm = normalize(categorical_features)
        
        # Kombinera med viktning
        combined_features = hstack([
            text_features_norm * self.text_weight,
            categorical_features_norm * (1.0 - self.text_weight)
        ])
        
        logger.info("Skapade kombinerade features med dimensioner %s", str(combined_features.shape))
        return combined_features
    
    def create_id_mapping(self, games_df: pd.DataFrame) -> None:
        """
        Skapar mapping mellan index och game_id.
        
        Args:
            games_df: DataFrame med speldata, måste innehålla 'game_id' kolumn
        """
        self.id_mapping = dict(enumerate(games_df['game_id']))
        self.reverse_mapping = {v: k for k, v in self.id_mapping.items()}
        
    def extract_features(self, games_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extraherar alla features från speldata.
        
        Args:
            games_df: DataFrame med speldata
            
        Returns:
            Dictionary med features och metadata
        """
        # Skapa ID-mapping
        self.create_id_mapping(games_df)
        
        # Extrahera features
        text_features = self.extract_text_features(games_df)
        categorical_features = self.extract_categorical_features(games_df)
        combined_features = self.combine_features(text_features, categorical_features)
        
        return {
            'text_features': text_features,
            'categorical_features': categorical_features,
            'combined_features': combined_features,
            'id_mapping': self.id_mapping,
            'reverse_mapping': self.reverse_mapping,
            'tfidf': self.tfidf,
            'mlb_genres': self.mlb_genres,
            'mlb_platforms': self.mlb_platforms,
            'mlb_themes': self.mlb_themes
        }
    
    def save_features(self, features: Dict[str, Any], output_dir: str) -> None:
        """
        Sparar extraherade features till disk.
        
        Args:
            features: Dictionary med features och metadata
            output_dir: Katalog att spara features i
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Spara sparse matrices
        save_npz(os.path.join(output_dir, 'text_features.npz'), features['text_features'])
        save_npz(os.path.join(output_dir, 'categorical_features.npz'), features['categorical_features'])
        save_npz(os.path.join(output_dir, 'combined_features.npz'), features['combined_features'])
        
        # Spara metadata
        with open(os.path.join(output_dir, 'features_metadata.pkl'), 'wb') as f:
            pickle.dump({
                'id_mapping': features['id_mapping'],
                'reverse_mapping': features['reverse_mapping'],
                'tfidf': features['tfidf'],
                'mlb_genres': features['mlb_genres'],
                'mlb_platforms': features['mlb_platforms'],
                'mlb_themes': features['mlb_themes']
            }, f)
        
        logger.info("Sparade features till %s", output_dir)
    
    @staticmethod
    def load_features(input_dir: str) -> Dict[str, Any]:
        """
        Laddar sparade features från disk.
        
        Args:
            input_dir: Katalog att ladda features från
            
        Returns:
            Dictionary med features och metadata
        """
        # Ladda sparse matrices
        text_features = load_npz(os.path.join(input_dir, 'text_features.npz'))
        categorical_features = load_npz(os.path.join(input_dir, 'categorical_features.npz'))
        combined_features = load_npz(os.path.join(input_dir, 'combined_features.npz'))
        
        # Ladda metadata
        with open(os.path.join(input_dir, 'features_metadata.pkl'), 'rb') as f:
            metadata = pickle.load(f)
        
        features = {
            'text_features': text_features,
            'categorical_features': categorical_features,
            'combined_features': combined_features,
            **metadata
        }
        
        logger.info("Laddade features från %s", input_dir)
        return features


def load_games_from_bigquery(limit: Optional[int] = None) -> pd.DataFrame:
    """
    Ladda speldata från BigQuery.
    
    Args:
        limit: Maximalt antal spel att ladda (None för alla)
        
    Returns:
        DataFrame med speldata
    """
    from google.cloud import bigquery
    
    client = bigquery.Client()
    
    # Skapa SQL-query
    limit_clause = f"LIMIT {limit}" if limit is not None else ""
    
    query = f"""
    SELECT
        game_id,
        canonical_name,
        display_name,
        summary,
        (SELECT ARRAY_AGG(genre) FROM UNNEST(genres) AS genre) AS genres,
        (SELECT ARRAY_AGG(platform) FROM UNNEST(platforms) AS platform) AS platforms,
        (SELECT ARRAY_AGG(theme) FROM UNNEST(themes) AS theme) AS themes,
        quality_score
    FROM
        `igdb-pipeline-v3.igdb_games_dev.games`
    WHERE
        summary IS NOT NULL
    ORDER BY
        quality_score DESC
    {limit_clause}
    """
    
    logger.info("Hämtar data från BigQuery%s", f" (limit: {limit})" if limit else "")
    return client.query(query).to_dataframe()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extrahera features från speldata")
    parser.add_argument("--limit", type=int, default=1000, help="Antal spel att ladda")
    parser.add_argument("--output", type=str, default="../data/features", help="Katalog att spara features i")
    parser.add_argument("--text-weight", type=float, default=0.7, help="Vikt för text-features (0.0-1.0)")
    parser.add_argument("--max-text-features", type=int, default=5000, help="Maximalt antal text-features")
    
    args = parser.parse_args()
    
    # Ladda data
    games_df = load_games_from_bigquery(args.limit)
    
    # Extrahera features
    extractor = FeatureExtractor(
        max_text_features=args.max_text_features,
        text_weight=args.text_weight
    )
    features = extractor.extract_features(games_df)
    
    # Spara features
    extractor.save_features(features, args.output)
