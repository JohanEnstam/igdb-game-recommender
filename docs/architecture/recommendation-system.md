# Rekommendationssystem - IGDB Game Recommendation System

## Komponentöversikt

Rekommendationssystemet är en content-based filtering lösning som använder feature extraction och similarity search för att hitta liknande spel. Systemet är designat för att vara enkelt, effektivt och skalbart för att hantera 300k+ spel.

## Arkitektur

Rekommendationssystemet består av tre huvuddelar:

1. **Feature Extraction Pipeline**: Extraherar och kombinerar features från speldata
2. **Similarity Search Engine**: Beräknar och lagrar likheter mellan spel
3. **Recommendation API**: Exponerar rekommendationer via ett REST API

### Dataflöde

```
+----------------+    +----------------+    +----------------+
| BigQuery       |--->| Feature        |--->| Feature        |
| (Games Data)   |    | Extraction     |    | Vectors        |
+----------------+    +----------------+    +----------------+
                                                   |
                                                   v
+----------------+    +----------------+    +----------------+
| API            |<---| Similarity     |<---| Vertex AI      |
| (FastAPI)      |    | Search         |    | Matching Engine|
+----------------+    +----------------+    +----------------+
        ^                                          ^
        |                                          |
        |                                          |
+----------------+                         +----------------+
| Redis Cache    |                         | Faiss Index    |
| (Results)      |                         | (Development)  |
+----------------+                         +----------------+
```

## Feature Extraction

### Textbaserade Features

Vi använder TF-IDF (Term Frequency-Inverse Document Frequency) för att extrahera features från spelsammanfattningar:

```python
def extract_text_features(games_df):
    """
    Extraherar textfeatures från spelsammanfattningar med TF-IDF.
    
    Args:
        games_df: DataFrame med speldata, måste innehålla 'summary' kolumn
        
    Returns:
        Sparse matrix med TF-IDF features
    """
    tfidf = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        min_df=5,
        ngram_range=(1, 2)
    )
    
    # Hantera saknade värden
    games_df['summary_clean'] = games_df['summary'].fillna('')
    
    # Transformera text till TF-IDF features
    text_features = tfidf.fit_transform(games_df['summary_clean'])
    
    return text_features, tfidf
```

### Kategoriska Features

Vi använder one-hot encoding för kategoriska features som genrer, plattformar och teman:

```python
def extract_categorical_features(games_df):
    """
    Extraherar kategoriska features med one-hot encoding.
    
    Args:
        games_df: DataFrame med speldata, måste innehålla 'genres', 'platforms', 'themes'
        
    Returns:
        Sparse matrix med one-hot encoded features
    """
    # Hantera listor av kategorier
    mlb_genres = MultiLabelBinarizer()
    genres_features = mlb_genres.fit_transform(games_df['genres'].fillna('').apply(lambda x: [] if x == '' else x))
    
    mlb_platforms = MultiLabelBinarizer()
    platforms_features = mlb_platforms.fit_transform(games_df['platforms'].fillna('').apply(lambda x: [] if x == '' else x))
    
    mlb_themes = MultiLabelBinarizer()
    themes_features = mlb_themes.fit_transform(games_df['themes'].fillna('').apply(lambda x: [] if x == '' else x))
    
    # Kombinera alla kategoriska features
    categorical_features = hstack([
        genres_features,
        platforms_features,
        themes_features
    ])
    
    feature_names = {
        'genres': mlb_genres.classes_,
        'platforms': mlb_platforms.classes_,
        'themes': mlb_themes.classes_
    }
    
    return categorical_features, feature_names
```

### Kombinerade Features

Vi kombinerar text- och kategoriska features med viktning:

```python
def combine_features(text_features, categorical_features, text_weight=0.7):
    """
    Kombinerar text- och kategoriska features med viktning.
    
    Args:
        text_features: Sparse matrix med TF-IDF features
        categorical_features: Sparse matrix med kategoriska features
        text_weight: Vikt för textfeatures (0.0-1.0)
        
    Returns:
        Sparse matrix med kombinerade features
    """
    # Normalisera features
    text_features_norm = normalize(text_features)
    categorical_features_norm = normalize(categorical_features)
    
    # Kombinera med viktning
    combined_features = hstack([
        text_features_norm * text_weight,
        categorical_features_norm * (1.0 - text_weight)
    ])
    
    return combined_features
```

## Similarity Search

### Lokal Implementation med Faiss

För utveckling och testning använder vi Faiss för effektiv similarity search:

```python
def build_faiss_index(feature_matrix):
    """
    Bygger ett Faiss-index för snabb similarity search.
    
    Args:
        feature_matrix: Dense matrix med feature vectors
        
    Returns:
        Faiss index
    """
    # Konvertera sparse matrix till dense
    feature_matrix_dense = feature_matrix.toarray().astype('float32')
    
    # Skapa L2-normaliserat index
    index = faiss.IndexFlatIP(feature_matrix_dense.shape[1])
    faiss.normalize_L2(feature_matrix_dense)
    
    # Lägg till vektorer till index
    index.add(feature_matrix_dense)
    
    return index

def get_similar_games(index, game_idx, id_mapping, top_n=10):
    """
    Hämtar liknande spel baserat på similarity search.
    
    Args:
        index: Faiss index
        game_idx: Index för spelet att hitta liknande spel för
        id_mapping: Mapping från index till game_id
        top_n: Antal rekommendationer att returnera
        
    Returns:
        Lista med tuples (game_id, similarity_score)
    """
    # Hämta feature vector för spelet
    query_vector = index.reconstruct(game_idx).reshape(1, -1)
    
    # Sök efter liknande spel
    distances, indices = index.search(query_vector, top_n + 1)
    
    # Konvertera till game_ids och exkludera query-spelet
    similar_games = []
    for i, idx in enumerate(indices[0]):
        if idx != game_idx:  # Exkludera query-spelet
            game_id = id_mapping[idx]
            similarity = distances[0][i]
            similar_games.append((game_id, float(similarity)))
    
    return similar_games[:top_n]
```

### Skalbar Implementation med Vertex AI Matching Engine

För produktion använder vi Vertex AI Matching Engine för att skala till 300k+ spel:

```python
def create_matching_engine_index(project_id, region, index_name, dimensions):
    """
    Skapar ett Matching Engine index i Vertex AI.
    
    Args:
        project_id: GCP projekt-ID
        region: GCP-region
        index_name: Namn på indexet
        dimensions: Antal dimensioner i feature vectors
        
    Returns:
        Index resource name
    """
    from google.cloud import aiplatform
    
    aiplatform.init(project=project_id, location=region)
    
    # Definiera index
    index = aiplatform.MatchingEngineIndex.create(
        display_name=index_name,
        dimensions=dimensions,
        approximate_neighbors_count=20,
        distance_measure_type="DOT_PRODUCT_DISTANCE"
    )
    
    return index.resource_name

def upload_embeddings_to_index(index_name, feature_matrix, ids):
    """
    Laddar upp embeddings till Matching Engine index.
    
    Args:
        index_name: Namn på indexet
        feature_matrix: Matrix med feature vectors
        ids: Lista med game_ids
    """
    from google.cloud import aiplatform
    
    # Konvertera sparse matrix till dense
    feature_matrix_dense = feature_matrix.toarray().astype('float32')
    
    # Normalisera vektorer
    faiss.normalize_L2(feature_matrix_dense)
    
    # Skapa index endpoint
    index = aiplatform.MatchingEngineIndex(index_name)
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=f"{index_name}-endpoint",
        public_endpoint_enabled=True
    )
    
    # Deploya index till endpoint
    deployed_index = index_endpoint.deploy_index(
        index=index,
        deployed_index_id=f"{index_name}-deployed"
    )
    
    # Ladda upp embeddings
    index.upsert_datapoints(
        embeddings=feature_matrix_dense,
        ids=[str(id) for id in ids]
    )
    
    return deployed_index
```

## API och Gränssnitt

### Recommendation API

```python
@app.get("/api/recommendations/{game_id}")
async def get_recommendations(
    game_id: str,
    limit: int = 10,
    cache: bool = True
):
    """
    Hämtar rekommendationer för ett specifikt spel.
    
    Args:
        game_id: ID för spelet att få rekommendationer för
        limit: Antal rekommendationer att returnera
        cache: Om resultat ska hämtas från cache
        
    Returns:
        Lista med rekommenderade spel
    """
    # Kontrollera cache först
    if cache:
        cached_result = await redis.get(f"rec:{game_id}:{limit}")
        if cached_result:
            return json.loads(cached_result)
    
    # Hämta rekommendationer
    recommendations = recommendation_service.get_recommendations(game_id, limit)
    
    # Hämta metadata för rekommenderade spel
    game_ids = [rec["game_id"] for rec in recommendations]
    games_metadata = await db.fetch_games_metadata(game_ids)
    
    # Kombinera rekommendationer med metadata
    result = []
    for rec in recommendations:
        game_metadata = next((g for g in games_metadata if g["game_id"] == rec["game_id"]), None)
        if game_metadata:
            result.append({
                **rec,
                **game_metadata
            })
    
    # Spara i cache
    if cache:
        await redis.set(
            f"rec:{game_id}:{limit}",
            json.dumps(result),
            expire=3600  # 1 timme
        )
    
    return result
```

## Prestanda och Skalbarhet

### Lokala Benchmarks

| Dataset Size | Operation | Execution Time | Memory Usage |
|--------------|-----------|----------------|-------------|
| 1,000 spel   | Feature Extraction | ~2 sekunder | ~100 MB |
| 1,000 spel   | Similarity Search | ~0.01 sekunder | ~50 MB |
| 10,000 spel  | Feature Extraction | ~20 sekunder | ~500 MB |
| 10,000 spel  | Similarity Search | ~0.1 sekunder | ~200 MB |
| 300,000 spel | Feature Extraction | ~10 minuter | ~8 GB |
| 300,000 spel | Similarity Search | ~3 sekunder | ~6 GB |

### Vertex AI Matching Engine

| Dataset Size | Operation | Latency | Kostnad (uppskattad) |
|--------------|-----------|---------|----------------------|
| 300,000 spel | Index Creation | ~30 minuter | $10-20 (engångskostnad) |
| 300,000 spel | Query | ~20ms | $50-200/månad |

### Optimeringsstrategier

1. **Caching**
   - Redis för att cacha populära rekommendationer
   - TTL på 1 timme för att balansera aktualitet och prestanda

2. **Batch Processing**
   - Precomputed recommendations för populära spel
   - Schemalagd uppdatering av rekommendationer

3. **Dimensionalitetsreduktion**
   - PCA för att reducera dimensionalitet av feature vectors
   - Förbättrar både prestanda och minnesutnyttjande

## Implementation Plan

1. **Proof of Concept (Lokal)**
   - Implementera feature extraction på 1,000 spel
   - Testa similarity search med scikit-learn
   - Utvärdera rekommendationskvalitet manuellt

2. **Skalning (Lokal)**
   - Skala upp till 10,000 spel
   - Implementera Faiss för effektiv similarity search
   - Optimera minnes- och CPU-användning

3. **Produktion (GCP)**
   - Implementera feature extraction i BigQuery
   - Sätta upp Vertex AI Matching Engine
   - Integrera med Cloud Run API
   - Implementera caching med Memorystore (Redis)

4. **Monitoring och Optimering**
   - Mäta latency och throughput
   - Optimera feature extraction och viktning
   - Implementera A/B-testning för olika rekommendationsstrategier

## Relaterade Dokument

- [Systemöversikt](./system-overview.md)
- [Datamodell](./data-model.md)
- [API-dokumentation](../development-guides/api-docs.md) *(planerad)*
