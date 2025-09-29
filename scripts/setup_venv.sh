#!/bin/bash

# IGDB Game Recommendation System - Virtual Environment Setup Script
# Detta skript skapar en virtuell Python-miljö och installerar nödvändiga beroenden

set -e  # Avbryt vid fel

# Definiera färger för output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Definiera sökvägar
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
DATA_PIPELINE_DIR="${PROJECT_ROOT}/data-pipeline"
ML_PIPELINE_DIR="${PROJECT_ROOT}/ml-pipeline"
WEB_APP_DIR="${PROJECT_ROOT}/web-app/backend"

echo -e "${GREEN}Setting up virtual environment for IGDB Game Recommendation System${NC}"
echo -e "${YELLOW}Project root: ${PROJECT_ROOT}${NC}"

# Kontrollera om Python 3 finns installerat
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.9+ and try again.${NC}"
    exit 1
fi

# Kontrollera Python-version
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo -e "${YELLOW}Detected Python version: ${PYTHON_VERSION}${NC}"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo -e "${RED}Python 3.9+ is required. You have ${PYTHON_VERSION}.${NC}"
    echo -e "${YELLOW}Please consider using pyenv to manage Python versions.${NC}"
    exit 1
fi

# Kontrollera om venv-modulen finns
python3 -c "import venv" 2>/dev/null || {
    echo -e "${RED}Python venv module is not available. Please install it and try again.${NC}"
    echo -e "${YELLOW}On macOS: brew install python3-venv${NC}"
    exit 1
}

# Skapa virtuell miljö om den inte redan finns
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${GREEN}Creating virtual environment in ${VENV_DIR}...${NC}"
    python3 -m venv "$VENV_DIR"
else
    echo -e "${YELLOW}Virtual environment already exists in ${VENV_DIR}${NC}"
fi

# Aktivera virtuell miljö
echo -e "${GREEN}Activating virtual environment...${NC}"
source "${VENV_DIR}/bin/activate"

# Uppgradera pip
echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip

# Installera beroenden för data-pipeline
if [ -f "${DATA_PIPELINE_DIR}/requirements.txt" ]; then
    echo -e "${GREEN}Installing data-pipeline dependencies...${NC}"
    pip install -r "${DATA_PIPELINE_DIR}/requirements.txt"
fi

# Installera beroenden för ml-pipeline om det finns
if [ -f "${ML_PIPELINE_DIR}/requirements.txt" ]; then
    echo -e "${GREEN}Installing ml-pipeline dependencies...${NC}"
    pip install -r "${ML_PIPELINE_DIR}/requirements.txt"
fi

# Installera beroenden för web-app/backend om det finns
if [ -f "${WEB_APP_DIR}/requirements.txt" ]; then
    echo -e "${GREEN}Installing web-app backend dependencies...${NC}"
    pip install -r "${WEB_APP_DIR}/requirements.txt"
fi

# Installera utvecklingsverktyg
echo -e "${GREEN}Installing development tools...${NC}"
pip install black flake8 pytest pytest-cov ipython

# Skapa .env-fil för IGDB API om den inte finns
IGDB_ENV_FILE="${DATA_PIPELINE_DIR}/ingestion/.env"
if [ ! -f "$IGDB_ENV_FILE" ]; then
    echo -e "${GREEN}Creating .env file for IGDB API...${NC}"
    cat > "$IGDB_ENV_FILE" << EOF
# IGDB API Credentials
IGDB_CLIENT_ID=your_client_id_here
IGDB_CLIENT_SECRET=your_client_secret_here
EOF
    echo -e "${YELLOW}Please edit ${IGDB_ENV_FILE} and add your IGDB API credentials.${NC}"
fi

# Skapa aktiveringsscript
ACTIVATE_SCRIPT="${PROJECT_ROOT}/activate.sh"
cat > "$ACTIVATE_SCRIPT" << EOF
#!/bin/bash
# Aktivera virtuell miljö för IGDB Game Recommendation System
source "${VENV_DIR}/bin/activate"
export PYTHONPATH="${PROJECT_ROOT}:\${PYTHONPATH}"
echo "Virtual environment activated. Run 'deactivate' to exit."
EOF
chmod +x "$ACTIVATE_SCRIPT"

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}To activate the virtual environment, run:${NC}"
echo -e "${GREEN}source ${ACTIVATE_SCRIPT}${NC}"
echo -e "${YELLOW}or${NC}"
echo -e "${GREEN}source .venv/bin/activate${NC}"

# Information om hur man kör skripten
echo -e "\n${YELLOW}To run the IGDB data fetching script:${NC}"
echo -e "${GREEN}source ${ACTIVATE_SCRIPT}${NC}"
echo -e "${GREEN}cd ${DATA_PIPELINE_DIR}/ingestion${NC}"
echo -e "${GREEN}python bulk_fetch.py --output ./data --limit 100${NC}"

echo -e "\n${YELLOW}Happy coding!${NC}"
