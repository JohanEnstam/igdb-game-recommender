#!/bin/bash
# Script to package and deploy all Cloud Functions

# Usage: ./deploy_all.sh [environment]
# Example: ./deploy_all.sh dev

# Default to dev environment if not specified
ENVIRONMENT=${1:-dev}

# Set output directory for zip files
OUTPUT_DIR="../../"

echo "Packaging Cloud Functions for deployment..."

# Package data cleaning pipeline function
echo "Packaging data cleaning pipeline function..."
cd data_cleaning_pipeline
chmod +x package.sh
./package.sh ${OUTPUT_DIR}
cd ..

# Package IGDB ingest function
echo "Packaging IGDB ingest function..."
cd igdb_ingest
chmod +x package.sh
./package.sh ${OUTPUT_DIR}
cd ..

# Package ETL processor function
echo "Packaging ETL processor function..."
cd etl_processor
chmod +x package.sh
./package.sh ${OUTPUT_DIR}
cd ..

echo "All Cloud Functions packaged successfully."
echo ""
echo "To deploy the Cloud Functions using Terraform, run:"
echo "cd ../../infrastructure/terraform"
echo "terraform init"
echo "terraform apply -var-file=environments/${ENVIRONMENT}.tfvars"
