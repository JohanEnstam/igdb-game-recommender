#!/bin/bash
# Script to deploy data cleaning modules to Cloud Storage

# Usage: ./deploy_modules.sh [environment]
# Example: ./deploy_modules.sh dev

# Default to dev environment if not specified
ENVIRONMENT=${1:-dev}

# Set bucket name based on environment
BUCKET_NAME="igdb-processed-data-${ENVIRONMENT}"

# Path to processing modules
MODULES_DIR="../../processing"

# Create a temporary directory for the modules
TMP_DIR=$(mktemp -d)

echo "Copying modules to temporary directory..."
cp ${MODULES_DIR}/name_processor.py ${TMP_DIR}/
cp ${MODULES_DIR}/game_grouper.py ${TMP_DIR}/
cp ${MODULES_DIR}/quality_scorer.py ${TMP_DIR}/
cp ${MODULES_DIR}/data_model.py ${TMP_DIR}/
cp ${MODULES_DIR}/utils.py ${TMP_DIR}/
cp ${MODULES_DIR}/etl_pipeline.py ${TMP_DIR}/

echo "Uploading modules to gs://${BUCKET_NAME}/modules/"
gsutil -m cp ${TMP_DIR}/*.py gs://${BUCKET_NAME}/modules/

echo "Cleaning up temporary directory..."
rm -rf ${TMP_DIR}

echo "Modules deployed successfully to gs://${BUCKET_NAME}/modules/"
