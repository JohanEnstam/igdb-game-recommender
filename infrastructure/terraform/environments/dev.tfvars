# Development environment configuration

project_id = "igdb-pipeline-v3"
environment = "dev"
region = "europe-west1"
zone = "europe-west1-b"

# BigQuery
bigquery_dataset_id = "igdb_games_dev"
bigquery_location = "EU"

# Storage
raw_data_bucket_name = "igdb-raw-data-dev"
model_artifacts_bucket_name = "igdb-model-artifacts-dev"
functions_source_bucket_name = "igdb-functions-source-dev"

# Pub/Sub
data_ingestion_topic_name = "igdb-data-ingestion-dev"
etl_processing_topic_name = "igdb-etl-processing-dev"
model_training_topic_name = "igdb-model-training-dev"

# Cloud SQL
db_instance_name = "igdb-postgres-dev"
db_name = "igdb_games_dev"
db_user = "igdb_app_dev"

# Cloud Run
api_service_name = "igdb-api-dev"

# Vertex AI
model_display_name = "igdb-recommendation-model-dev"

# Monitoring
alert_notification_email = "dev@example.com"
