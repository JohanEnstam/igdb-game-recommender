"""
Tester för game_grouper-modulen.
"""

import unittest
from data_pipeline.processing.game_grouper import GameGrouper


class TestGameGrouper(unittest.TestCase):
    """Testfall för game_grouper-modulen."""
    
    def setUp(self):
        """Förbered testdata."""
        # Skapa testdata
        self.test_games = [
            # Exakta dubbletter
            {"id": "1", "name": "Super Mario Bros."},
            {"id": "2", "name": "Super Mario Bros."},
            
            # Versioner av samma spel
            {"id": "3", "name": "The Witcher 3: Wild Hunt"},
            {"id": "4", "name": "The Witcher 3: Wild Hunt - Complete Edition"},
            {"id": "5", "name": "The Witcher 3: Wild Hunt - Game of the Year Edition"},
            
            # Spel i samma serie
            {"id": "6", "name": "Mass Effect"},
            {"id": "7", "name": "Mass Effect 2"},
            {"id": "8", "name": "Mass Effect 3"},
            {"id": "9", "name": "Mass Effect: Andromeda"},
            
            # Spel med utgivningsdatum
            {"id": "10", "name": "FIFA 20", "first_release_date": 1569456000},  # 2019-09-26
            {"id": "11", "name": "FIFA 21", "first_release_date": 1601596800},  # 2020-10-02
            {"id": "12", "name": "FIFA 22", "first_release_date": 1633046400},  # 2021-10-01
            
            # Oberoende spel
            {"id": "13", "name": "Minecraft"},
            {"id": "14", "name": "Tetris"}
        ]
        
        # Skapa en instans av GameGrouper
        self.grouper = GameGrouper()
        
        # Bearbeta testdata
        self.grouper.process_games(self.test_games)
    
    def test_exact_duplicates(self):
        """Testa identifiering av exakta dubbletter."""
        # Kontrollera att Super Mario Bros. identifieras som dubblett
        self.assertIn("super mario bros.", self.grouper.exact_duplicates)
        self.assertEqual(len(self.grouper.exact_duplicates["super mario bros."]), 2)
        
        # Kontrollera att spel-ID:n är korrekta
        game_ids = [game["id"] for game in self.grouper.exact_duplicates["super mario bros."]]
        self.assertIn("1", game_ids)
        self.assertIn("2", game_ids)
    
    def test_version_groups(self):
        """Testa identifiering av versionsgrupper."""
        # Kontrollera att The Witcher 3 identifieras som versionsgrupp
        self.assertIn("the witcher 3: wild hunt", self.grouper.version_groups)
        self.assertEqual(len(self.grouper.version_groups["the witcher 3: wild hunt"]), 3)
        
        # Kontrollera att spel-ID:n är korrekta
        game_ids = [game["id"] for game in self.grouper.version_groups["the witcher 3: wild hunt"]]
        self.assertIn("3", game_ids)
        self.assertIn("4", game_ids)
        self.assertIn("5", game_ids)
    
    def test_series_groups(self):
        """Testa identifiering av spelserier."""
        # Kontrollera att Mass Effect identifieras som spelserie
        self.assertIn("mass effect", self.grouper.series_groups)
        self.assertEqual(len(self.grouper.series_groups["mass effect"]), 4)
        
        # Kontrollera att spel-ID:n är korrekta
        game_ids = [game["id"] for game in self.grouper.series_groups["mass effect"]]
        self.assertIn("6", game_ids)
        self.assertIn("7", game_ids)
        self.assertIn("8", game_ids)
        self.assertIn("9", game_ids)
        
        # Kontrollera att FIFA identifieras som spelserie
        self.assertIn("fifa", self.grouper.series_groups)
        self.assertEqual(len(self.grouper.series_groups["fifa"]), 3)
    
    def test_get_game_relationships(self):
        """Testa generering av spelrelationer."""
        relationships = self.grouper.get_game_relationships()
        
        # Kontrollera att det finns relationer
        self.assertTrue(len(relationships) > 0)
        
        # Kontrollera att relationer har rätt struktur
        for rel in relationships:
            self.assertIn("source_game_id", rel)
            self.assertIn("target_game_id", rel)
            self.assertIn("relationship_type", rel)
            self.assertIn("confidence_score", rel)
            
            # Kontrollera att relationstyper är giltiga
            self.assertIn(rel["relationship_type"], ["duplicate_of", "version_of", "sequel_to"])
    
    def test_get_game_groups(self):
        """Testa generering av spelgrupper."""
        groups = self.grouper.get_game_groups()
        
        # Kontrollera att det finns grupper
        self.assertTrue(len(groups) > 0)
        
        # Kontrollera att grupper har rätt struktur
        for group in groups:
            self.assertIn("group_id", group)
            self.assertIn("group_type", group)
            self.assertIn("canonical_name", group)
            self.assertIn("representative_game_id", group)
            self.assertIn("game_count", group)
            
            # Kontrollera att grupptyper är giltiga
            self.assertIn(group["group_type"], ["version_group", "series"])
    
    def test_get_group_members(self):
        """Testa generering av gruppmedlemskap."""
        members = self.grouper.get_group_members()
        
        # Kontrollera att det finns gruppmedlemskap
        self.assertTrue(len(members) > 0)
        
        # Kontrollera att gruppmedlemskap har rätt struktur
        for member in members:
            self.assertIn("group_id", member)
            self.assertIn("game_id", member)
            self.assertIn("is_primary", member)


if __name__ == "__main__":
    unittest.main()
