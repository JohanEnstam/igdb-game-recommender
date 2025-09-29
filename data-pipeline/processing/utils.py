"""
Hjälpfunktioner för datarensningsprocessen.

Denna modul innehåller diverse hjälpfunktioner som används i datarensningsprocessen.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import datetime


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Skapa och konfigurera en logger.
    
    Args:
        name: Namnet på loggern
        level: Loggnivå
        
    Returns:
        En konfigurerad logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Skapa en handler som skriver till stdout
    handler = logging.StreamHandler()
    handler.setLevel(level)
    
    # Skapa en formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Lägg till handler till loggern
    logger.addHandler(handler)
    
    return logger


def load_games_from_file(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Ladda spel från en JSON-fil.
    
    Args:
        file_path: Sökväg till JSON-filen
        
    Returns:
        Lista med spel
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_games_from_directory(directory: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Ladda spel från alla JSON-filer i en katalog.
    
    Args:
        directory: Sökväg till katalogen
        
    Returns:
        Lista med spel
    """
    directory_path = Path(directory)
    games = []
    
    # Hitta alla JSON-filer i katalogen
    json_files = sorted(directory_path.glob('*.json'))
    
    for file_path in json_files:
        games.extend(load_games_from_file(file_path))
    
    return games


def save_to_json(data: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """
    Spara data till en JSON-fil.
    
    Args:
        data: Data att spara
        file_path: Sökväg till filen
        indent: Indenteringsnivå för JSON
    """
    # Skapa katalogen om den inte finns
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Serialisera datetime-objekt
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            return super().default(obj)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent, cls=DateTimeEncoder)


def group_by_key(items: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict[str, Any]]]:
    """
    Gruppera en lista med dictionaries efter en nyckel.
    
    Args:
        items: Lista med dictionaries
        key: Nyckeln att gruppera efter
        
    Returns:
        Dictionary med grupper
    """
    result = {}
    
    for item in items:
        if key in item:
            key_value = item[key]
            if key_value not in result:
                result[key_value] = []
            result[key_value].append(item)
    
    return result
