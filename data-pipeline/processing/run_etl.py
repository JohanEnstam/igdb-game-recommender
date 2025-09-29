#!/usr/bin/env python3
"""
Kör ETL-pipelinen för datarensning.

Detta skript kör ETL-pipelinen för att rensa IGDB-speldata.
"""

import os
import sys
import argparse
from etl_pipeline import DataCleaningPipeline

def main():
    """Huvudfunktion för att köra ETL-pipelinen."""
    parser = argparse.ArgumentParser(description="Rensa IGDB-speldata")
    parser.add_argument("--input", type=str, required=True, help="Katalog med rådata")
    parser.add_argument("--output", type=str, required=True, help="Katalog för rensad data")
    parser.add_argument("--log-level", type=str, default="INFO", help="Loggnivå")
    
    args = parser.parse_args()
    
    # Skapa och kör pipeline
    pipeline = DataCleaningPipeline(args.input, args.output)
    pipeline.run()

if __name__ == "__main__":
    main()
