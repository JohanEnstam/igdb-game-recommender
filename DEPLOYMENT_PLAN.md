# IGDB Game Recommender - Deployment Plan

## Nuläge: Infrastruktur och ML-integration är klar

### Befintlig infrastruktur (via Terraform)
✅ **Deployad och fungerar:**
- BigQuery: `igdb_games_dev` dataset med 24,997 spel
- Cloud Storage: 
  - `igdb-model-artifacts-dev` (features: 1,000 spel, 1,949 dimensioner)
  - `igdb-raw-data-dev` 
  - `igdb-processed-data-dev`
- Cloud Run Jobs: 
  - `igdb-feature-extraction-dev`
  - `igdb-etl-pipeline-dev`
- Cloud Functions:
  - `data-cleaning-pipeline-dev`
  - `igdb-api-ingest-dev`
  - `etl-processor-dev`
- IAM: Service accounts och permissions

### Vad som saknas för produktionsdrift

#### 1. Cloud Run API Service (inte deployad än)
**Terraform definition:** `igdb-recommendation-api-dev`
- Terraform-konfiguration finns i `infrastructure/terraform/modules/cloud_run/main.tf`
- Docker image förväntas: `europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-recommendation-api:latest`
- **Status:** Konfigurerad i Terraform men Docker image saknas i Artifact Registry

#### 2. Docker Images
**Behöver byggas och pushas till Artifact Registry:**

a) **Recommendation API** (`web-app/backend/`)
   - Dockerfile: ✅ Klar
   - Requirements.txt: ✅ Uppdaterad (numpy 1.26.4, db-dtypes 1.2.0)
   - Source code: ✅ Testad lokalt
   - Image name: `europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-recommendation-api:latest`

b) **Feature Extraction Job** (`ml-pipeline/`)
   - Dockerfile: Behöver skapas
   - Source: `ml-pipeline/feature_engineering/`
   - Image name: `europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-feature-extraction:latest`

c) **ETL Pipeline Job** (`data-pipeline/`)
   - Dockerfile: Finns redan (`ml-pipeline/Dockerfile.etl-pipeline`)
   - Source: `data-pipeline/processing/`
   - Image name: `europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-etl-pipeline:latest`

#### 3. Frontend (Web App)
**Inte inkluderad i Terraform än:**
- Source: `web-app/frontend/`
- Dockerfile: ✅ Klar
- Behöver: Separat Cloud Run service eller hosting via Firebase/Cloud Storage + CDN

---

## Deployment-steg

### Fas 1: Bygg och pusha Docker images (10-15 min)

```bash
# 1. Sätt GCP projekt
gcloud config set project igdb-pipeline-v3

# 2. Konfigurera Docker för Artifact Registry
gcloud auth configure-docker europe-west1-docker.pkg.dev

# 3. Bygg och pusha Recommendation API
cd web-app/backend
docker build -t europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-recommendation-api:latest .
docker push europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-recommendation-api:latest

# 4. Bygg och pusha Feature Extraction (om behövs)
cd ../../ml-pipeline
docker build -f Dockerfile.feature-extraction \
  -t europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-feature-extraction:latest .
docker push europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-feature-extraction:latest

# 5. Bygg och pusha ETL Pipeline (om behövs)
docker build -f Dockerfile.etl-pipeline \
  -t europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-etl-pipeline:latest .
docker push europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-etl-pipeline:latest
```

### Fas 2: Deploy med Terraform (5 min)

```bash
cd infrastructure/terraform

# 1. Terraform plan för att se vad som kommer ändras
terraform plan -var-file=environments/dev.tfvars

# 2. Apply för att deploya Cloud Run API
terraform apply -var-file=environments/dev.tfvars

# 3. Hämta API URL
terraform output recommendation_api_url
```

### Fas 3: Verifiera deployment (5 min)

```bash
# 1. Hämta API URL från Terraform output
API_URL=$(terraform output -raw recommendation_api_url)

# 2. Testa health endpoint
curl $API_URL/health

# 3. Testa sökning
curl "$API_URL/games/search?query=zelda&limit=3"

# 4. Testa rekommendationer (använd ett game_id från sökningen)
curl "$API_URL/recommendations/5190?limit=3"
```

### Fas 4: Frontend deployment (valfritt, 10 min)

**Alternativ A: Cloud Run**
```bash
cd web-app/frontend

# 1. Bygg och pusha image
docker build -t europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-recommendation-frontend:latest .
docker push europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-recommendation-frontend:latest

# 2. Deploy till Cloud Run
gcloud run deploy igdb-recommendation-frontend-dev \
  --image europe-west1-docker.pkg.dev/igdb-pipeline-v3/igdb-recommender/igdb-recommendation-frontend:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=$API_URL
```

**Alternativ B: Cloud Storage + CDN (billigare för statisk site)**
```bash
# 1. Bygg produktionsversion
npm run build
npm run export

# 2. Deploya till Cloud Storage
gsutil -m rsync -r out/ gs://igdb-frontend-dev/

# 3. Konfigurera bucket för web hosting
gsutil web set -m index.html gs://igdb-frontend-dev/
```

---

## Kostnadsuppskattning

### Nuvarande setup (dev):
- **BigQuery:** ~$2-5/månad (24k rader, queries)
- **Cloud Storage:** ~$1-2/månad (features + data)
- **Cloud Functions:** ~$0 (scale-to-zero, minimal användning)
- **Total befintlig:** ~$3-7/månad

### Efter API deployment:
- **Cloud Run API:** ~$5-20/månad (scale-to-zero, CPU-tid vid requests)
- **Cloud Run Jobs:** ~$0-5/månad (scheduled/on-demand)
- **Frontend (Cloud Run):** ~$2-5/månad
- **Frontend (Cloud Storage):** ~$0.50-1/månad
- **Total efter deployment:** ~$10-35/månad (dev environment)

### Produktion (uppskattning):
- Med trafik: ~$50-150/månad
- Med heavy ML workloads: ~$100-300/månad

---

## Nästa steg (prioriterat)

### Kritiskt (för att få systemet live):
1. **Bygg Recommendation API Docker image** (5 min)
2. **Pusha till Artifact Registry** (2 min)
3. **Terraform apply** (2 min)
4. **Verifiera API i molnet** (5 min)

### Viktigt (för fullständig lösning):
5. **Deploy frontend** (10 min)
6. **Konfigurera custom domain** (valfritt, 15 min)
7. **Sätt upp monitoring/alerting** (15 min)

### Kan vänta:
8. Feature extraction job (körs on-demand)
9. ETL pipeline job (schemalagd eller on-demand)
10. Produktionsmiljö (staging + prod environments)

---

## Troubleshooting

### Om Docker build misslyckas:
```bash
# Kontrollera Dockerfile syntax
docker build --no-cache -t test-image .

# Testa lokalt först
docker run -p 8000:8000 -e FEATURES_BUCKET=igdb-model-artifacts-dev test-image
```

### Om Terraform apply misslyckas:
```bash
# Kontrollera att Artifact Registry repository finns
gcloud artifacts repositories list --location=europe-west1

# Om det saknas, skapa det:
gcloud artifacts repositories create igdb-recommender \
  --repository-format=docker \
  --location=europe-west1
```

### Om API inte svarar efter deployment:
```bash
# Kontrollera Cloud Run logs
gcloud run services logs read igdb-recommendation-api-dev \
  --region=europe-west1 \
  --limit=50

# Kontrollera service account permissions
gcloud projects get-iam-policy igdb-pipeline-v3 \
  --flatten="bindings[].members" \
  --filter="bindings.members:*cloud-run*"
```

---

## Sammanfattning

**Infrastruktur: 90% klar**
- BigQuery, Cloud Storage, IAM: ✅ Deployad
- Cloud Functions: ✅ Deployad
- Cloud Run Jobs: ✅ Konfigurerad (images saknas)

**Applikation: 95% klar**
- Backend API: ✅ Testad lokalt, fungerar
- ML-integration: ✅ Verifierad
- Frontend: ✅ Prototyp klar

**Återstår för production:**
1. Bygg och pusha 1 Docker image (API)
2. Kör `terraform apply`
3. Verifiera deployment
4. (Valfritt) Deploy frontend

**Total tid till live system: 15-30 minuter**
