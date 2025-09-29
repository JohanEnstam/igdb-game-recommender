# IGDB Game Recommendation System

Ett Data Engineering-projekt som implementerar ett komplett rekommendationssystem för spel baserat på IGDB API. Projektet demonstrerar professionell infrastruktur, CI/CD, och ML-pipelines samtidigt som det löser ett praktiskt problem med spelrekommendationer.

## Arkitekturöversikt

Systemet består av tre huvudkomponenter med tydlig separation of concerns:

1. **Data Pipeline (IGDB → BigQuery)**
   - Cloud Scheduler för automatiserad daglig synkronisering
   - Cloud Functions för IGDB API-anrop med korrekt rate limiting (4 req/s)
   - Cloud Storage för rådata-backup och staging
   - BigQuery som central data warehouse med staging + MERGE patterns
   - Pub/Sub för event-driven ETL

2. **ML Pipeline (BigQuery → Vertex AI → Model Registry)**
   - Vertex AI för komplett ML-lifecycle (training, evaluation, deployment)
   - Cloud Build för automatiserad ML-pipeline vid data-uppdateringar
   - Artifact Registry för versionshanterade ML-modeller
   - Feature Store för real-time features och incremental learning
   - BigQuery ML för initial feature engineering

3. **Web Application (Model + Data → User Interface)**
   - Cloud Run för backend API (autoscalar, serverless, kostnadseffektivt)
   - Cloud SQL (PostgreSQL) för snabb sökning och autocomplettering
   - Vertex AI Prediction för real-time recommendations
   - Cloud CDN + Load Balancer för frontend-distribution
   - Memorystore (Redis) för caching av frekventa sökningar och recommendations

## Lokal utveckling

```
Docker Compose Stack:
├── PostgreSQL (lokalt med subset av data: 1000 spel)
├── Redis (för caching-tester)
├── Python API (FastAPI med hot-reload)
└── React Frontend (Next.js med hot-reload)

GCP Integration:
├── Cloud SQL Proxy (säker anslutning till dev-databas)
├── Cloud Storage (för modell-artifacts)
└── BigQuery (för ML-träning med större dataset)
```

## Kom igång

### Förutsättningar

- macOS med installerade verktyg:
  - `gcloud` CLI
  - `terraform`
  - `docker` och `docker-compose`
  - `gh` (GitHub CLI)
  - Python 3.9+, Node.js 18+

### Installation

1. Klona repository
   ```bash
   git clone https://github.com/yourusername/igdb-game-recommender.git
   cd igdb-game-recommender
   ```

2. Konfigurera miljövariabler
   ```bash
   cp .env.example .env
   # Redigera .env med dina API-nycklar och konfiguration
   ```

3. Starta lokal utvecklingsmiljö
   ```bash
   ./scripts/setup-local.sh
   docker-compose up -d
   ```

4. Öppna webbapplikationen
   ```
   http://localhost:3000
   ```

## Deployment

Se [deployment.md](docs/deployment.md) för fullständiga instruktioner.

## Demo Scenario

För att köra demo-scenariot med 200 nya spel:

```bash
./scripts/demo-data.sh
```

Se [demo-script.md](docs/demo-script.md) för detaljerad information om demo-flödet.
