#!/bin/bash
# Script för att ladda upp rådata till Cloud Storage

# Användning: ./upload_raw_data.sh [environment]
# Exempel: ./upload_raw_data.sh dev

# Standardvärde för miljö om inget anges
ENVIRONMENT=${1:-dev}

# Sätt bucket-namn baserat på miljö
RAW_DATA_BUCKET="igdb-raw-data-${ENVIRONMENT}"
DATA_DIR="igdb-game-recommender/data-pipeline/ingestion/data"

echo "Laddar upp rådata till gs://${RAW_DATA_BUCKET}/raw_data/"

# Kontrollera att bucket finns
if ! gsutil ls -b gs://${RAW_DATA_BUCKET} > /dev/null 2>&1; then
  echo "Fel: Bucket gs://${RAW_DATA_BUCKET} finns inte."
  exit 1
fi

# Ladda upp alla JSON-filer med parallella överföringar
echo "Startar uppladdning av JSON-filer..."
gsutil -m cp ${DATA_DIR}/*.json gs://${RAW_DATA_BUCKET}/raw_data/

echo "Uppladdning klar."
echo ""
echo "För att kontrollera uppladdade filer:"
echo "gsutil ls gs://${RAW_DATA_BUCKET}/raw_data/"
