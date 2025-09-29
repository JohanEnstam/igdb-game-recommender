#!/bin/bash
# Skript för att köra datarensningspipelinen

# Gå till projektets rotkatalog
cd "$(dirname "$0")/../.."

# Kontrollera om virtuell miljö är aktiverad
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "VARNING: Virtuell miljö är inte aktiverad!"
    echo "Aktiverar virtuell miljö..."
    
    if [ -f "./activate.sh" ]; then
        source ./activate.sh
    else
        echo "Kunde inte hitta activate.sh. Avbryter..."
        exit 1
    fi
fi

# Kontrollera att virtuell miljö nu är aktiverad
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Kunde inte aktivera virtuell miljö. Avbryter..."
    exit 1
fi

echo "Virtuell miljö aktiverad: $VIRTUAL_ENV"

# Kontrollera om input och output angivits
if [ "$#" -lt 2 ]; then
    echo "Användning: $0 INPUT_DIR OUTPUT_DIR [LOG_LEVEL]"
    echo "Exempel: $0 ./data-pipeline/ingestion/data ./data-pipeline/processing/cleaned_data"
    exit 1
fi

INPUT_DIR=$1
OUTPUT_DIR=$2
LOG_LEVEL=${3:-INFO}

# Kontrollera att input-katalogen finns
if [ ! -d "$INPUT_DIR" ]; then
    echo "Input-katalog finns inte: $INPUT_DIR"
    exit 1
fi

# Skapa output-katalog om den inte finns
mkdir -p "$OUTPUT_DIR"

echo "Kör datarensningspipeline..."
echo "Input: $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo "Log level: $LOG_LEVEL"

# Kör pipelinen
python -m data_pipeline.processing.etl_pipeline --input "$INPUT_DIR" --output "$OUTPUT_DIR" --log-level "$LOG_LEVEL"

# Kontrollera om pipelinen lyckades
if [ $? -eq 0 ]; then
    echo "Datarensningspipeline slutförd!"
    exit 0
else
    echo "Datarensningspipeline misslyckades!"
    exit 1
fi
