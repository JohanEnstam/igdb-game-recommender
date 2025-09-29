# GCP Setup Guide - IGDB Game Recommendation System

Detta dokument innehåller steg-för-steg instruktioner för att konfigurera GCP-miljön för projektet, med fokus på att använda gcloud CLI istället för konsolen.

## 1. Grundläggande GCP-konfiguration

### Autentisering och Projektval
```bash
# Autentisera mot GCP
gcloud auth login

# Sätt aktivt projekt
gcloud config set project igdb-pipeline-v3

# Verifiera att rätt projekt är valt
gcloud config get-value project
```

### Aktivera Nödvändiga APIs
```bash
# Aktivera nödvändiga GCP-tjänster
gcloud services enable compute.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  cloudfunctions.googleapis.com \
  pubsub.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com \
  redis.googleapis.com \
  sqladmin.googleapis.com \
  cloudscheduler.googleapis.com
```

## 2. Terraform State Setup

### Skapa GCS Bucket för Terraform State
```bash
# Skapa bucket för Terraform state
gcloud storage buckets create gs://igdb-terraform-state \
  --location=europe-west1 \
  --uniform-bucket-level-access

# Verifiera att bucketen skapades
gcloud storage buckets list --filter="name:igdb-terraform-state"
```

## 3. Service Accounts för Terraform och CI/CD

### Skapa Service Account för Terraform
```bash
# Skapa service account för Terraform
gcloud iam service-accounts create terraform-admin \
  --display-name="Terraform Admin Service Account"

# Ge service account nödvändiga behörigheter
gcloud projects add-iam-policy-binding igdb-pipeline-v3 \
  --member="serviceAccount:terraform-admin@igdb-pipeline-v3.iam.gserviceaccount.com" \
  --role="roles/editor"

# Skapa och ladda ner nyckel för service account
gcloud iam service-accounts keys create terraform-admin-key.json \
  --iam-account=terraform-admin@igdb-pipeline-v3.iam.gserviceaccount.com
```

### Skapa Service Accounts för Cloud Functions och Cloud Run
```bash
# Skapa service account för Cloud Functions
gcloud iam service-accounts create cf-igdb-ingest \
  --display-name="IGDB Ingest Cloud Functions Service Account"

# Skapa service account för Cloud Run
gcloud iam service-accounts create cloud-run-igdb-api \
  --display-name="IGDB API Cloud Run Service Account"

# Ge Cloud Functions service account nödvändiga behörigheter
gcloud projects add-iam-policy-binding igdb-pipeline-v3 \
  --member="serviceAccount:cf-igdb-ingest@igdb-pipeline-v3.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding igdb-pipeline-v3 \
  --member="serviceAccount:cf-igdb-ingest@igdb-pipeline-v3.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding igdb-pipeline-v3 \
  --member="serviceAccount:cf-igdb-ingest@igdb-pipeline-v3.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

# Ge Cloud Run service account nödvändiga behörigheter
gcloud projects add-iam-policy-binding igdb-pipeline-v3 \
  --member="serviceAccount:cloud-run-igdb-api@igdb-pipeline-v3.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding igdb-pipeline-v3 \
  --member="serviceAccount:cloud-run-igdb-api@igdb-pipeline-v3.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding igdb-pipeline-v3 \
  --member="serviceAccount:cloud-run-igdb-api@igdb-pipeline-v3.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

## 4. GitHub Actions Secrets Setup

För att konfigurera GitHub Actions behöver följande secrets läggas till i GitHub-repositoryt:

1. `GCP_PROJECT_ID`: igdb-pipeline-v3
2. `GCP_SA_KEY`: Innehållet i terraform-admin-key.json (base64-encodad)
3. `TF_STATE_BUCKET`: igdb-terraform-state
4. `CF_SERVICE_ACCOUNT`: cf-igdb-ingest@igdb-pipeline-v3.iam.gserviceaccount.com
5. `CLOUD_RUN_SERVICE_ACCOUNT`: cloud-run-igdb-api@igdb-pipeline-v3.iam.gserviceaccount.com
6. `GCP_REGION`: europe-west1

```bash
# Base64-encodera service account-nyckeln (för GitHub Actions)
cat terraform-admin-key.json | base64
```

## 5. Terraform Initialisering

Efter att ha konfigurerat GCP och GitHub Actions kan Terraform initialiseras:

```bash
# Exportera service account-nyckeln för lokal användning
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/terraform-admin-key.json"

# Gå till Terraform-katalogen
cd infrastructure/terraform

# Initialisera Terraform med remote state
terraform init \
  -backend-config="bucket=igdb-terraform-state" \
  -backend-config="prefix=terraform/state/dev"

# Validera Terraform-konfigurationen
terraform validate

# Skapa en plan för dev-miljön
terraform plan -var-file="environments/dev.tfvars"
```

## Säkerhet och Bästa Praxis

1. **Förvara aldrig service account-nycklar i Git-repositoryt**
2. **Använd minsta möjliga behörigheter för service accounts**
3. **Aktivera endast de GCP-tjänster som behövs**
4. **Använd Terraform för all infrastrukturkonfiguration**
5. **Kör terraform plan innan terraform apply**
