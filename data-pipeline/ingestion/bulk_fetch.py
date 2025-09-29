#!/usr/bin/env python3
"""
IGDB Bulk Fetch Script

Detta skript hämtar alla spel från IGDB API och validerar antagandet om
att det tar cirka 15 minuter att hämta 350k spel med rate limiting på 4 req/s
och batch size på 500 spel per request.

Användning:
    python bulk_fetch.py [--output OUTPUT_DIR] [--limit LIMIT]

Exempel:
    python bulk_fetch.py --output ./data --limit 1000
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Ladda miljövariabler från .env-filen
load_dotenv()

# Lägg till parent-katalogen i sys.path för att kunna importera igdb_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.igdb_client import IGDBClient

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bulk_fetch.log")
    ]
)
logger = logging.getLogger(__name__)

# Fält att hämta från IGDB API
FIELDS = [
    "id",
    "name",
    "summary",
    "storyline",
    "first_release_date",
    "rating",
    "rating_count",
    "aggregated_rating",
    "aggregated_rating_count",
    "cover.url",
    "genres.id",
    "genres.name",
    "platforms.id",
    "platforms.name",
    "themes.id",
    "themes.name"
]

def parse_arguments():
    """Parsa kommandoradsargument"""
    parser = argparse.ArgumentParser(description="Hämta alla spel från IGDB API")
    parser.add_argument(
        "--output",
        type=str,
        default="./data",
        help="Katalog där data ska sparas (default: ./data)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max antal spel att hämta (default: alla)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Antal spel att hämta per request (default: 500)"
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=4.0,
        help="Requests per sekund (default: 4.0)"
    )
    return parser.parse_args()

def ensure_output_dir(output_dir: str) -> Path:
    """Skapa output-katalog om den inte finns"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path

def save_games(games: List[Dict[str, Any]], output_path: Path, batch_num: int) -> None:
    """Spara spel till JSON-fil"""
    filename = output_path / f"games_batch_{batch_num}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)
    logger.info(f"Sparade {len(games)} spel till {filename}")

def fetch_all_games(
    client: IGDBClient,
    output_dir: Path,
    limit: Optional[int] = None,
    batch_size: int = 500
) -> None:
    """Hämta alla spel från IGDB API"""
    start_time = time.time()
    total_games = 0
    batch_num = 0
    
    logger.info(f"Startar hämtning av spel från IGDB API (max: {limit or 'alla'})")
    
    # Hämta totalt antal spel för att kunna visa progress
    try:
        count_query = "fields id; limit 1; where version_parent = null;"
        count_result = client._make_request("games/count", count_query)
        total_count = count_result.get("count", 0)
        logger.info(f"Totalt antal spel i IGDB: {total_count}")
    except Exception as e:
        logger.warning(f"Kunde inte hämta totalt antal spel: {e}")
        total_count = 350000  # Uppskattning baserat på projektspecifikationen
    
    # Hämta alla spel med pagination
    try:
        # Filtrera bort versionerade spel (DLC, remasters, etc.)
        filters = "where version_parent = null;"
        
        # Starta timer för att mäta prestanda
        fetch_start_time = time.time()
        
        # Hämta alla spel
        all_games = client.get_all_games(FIELDS, filters, limit)
        
        # Beräkna total tid
        fetch_time = time.time() - fetch_start_time
        
        # Spara alla spel i batches om 10000 för att undvika för stora filer
        for i in range(0, len(all_games), 10000):
            batch = all_games[i:i+10000]
            save_games(batch, output_dir, batch_num)
            batch_num += 1
        
        total_games = len(all_games)
        
    except Exception as e:
        logger.error(f"Fel vid hämtning av spel: {e}")
        raise
    
    # Beräkna statistik
    end_time = time.time()
    total_time = end_time - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    
    # Spara statistik
    stats = {
        "total_games": total_games,
        "total_time_seconds": total_time,
        "games_per_second": total_games / total_time if total_time > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_dir / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Hämtning klar! Hämtade {total_games} spel på {minutes} minuter och {seconds} sekunder")
    logger.info(f"Genomsnittlig hastighet: {stats['games_per_second']:.2f} spel per sekund")

def main():
    """Huvudfunktion"""
    args = parse_arguments()
    
    # Skapa output-katalog
    output_dir = ensure_output_dir(args.output)
    
    # Hämta API-nycklar från miljövariabler
    client_id = os.environ.get("IGDB_CLIENT_ID")
    client_secret = os.environ.get("IGDB_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logger.error("IGDB_CLIENT_ID och IGDB_CLIENT_SECRET miljövariabler måste vara satta")
        sys.exit(1)
    
    # Skapa IGDB-klient
    client = IGDBClient(
        client_id=client_id,
        client_secret=client_secret,
        rate_limit=args.rate_limit,
        batch_size=args.batch_size
    )
    
    # Hämta alla spel
    fetch_all_games(client, output_dir, args.limit, args.batch_size)

if __name__ == "__main__":
    main()
