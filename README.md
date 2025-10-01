# IGDB Game Recommendation System

Ett Data Engineering-projekt som implementerar ett komplett rekommendationssystem för spel baserat på IGDB API. Projektet demonstrerar professionell infrastruktur, CI/CD, och ML-pipelines samtidigt som det löser ett praktiskt problem med spelrekommendationer.

## 🎯 Aktuell Status: 85% Slutfört

Systemet är i fas 5 (ML Pipeline) och närmar sig slutförande. Infrastrukturen är deployad och fungerar, med 24,997 spel i BigQuery och fungerande feature extraction.

### ✅ Slutförda Komponenter
- **Infrastruktur**: 40+ GCP-resurser deployade via Terraform
- **Data Pipeline**: 24,997 spel i BigQuery med kategoriska features
- **ML Pipeline**: Feature extraction fungerar i molnet (1,949 features)
- **API Infrastructure**: Cloud Run service deployad och svarar

### 🔄 Pågående Arbete
- **ML Model Integration**: API använder placeholder-rekommendationer
- **Web Application**: Frontend inte implementerad än

## Arkitekturöversikt

Systemet består av tre huvudkomponenter med tydlig separation of concerns:

1. **Data Pipeline (IGDB → BigQuery)**
   - Cloud Run Jobs för batch ETL-processing
   - Cloud Storage för rådata-backup och staging
   - BigQuery som central data warehouse med 24,997 spel
   - Hybrid-lösning med lokal data + BigQuery

2. **ML Pipeline (BigQuery → Cloud Storage)**
   - Cloud Run Jobs för feature extraction (90s för 1,000 spel)
   - Cloud Storage för features (1,809 text + 140 kategoriska)
   - Faiss similarity search för rekommendationer
   - Scale-to-zero kostnadseffektivitet

3. **Web Application (Model + Data → User Interface)**
   - Cloud Run för backend API (autoscalar, serverless)
   - BigQuery för speldata och metadata
   - Cloud Storage för ML-features
   - Next.js frontend (planerad)

## 🚀 Live System

### Data & Features
- **BigQuery**: 24,997 spel i `igdb_games_dev.games_with_categories`
- **Features**: 4 filer i `gs://igdb-model-artifacts-dev/features/`
- **Performance**: 90s feature extraction, <2s API response

## Kom igång

### Förutsättningar

- macOS med installerade verktyg:
  - `gcloud` CLI
  - `terraform`
  - `docker` och `docker-compose`
  - Python 3.9+

### Installation

1. Klona repository
   ```bash
   git clone https://github.com/JohanEnstam/igdb-game-recommender.git
   cd igdb-game-recommender
   ```

2. Konfigurera GCP
   ```bash
   gcloud auth login
   gcloud config set project igdb-pipeline-v3
   ```

3. Aktivera virtuell miljö
   ```bash
   source activate.sh
   ```


## Deployment

Se [revised-deployment-plan.md](docs/revised-deployment-plan.md) för fullständiga instruktioner.

## Nästa Steg

1. **ML Model Integration** - Koppla features till rekommendationer
2. **Web Application** - Skapa Next.js frontend
3. **Production Readiness** - Optimera prestanda och monitoring

## Dokumentation

- [Projektstatus](docs/project-status-updated.md) - Detaljerad status
- [Teknisk Arkitektur](docs/technical-architecture.md) - Systemdesign
- [Deployment Plan](docs/revised-deployment-plan.md) - GCP-deployment
