#!/bin/bash
# Test script för ETL-pipeline

set -e  # Exit vid fel

echo "=== ETL Pipeline Test ==="
echo "Testar hela ETL-pipelinen från IGDB API till BigQuery"
echo ""

# Kontrollera att användaren är autentiserad mot GCP
if ! gcloud auth print-identity-token &>/dev/null; then
  echo "❌ Du är inte autentiserad mot GCP. Kör 'gcloud auth login' först."
  exit 1
fi

# Hämta projektinformation
PROJECT_ID=$(gcloud config get-value project)
REGION="europe-west1"
ENVIRONMENT="dev"

echo "Projekt: $PROJECT_ID"
echo "Region: $REGION"
echo "Miljö: $ENVIRONMENT"
echo ""

# Steg 1: Anropa IGDB API Ingest-funktionen
echo "1. Anropar IGDB API Ingest-funktionen (hämtar 10 spel)..."
RESPONSE=$(curl -s -X POST "https://$REGION-$PROJECT_ID.cloudfunctions.net/igdb-api-ingest-$ENVIRONMENT" \
  -H "Authorization: bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"max_games": 10}')

echo "Svar från IGDB API Ingest:"
echo "$RESPONSE" | jq .
echo ""

# Extrahera sökväg till lagrad fil
STORAGE_PATH=$(echo $RESPONSE | jq -r '.storage_path')
if [ -z "$STORAGE_PATH" ] || [ "$STORAGE_PATH" == "null" ]; then
  echo "❌ Kunde inte hämta sökväg till lagrad fil."
  exit 1
fi

echo "Fil sparad till: $STORAGE_PATH"
echo ""

# Steg 2: Vänta på att data ska bearbetas genom pipelinen
echo "2. Väntar på att data ska bearbetas genom pipelinen..."
echo "   (Detta kan ta upp till 2 minuter)"

# Extrahera bucket och filnamn från sökvägen
BUCKET=$(echo $STORAGE_PATH | cut -d'/' -f3)
FILE_PATH=$(echo $STORAGE_PATH | cut -d'/' -f4-)
TIMESTAMP=$(date +%Y%m%d)

# Vänta och kontrollera om cleaned_data har genererats
MAX_WAIT=120  # sekunder
WAIT_INTERVAL=10  # sekunder
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
  echo "   Har väntat $ELAPSED sekunder..."
  
  # Kontrollera om det finns cleaned_data-filer från dagens datum
  CLEANED_FILES=$(gsutil ls -l "gs://igdb-processed-data-$ENVIRONMENT/cleaned_data/$TIMESTAMP*" 2>/dev/null || echo "")
  
  if [ -n "$CLEANED_FILES" ]; then
    echo "✅ Hittade bearbetad data!"
    echo "$CLEANED_FILES"
    break
  fi
  
  sleep $WAIT_INTERVAL
  ELAPSED=$((ELAPSED + WAIT_INTERVAL))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
  echo "❌ Timeout: Ingen bearbetad data hittades inom $MAX_WAIT sekunder."
  echo "   Kontrollera Cloud Functions-loggarna för eventuella fel."
  exit 1
fi

echo ""

# Steg 3: Verifiera att data har laddats till BigQuery
echo "3. Verifierar att data har laddats till BigQuery..."
echo "   (Detta kan ta ytterligare tid)"

# Vänta lite till för att BigQuery-laddningen ska hinna slutföras
sleep 30

# Kontrollera om det finns data i BigQuery-tabellerna
GAMES_COUNT=$(bq query --use_legacy_sql=false --format=csv "SELECT COUNT(*) FROM \`$PROJECT_ID.igdb_games_$ENVIRONMENT.games\`" | tail -n 1)
RELATIONSHIPS_COUNT=$(bq query --use_legacy_sql=false --format=csv "SELECT COUNT(*) FROM \`$PROJECT_ID.igdb_games_$ENVIRONMENT.game_relationships\`" | tail -n 1)
GROUPS_COUNT=$(bq query --use_legacy_sql=false --format=csv "SELECT COUNT(*) FROM \`$PROJECT_ID.igdb_games_$ENVIRONMENT.game_groups\`" | tail -n 1)
MEMBERS_COUNT=$(bq query --use_legacy_sql=false --format=csv "SELECT COUNT(*) FROM \`$PROJECT_ID.igdb_games_$ENVIRONMENT.game_group_members\`" | tail -n 1)

echo "Antal rader i BigQuery-tabeller:"
echo "   games: $GAMES_COUNT"
echo "   game_relationships: $RELATIONSHIPS_COUNT"
echo "   game_groups: $GROUPS_COUNT"
echo "   game_group_members: $MEMBERS_COUNT"
echo ""

# Steg 4: Visa loggar från Cloud Functions
echo "4. Visar senaste loggar från Cloud Functions..."

echo "=== IGDB API Ingest-loggar ==="
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=igdb-api-ingest-$ENVIRONMENT" --limit=5 --format="table(timestamp,severity,textPayload)"
echo ""

echo "=== Data Cleaning Pipeline-loggar ==="
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=data-cleaning-pipeline-$ENVIRONMENT" --limit=5 --format="table(timestamp,severity,textPayload)"
echo ""

echo "=== ETL Processor-loggar ==="
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=etl-processor-$ENVIRONMENT" --limit=5 --format="table(timestamp,severity,textPayload)"
echo ""

echo "=== Test slutfört ==="
if [ "$GAMES_COUNT" -gt 0 ]; then
  echo "✅ ETL-pipelinen fungerar! Data har flödat genom hela pipelinen."
else
  echo "❓ Osäkert resultat. Kontrollera loggarna för mer information."
fi
