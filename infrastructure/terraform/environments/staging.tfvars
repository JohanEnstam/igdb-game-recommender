# Staging environment configuration

project_id = "igdb-recommender-staging"
environment = "staging"
region = "europe-west1"
zone = "europe-west1-b"

# BigQuery
bigquery_dataset_id = "igdb_games_staging"
bigquery_location = "EU"

# Storage
raw_data_bucket_name = "igdb-raw-data-staging"
model_artifacts_bucket_name = "igdb-model-artifacts-staging"
functions_source_bucket_name = "igdb-functions-source-staging"

# Pub/Sub
data_ingestion_topic_name = "igdb-data-ingestion-staging"
etl_processing_topic_name = "igdb-etl-processing-staging"
model_training_topic_name = "igdb-model-training-staging"

# Cloud SQL
db_instance_name = "igdb-postgres-staging"
db_name = "igdb_games_staging"
db_user = "igdb_app_staging"

# Cloud Run
api_service_name = "igdb-api-staging"

# Vertex AI
model_display_name = "igdb-recommendation-model-staging"

# Monitoring
alert_notification_email = "staging@example.com"
