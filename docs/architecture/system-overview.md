# Systemöversikt - IGDB Game Recommendation System

## Introduktion

IGDB Game Recommendation System är en komplett lösning för spelrekommendationer baserad på data från IGDB API. Systemet använder modern molnarkitektur med fokus på skalbarhet, automatisering och hög datakvalitet.

## Systemarkitektur

Systemet består av tre huvudkomponenter med tydlig separation of concerns:

### 1. Data Pipeline (IGDB → BigQuery)

Ansvarar för datainsamling, rensning och lagring.

- **Datakällor**:
  - IGDB API (primär datakälla)
  - Användarinteraktioner (planerad framtida datakälla)

- **Databearbetning**:
  - Insamling av rådata från IGDB API
  - Datarensning och deduplicering
  - Identifiering av spelrelationer och grupper
  - Kvalitetsbedömning av data

- **Datalagring**:
  - Cloud Storage för rådata-backup
  - BigQuery för strukturerad data
  - Staging och production-miljöer för säker datahantering

### 2. ML Pipeline (BigQuery → Vertex AI Matching Engine)

Ansvarar för feature extraction och similarity search för rekommendationer.

- **Feature Extraction**:
  - TF-IDF vektorisering av spelsammanfattningar
  - One-hot encoding av kategoriska features (genrer, plattformar, teman)
  - Kombinerad feature-vektor för varje spel

- **Similarity Search**:
  - Cosine similarity för att hitta liknande spel
  - Faiss för lokal utveckling och testning
  - Vertex AI Matching Engine för skalbar produktion

- **Recommendation Serving**:
  - Precomputed recommendations för vanliga sökningar
  - Real-time similarity search för dynamiska frågor
  - Caching av resultat för optimerad prestanda

### 3. Web Application (Model + Data → User Interface)

Ansvarar för användarinteraktion och presentation av rekommendationer.

- **Backend**:
  - FastAPI för RESTful API
  - PostgreSQL för snabb sökning och autocomplettering
  - Redis för caching av frekventa sökningar och rekommendationer

- **Frontend**:
  - Next.js för server-side rendering och SEO
  - React för interaktiva komponenter
  - Responsive design för mobil och desktop

## Dataflöde

```
+-------------+    +----------------+    +----------------+    +----------------+
|  IGDB API   |--->| Cloud Function |--->| Cloud Storage  |--->| BigQuery      |
+-------------+    | (Ingest)      |    | (Raw Data)     |    | (Staging)      |
                   +----------------+    +----------------+    +----------------+
                                                                      |
                                                                      v
+----------------+    +----------------+    +----------------+    +----------------+
| Web Frontend   |<---| Cloud Run API  |<---| Vertex AI      |<---| BigQuery      |
| (Next.js)      |    | (FastAPI)      |    | (Predictions)  |    | (Production)  |
+----------------+    +----------------+    +----------------+    +----------------+
        ^                     ^                     ^                     ^
        |                     |                     |                     |
        |                     |                     |                     |
+----------------+    +----------------+    +----------------+    +----------------+
| Cloud CDN      |    | PostgreSQL     |    | ML Models      |    | ETL Functions |
| (Caching)      |    | (Search)       |    | (Training)     |    | (Processing)  |
+----------------+    +----------------+    +----------------+    +----------------+
```

## Teknologistack

### Google Cloud Platform (GCP)
- **Compute**: Cloud Functions, Cloud Run
- **Storage**: BigQuery, Cloud Storage, Cloud SQL, Memorystore
- **ML**: Vertex AI, AI Platform
- **Messaging**: Pub/Sub
- **Orchestration**: Cloud Scheduler

### Utvecklingsteknologier
- **Backend**: Python 3.9+, FastAPI
- **Frontend**: TypeScript, Next.js, React
- **Data Processing**: Pandas, NumPy
- **ML**: TensorFlow, scikit-learn
- **Infrastructure as Code**: Terraform

### DevOps
- **CI/CD**: GitHub Actions
- **Containerization**: Docker
- **Monitoring**: Cloud Monitoring, Cloud Logging
- **Version Control**: Git, GitHub

## Säkerhet

- **Autentisering**: IAM för GCP-resurser
- **Auktorisering**: Role-based access control
- **Secrets Management**: Secret Manager för API-nycklar
- **Nätverkssäkerhet**: VPC för isolering av resurser

## Skalbarhet och Prestanda

- **Horisontell skalning**: Cloud Run auto-scaling
- **Caching**: Redis för frekventa frågor
- **Datapartitionering**: BigQuery-partitionering för effektiva frågor
- **Lazy loading**: För att minimera initial laddningstid

## Övervakning och Loggning

- **Dashboards**: Cloud Monitoring dashboards för nyckelmetrik
- **Alerting**: Automatiska alerts för kritiska fel
- **Loggning**: Strukturerad loggning för enkel felsökning
- **Tracing**: Distributed tracing för prestandaanalys

## Miljöer

- **Utveckling**: Lokal Docker Compose-miljö
- **Staging**: GCP-miljö för testning före produktion
- **Produktion**: Fullständig GCP-deployment

## Nästa Steg i Utvecklingen

1. **Implementera feature extraction pipeline** för speldata i BigQuery
2. **Utveckla similarity search** med Faiss och Vertex AI Matching Engine
3. **Skapa API-endpoints** för att exponera rekommendationer
4. **Implementera caching** för optimerad prestanda

## Relaterade Dokument

- [Datamodell](./data-model.md)
- [Datarensningsplan](../data-cleaning-plan.md)
- [GCP Setup](../gcp-setup.md)
