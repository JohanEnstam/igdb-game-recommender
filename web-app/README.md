# IGDB Game Recommendation System - Web Application

## Översikt

Detta är web-applikationen för IGDB Game Recommendation System som nu inkluderar fullständig ML-integration med riktiga rekommendationer baserat på similarity search.

## Arkitektur

```
Frontend (Next.js) ←→ Backend API (FastAPI) ←→ ML Model (Faiss + BigQuery)
```

### Komponenter

1. **Frontend** (`/frontend`)
   - Next.js med TypeScript
   - ShadCN komponenter, Lucide ikoner och Tailwind CSS för styling
   - Sökfunktionalitet för spel
   - Visning av rekommendationer

2. **Backend API** (`/backend`)
   - FastAPI med Python
   - ML-integration med Faiss similarity search
   - BigQuery-integration för speldata
   - Cloud Storage-integration för features

3. **ML Model**
   - Features laddas från Cloud Storage
   - Faiss-index för snabb similarity search
   - 1,949 features per spel (text + kategoriska)

## Snabbstart

### Förutsättningar

- Docker och Docker Compose
- GCP credentials (`terraform-admin-key.json`)
- Features sparade i Cloud Storage

### Kör systemet lokalt

1. **Starta alla tjänster:**
   ```bash
   cd igdb-game-recommender
   ./scripts/test_local_system.sh
   ```

2. **Eller manuellt:**
   ```bash
   cd web-app
   docker-compose up --build
   ```

3. **Öppna i webbläsare:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Testa systemet

```bash
# Testa API:et direkt
python web-app/backend/test_api.py

# Eller använd curl
curl "http://localhost:8000/games/search?query=zelda&limit=5"
curl "http://localhost:8000/recommendations/1942?limit=5"
```

## API Endpoints

### Sök spel
```
GET /games/search?query={query}&limit={limit}
```

### Hämta spelinformation
```
GET /games/{game_id}
```

### Få rekommendationer
```
GET /recommendations/{game_id}?limit={limit}
```

### Health check
```
GET /health
```

## ML Model Integration

### Features
- **Text features**: TF-IDF från spelbeskrivningar (1,809 dimensioner)
- **Kategoriska features**: Genres, platforms, themes (140 dimensioner)
- **Total**: 1,949 features per spel

### Similarity Search
- Faiss IndexFlatIP för cosine similarity
- Normaliserade vektorer för optimal prestanda
- Sub-sekund svarstider för rekommendationer

### Data Sources
- **BigQuery**: 24,997 spel i `games_with_categories`
- **Cloud Storage**: Features i `gs://igdb-model-artifacts-dev/features/`

## Utveckling

### Backend Development

```bash
cd web-app/backend
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### Frontend Development

```bash
cd web-app/frontend
npm install
npm run dev
```

### Environment Variables

**Backend:**
- `FEATURES_BUCKET`: Cloud Storage bucket för features
- `GOOGLE_APPLICATION_CREDENTIALS`: Sökväg till GCP credentials
- `DEBUG`: Aktivera debug-läge

**Frontend:**
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Deployment

### Lokal Docker
```bash
docker-compose up --build
```

### GCP Cloud Run
```bash
# Backend
gcloud run deploy igdb-recommendation-api \
  --source web-app/backend \
  --platform managed \
  --region europe-west1

# Frontend
gcloud run deploy igdb-recommendation-frontend \
  --source web-app/frontend \
  --platform managed \
  --region europe-west1
```

## Prestanda

### API Response Times
- **Sök**: ~200-500ms
- **Rekommendationer**: ~100-300ms
- **Spelinformation**: ~100-200ms

### ML Model
- **Index-byggning**: ~30 sekunder (vid startup)
- **Similarity search**: ~10-50ms per query
- **Memory usage**: ~500MB för 1,000 spel

## Felsökning

### Vanliga problem

1. **"Game ID not found"**
   - Kontrollera att spelet finns i BigQuery
   - Verifiera att features är laddade

2. **"No recommendations found"**
   - Kontrollera att ML-modellen är initialiserad
   - Verifiera att features finns i Cloud Storage

3. **"API not responding"**
   - Kontrollera Docker containers
   - Verifiera GCP credentials
   - Kontrollera Cloud Storage-behörigheter

### Loggar

```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# All logs
docker-compose logs
```

## Nästa steg

1. **Prestanda-optimering**
   - Caching av rekommendationer
   - Batch-processing för flera queries
   - CDN för statiska resurser

2. **Funktionalitet**
   - Användarprofiler
   - Rekommendationshistorik
   - A/B-testing

3. **Skalning**
   - Horizontal scaling
   - Load balancing
   - Database optimization

## Support

För frågor eller problem, kontakta utvecklingsteamet eller skapa en issue i projektet.
