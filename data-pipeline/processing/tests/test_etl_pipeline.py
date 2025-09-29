"""
Tester för etl_pipeline-modulen.
"""

import unittest
import os
import shutil
import tempfile
import json
from pathlib import Path
from data_pipeline.processing.etl_pipeline import DataCleaningPipeline


class TestETLPipeline(unittest.TestCase):
    """Testfall för etl_pipeline-modulen."""
    
    def setUp(self):
        """Förbered testdata och temporära kataloger."""
        # Skapa temporära kataloger
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.temp_dir, "input")
        self.output_dir = os.path.join(self.temp_dir, "output")
        
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Skapa testdata
        self.test_games = [
            # Exakta dubbletter
            {"id": 1, "name": "Super Mario Bros."},
            {"id": 2, "name": "Super Mario Bros."},
            
            # Versioner av samma spel
            {"id": 3, "name": "The Witcher 3: Wild Hunt", "summary": "RPG game", "cover": {"url": "//test.jpg"}},
            {"id": 4, "name": "The Witcher 3: Wild Hunt - Complete Edition", "summary": "RPG game with DLC", "cover": {"url": "//test2.jpg"}},
            {"id": 5, "name": "The Witcher 3: Wild Hunt - Game of the Year Edition", "summary": "RPG game GOTY", "cover": {"url": "//test3.jpg"}},
            
            # Spel i samma serie
            {"id": 6, "name": "Mass Effect", "first_release_date": 1164931200},  # 2006-12-01
            {"id": 7, "name": "Mass Effect 2", "first_release_date": 1264464000},  # 2010-01-26
            {"id": 8, "name": "Mass Effect 3", "first_release_date": 1331078400},  # 2012-03-07
            
            # Oberoende spel
            {"id": 9, "name": "Minecraft", "summary": "Block game", "rating": 90.0, "cover": {"url": "//test4.jpg"}, "first_release_date": 1321056000},
            {"id": 10, "name": "Tetris", "summary": "Puzzle game", "rating": 95.0, "cover": {"url": "//test5.jpg"}, "first_release_date": 591494400}
        ]
        
        # Spara testdata till fil
        with open(os.path.join(self.input_dir, "games_batch_0.json"), "w", encoding="utf-8") as f:
            json.dump(self.test_games, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """Rensa upp temporära kataloger."""
        shutil.rmtree(self.temp_dir)
    
    def test_extract(self):
        """Testa extract-metoden."""
        pipeline = DataCleaningPipeline(self.input_dir, self.output_dir)
        pipeline.extract()
        
        # Kontrollera att rätt antal spel laddats
        self.assertEqual(len(pipeline.raw_games), len(self.test_games))
    
    def test_transform(self):
        """Testa transform-metoden."""
        pipeline = DataCleaningPipeline(self.input_dir, self.output_dir)
        pipeline.extract()
        pipeline.transform()
        
        # Kontrollera att transformeringen genererat data
        self.assertTrue(len(pipeline.cleaned_games) > 0)
        self.assertTrue(len(pipeline.game_relationships) > 0)
        self.assertTrue(len(pipeline.game_groups) > 0)
        self.assertTrue(len(pipeline.group_members) > 0)
    
    def test_load(self):
        """Testa load-metoden."""
        pipeline = DataCleaningPipeline(self.input_dir, self.output_dir)
        pipeline.extract()
        pipeline.transform()
        pipeline.load()
        
        # Kontrollera att filer har skapats
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "games.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "game_relationships.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "game_groups.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "game_group_members.json")))
        
        # Kontrollera att filerna innehåller data
        with open(os.path.join(self.output_dir, "games.json"), "r", encoding="utf-8") as f:
            games_data = json.load(f)
            self.assertTrue(len(games_data) > 0)
        
        with open(os.path.join(self.output_dir, "game_relationships.json"), "r", encoding="utf-8") as f:
            relationships_data = json.load(f)
            self.assertTrue(len(relationships_data) > 0)
    
    def test_run(self):
        """Testa run-metoden."""
        pipeline = DataCleaningPipeline(self.input_dir, self.output_dir)
        pipeline.run()
        
        # Kontrollera att filer har skapats
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "games.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "game_relationships.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "game_groups.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "game_group_members.json")))


if __name__ == "__main__":
    unittest.main()
