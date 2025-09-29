# Datarensningsplan - IGDB Game Recommendation System

## Bakgrund och Utmaningar

Efter att ha analyserat hela IGDB-databasen med 328,924 spel har vi identifierat flera utmaningar relaterade till datakvalitet och dubbletter som behöver hanteras för att bygga en effektiv rekommendationsmotor:

### Identifierade Problem

1. **Dubbletter och Versioner:**
   - 11,271 spel med exakt samma namn (t.ex. "Batman" finns 11 gånger)
   - 5,481 potentiella versionsgrupper (olika utgåvor av samma spel)
   - 11,881 potentiella spelserier (spel i samma franchise)

2. **Datakvalitet:**
   - Endast 9.8% av spelen har betyg
   - 85.6% har sammanfattningar
   - 79.8% har omslagsbilder
   - 72.8% har utgivningsdatum

3. **Namnkonventioner:**
   - Inkonsekvent namngivning för versioner (Edition, Deluxe, GOTY, etc.)
   - Inkonsekvent hantering av spelserier (numrering, undertitlar)

## Strategi för Datarensning

### Fas 1: Identifiering och Gruppering av Relaterade Spel

**Mål:** Skapa en robust metod för att identifiera unika spel och relaterade versioner.

1. **Implementera kanonisk namnextrahering:**
   - Utveckla algoritm för att extrahera "basnamn" från speltitlar
   - Ta bort versionsmarkörer (Edition, Deluxe, GOTY, etc.)
   - Normalisera specialtecken och mellanslag

2. **Skapa hierarkisk gruppering:**
   - Nivå 1: Exakt samma spel (olika plattformar)
   - Nivå 2: Versioner av samma spel (remasters, utgåvor)
   - Nivå 3: Spel i samma serie (uppföljare, prequels)

3. **Utveckla fingerprinting för spel:**
   - Kombinera namn, utgivningsår, genre och utvecklare för unik identifiering
   - Implementera fuzzy matching med högre tröskel för att fånga nära dubbletter

### Fas 2: Dataförbättring och Normalisering

**Mål:** Förbättra datakvaliteten och normalisera datastrukturen.

1. **Dataförbättring för nyckelattribut:**
   - Prioritera spel med komplett information
   - Aggregera metadata från olika versioner av samma spel
   - Berika spel med låg datakvalitet genom att ärva attribut från relaterade spel

2. **Normalisera metadata:**
   - Standardisera genrer och teman
   - Normalisera plattformsnamn
   - Harmonisera utgivningsdatum för samma spel på olika plattformar

3. **Skapa relationsmodell:**
   - Definiera relationer mellan spel (är_version_av, tillhör_serie, är_dlc_till)
   - Implementera grafdatastruktur för att representera spelrelationer

### Fas 3: ETL-Pipeline för Datarensning

**Mål:** Implementera automatiserad pipeline för kontinuerlig datarensning.

1. **Designa ETL-flöde:**
   - Extrahera rådata från IGDB API
   - Transformera data med rensnings- och grupperingslogik
   - Ladda data till BigQuery med optimerad schema

2. **Implementera kvalitetskontroller:**
   - Validera dataintegritet före och efter transformationer
   - Identifiera och flagga anomalier
   - Loggning av datakvalitetsmetrik

3. **Skapa inkrementell uppdateringslogik:**
   - Identifiera nya och uppdaterade spel
   - Hantera sammanslagning av ny data med befintlig data
   - Upprätthålla relationer vid inkrementella uppdateringar

## Teknisk Implementation

### Schema för Rensad Data

```sql
-- Basschema för spel
CREATE TABLE games (
  game_id STRING NOT NULL,
  canonical_name STRING NOT NULL,
  display_name STRING NOT NULL,
  release_date TIMESTAMP,
  summary STRING,
  rating FLOAT64,
  cover_url STRING,
  has_complete_data BOOL,
  quality_score FLOAT64,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Schema för spelrelationer
CREATE TABLE game_relationships (
  source_game_id STRING NOT NULL,
  target_game_id STRING NOT NULL,
  relationship_type STRING NOT NULL,  -- "version_of", "sequel_to", "in_series", "dlc_for", etc.
  confidence_score FLOAT64,
  created_at TIMESTAMP
);

-- Schema för spelgrupper
CREATE TABLE game_groups (
  group_id STRING NOT NULL,
  group_type STRING NOT NULL,  -- "version_group", "series", "franchise"
  canonical_name STRING NOT NULL,
  representative_game_id STRING,
  game_count INT64,
  created_at TIMESTAMP
);

-- Koppling mellan spel och grupper
CREATE TABLE game_group_members (
  group_id STRING NOT NULL,
  game_id STRING NOT NULL,
  is_primary BOOL,
  created_at TIMESTAMP
);
```

### Algoritm för Kanonisk Namnextrahering

```python
def extract_canonical_name(game_name):
    # Konvertera till lowercase
    name = game_name.lower()
    
    # Ta bort vanliga versionsmarkörer
    version_patterns = [
        r"(deluxe|premium|gold|complete|definitive|enhanced|remastered|hd|special|collector'?s?|goty|game of the year)",
        r"(edition|version|collection|bundle)",
        r"(dlc|expansion|season pass|content pack)",
        r"(remake|reboot|remaster)",
        r"(\d{4}|\d{2}|\d)$",  # Årtal eller versionsnummer i slutet
        r"(vol\.?\s*\d+|volume\s*\d+)",
        r"(chapter|episode|part)\s*\d+"
    ]
    
    combined_pattern = re.compile("|".join(version_patterns), re.IGNORECASE)
    canonical = re.sub(combined_pattern, "", name).strip()
    
    # Ta bort eventuella kolon, bindestreck och andra separatorer i slutet
    canonical = re.sub(r"[:;-–—_\s]+$", "", canonical).strip()
    
    return canonical
```

### Kvalitetsscore för Spel

```python
def calculate_quality_score(game):
    score = 0
    weights = {
        "has_name": 1.0,
        "has_summary": 0.8,
        "has_cover": 0.7,
        "has_release_date": 0.6,
        "has_rating": 0.5,
        "has_genres": 0.4,
        "has_platforms": 0.3,
        "has_themes": 0.2
    }
    
    if game.get("name"):
        score += weights["has_name"]
    if game.get("summary"):
        score += weights["has_summary"]
    if game.get("cover"):
        score += weights["has_cover"]
    if game.get("first_release_date"):
        score += weights["has_release_date"]
    if game.get("rating"):
        score += weights["has_rating"]
    if game.get("genres"):
        score += weights["has_genres"]
    if game.get("platforms"):
        score += weights["has_platforms"]
    if game.get("themes"):
        score += weights["has_themes"]
    
    # Normalisera till 0-100
    max_possible = sum(weights.values())
    normalized_score = (score / max_possible) * 100
    
    return normalized_score
```

## Nästa Steg

1. **Implementera datarensningspipeline:**
   - Utveckla Python-moduler för kanonisk namnextrahering
   - Skapa grupperings- och relationsalgoritmer
   - Implementera kvalitetsscoring

2. **Testa med delmängd av data:**
   - Validera rensningsalgoritmer på representativt urval
   - Mäta effektivitet i att identifiera dubbletter
   - Finjustera parametrar baserat på resultat

3. **Integrera med ETL-pipeline:**
   - Koppla datarensning till Cloud Functions
   - Implementera BigQuery-schema för rensad data
   - Skapa datavalideringssteget

4. **Dokumentera och utvärdera:**
   - Dokumentera datarensningslogik och beslut
   - Utvärdera datakvalitet före och efter rensning
   - Identifiera områden för ytterligare förbättring

## Förväntade Resultat

Efter implementering av datarensningsplanen förväntar vi oss:

1. Reducering av redundans i databasen med minst 20%
2. Förbättrad datakvalitet genom aggregering av metadata
3. Tydliga relationer mellan spel som kan användas för rekommendationer
4. Konsekvent namngivning och kategorisering av spel
5. Högre kvalitet på rekommendationer genom bättre förståelse av spelrelationer
