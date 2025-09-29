# IGDB Game Recommender - Cloud Functions

Detta är Cloud Functions-komponenten av IGDB Game Recommender-projektet, som hanterar datainsamling, datarensning och ETL-processen i molnet.

## Översikt

Systemet består av tre huvudsakliga Cloud Functions:

1. **IGDB API Ingest** - Hämtar speldata från IGDB API och lagrar den i Cloud Storage
2. **Data Cleaning Pipeline** - Bearbetar rådata, extraherar kanoniska namn, identifierar relationer och skapar spelgrupper
3. **ETL Processor** - Laddar den rensade datan till BigQuery för analys och rekommendationer

## Arkitektur

Dataflödet är följande:

1. **IGDB API Ingest** triggas via HTTP eller Cloud Scheduler
   - Hämtar speldata från IGDB API
   - Sparar rådata till `gs://{RAW_DATA_BUCKET}/raw_data/`

2. **Data Cleaning Pipeline** triggas när ny rådata laddas upp
   - Bearbetar rådata med datarensningspipelinen
   - Extraherar kanoniska namn, identifierar relationer och skapar spelgrupper
   - Sparar rensad data till `gs://{PROCESSED_DATA_BUCKET}/cleaned_data/`

3. **ETL Processor** triggas när ny rensad data laddas upp
   - Laddar rensad data till BigQuery-tabeller
   - Möjliggör analys och rekommendationer

## Förutsättningar

- Google Cloud Platform-konto med aktiverade API:er:
  - Cloud Functions
  - Cloud Storage
  - BigQuery
  - Cloud Scheduler
  - Pub/Sub
- IGDB API-nycklar (Client ID och Client Secret)
- Terraform installerat lokalt

## Deployment

### 1. Paketera Cloud Functions

Kör följande kommando för att paketera alla Cloud Functions:

```bash
cd data-pipeline/cloud_functions
chmod +x deploy_all.sh
./deploy_all.sh [environment]
```

Detta skapar ZIP-filer för varje Cloud Function i `data-pipeline/`-katalogen.

### 2. Ladda upp moduler för datarensning

Datarensningspipelinen behöver tillgång till Python-modulerna för datarensning. Ladda upp dessa till Cloud Storage:

```bash
cd data-pipeline/cloud_functions/data_cleaning_pipeline
chmod +x deploy_modules.sh
./deploy_modules.sh [environment]
```

### 3. Distribuera med Terraform

Använd Terraform för att distribuera infrastrukturen:

```bash
cd infrastructure/terraform
terraform init
terraform apply -var-file=environments/dev.tfvars
```

## Miljövariabler

Följande miljövariabler måste konfigureras för Cloud Functions:

### IGDB API Ingest
- `PROJECT_ID` - GCP-projektets ID
- `ENVIRONMENT` - Miljö (dev, staging, prod)
- `RAW_DATA_BUCKET` - GCS-bucket för rådata
- `IGDB_CLIENT_ID` - IGDB API Client ID
- `IGDB_CLIENT_SECRET` - IGDB API Client Secret

### Data Cleaning Pipeline
- `PROJECT_ID` - GCP-projektets ID
- `ENVIRONMENT` - Miljö (dev, staging, prod)
- `RAW_DATA_BUCKET` - GCS-bucket för rådata
- `PROCESSED_DATA_BUCKET` - GCS-bucket för bearbetad data

### ETL Processor
- `PROJECT_ID` - GCP-projektets ID
- `ENVIRONMENT` - Miljö (dev, staging, prod)
- `PROCESSED_DATA_BUCKET` - GCS-bucket för bearbetad data
- `BIGQUERY_DATASET` - BigQuery-dataset för datatabeller

## Testning

För att testa ETL-pipelinen:

1. Anropa IGDB API Ingest-funktionen via HTTP:
   ```
   curl -X POST https://[REGION]-[PROJECT_ID].cloudfunctions.net/igdb-api-ingest-[ENVIRONMENT] -H "Authorization: bearer $(gcloud auth print-identity-token)" -H "Content-Type: application/json" -d '{"max_games": 1000}'
   ```

2. Kontrollera att Data Cleaning Pipeline och ETL Processor triggas automatiskt
3. Verifiera att data har laddats till BigQuery-tabellerna

## Schemaläggning

För att schemalägga regelbunden datainsamling, skapa ett Cloud Scheduler-jobb som anropar IGDB API Ingest-funktionen:

```bash
gcloud scheduler jobs create http igdb-data-fetch-[ENVIRONMENT] \
  --schedule="0 0 * * 0" \
  --uri="https://[REGION]-[PROJECT_ID].cloudfunctions.net/igdb-api-ingest-[ENVIRONMENT]" \
  --http-method=POST \
  --oidc-service-account-email=[SERVICE_ACCOUNT_EMAIL] \
  --message-body='{"max_games": null}'
```

Detta schemalägger datainsamling varje söndag vid midnatt.

## Övervakning

Använd Cloud Monitoring för att övervaka Cloud Functions:

1. Skapa en dashboard för att övervaka:
   - Funktionsanrop och felfrekvens
   - Exekveringstid
   - Minnesanvändning

2. Konfigurera aviseringar för:
   - Funktionsfel
   - Lång exekveringstid
   - Minnesbegränsningar

## Felsökning

Om något går fel, kontrollera Cloud Functions-loggarna:

```bash
gcloud functions logs read igdb-api-ingest-[ENVIRONMENT] --limit=50
gcloud functions logs read data-cleaning-pipeline-[ENVIRONMENT] --limit=50
gcloud functions logs read etl-processor-[ENVIRONMENT] --limit=50
```
