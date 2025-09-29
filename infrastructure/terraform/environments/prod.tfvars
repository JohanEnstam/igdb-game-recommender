# Production environment configuration

project_id = "igdb-pipeline-v3"
environment = "prod"
region = "europe-west1"
zone = "europe-west1-b"

# BigQuery
bigquery_dataset_id = "igdb_games"
bigquery_location = "EU"

# Storage
raw_data_bucket_name = "igdb-raw-data"
model_artifacts_bucket_name = "igdb-model-artifacts"
functions_source_bucket_name = "igdb-functions-source"

# Pub/Sub
data_ingestion_topic_name = "igdb-data-ingestion"
etl_processing_topic_name = "igdb-etl-processing"
model_training_topic_name = "igdb-model-training"

# Cloud SQL
db_instance_name = "igdb-postgres"
db_name = "igdb_games"
db_user = "igdb_app"

# Cloud Run
api_service_name = "igdb-api"

# Vertex AI
model_display_name = "igdb-recommendation-model"

# Monitoring
alert_notification_email = "alerts@example.com"
