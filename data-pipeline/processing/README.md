# IGDB Datarensningsmodul

Denna modul innehåller kod för att rensa och bearbeta speldata från IGDB API. Modulen hanterar dubbletter, versioner av samma spel och spelserier för att skapa en ren och strukturerad datamodell.

## Funktionalitet

Modulen består av följande komponenter:

1. **Kanonisk namnextrahering**: Extraherar basnamn från speltitlar genom att ta bort versionsmarkörer, årtal och andra variationer.

2. **Spelgruppering**: Identifierar och grupperar spel som är:
   - Exakta dubbletter (samma namn)
   - Olika versioner av samma spel (t.ex. GOTY-utgåvor)
   - Spel i samma serie (t.ex. uppföljare)

3. **Kvalitetsbedömning**: Beräknar en kvalitetspoäng för varje spel baserat på tillgängliga metadata.

4. **Datamodell**: Definierar en strukturerad datamodell för spel, spelrelationer och spelgrupper.

5. **ETL-pipeline**: Implementerar en komplett pipeline för att extrahera, transformera och ladda data.

## Användning

### Kör datarensningspipelinen

```bash
python -m processing.etl_pipeline --input /path/to/raw/data --output /path/to/cleaned/data
```

### Kör tester

```bash
cd data-pipeline/processing
./run_tests.sh
```

## Datamodell

Modulen genererar följande tabeller:

1. **games**: Rensad speldata med kanoniska namn och kvalitetspoäng
2. **game_relationships**: Relationer mellan spel (t.ex. "version_of", "sequel_to")
3. **game_groups**: Grupper av relaterade spel (t.ex. versionsgrupper, spelserier)
4. **game_group_members**: Koppling mellan spel och grupper

## Algoritmer

### Kanonisk namnextrahering

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

### Kvalitetsscore för spel

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
