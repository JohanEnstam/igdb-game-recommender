"""
Tester för quality_scorer-modulen.
"""

import unittest
from data_pipeline.processing.quality_scorer import calculate_quality_score, has_complete_data, select_representative_game


class TestQualityScorer(unittest.TestCase):
    """Testfall för quality_scorer-modulen."""
    
    def test_calculate_quality_score(self):
        """Testa funktionen calculate_quality_score."""
        # Tomt spel
        empty_game = {}
        self.assertEqual(calculate_quality_score(empty_game), 0.0)
        
        # Spel med bara namn
        name_only_game = {"name": "Test Game"}
        expected_score = 1.0 / 4.5 * 100  # name har vikt 1.0, totalt 4.5
        self.assertAlmostEqual(calculate_quality_score(name_only_game), expected_score, places=1)
        
        # Spel med alla attribut
        complete_game = {
            "name": "Test Game",
            "summary": "This is a test game",
            "cover": {"url": "http://example.com/cover.jpg"},
            "first_release_date": 1609459200,  # 2021-01-01
            "rating": 85.0,
            "genres": [{"id": 1, "name": "Action"}],
            "platforms": [{"id": 1, "name": "PC"}],
            "themes": [{"id": 1, "name": "Fantasy"}]
        }
        self.assertEqual(calculate_quality_score(complete_game), 100.0)
        
        # Spel med några attribut
        partial_game = {
            "name": "Test Game",
            "summary": "This is a test game",
            "cover": {"url": "http://example.com/cover.jpg"},
            "first_release_date": 1609459200  # 2021-01-01
        }
        expected_score = (1.0 + 0.8 + 0.7 + 0.6) / 4.5 * 100
        self.assertAlmostEqual(calculate_quality_score(partial_game), expected_score, places=1)
    
    def test_has_complete_data(self):
        """Testa funktionen has_complete_data."""
        # Tomt spel
        empty_game = {}
        self.assertFalse(has_complete_data(empty_game))
        
        # Spel med bara namn
        name_only_game = {"name": "Test Game"}
        self.assertFalse(has_complete_data(name_only_game))
        
        # Spel med alla obligatoriska fält men inga valfria
        required_only_game = {
            "name": "Test Game",
            "summary": "This is a test game",
            "cover": {"url": "http://example.com/cover.jpg"}
        }
        self.assertFalse(has_complete_data(required_only_game))
        
        # Spel med alla obligatoriska fält och ett valfritt
        almost_complete_game = {
            "name": "Test Game",
            "summary": "This is a test game",
            "cover": {"url": "http://example.com/cover.jpg"},
            "first_release_date": 1609459200  # 2021-01-01
        }
        self.assertFalse(has_complete_data(almost_complete_game))
        
        # Spel med alla obligatoriska fält och två valfria
        complete_game = {
            "name": "Test Game",
            "summary": "This is a test game",
            "cover": {"url": "http://example.com/cover.jpg"},
            "first_release_date": 1609459200,  # 2021-01-01
            "rating": 85.0
        }
        self.assertTrue(has_complete_data(complete_game))
    
    def test_select_representative_game(self):
        """Testa funktionen select_representative_game."""
        # Tom lista
        with self.assertRaises(ValueError):
            select_representative_game([])
        
        # Lista med ett spel
        single_game = {"name": "Test Game"}
        self.assertEqual(select_representative_game([single_game]), single_game)
        
        # Lista med flera spel av olika kvalitet
        low_quality_game = {"name": "Low Quality Game"}
        medium_quality_game = {
            "name": "Medium Quality Game",
            "summary": "This is a medium quality game",
            "cover": {"url": "http://example.com/cover.jpg"}
        }
        high_quality_game = {
            "name": "High Quality Game",
            "summary": "This is a high quality game",
            "cover": {"url": "http://example.com/cover.jpg"},
            "first_release_date": 1609459200,  # 2021-01-01
            "rating": 85.0
        }
        
        games = [low_quality_game, medium_quality_game, high_quality_game]
        self.assertEqual(select_representative_game(games), high_quality_game)


if __name__ == "__main__":
    unittest.main()
