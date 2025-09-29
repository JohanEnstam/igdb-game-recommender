#!/usr/bin/env python3
"""
Analysera resultaten från datarensningen.

Detta skript analyserar resultaten från datarensningspipelinen och genererar statistik.
"""

import os
import json
import argparse
from collections import Counter, defaultdict
from pathlib import Path


def load_json_file(file_path):
    """Ladda data från en JSON-fil."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_games(games_data):
    """Analysera speldata."""
    total_games = len(games_data)
    games_with_canonical_name = sum(1 for game in games_data if game.get('canonical_name'))
    games_with_summary = sum(1 for game in games_data if game.get('summary'))
    games_with_cover = sum(1 for game in games_data if game.get('cover_url'))
    games_with_release_date = sum(1 for game in games_data if game.get('release_date'))
    games_with_rating = sum(1 for game in games_data if game.get('rating'))
    games_with_complete_data = sum(1 for game in games_data if game.get('has_complete_data'))
    
    quality_scores = [game.get('quality_score', 0) for game in games_data]
    avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    print("\n=== SPELSTATISTIK ===")
    print(f"Totalt antal spel: {total_games}")
    print(f"Spel med kanoniskt namn: {games_with_canonical_name} ({games_with_canonical_name/total_games*100:.1f}%)")
    print(f"Spel med sammanfattning: {games_with_summary} ({games_with_summary/total_games*100:.1f}%)")
    print(f"Spel med omslagsbild: {games_with_cover} ({games_with_cover/total_games*100:.1f}%)")
    print(f"Spel med utgivningsdatum: {games_with_release_date} ({games_with_release_date/total_games*100:.1f}%)")
    print(f"Spel med betyg: {games_with_rating} ({games_with_rating/total_games*100:.1f}%)")
    print(f"Spel med komplett data: {games_with_complete_data} ({games_with_complete_data/total_games*100:.1f}%)")
    print(f"Genomsnittlig kvalitetspoäng: {avg_quality_score:.1f}")


def analyze_relationships(relationships_data):
    """Analysera spelrelationer."""
    total_relationships = len(relationships_data)
    relationship_types = Counter(rel['relationship_type'] for rel in relationships_data)
    
    print("\n=== RELATIONSSTATISTIK ===")
    print(f"Totalt antal relationer: {total_relationships}")
    for rel_type, count in relationship_types.items():
        print(f"Relationstyp '{rel_type}': {count} ({count/total_relationships*100:.1f}%)")


def analyze_groups(groups_data):
    """Analysera spelgrupper."""
    total_groups = len(groups_data)
    group_types = Counter(group['group_type'] for group in groups_data)
    
    # Beräkna genomsnittlig gruppstorlek
    avg_group_size = sum(group.get('game_count', 0) for group in groups_data) / total_groups if total_groups else 0
    
    print("\n=== GRUPPSTATISTIK ===")
    print(f"Totalt antal grupper: {total_groups}")
    for group_type, count in group_types.items():
        print(f"Grupptype '{group_type}': {count} ({count/total_groups*100:.1f}%)")
    print(f"Genomsnittlig gruppstorlek: {avg_group_size:.1f} spel")


def analyze_group_members(members_data):
    """Analysera gruppmedlemskap."""
    total_members = len(members_data)
    primary_members = sum(1 for member in members_data if member.get('is_primary'))
    
    # Gruppera medlemskap efter grupp-ID
    group_sizes = defaultdict(int)
    for member in members_data:
        group_sizes[member.get('group_id')] += 1
    
    # Beräkna statistik om gruppstorlekar
    sizes = list(group_sizes.values())
    avg_members_per_group = sum(sizes) / len(sizes) if sizes else 0
    max_group_size = max(sizes) if sizes else 0
    
    print("\n=== MEDLEMSKAPSSTATISTIK ===")
    print(f"Totalt antal gruppmedlemskap: {total_members}")
    print(f"Primära medlemmar: {primary_members} ({primary_members/total_members*100:.1f}%)")
    print(f"Genomsnittligt antal medlemmar per grupp: {avg_members_per_group:.1f}")
    print(f"Största gruppstorlek: {max_group_size} spel")


def main():
    """Huvudfunktion."""
    parser = argparse.ArgumentParser(description="Analysera resultat från datarensningen")
    parser.add_argument("--input", type=str, required=True, help="Katalog med rensad data")
    
    args = parser.parse_args()
    input_dir = Path(args.input)
    
    # Kontrollera att katalogen finns
    if not input_dir.exists():
        print(f"Katalogen {input_dir} finns inte")
        return
    
    # Ladda data från filer
    games_file = input_dir / "games.json"
    relationships_file = input_dir / "game_relationships.json"
    groups_file = input_dir / "game_groups.json"
    members_file = input_dir / "game_group_members.json"
    
    if games_file.exists():
        games_data = load_json_file(games_file)
        analyze_games(games_data)
    
    if relationships_file.exists():
        relationships_data = load_json_file(relationships_file)
        analyze_relationships(relationships_data)
    
    if groups_file.exists():
        groups_data = load_json_file(groups_file)
        analyze_groups(groups_data)
    
    if members_file.exists():
        members_data = load_json_file(members_file)
        analyze_group_members(members_data)


if __name__ == "__main__":
    main()
