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
processed_data_bucket_name = "igdb-processed-data-dev"
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

# IGDB API
# These should be set via environment variables or a secure method
igdb_client_id = "c6avswhxkd0m3k4zfgz121qzoelh0x"
igdb_client_secret = "1a72hejzf1x9jxbx3gmfti999khvln"

# Cloud Functions source code paths
data_cleaning_function_source_zip = "/Users/johanenstam/Sync/Utveckling/IGDB-V3/igdb-game-recommender/data-pipeline/data_cleaning_pipeline.zip"
igdb_ingest_function_source_zip = "/Users/johanenstam/Sync/Utveckling/IGDB-V3/igdb-game-recommender/data-pipeline/igdb_ingest.zip"
etl_processor_function_source_zip = "/Users/johanenstam/Sync/Utveckling/IGDB-V3/igdb-game-recommender/data-pipeline/etl_processor.zip"