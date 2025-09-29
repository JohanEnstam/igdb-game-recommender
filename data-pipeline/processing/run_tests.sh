#!/bin/bash
# Skript för att köra alla tester för datarensningsmodulen

# Gå till katalogen för skriptet
cd "$(dirname "$0")"

# Kontrollera om virtuell miljö är aktiverad
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "VARNING: Virtuell miljö är inte aktiverad!"
    echo "Aktivera virtuell miljö med: source ../../activate.sh"
    echo "Avbryter..."
    exit 1
fi

# Kör alla tester
echo "Kör tester för datarensningsmodulen..."
# Gå till projektets rotkatalog
cd ../..
# Lägg till projektets rotkatalog i PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "PYTHONPATH: $PYTHONPATH"
# Kör testerna
python -m unittest discover -s data-pipeline/processing/tests

# Kontrollera om testerna lyckades
if [ $? -eq 0 ]; then
    echo "Alla tester lyckades!"
    exit 0
else
    echo "Tester misslyckades!"
    exit 1
fi
