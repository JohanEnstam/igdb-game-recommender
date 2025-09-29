"""
Tester för data_model-modulen.
"""

import unittest
from datetime import datetime
from data_pipeline.processing.data_model import Game, GameRelationship, GameGroup, GameGroupMember, convert_to_bigquery_schema


class TestDataModel(unittest.TestCase):
    """Testfall för data_model-modulen."""
    
    def test_game_from_igdb_game(self):
        """Testa Game.from_igdb_game-metoden."""
        # Skapa ett IGDB-spel
        igdb_game = {
            "id": 1234,
            "name": "Test Game",
            "summary": "This is a test game",
            "first_release_date": 1609459200,  # 2021-01-01
            "rating": 85.0,
            "cover": {"url": "//images.igdb.com/test.jpg"}
        }
        
        # Skapa ett Game-objekt från IGDB-spelet
        canonical_name = "test game"
        quality_score = 90.5
        game = Game.from_igdb_game(igdb_game, canonical_name, quality_score)
        
        # Kontrollera att attributen är korrekta
        self.assertEqual(game.game_id, "1234")
        self.assertEqual(game.canonical_name, "test game")
        self.assertEqual(game.display_name, "Test Game")
        self.assertEqual(game.summary, "This is a test game")
        self.assertEqual(game.rating, 85.0)
        self.assertEqual(game.cover_url, "//images.igdb.com/test.jpg")
        self.assertEqual(game.quality_score, 90.5)
        self.assertTrue(game.has_complete_data)
        
        # Kontrollera att release_date är korrekt konverterad
        expected_date = datetime.fromtimestamp(1609459200)
        self.assertEqual(game.release_date, expected_date)
    
    def test_game_group_create_methods(self):
        """Testa GameGroup.create_*-metoderna."""
        # Skapa en versionsgrupp
        version_group = GameGroup.create_version_group(
            canonical_name="test game",
            representative_game_id="1234",
            game_count=3
        )
        
        # Kontrollera att attributen är korrekta
        self.assertEqual(version_group.group_type, "version_group")
        self.assertEqual(version_group.canonical_name, "test game")
        self.assertEqual(version_group.representative_game_id, "1234")
        self.assertEqual(version_group.game_count, 3)
        
        # Skapa en seriegrupp
        series_group = GameGroup.create_series_group(
            series_name="test series",
            representative_game_id="5678",
            game_count=4
        )
        
        # Kontrollera att attributen är korrekta
        self.assertEqual(series_group.group_type, "series")
        self.assertEqual(series_group.canonical_name, "test series")
        self.assertEqual(series_group.representative_game_id, "5678")
        self.assertEqual(series_group.game_count, 4)
    
    def test_convert_to_bigquery_schema(self):
        """Testa convert_to_bigquery_schema-funktionen."""
        # Skapa testdata
        games = [
            Game(
                game_id="1234",
                canonical_name="test game 1",
                display_name="Test Game 1",
                release_date=datetime(2021, 1, 1),
                summary="This is test game 1",
                rating=85.0,
                cover_url="//images.igdb.com/test1.jpg",
                has_complete_data=True,
                quality_score=90.5
            ),
            Game(
                game_id="5678",
                canonical_name="test game 2",
                display_name="Test Game 2",
                release_date=datetime(2022, 1, 1),
                summary="This is test game 2",
                rating=75.0,
                cover_url="//images.igdb.com/test2.jpg",
                has_complete_data=True,
                quality_score=80.5
            )
        ]
        
        relationships = [
            GameRelationship(
                source_game_id="5678",
                target_game_id="1234",
                relationship_type="sequel_to",
                confidence_score=0.9
            )
        ]
        
        groups = [
            GameGroup(
                group_id="group1",
                group_type="series",
                canonical_name="test series",
                representative_game_id="1234",
                game_count=2
            )
        ]
        
        members = [
            GameGroupMember(
                group_id="group1",
                game_id="1234",
                is_primary=True
            ),
            GameGroupMember(
                group_id="group1",
                game_id="5678",
                is_primary=False
            )
        ]
        
        # Konvertera till BigQuery-schema
        bq_data = convert_to_bigquery_schema(games, relationships, groups, members)
        
        # Kontrollera att alla tabeller finns
        self.assertIn("games", bq_data)
        self.assertIn("game_relationships", bq_data)
        self.assertIn("game_groups", bq_data)
        self.assertIn("game_group_members", bq_data)
        
        # Kontrollera att antalet rader är korrekt
        self.assertEqual(len(bq_data["games"]), 2)
        self.assertEqual(len(bq_data["game_relationships"]), 1)
        self.assertEqual(len(bq_data["game_groups"]), 1)
        self.assertEqual(len(bq_data["game_group_members"]), 2)
        
        # Kontrollera att data är korrekt konverterad
        self.assertEqual(bq_data["games"][0]["game_id"], "1234")
        self.assertEqual(bq_data["game_relationships"][0]["relationship_type"], "sequel_to")
        self.assertEqual(bq_data["game_groups"][0]["canonical_name"], "test series")
        self.assertEqual(bq_data["game_group_members"][0]["is_primary"], True)


if __name__ == "__main__":
    unittest.main()
