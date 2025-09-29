#!/bin/bash
# Ett enkelt skript för att köra tester för datarensningsmodulen

# Kontrollera om virtuell miljö är aktiverad
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "VARNING: Virtuell miljö är inte aktiverad!"
    echo "Aktivera virtuell miljö med: source ../../activate.sh"
    echo "Avbryter..."
    exit 1
fi

# Gå till testkatalogen
cd "$(dirname "$0")/tests"

# Kör testet för name_processor direkt
echo "Kör test_name_processor.py..."
python -m unittest test_name_processor.py

# Kontrollera om testet lyckades
if [ $? -eq 0 ]; then
    echo "Test name_processor lyckades!"
else
    echo "Test name_processor misslyckades!"
    exit 1
fi

echo "Alla tester slutförda!"
