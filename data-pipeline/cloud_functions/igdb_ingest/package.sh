#!/bin/bash
# Script to package the IGDB ingest Cloud Function for deployment

# Usage: ./package.sh [output_dir]
# Example: ./package.sh ../../..

# Default output directory if not specified
OUTPUT_DIR=${1:-../..}

# Create a temporary directory
TMP_DIR=$(mktemp -d)

# Copy function code and requirements
cp main.py ${TMP_DIR}/
cp requirements.txt ${TMP_DIR}/

# Create the zip file
cd ${TMP_DIR}
zip -r igdb_ingest.zip main.py requirements.txt
cd -

# Move the zip file to the output directory
mkdir -p ${OUTPUT_DIR}
mv ${TMP_DIR}/igdb_ingest.zip ${OUTPUT_DIR}/

# Clean up
rm -rf ${TMP_DIR}

echo "Cloud Function packaged to ${OUTPUT_DIR}/igdb_ingest.zip"
