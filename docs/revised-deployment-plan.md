# Reviderad Deployment Plan - Cloud Run + Batch Jobs

## Översikt

Baserat på analys av Vertex AI:s kostnadsstruktur och skalbarhet har vi reviderat vår deployment-strategi för att fokusera på kostnadseffektiva, serverless lösningar med scale-to-zero kapacitet.

## 🎯 Status: 85% Slutfört

Deployment-planen har implementerats framgångsrikt med följande resultat:
- ✅ **Infrastruktur**: 40+ GCP-resurser deployade via Terraform
- ✅ **Cloud Run**: Service och Jobs fungerar
- ✅ **BigQuery**: 24,997 spel med kategoriska features
- ✅ **Feature Extraction**: Fungerar i molnet (90s för 1,000 spel)
- 🔄 **ML Integration**: API använder placeholder-rekommendationer

## Ny Arkitektur

### Huvudkomponenter

1. **Cloud Run Service** - Rekommendations-API (skalar till noll)
2. **Cloud Run Jobs** - Feature extraction (batch processing)
3. **Cloud Storage** - Features, modeller och data
4. **BigQuery** - Speldata och metadata
5. **Cloud Scheduler** - Orchestration av batch-jobb
6. **Vertex AI** - Endast för batch-pipelines (ingen konstant kostnad)

### Kostnadsjämförelse

| Komponent | Tidigare Plan | Ny Plan | Kostnadsbesparing |
|-----------|---------------|---------|-------------------|
| API Serving | Vertex AI Endpoint | Cloud Run | 90% (scale-to-zero) |
| Feature Extraction | Vertex AI Pipeline | Cloud Run Jobs | 80% (batch processing) |
| Orchestration | Kubernetes | Cloud Scheduler | 95% (serverless) |
| Monitoring | Custom | Cloud Monitoring | 70% (managed service) |

## Deployment Faser

### Fas 1: Infrastruktur ✅ Slutförd

#### 1.1 Uppdatera Terraform-moduler
- ✅ Cloud Run-modulen implementerad
- ✅ Vertex AI-modulen förenklad för batch-pipelines
- ✅ IAM-behörigheter konfigurerade
- ✅ 40+ GCP-resurser deployade

#### 1.2 Skapa produktions-Dockerfiler
- ✅ `Dockerfile.feature-extraction` - för Cloud Run Jobs
- ✅ `Dockerfile.recommendation-api` - för Cloud Run Service
- ✅ Optimera för GCP-miljön

#### 1.3 Konfigurera Cloud Build
```bash
# Build feature extraction image
docker build -f ml-pipeline/Dockerfile.feature-extraction \
  -t europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-feature-extraction:latest .

# Build recommendation API image
docker build -f ml-pipeline/Dockerfile.recommendation-api \
  -t europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-recommendation-api:latest .
```

### Fas 2: Feature Pipeline ✅ Slutförd

#### 2.1 Cloud Run Job för Feature Extraction
- ✅ **Input**: BigQuery game data (24,997 spel)
- ✅ **Processing**: TF-IDF + categorical features (1,949 features)
- ✅ **Output**: Features och Faiss-index till Cloud Storage
- ✅ **Performance**: 90s för 1,000 spel
- ⬜ **Orchestration**: Cloud Scheduler (veckovis) - planerad

#### 2.2 Konfiguration
```yaml
# cloud-scheduler.yaml
schedule: "0 2 * * 0"  # Varje söndag kl 02:00
time_zone: "Europe/Stockholm"
target:
  http_target:
    uri: "https://europe-west1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/igdb-pipeline-v3/jobs/igdb-feature-extraction-dev:run"
    http_method: POST
```

### Fas 3: API Service 🔄 Pågående

#### 3.1 Cloud Run Service för Rekommendationer
- ✅ **Infrastructure**: Cloud Run service deployad
- ✅ **Endpoint**: `https://igdb-recommendation-api-dev-5wxthq523q-ew.a.run.app`
- ✅ **Response Time**: <2s
- 🔄 **ML Integration**: Använder placeholder-rekommendationer
- ⬜ **Caching**: Redis (optional, för prestanda) - planerad

#### 3.2 Aktuell Status
```bash
# Testa API:et
curl "https://igdb-recommendation-api-dev-5wxthq523q-ew.a.run.app/api/recommendations/123"

# Response (placeholder)
{
  "game_id": "123",
  "recommendations": [...],
  "message": "Placeholder recommendations - ML model not yet loaded"
}
```

#### 3.3 Prestandaoptimering
- ✅ **Cold Start**: Minimera container-storlek
- ⬜ **Caching**: Faiss-index i minnet - planerad
- ✅ **Autoscaling**: 0-10 instanser baserat på trafik

### Fas 4: Monitoring och Produktion ⬜ Planerad

#### 4.1 Cloud Monitoring
- ⬜ **Metrics**: Response time, error rate, throughput
- ⬜ **Alerts**: Error rate > 5%, response time > 2s
- ⬜ **Dashboards**: Real-time monitoring

#### 4.2 Kostnadsoptimering
- ⬜ **Budget Alerts**: $50/månad
- ⬜ **Usage Monitoring**: Cloud Billing API
- ⬜ **Resource Optimization**: Rätt storlek på containers

## Teknisk Implementation

### Feature Extraction Job

```python
# cloud_run_job.py
def main():
    # Load data from BigQuery
    games_df = load_from_bigquery()
    
    # Extract features with optimized parameters
    extractor = FeatureExtractor(
        text_weight=0.6,
        max_features=5000,
        min_df=5,
        ngram_range=(1, 2)
    )
    features = extractor.extract_features(games_df)
    
    # Save to Cloud Storage
    save_to_gcs(features, "gs://igdb-v3-features/")
    
    # Build Faiss index
    index = build_faiss_index(features)
    save_index_to_gcs(index, "gs://igdb-v3-features/")
```

### Recommendation API

```python
# FastAPI implementation
@app.get("/api/recommendations/{game_id}")
async def get_recommendations(game_id: str, limit: int = 10):
    # Load Faiss index from Cloud Storage (cached)
    # Return recommendations
    recommendations = similarity_search.get_similar_games(
        game_id=game_id,
        top_n=limit
    )
    return {"recommendations": recommendations}
```

## Kostnadsuppskattning

### Månatliga Kostnader (Uppdaterade)

| Tjänst | Användning | Kostnad |
|--------|------------|---------|
| Cloud Run (API) | 1000 requests/månad | $5-10 |
| Cloud Run Jobs | 4 körningar/månad | $2-5 |
| Cloud Storage | 10GB features + data | $2-5 |
| BigQuery | 100GB queries/månad | $5-10 |
| Cloud Scheduler | 4 jobs/månad | $0.10 |
| **Total** | | **$15-30/månad** |

### Jämfört med tidigare plan
- **Vertex AI Endpoint**: $200-400/månad (konstant kostnad)
- **Kubernetes**: $100-200/månad (kluster-kostnad)
- **Ny plan**: $15-30/månad (90% besparing)

## Riskbedömning

### Låg Risk
- **Cloud Run**: Bevisad teknisk lösning
- **Feature Extraction**: Redan testad och validerad
- **Kostnad**: Förutsägbar och låg

### Medium Risk
- **Cold Starts**: API-latens vid första anropet
- **Data Consistency**: Features vs game data sync
- **Scaling**: Okänd belastning under presentation

### Åtgärder
- **Cold Starts**: Keep-warm requests, minimum instances
- **Data Consistency**: Versioning, validation checks
- **Scaling**: Load testing, auto-scaling configuration

## Success Metrics

### Prestanda
- **API Response Time**: <200ms (95th percentile)
- **Feature Extraction**: <5 minuter för 328k spel
- **Availability**: 99.9% uptime
- **Cold Start**: <10 sekunder

### Kvalitet
- **Precision@10**: Behåll 0.8-1.0 över kategorier
- **Coverage**: 90% av populära spel hittas
- **Consistency**: Stabila resultat över tid

## Nästa Steg

### Omedelbart (1-2 dagar)
1. ✅ **Dockerfiler** testade och deployade
2. ✅ **Cloud Run-moduler** deployade med Terraform
3. ✅ **Container-images** byggda och testade
4. 🔄 **ML Model Integration** - koppla features till API

### Kort sikt (2-3 dagar)
1. ✅ **Feature extraction job** implementerat
2. 🔄 **Recommendation API** - behöver ML-integration
3. ⬜ **Web Application** - skapa Next.js frontend
4. ⬜ **End-to-end test** - validera hela systemet

### Medellång sikt (1 vecka)
1. ⬜ **Produktionsdeployment** med monitoring
2. ⬜ **Optimera** prestanda och kostnader
3. ⬜ **Skala** till fler användare
2. **Load testing** under presentation
3. **Kostnadsoptimering** baserat på användning

## Slutsats

Den reviderade planen fokuserar på kostnadseffektivitet och enkelhet utan att kompromissa med funktionalitet. Cloud Run + batch jobs ger oss:

- **90% kostnadsbesparing** jämfört med Vertex AI endpoints
- **Scale-to-zero** kapacitet för låg trafik
- **Enkel drift** med managed services
- **Samma prestanda** som tidigare plan

**Rekommendation**: Fortsätt med den reviderade planen för optimal kostnadseffektivitet och enkelhet.
