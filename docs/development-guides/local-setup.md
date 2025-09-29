# Lokal Utvecklingsmiljö - IGDB Game Recommendation System

## Översikt

Detta dokument beskriver hur du sätter upp och använder den lokala utvecklingsmiljön för IGDB Game Recommendation System.

## Förutsättningar

Följande verktyg måste vara installerade på din dator:

- **Git**
- **Docker** och **Docker Compose**
- **Python 3.9+**
- **Node.js 18+**
- **gcloud CLI** (för GCP-integration)
- **Terraform** (för infrastrukturändringar)

## Installation

### 1. Klona Repositoryt

```bash
git clone https://github.com/JohanEnstam/igdb-game-recommender.git
cd igdb-game-recommender
```

### 2. Kör Setup-skriptet

```bash
./scripts/setup-local.sh
```

Detta skript kommer att:
- Skapa en virtuell Python-miljö
- Installera alla Python-beroenden
- Installera Node.js-beroenden för frontend
- Konfigurera lokala miljövariabler

### 3. Aktivera Virtuell Miljö

```bash
source ./activate.sh
```

## Komponenter i Lokal Miljö

### Docker Compose Stack

Den lokala utvecklingsmiljön använder Docker Compose för att köra följande tjänster:

- **PostgreSQL**: Lokal databas för utveckling
- **Redis**: Caching-server för prestandaoptimering
- **FastAPI Backend**: Python API med hot-reload
- **Next.js Frontend**: React-baserad frontend med hot-reload

### Starta Lokal Miljö

```bash
cd web-app
docker-compose up -d
```

### Stoppa Lokal Miljö

```bash
cd web-app
docker-compose down
```

## Datapipeline-utveckling

### Hämta Data från IGDB API

```bash
cd data-pipeline/ingestion
python bulk_fetch.py --output ./data
```

### Analysera Data

```bash
cd data-pipeline/ingestion
python analyze_data.py --input ./data --output ./analysis
```

### Kör Datarensningspipeline

```bash
cd data-pipeline/processing
python run_etl.py --input ../ingestion/data --output ./cleaned_data
```

### Kör Tester

```bash
cd data-pipeline/processing
./run_simple_test.sh
```

## Utvecklingsarbetsflöde

1. **Aktivera virtuell miljö**
   ```bash
   source ./activate.sh
   ```

2. **Starta lokal utvecklingsmiljö**
   ```bash
   cd web-app && docker-compose up -d
   ```

3. **Utveckla och testa**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - API-dokumentation: http://localhost:8000/docs

4. **Kör tester**
   ```bash
   # Backend-tester
   cd web-app/backend
   pytest

   # Frontend-tester
   cd web-app/frontend
   npm test

   # Data pipeline-tester
   cd data-pipeline/processing
   ./run_simple_test.sh
   ```

## Felsökning

### Vanliga Problem

#### Docker Compose startar inte
```bash
# Kontrollera Docker-status
docker ps -a

# Rensa Docker-cache
docker system prune
```

#### Virtuell miljö fungerar inte
```bash
# Återskapa virtuell miljö
rm -rf .venv
./scripts/setup_venv.sh
source ./activate.sh
```

#### IGDB API-fel
```bash
# Kontrollera API-nycklar
cat .env

# Uppdatera API-nycklar
nano .env
```

## Nästa Steg

1. **Utforska API-dokumentation**: http://localhost:8000/docs
2. **Granska koden**: Se README.md i respektive katalog för mer information
3. **Bidra till projektet**: Se CONTRIBUTING.md för riktlinjer

## Relaterade Dokument

- [Projektöversikt](../README.md)
- [Systemarkitektur](../architecture/system-overview.md)
