# IGDB Game Recommendation System - Project Specification

## Projektöversikt

Ett Data Engineering-projekt för kursbetyg som implementerar ett komplett rekommendationssystem för spel baserat på IGDB API. Projektet demonstrerar professionell infrastruktur, CI/CD, och ML-pipelines samtidigt som det löser ett praktiskt problem med spelrekommendationer.

## 🎯 Aktuell Status: 85% Slutfört

Systemet är deployat på GCP med fungerande infrastruktur, data pipeline och feature extraction. Nästa steg är ML model integration och web application.

## Korrigerade Grundförutsättningar

### IGDB API - Korrekt Förståelse
- **Rate Limit**: 4 requests/second
- **Batch Size**: 500 spel per request
- **Total Tid för 350k spel**: ~15 minuter (INTE veckor som tidigare antaget)
- **Data Volym**: ~700MB (inte "big data")
- **Slutsats**: Ingen komplex event-driven arkitektur behövs för batch-processing

### Kursmål och Demonstrationskrav
- **Tidsram**: Presentation på 10-12 minuter
- **Demo-scenario**: Visa 200 nya spel som flödar genom hela systemet live
- **Fokus**: Automatisering av hela kedjan från data-ingestion till web-app
- **Målsättning**: Professionell Data Engineering-infrastruktur som grund för betyg

## Övergripande Arkitekturstrategi

Tre huvudkomponenter med tydlig separation of concerns:

### 1. Data Pipeline (IGDB → BigQuery)
- **Cloud Scheduler** för automatiserad daglig synkronisering
- **Cloud Functions** för IGDB API-anrop med korrekt rate limiting (4 req/s)
- **Cloud Storage** för rådata-backup och staging
- **BigQuery** som central data warehouse med staging + MERGE patterns
- **Pub/Sub** för event-driven ETL (sofistikerat för kursbetyg)

### 2. ML Pipeline (BigQuery → Vertex AI → Model Registry)
- **Vertex AI** för komplett ML-lifecycle (training, evaluation, deployment)
- **Cloud Build** för automatiserad ML-pipeline vid data-uppdateringar
- **Artifact Registry** för versionshanterade ML-modeller
- **Feature Store** för real-time features och incremental learning
- **BigQuery ML** för initial feature engineering

### 3. Web Application (Model + Data → User Interface)
- **Cloud Run** för backend API (autoscalar, serverless, kostnadseffektivt)
- **Cloud SQL** (PostgreSQL) för snabb sökning och autocomplettering
- **Vertex AI Prediction** för real-time recommendations
- **Cloud CDN + Load Balancer** för frontend-distribution
- **Memorystore (Redis)** för caching av frekventa sökningar och recommendations

## Teknisk Implementation

### Dataflöde - Produktionssystem
```
IGDB API → Cloud Scheduler → Cloud Functions → Cloud Storage → BigQuery Staging
                                                                      ↓
BigQuery Production ← Pub/Sub ← ETL Functions ← Deduplication/MERGE ←┘
                                                                      ↓
Vertex AI Training → Model Registry → Vertex AI Endpoints → Cloud Run API
                                                                      ↓
Frontend (Vercel) ← PostgreSQL ← Recommendation Service ←──────────────┘
```

### Dataflöde - Demo Scenario (200 nya spel)
```
Manual Trigger → Cloud Function → New Games Data → BigQuery Staging
                                                            ↓
                                    Pub/Sub Event → ETL → MERGE
                                                            ↓
                        Auto-trigger ML Pipeline → New Model Version
                                                            ↓
                            Cloud Run Deployment → Updated Web App
                                                            ↓
                                    Live Demo → New Games Searchable
```

## Miljöstrategi

### Utvecklingsmiljöer
**Rekommendation**: Ett GCP-projekt med miljö-tagging för kursprojekt
- **Utveckling**: Lokal Docker Compose + Cloud SQL Proxy
- **Staging**: Automatisk deployment från main branch
- **Production**: Manuell promotion efter staging-validering

### Lokal Utveckling
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

## Project Structure

```
igdb-game-recommender/
├── infrastructure/terraform/           # Infrastructure as Code
│   ├── environments/
│   │   ├── dev.tfvars
│   │   ├── staging.tfvars
│   │   └── prod.tfvars
│   ├── modules/
│   │   ├── bigquery/                  # Data warehouse setup
│   │   ├── cloud_functions/           # Serverless functions
│   │   ├── cloud_run/                # API deployment
│   │   ├── cloud_sql/                # PostgreSQL for web-app
│   │   ├── vertex_ai/                # ML infrastructure
│   │   ├── storage/                  # GCS buckets
│   │   ├── pubsub/                   # Event-driven messaging
│   │   ├── monitoring/               # Logging, metrics, alerting
│   │   └── iam/                      # Security and permissions
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── data-pipeline/
│   ├── ingestion/
│   │   ├── igdb_client.py            # IGDB API client med korrekt rate limiting
│   │   ├── bulk_fetch.py             # Hämta alla 350k spel på 15 min
│   │   └── incremental_sync.py       # Daglig synkronisering
│   ├── processing/
│   │   ├── etl_staging.py            # BigQuery staging operations
│   │   ├── data_quality.py           # Validation och deduplication
│   │   └── merge_production.py       # Staging → Production MERGE
│   └── cloud_functions/
│       ├── igdb_ingest/              # Cloud Function för IGDB API
│       ├── etl_processor/            # ETL Cloud Function
│       └── data_validator/           # Data quality checks
├── ml-pipeline/
│   ├── feature_engineering/
│   │   ├── text_features.py          # TF-IDF, embeddings
│   │   ├── categorical_features.py   # Genres, platforms, themes
│   │   └── feature_store.py          # Vertex AI Feature Store
│   ├── training/
│   │   ├── content_based_model.py    # Similarity-baserad rekommendation
│   │   ├── hybrid_model.py           # Combined approach
│   │   └── evaluation.py             # Model validation metrics
│   ├── serving/
│   │   ├── prediction_service.py     # Vertex AI Prediction wrapper
│   │   └── batch_predictions.py      # Bulk recommendation generation
│   └── vertex_ai_pipelines/
│       ├── training_pipeline.py      # Automatiserad träning
│       └── deployment_pipeline.py    # Model deployment automation
├── web-app/
│   ├── backend/
│   │   ├── api/
│   │   │   ├── main.py               # FastAPI application
│   │   │   ├── recommendations.py    # Recommendation endpoints
│   │   │   ├── search.py             # Game search och autocomplete
│   │   │   └── health.py             # Health checks för monitoring
│   │   ├── models/
│   │   │   ├── database.py           # PostgreSQL models
│   │   │   ├── cache.py              # Redis integration
│   │   │   └── ml_client.py          # Vertex AI client
│   │   ├── services/
│   │   │   ├── game_service.py       # Business logic för games
│   │   │   ├── recommendation_service.py # ML integration
│   │   │   └── search_service.py     # Elasticsearch-liknande sökning
│   │   └── requirements.txt
│   ├── frontend/
│   │   ├── pages/                    # Next.js pages
│   │   ├── components/               # React components
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── utils/                    # Helper functions
│   │   └── package.json
│   └── docker-compose.yml            # Lokal utvecklingsmiljö
├── .github/workflows/
│   ├── terraform.yml                 # Infrastructure CI/CD
│   ├── data-pipeline.yml             # Data pipeline deployment
│   ├── ml-pipeline.yml               # ML model deployment
│   ├── web-app.yml                   # Application deployment
│   └── security-scan.yml             # Security scanning (Bandit, Safety)
├── monitoring/
│   ├── dashboards/                   # Cloud Monitoring dashboards
│   ├── alerts/                       # Alerting policies
│   └── logging/                      # Structured logging config
├── docs/
│   ├── architecture.md               # System architecture
│   ├── api.md                        # API documentation
│   ├── deployment.md                 # Deployment guide
│   └── demo-script.md                # Presentation demo guide
├── tests/
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── e2e/                          # End-to-end tests
├── scripts/
│   ├── setup-local.sh                # Lokal miljösetup
│   ├── deploy.sh                     # Deployment automation
│   └── demo-data.sh                  # Demo data preparation
├── .env.example                      # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## Implementationsplan

### Phase 1: Foundation (Dag 1-2)
- **Terraform setup**: Modulär infrastruktur från dag ett
- **GitHub Actions**: CI/CD pipelines för alla komponenter
- **Docker Compose**: Lokal utvecklingsmiljö
- **Basic project structure**: Alla mappar och placeholder-filer

### Phase 2: Data Pipeline (Dag 3-4)
- **IGDB client**: Korrekt implementation med 4 req/s rate limiting
- **BigQuery setup**: Staging + Production tabeller
- **Cloud Functions**: Ingestion och ETL automation
- **Pub/Sub integration**: Event-driven processing

### Phase 3: ML Pipeline (Dag 5-6)
- **Feature engineering**: TF-IDF, categorical features, embeddings
- **Vertex AI integration**: Training pipelines och model registry
- **Model serving**: Real-time predictions via Vertex AI endpoints
- **Evaluation framework**: Model validation och A/B testing setup

### Phase 4: Web Application (Dag 7-8)
- **Backend API**: FastAPI med PostgreSQL integration
- **Frontend**: Next.js med search och recommendation components
- **Caching layer**: Redis för performance optimization
- **Cloud Run deployment**: Automatiserad containerized deployment

### Phase 5: Integration & Demo Prep (Dag 9-10)
- **End-to-end testing**: Hela flödet från IGDB till web-app
- **Demo scenario**: 200 nya spel workflow automation
- **Monitoring setup**: Dashboards för live demonstration
- **Performance optimization**: Caching, query optimization

### Phase 6: Presentation Ready (Dag 11-12)
- **Demo script**: 10-12 minuters presentation med live demo
- **Documentation**: Architecture och API documentation
- **Video recording**: Backup för presentation
- **Cost optimization**: Cleanup av resurser efter demo

## Demo Scenario - "200 Nya Spel"

### Pre-Demo Setup
- Databas med 349,800 spel (300k minus 200 "nya")
- Tränad ML-modell på dessa spel
- Fungerande web-app med search och recommendations

### Live Demo Flow (10-12 minuter)
1. **Trigger Data Pipeline** (2 min)
   - Visa Cloud Scheduler trigger i Console
   - Cloud Function startar → Pub/Sub meddelanden
   - "Vi simulerar att IGDB har 200 nya spel"

2. **Data Processing** (3 min)
   - BigQuery staging table uppdateras live
   - ETL Cloud Function kör deduplication
   - MERGE operation från staging till production
   - Row count: 349,800 → 350,000

3. **ML Pipeline Automation** (3 min)
   - Vertex AI training pipeline triggas automatiskt
   - Incremental learning på nya spel-features
   - Model evaluation och validation
   - Ny model version deployed till endpoint

4. **Web Application Update** (2-3 min)
   - Cloud Run service får automatisk redeploy
   - PostgreSQL sync med nya spel-data
   - Demo search för nya speltitlar
   - Visa recommendations som inkluderar nya spel

5. **Monitoring & Metrics** (1 min)
   - Cloud Monitoring dashboard med pipeline metrics
   - Cost tracking och resource utilization
   - End-to-end latency från trigger till web-app

## Tekniska Krav

### Development Environment
- **macOS** med installerade verktyg:
  - `gcloud` CLI
  - `terraform`
  - `docker` och `docker-compose`
  - `gh` (GitHub CLI)
  - Python 3.9+, Node.js 18+

### GCP Services
- **Compute**: Cloud Functions, Cloud Run, Vertex AI
- **Storage**: BigQuery, Cloud SQL, Cloud Storage, Memorystore
- **Networking**: Load Balancer, Cloud CDN
- **Management**: Cloud Scheduler, Pub/Sub, Artifact Registry
- **Monitoring**: Cloud Monitoring, Cloud Logging, Error Reporting

### Cost Optimization
- **Resource Tagging**: Environment, component, cost-center
- **Auto-scaling**: Cloud Run concurrency, BigQuery slots
- **Scheduled Resources**: Dev environments stängs nattetid
- **Monitoring**: Budget alerts och cost anomaly detection

## Framgångskriterier

### Tekniska Mål
- ✅ Komplett automation från IGDB API till web-app
- ✅ Sub-sekund response times för search och recommendations
- ✅ Skalbar arkitektur som hanterar 350k+ spel
- ✅ Zero-downtime deployments via CI/CD
- ✅ Comprehensive monitoring och alerting

### Kursmål (Data Engineering)
- ✅ Professionell Infrastructure as Code (Terraform)
- ✅ Advanced ETL patterns (staging, MERGE, deduplication)
- ✅ ML Operations (automated training, model registry, serving)
- ✅ Event-driven architecture (Pub/Sub, Cloud Functions)
- ✅ Security compliance (IAM, secrets management, scanning)

### Demonstrationsmål
- ✅ 10-12 minuters engaging presentation
- ✅ Live demo av hela data pipeline
- ✅ Synlig automation utan manuella steg
- ✅ Professional web interface med real-time updates
- ✅ Clear visualization av varje arkitekturkomponent

## Nästa Steg

1. **Skapa Terraform foundation** med modulär struktur
2. **Setup GitHub repository** med CI/CD templates
3. **Implementera IGDB client** med korrekt rate limiting
4. **Docker Compose** för lokal utveckling
5. **Basic web-app** för att testa end-to-end flöde

**Prioritet**: Börja med Terraform-modulerna eftersom de är svårast att "eftermontera" och sätter grunden för all automation.