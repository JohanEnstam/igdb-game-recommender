"""
Tester för name_processor-modulen.
"""

import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from processing.name_processor import extract_canonical_name, normalize_name, extract_series_name, is_likely_same_game

# Förväntade resultat för extract_canonical_name
CANONICAL_NAME_MAP = {
    "Batman: Arkham City - Game of the Year Edition": "batman: arkham city",
    "The Witcher 3: Wild Hunt - Complete Edition": "the witcher 3: wild hunt",
    "Doom 2016": "doom",
    "Final Fantasy VII Remake": "final fantasy vii",
    "Resident Evil 4 HD": "resident evil 4",
    "Halo: The Master Chief Collection": "halo",
    "Assassin's Creed: Brotherhood": "assassin's creed",
    "Mass Effect: Legendary Edition": "mass effect",
    "Fallout 4: Far Harbor DLC": "fallout 4",
    "The Elder Scrolls V: Skyrim - Dawnguard": "the elder scrolls v: skyrim",
    "FIFA 22": "fifa",
    "Call of Duty: Modern Warfare 2019": "call of duty: modern warfare"
}


class TestNameProcessor(unittest.TestCase):
    """Testfall för name_processor-modulen."""
    
    def test_extract_canonical_name(self):
        """Testa funktionen extract_canonical_name."""
        for input_name, expected_output in CANONICAL_NAME_MAP.items():
            with self.subTest(input_name=input_name):
                self.assertEqual(extract_canonical_name(input_name), expected_output)
    
    def test_normalize_name(self):
        """Testa funktionen normalize_name."""
        self.assertEqual(normalize_name("The Legend of Zelda: Breath of the Wild"), "the legend of zelda breath of the wild")
        self.assertEqual(normalize_name("Super Mario Bros. 3"), "super mario bros 3")
        self.assertEqual(normalize_name("Half-Life 2"), "half life 2")
        self.assertEqual(normalize_name("Assassin's Creed IV: Black Flag"), "assassin s creed iv black flag")
    
    def test_extract_series_name(self):
        """Testa funktionen extract_series_name."""
        # Testa numeriska serier
        self.assertEqual(extract_series_name("Final Fantasy VII"), "final fantasy")
        self.assertEqual(extract_series_name("Resident Evil 4"), "resident evil")
        self.assertEqual(extract_series_name("The Elder Scrolls V: Skyrim"), "the elder scrolls")
        
        # Testa serier med kolon
        self.assertEqual(extract_series_name("Assassin's Creed: Brotherhood"), "assassin's creed")
        self.assertEqual(extract_series_name("Mass Effect: Andromeda"), "mass effect")
        
        # Testa fall där inget serienamn kan extraheras
        self.assertIsNone(extract_series_name("The Last of Us"))
        self.assertIsNone(extract_series_name("Horizon Zero Dawn"))
    
    def test_is_likely_same_game(self):
        """Testa funktionen is_likely_same_game."""
        # Testa exakt samma spel
        self.assertTrue(is_likely_same_game("The Witcher 3: Wild Hunt", "The Witcher 3: Wild Hunt"))
        
        # Testa versioner av samma spel
        self.assertTrue(is_likely_same_game("The Witcher 3: Wild Hunt", "The Witcher 3: Wild Hunt - Complete Edition"))
        self.assertTrue(is_likely_same_game("Skyrim", "The Elder Scrolls V: Skyrim"))
        
        # Testa olika spel
        self.assertFalse(is_likely_same_game("The Witcher 3", "The Witcher 2"))
        self.assertFalse(is_likely_same_game("Call of Duty: Modern Warfare", "Call of Duty: Black Ops"))
        
        # Testa med olika tröskelvärden
        self.assertTrue(is_likely_same_game("FIFA 22", "FIFA 22 Ultimate Edition", 0.7))
        self.assertFalse(is_likely_same_game("FIFA 22", "FIFA 21", 0.7))


if __name__ == "__main__":
    unittest.main()
