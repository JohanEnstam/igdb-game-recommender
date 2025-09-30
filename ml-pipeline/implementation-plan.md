# Implementation Plan - Rekommendationssystem

Detta dokument beskriver den stegvisa implementationsplanen för rekommendationssystemet i IGDB Game Recommendation System.

## Översikt

Vi implementerar ett enkelt men effektivt content-based rekommendationssystem baserat på feature extraction och similarity search. Systemet är designat för att vara skalbart och kunna hantera 300k+ spel med god prestanda.

## Faser

### Fas 1: Proof of Concept (Lokal utveckling)

**Mål**: Validera grundläggande approach med en mindre delmängd av data.

**Steg**:

1. **Datahämtning från BigQuery**
   - Hämta 1,000 spel med högst kvalitetspoäng
   - Inkludera nödvändiga attribut: summary, genres, platforms, themes

2. **Feature Extraction**
   - Implementera TF-IDF för textsammanfattningar
   - Implementera one-hot encoding för kategoriska attribut
   - Kombinera features med lämplig viktning

3. **Similarity Search**
   - Implementera cosine similarity med scikit-learn
   - Utvärdera rekommendationskvalitet manuellt
   - Justera viktning mellan text och kategoriska features

**Uppskattad tidsåtgång**: 1-2 dagar

**Kod**:

```python
# feature_extraction.py
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack, save_npz, load_npz

def load_games_from_bigquery(limit=1000):
    """Ladda speldata från BigQuery"""
    from google.cloud import bigquery
    
    client = bigquery.Client()
    query = f"""
    SELECT game_id, canonical_name, display_name, summary, 
           (SELECT ARRAY_AGG(genre) FROM UNNEST(genres) AS genre) AS genres,
           (SELECT ARRAY_AGG(platform) FROM UNNEST(platforms) AS platform) AS platforms,
           (SELECT ARRAY_AGG(theme) FROM UNNEST(themes) AS theme) AS themes,
           quality_score
    FROM `igdb-pipeline-v3.igdb_games_dev.games`
    WHERE summary IS NOT NULL
    ORDER BY quality_score DESC
    LIMIT {limit}
    """
    
    return client.query(query).to_dataframe()

def extract_features(games_df):
    """Extrahera features från speldata"""
    # Text features
    tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
    text_features = tfidf.fit_transform(games_df['summary'].fillna(''))
    
    # Categorical features
    mlb_genres = MultiLabelBinarizer()
    genres_features = mlb_genres.fit_transform(games_df['genres'].fillna('').apply(lambda x: [] if x == '' else x))
    
    mlb_platforms = MultiLabelBinarizer()
    platforms_features = mlb_platforms.fit_transform(games_df['platforms'].fillna('').apply(lambda x: [] if x == '' else x))
    
    mlb_themes = MultiLabelBinarizer()
    themes_features = mlb_themes.fit_transform(games_df['themes'].fillna('').apply(lambda x: [] if x == '' else x))
    
    # Combine features
    categorical_features = hstack([genres_features, platforms_features, themes_features])
    
    # Create mapping from index to game_id
    id_mapping = dict(enumerate(games_df['game_id']))
    reverse_mapping = {v: k for k, v in id_mapping.items()}
    
    return {
        'text_features': text_features,
        'categorical_features': categorical_features,
        'id_mapping': id_mapping,
        'reverse_mapping': reverse_mapping,
        'tfidf': tfidf,
        'mlb_genres': mlb_genres,
        'mlb_platforms': mlb_platforms,
        'mlb_themes': mlb_themes
    }

def combine_features(text_features, categorical_features, text_weight=0.7):
    """Kombinera text och kategoriska features med viktning"""
    from sklearn.preprocessing import normalize
    
    # Normalize features
    text_features_norm = normalize(text_features)
    categorical_features_norm = normalize(categorical_features)
    
    # Combine with weighting
    combined_features = hstack([
        text_features_norm * text_weight,
        categorical_features_norm * (1.0 - text_weight)
    ])
    
    return combined_features

def get_recommendations(game_id, features, id_mapping, reverse_mapping, top_n=10):
    """Hämta rekommendationer baserat på similarity"""
    if game_id not in reverse_mapping:
        return []
    
    game_idx = reverse_mapping[game_id]
    game_features = features[game_idx:game_idx+1]
    
    # Calculate similarity
    similarities = cosine_similarity(game_features, features)[0]
    
    # Get top similar games
    similar_indices = np.argsort(similarities)[::-1][1:top_n+1]  # Skip the first one (self)
    
    # Convert to game_ids and scores
    recommendations = [
        {
            'game_id': id_mapping[idx],
            'similarity_score': float(similarities[idx])
        }
        for idx in similar_indices
    ]
    
    return recommendations

def main():
    """Huvudfunktion för proof of concept"""
    # Load data
    print("Loading data from BigQuery...")
    games_df = load_games_from_bigquery(limit=1000)
    print(f"Loaded {len(games_df)} games")
    
    # Extract features
    print("Extracting features...")
    features_dict = extract_features(games_df)
    
    # Combine features
    print("Combining features...")
    combined_features = combine_features(
        features_dict['text_features'],
        features_dict['categorical_features'],
        text_weight=0.7
    )
    
    # Test recommendations
    print("Testing recommendations...")
    test_game_id = games_df['game_id'].iloc[0]
    test_game_name = games_df[games_df['game_id'] == test_game_id]['display_name'].iloc[0]
    
    print(f"Getting recommendations for: {test_game_name} (ID: {test_game_id})")
    recommendations = get_recommendations(
        test_game_id,
        combined_features,
        features_dict['id_mapping'],
        features_dict['reverse_mapping'],
        top_n=10
    )
    
    # Print recommendations
    print("\nTop 10 recommendations:")
    for i, rec in enumerate(recommendations):
        game_name = games_df[games_df['game_id'] == rec['game_id']]['display_name'].iloc[0]
        print(f"{i+1}. {game_name} (Score: {rec['similarity_score']:.4f})")
    
    # Save features for later use
    print("\nSaving features...")
    save_npz('text_features.npz', features_dict['text_features'])
    save_npz('categorical_features.npz', features_dict['categorical_features'])
    save_npz('combined_features.npz', combined_features)
    
    import pickle
    with open('features_metadata.pkl', 'wb') as f:
        pickle.dump({
            'id_mapping': features_dict['id_mapping'],
            'reverse_mapping': features_dict['reverse_mapping'],
            'games_df': games_df
        }, f)
    
    print("Done!")

if __name__ == "__main__":
    main()
```

### Fas 2: Skalning med Faiss (Lokal utveckling)

**Mål**: Skala upp till större dataset och optimera för prestanda.

**Steg**:

1. **Datahämtning från BigQuery**
   - Skala upp till 10,000-50,000 spel
   - Optimera datahämtning för större dataset

2. **Optimerad Feature Extraction**
   - Implementera batch-processing för större dataset
   - Optimera minnesutnyttjande
   - Experimentera med dimensionalitetsreduktion (PCA)

3. **Faiss Implementation**
   - Implementera Faiss för effektiv similarity search
   - Jämför prestanda med baseline (scikit-learn)
   - Optimera indextyp och parametrar

**Uppskattad tidsåtgång**: 2-3 dagar

**Kod**:

```python
# faiss_recommender.py
import pandas as pd
import numpy as np
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from scipy.sparse import hstack, save_npz, load_npz

def load_games_from_bigquery(limit=10000):
    """Ladda speldata från BigQuery"""
    # Samma som i Fas 1, men med större limit
    pass

def extract_features_batched(games_df, batch_size=1000):
    """Extrahera features i batches för att spara minne"""
    # Implementera batch-processing för feature extraction
    pass

def build_faiss_index(feature_matrix):
    """Bygger ett Faiss-index för snabb similarity search"""
    # Convert to float32 (required by Faiss)
    feature_matrix_dense = feature_matrix.toarray().astype('float32')
    
    # Normalize vectors (for cosine similarity)
    faiss.normalize_L2(feature_matrix_dense)
    
    # Create index
    d = feature_matrix_dense.shape[1]  # Dimensions
    index = faiss.IndexFlatIP(d)  # Inner product = cosine similarity for normalized vectors
    
    # Add vectors to index
    index.add(feature_matrix_dense)
    
    return index

def get_recommendations_faiss(index, game_idx, id_mapping, top_n=10):
    """Hämta rekommendationer med Faiss"""
    # Get the feature vector for the query game
    query_vector = index.reconstruct(game_idx).reshape(1, -1)
    
    # Search for similar games
    distances, indices = index.search(query_vector, top_n + 1)
    
    # Convert to game_ids and scores (skip the first one which is the query game)
    recommendations = []
    for i in range(1, len(indices[0])):
        idx = indices[0][i]
        game_id = id_mapping[idx]
        similarity = float(distances[0][i])
        recommendations.append({
            'game_id': game_id,
            'similarity_score': similarity
        })
    
    return recommendations

def benchmark_performance(index, id_mapping, reverse_mapping, games_df, num_queries=100):
    """Mät prestanda för rekommendationssystemet"""
    import time
    import random
    
    # Select random games for benchmarking
    sample_game_ids = random.sample(list(reverse_mapping.keys()), min(num_queries, len(reverse_mapping)))
    
    # Measure query time
    start_time = time.time()
    for game_id in sample_game_ids:
        game_idx = reverse_mapping[game_id]
        _ = get_recommendations_faiss(index, game_idx, id_mapping, top_n=10)
    
    total_time = time.time() - start_time
    avg_time = total_time / len(sample_game_ids)
    
    print(f"Benchmark results:")
    print(f"- Total time for {len(sample_game_ids)} queries: {total_time:.4f} seconds")
    print(f"- Average query time: {avg_time*1000:.2f} ms")
    print(f"- Queries per second: {len(sample_game_ids)/total_time:.2f}")

def main():
    """Huvudfunktion för Faiss implementation"""
    # Load data
    print("Loading data from BigQuery...")
    games_df = load_games_from_bigquery(limit=10000)
    print(f"Loaded {len(games_df)} games")
    
    # Extract features
    print("Extracting features...")
    features_dict = extract_features_batched(games_df)
    
    # Combine features
    print("Combining features...")
    combined_features = combine_features(
        features_dict['text_features'],
        features_dict['categorical_features'],
        text_weight=0.7
    )
    
    # Build Faiss index
    print("Building Faiss index...")
    faiss_index = build_faiss_index(combined_features)
    
    # Benchmark performance
    print("Benchmarking performance...")
    benchmark_performance(
        faiss_index,
        features_dict['id_mapping'],
        features_dict['reverse_mapping'],
        games_df
    )
    
    # Save index and metadata
    print("Saving index and metadata...")
    faiss.write_index(faiss_index, "faiss_index.bin")
    
    import pickle
    with open('faiss_metadata.pkl', 'wb') as f:
        pickle.dump({
            'id_mapping': features_dict['id_mapping'],
            'reverse_mapping': features_dict['reverse_mapping'],
            'games_df': games_df
        }, f)
    
    print("Done!")

if __name__ == "__main__":
    main()
```

### Fas 3: Cloud Deployment (GCP)

**Mål**: Deploya rekommendationssystemet i GCP för produktion.

**Steg**:

1. **Feature Extraction i BigQuery**
   - Implementera feature extraction direkt i BigQuery med SQL
   - Exportera feature vectors till Cloud Storage

2. **Vertex AI Matching Engine**
   - Skapa Matching Engine index
   - Ladda upp feature vectors
   - Konfigurera index endpoint

3. **Cloud Run API**
   - Implementera FastAPI-tjänst för rekommendationer
   - Integrera med Matching Engine
   - Implementera caching med Redis

**Uppskattad tidsåtgång**: 3-4 dagar

**Kod**:

```sql
-- BigQuery Feature Extraction
-- Extract TF-IDF features (approximation using SQL)
WITH game_words AS (
  SELECT
    game_id,
    REGEXP_EXTRACT_ALL(LOWER(summary), r'[a-zA-Z]+') AS words
  FROM
    `igdb-pipeline-v3.igdb_games_dev.games`
  WHERE
    summary IS NOT NULL
),
word_counts AS (
  SELECT
    game_id,
    word,
    COUNT(*) AS term_frequency
  FROM
    game_words,
    UNNEST(words) AS word
  GROUP BY
    game_id, word
),
document_counts AS (
  SELECT
    word,
    COUNT(DISTINCT game_id) AS document_frequency
  FROM
    word_counts
  GROUP BY
    word
),
total_documents AS (
  SELECT COUNT(DISTINCT game_id) AS total
  FROM game_words
)
SELECT
  wc.game_id,
  wc.word,
  wc.term_frequency * LOG(td.total / dc.document_frequency) AS tfidf
FROM
  word_counts wc
JOIN
  document_counts dc ON wc.word = dc.word
CROSS JOIN
  total_documents td
WHERE
  dc.document_frequency > 5  -- Filter out rare words
  AND LENGTH(wc.word) > 3    -- Filter out short words
ORDER BY
  wc.game_id, tfidf DESC;
```

```python
# vertex_ai_matching_engine.py
from google.cloud import aiplatform
from google.cloud import bigquery
from google.cloud import storage
import numpy as np
import pandas as pd
import os
import json
import time

def extract_features_bigquery():
    """Extrahera features med BigQuery"""
    client = bigquery.Client()
    
    # Run feature extraction query
    query = """
    -- Feature extraction SQL from above
    """
    
    job = client.query(query)
    results = job.result()
    
    # Process results
    # ...
    
    return features, id_mapping

def create_matching_engine_index(project_id, region, index_name, dimensions):
    """Skapa ett Matching Engine index i Vertex AI"""
    aiplatform.init(project=project_id, location=region)
    
    # Create index
    index = aiplatform.MatchingEngineIndex.create(
        display_name=index_name,
        dimensions=dimensions,
        approximate_neighbors_count=20,
        distance_measure_type="DOT_PRODUCT_DISTANCE"
    )
    
    return index

def upload_embeddings_to_index(index, features, id_mapping):
    """Ladda upp embeddings till Matching Engine index"""
    # Convert features to required format
    # ...
    
    # Upload in batches
    for i in range(0, len(features), 1000):
        batch = features[i:i+1000]
        batch_ids = [id_mapping[j] for j in range(i, min(i+1000, len(features)))]
        
        index.upsert_embeddings(
            embeddings=batch,
            ids=batch_ids
        )
        
        print(f"Uploaded batch {i//1000 + 1}/{(len(features) + 999) // 1000}")
        time.sleep(1)  # Avoid rate limiting

def deploy_index_endpoint(index, endpoint_name):
    """Deploya index till en endpoint"""
    # Create endpoint
    endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=endpoint_name,
        public_endpoint_enabled=True
    )
    
    # Deploy index to endpoint
    deployed_index = endpoint.deploy_index(
        index=index,
        deployed_index_id=f"{index.name}-deployed"
    )
    
    return endpoint, deployed_index

def main():
    """Huvudfunktion för Vertex AI Matching Engine deployment"""
    # Configuration
    project_id = "igdb-pipeline-v3"
    region = "europe-west1"
    index_name = "igdb-game-recommendations"
    
    # Extract features
    print("Extracting features from BigQuery...")
    features, id_mapping = extract_features_bigquery()
    dimensions = features.shape[1]
    
    # Create index
    print("Creating Matching Engine index...")
    index = create_matching_engine_index(
        project_id,
        region,
        index_name,
        dimensions
    )
    
    # Upload embeddings
    print("Uploading embeddings to index...")
    upload_embeddings_to_index(index, features, id_mapping)
    
    # Deploy index endpoint
    print("Deploying index endpoint...")
    endpoint, deployed_index = deploy_index_endpoint(
        index,
        f"{index_name}-endpoint"
    )
    
    # Save metadata
    print("Saving metadata...")
    metadata = {
        "index_name": index.name,
        "endpoint_name": endpoint.name,
        "deployed_index_id": deployed_index.deployed_index_id,
        "dimensions": dimensions
    }
    
    with open("matching_engine_metadata.json", "w") as f:
        json.dump(metadata, f)
    
    print("Done!")

if __name__ == "__main__":
    main()
```

```python
# app.py (FastAPI service)
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import aiplatform
from redis import asyncio as aioredis
import os
import json
import asyncio
import logging

app = FastAPI(title="IGDB Game Recommendations API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis client
redis = None

# Vertex AI client
endpoint = None
deployed_index_id = None

@app.on_event("startup")
async def startup_event():
    global redis, endpoint, deployed_index_id
    
    # Initialize Redis
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = int(os.environ.get("REDIS_PORT", 6379))
    redis = aioredis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    # Initialize Vertex AI
    aiplatform.init(
        project=os.environ.get("PROJECT_ID"),
        location=os.environ.get("REGION")
    )
    
    # Load endpoint
    endpoint_name = os.environ.get("ENDPOINT_NAME")
    endpoint = aiplatform.MatchingEngineIndexEndpoint(endpoint_name)
    deployed_index_id = os.environ.get("DEPLOYED_INDEX_ID")
    
    logger.info("API initialized successfully")

@app.get("/api/recommendations/{game_id}")
async def get_recommendations(
    game_id: str,
    limit: int = Query(10, ge=1, le=50),
    use_cache: bool = Query(True)
):
    """Get game recommendations based on similarity"""
    # Check cache
    if use_cache:
        cache_key = f"rec:{game_id}:{limit}"
        cached = await redis.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {cache_key}")
            return json.loads(cached)
    
    try:
        # Query Matching Engine
        response = endpoint.find_neighbors(
            deployed_index_id=deployed_index_id,
            queries=[game_id],
            num_neighbors=limit
        )
        
        # Process results
        if not response or not response[0]:
            return {"recommendations": []}
        
        recommendations = []
        for neighbor in response[0]:
            recommendations.append({
                "game_id": neighbor.id,
                "similarity_score": float(neighbor.distance)
            })
        
        result = {"recommendations": recommendations}
        
        # Cache results
        if use_cache:
            await redis.set(
                f"rec:{game_id}:{limit}",
                json.dumps(result),
                ex=3600  # 1 hour expiration
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Fas 4: Optimering och Monitoring

**Mål**: Optimera rekommendationskvalitet och implementera monitoring.

**Steg**:

1. **Kvalitetsutvärdering**
   - Implementera verktyg för manuell utvärdering
   - A/B-testa olika feature-viktningar
   - Samla feedback från användare

2. **Prestandaoptimering**
   - Optimera caching-strategi
   - Implementera batch-rekommendationer
   - Finjustera Matching Engine-parametrar

3. **Monitoring och Alerting**
   - Implementera Cloud Monitoring dashboards
   - Sätta upp alerting för latency och fel
   - Implementera loggning för rekommendationskvalitet

**Uppskattad tidsåtgång**: 2-3 dagar

## Tidsplan

| Fas | Beskrivning | Uppskattad tidsåtgång | Status |
|-----|-------------|------------------------|--------|
| 1   | Proof of Concept (Lokal) | 1-2 dagar | Ej påbörjad |
| 2   | Skalning med Faiss (Lokal) | 2-3 dagar | Ej påbörjad |
| 3   | Cloud Deployment (GCP) | 3-4 dagar | Ej påbörjad |
| 4   | Optimering och Monitoring | 2-3 dagar | Ej påbörjad |

**Total uppskattad tidsåtgång**: 8-12 dagar

## Kostnadsuppskattning

| Komponent | Uppskattad kostnad |
|-----------|---------------------|
| BigQuery (Feature Extraction) | $5-10 (engångskostnad) |
| Vertex AI Matching Engine (Index Creation) | $10-20 (engångskostnad) |
| Vertex AI Matching Engine (Queries) | $50-200/månad |
| Cloud Run (API) | $20-50/månad |
| Memorystore (Redis) | $30-50/månad |
| **Total uppskattad månadskostnad** | **$100-300/månad** |

## Risker och Utmaningar

1. **Skalbarhetsproblem**
   - Risk: Prestanda degraderas med fullt dataset (300k+ spel)
   - Åtgärd: Implementera dimensionalitetsreduktion, optimera indextyp

2. **Rekommendationskvalitet**
   - Risk: Rekommendationer matchar inte användarförväntningar
   - Åtgärd: Iterativ optimering av feature-viktning, manuell utvärdering

3. **Kostnadsöverskridning**
   - Risk: Vertex AI Matching Engine blir dyrare än förväntat
   - Åtgärd: Implementera aggressiv caching, precomputed recommendations

## Nästa Steg

1. Implementera Proof of Concept (Fas 1)
2. Utvärdera rekommendationskvalitet
3. Fortsätta med Fas 2 (Skalning med Faiss)
