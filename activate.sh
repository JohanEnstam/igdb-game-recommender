#!/bin/bash
# Aktivera virtuell miljö för IGDB Game Recommendation System
source "/Users/johanenstam/Sync/Utveckling/IGDB-V3/igdb-game-recommender/.venv/bin/activate"
export PYTHONPATH="/Users/johanenstam/Sync/Utveckling/IGDB-V3/igdb-game-recommender:${PYTHONPATH:-}"
echo "Virtual environment activated. Run 'deactivate' to exit."