#!/bin/bash
# Setup script för övervakning av ETL-pipelinen

set -e  # Exit vid fel

echo "=== ETL Pipeline Monitoring Setup ==="
echo "Sätter upp övervakning för ETL-pipelinen"
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

# Skapa Dashboard med gcloud CLI
echo "1. Skapar monitoring dashboard för ETL-pipelinen..."

# Skapa en temporär dashboard-konfigurationsfil
DASHBOARD_CONFIG=$(cat <<EOF
{
  "displayName": "IGDB ETL Pipeline Dashboard",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "Cloud Function Executions",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" resource.type=\"cloud_function\" resource.label.\"function_name\"=~\".*-$ENVIRONMENT\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE",
                    "crossSeriesReducer": "REDUCE_SUM",
                    "groupByFields": [
                      "resource.label.\"function_name\""
                    ]
                  }
                },
                "unitOverride": "1"
              },
              "plotType": "LINE",
              "legendTemplate": "{{resource.label.function_name}}"
            }
          ],
          "yAxis": {
            "label": "Executions/s",
            "scale": "LINEAR"
          }
        }
      },
      {
        "title": "Cloud Function Errors",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" resource.type=\"cloud_function\" resource.label.\"function_name\"=~\".*-$ENVIRONMENT\" metric.label.\"status\"=\"error\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE",
                    "crossSeriesReducer": "REDUCE_SUM",
                    "groupByFields": [
                      "resource.label.\"function_name\""
                    ]
                  }
                },
                "unitOverride": "1"
              },
              "plotType": "LINE",
              "legendTemplate": "{{resource.label.function_name}}"
            }
          ],
          "yAxis": {
            "label": "Errors/s",
            "scale": "LINEAR"
          }
        }
      },
      {
        "title": "Cloud Function Execution Times",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"cloudfunctions.googleapis.com/function/execution_times\" resource.type=\"cloud_function\" resource.label.\"function_name\"=~\".*-$ENVIRONMENT\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_PERCENTILE_99",
                    "crossSeriesReducer": "REDUCE_MEAN",
                    "groupByFields": [
                      "resource.label.\"function_name\""
                    ]
                  }
                },
                "unitOverride": "ms"
              },
              "plotType": "LINE",
              "legendTemplate": "{{resource.label.function_name}}"
            }
          ],
          "yAxis": {
            "label": "99th percentile latency (ms)",
            "scale": "LINEAR"
          }
        }
      },
      {
        "title": "Cloud Function Memory Usage",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"cloudfunctions.googleapis.com/function/user_memory_bytes\" resource.type=\"cloud_function\" resource.label.\"function_name\"=~\".*-$ENVIRONMENT\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_PERCENTILE_95",
                    "crossSeriesReducer": "REDUCE_MEAN",
                    "groupByFields": [
                      "resource.label.\"function_name\""
                    ]
                  }
                },
                "unitOverride": "By"
              },
              "plotType": "LINE",
              "legendTemplate": "{{resource.label.function_name}}"
            }
          ],
          "yAxis": {
            "label": "Memory usage (bytes)",
            "scale": "LINEAR"
          }
        }
      }
    ]
  }
}
EOF
)

# Spara konfigurationen till en temporär fil
TEMP_FILE=$(mktemp)
echo "$DASHBOARD_CONFIG" > "$TEMP_FILE"

# Skapa dashboard med gcloud CLI
echo "Skapar dashboard med gcloud CLI..."
gcloud monitoring dashboards create --config-from-file="$TEMP_FILE"

# Rensa temporär fil
rm "$TEMP_FILE"

echo "✅ Dashboard skapad!"
echo ""

# Skapa aviseringar
echo "2. Skapar aviseringspolicyer..."

# Avisering för Cloud Function-fel
echo "Skapar avisering för Cloud Function-fel..."
gcloud alpha monitoring policies create \
  --notification-channels="projects/$PROJECT_ID/notificationChannels/NOTIFICATION_CHANNEL_ID" \
  --display-name="IGDB ETL Function Errors" \
  --condition-filter="metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" resource.type=\"cloud_function\" metric.label.\"status\"=\"error\" resource.label.\"function_name\"=~\".*-$ENVIRONMENT\"" \
  --condition-threshold-value=1 \
  --condition-threshold-filter="count_true() > 0" \
  --condition-aggregations-alignment-period=60s \
  --condition-aggregations-per-series-aligner=ALIGN_RATE \
  --condition-aggregations-cross-series-reducer=REDUCE_SUM \
  --condition-trigger-count=1 \
  --condition-duration=0s \
  --if-policy-exists=update

# Avisering för lång exekveringstid
echo "Skapar avisering för lång exekveringstid..."
gcloud alpha monitoring policies create \
  --notification-channels="projects/$PROJECT_ID/notificationChannels/NOTIFICATION_CHANNEL_ID" \
  --display-name="IGDB ETL Long Execution Time" \
  --condition-filter="metric.type=\"cloudfunctions.googleapis.com/function/execution_times\" resource.type=\"cloud_function\" resource.label.\"function_name\"=~\".*-$ENVIRONMENT\"" \
  --condition-threshold-value=30000 \
  --condition-threshold-comparison=COMPARISON_GT \
  --condition-aggregations-alignment-period=60s \
  --condition-aggregations-per-series-aligner=ALIGN_PERCENTILE_99 \
  --condition-trigger-count=1 \
  --condition-duration=0s \
  --if-policy-exists=update

echo "✅ Aviseringspolicyer skapade!"
echo ""

echo "3. Skapar Cloud Scheduler-jobb för regelbunden datainsamling..."

# Skapa Cloud Scheduler-jobb för att köra IGDB API Ingest varje vecka
gcloud scheduler jobs create http igdb-data-fetch-$ENVIRONMENT \
  --schedule="0 0 * * 0" \
  --uri="https://$REGION-$PROJECT_ID.cloudfunctions.net/igdb-api-ingest-$ENVIRONMENT" \
  --http-method=POST \
  --oidc-service-account-email="cf-igdb-ingest@$PROJECT_ID.iam.gserviceaccount.com" \
  --message-body='{"max_games": null}'

echo "✅ Cloud Scheduler-jobb skapat!"
echo ""

echo "=== Övervakning konfigurerad ==="
echo "Du kan nu se ETL-pipelinen i Cloud Console:"
echo "- Dashboard: https://console.cloud.google.com/monitoring/dashboards"
echo "- Aviseringar: https://console.cloud.google.com/monitoring/alerting"
echo "- Cloud Scheduler: https://console.cloud.google.com/cloudscheduler"
echo ""
echo "OBS: Du behöver uppdatera notification_channels i skriptet med dina egna kanalID:n"
echo "för att aviseringarna ska skickas till rätt mottagare."
