#!/bin/bash

# IGDB API Test Script
# Detta skript kör ett test för att hämta ett begränsat antal spel från IGDB API

set -e  # Avbryt vid fel

# Definiera färger för output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Definiera sökvägar
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
DATA_DIR="${SCRIPT_DIR}/data"
ANALYSIS_DIR="${SCRIPT_DIR}/analysis"

# Kontrollera om virtuell miljö finns
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Virtual environment not found. Please run setup_venv.sh first.${NC}"
    echo -e "${YELLOW}Run: ${PROJECT_ROOT}/scripts/setup_venv.sh${NC}"
    exit 1
fi

# Aktivera virtuell miljö
echo -e "${GREEN}Activating virtual environment...${NC}"
source "${VENV_DIR}/bin/activate"

# Sätt PYTHONPATH för att hitta moduler
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

# Kontrollera om .env-fil finns
ENV_FILE="${SCRIPT_DIR}/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}.env file not found. Creating template...${NC}"
    cat > "$ENV_FILE" << EOF
# IGDB API Credentials
IGDB_CLIENT_ID=your_client_id_here
IGDB_CLIENT_SECRET=your_client_secret_here
EOF
    echo -e "${YELLOW}Please edit ${ENV_FILE} and add your IGDB API credentials.${NC}"
    exit 1
fi

# Kontrollera om API-nycklar är konfigurerade
if grep -q "your_client_id_here" "$ENV_FILE" || grep -q "your_client_secret_here" "$ENV_FILE"; then
    echo -e "${RED}IGDB API credentials not configured.${NC}"
    echo -e "${YELLOW}Please edit ${ENV_FILE} and add your IGDB API credentials.${NC}"
    exit 1
fi

# Skapa kataloger om de inte finns
mkdir -p "$DATA_DIR"
mkdir -p "$ANALYSIS_DIR"

# Installera python-dotenv om det inte redan är installerat
pip install python-dotenv

# Kör test för att hämta ett begränsat antal spel
echo -e "${GREEN}Running test to fetch a limited number of games from IGDB API...${NC}"
python "${SCRIPT_DIR}/bulk_fetch.py" --output "$DATA_DIR" --limit 100

# Om hämtningen lyckades, analysera data
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Data fetched successfully. Analyzing data...${NC}"
    python "${SCRIPT_DIR}/analyze_data.py" --input "$DATA_DIR" --output "$ANALYSIS_DIR"
    
    echo -e "${GREEN}Test completed successfully!${NC}"
    echo -e "${YELLOW}Data saved to: ${DATA_DIR}${NC}"
    echo -e "${YELLOW}Analysis saved to: ${ANALYSIS_DIR}${NC}"
    
    echo -e "\n${GREEN}To fetch all games, run:${NC}"
    echo -e "${YELLOW}python ${SCRIPT_DIR}/bulk_fetch.py --output ${DATA_DIR}${NC}"
else
    echo -e "${RED}Failed to fetch data from IGDB API.${NC}"
    exit 1
fi
