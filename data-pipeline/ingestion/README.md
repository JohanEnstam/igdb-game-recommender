# IGDB Data Ingestion

Detta är modulen för att hämta data från IGDB API och förbereda den för vidare bearbetning.

## Komponenter

- **igdb_client.py**: Klient för att interagera med IGDB API med korrekt rate limiting
- **bulk_fetch.py**: Skript för att hämta alla spel från IGDB API
- **analyze_data.py**: Skript för att analysera hämtad data

## Användning

### Installation

Installera beroenden:

```bash
pip install -r ../requirements.txt
```

### Miljövariabler

Skapa en `.env`-fil i denna katalog med följande innehåll:

```
IGDB_CLIENT_ID=ditt_client_id
IGDB_CLIENT_SECRET=din_client_secret
```

Du kan också sätta dessa miljövariabler direkt i terminalen:

```bash
export IGDB_CLIENT_ID=ditt_client_id
export IGDB_CLIENT_SECRET=din_client_secret
```

### Hämta alla spel

För att hämta alla spel från IGDB API:

```bash
python bulk_fetch.py --output ./data
```

För att hämta ett begränsat antal spel (t.ex. för testning):

```bash
python bulk_fetch.py --output ./data --limit 1000
```

### Analysera data

Efter att du har hämtat data kan du analysera den:

```bash
python analyze_data.py --input ./data --output ./analysis
```

## Datastruktur

Data sparas i JSON-format i batches om 10000 spel per fil. Varje spel innehåller följande fält:

- `id`: IGDB spel-ID
- `name`: Spelets namn
- `summary`: Kort sammanfattning
- `storyline`: Längre beskrivning av handlingen
- `first_release_date`: Utgivningsdatum (UNIX timestamp)
- `rating`: Användarbetyg (0-100)
- `rating_count`: Antal användarröster
- `aggregated_rating`: Kritikernas betyg (0-100)
- `aggregated_rating_count`: Antal kritikerröster
- `cover.url`: URL till omslagsbild
- `genres`: Lista med genrer (id, name)
- `platforms`: Lista med plattformar (id, name)
- `themes`: Lista med teman (id, name)

## Prestanda

Skriptet är optimerat för att respektera IGDB API:s rate limit på 4 requests per sekund och batch size på 500 spel per request. Med dessa inställningar bör det ta cirka 15 minuter att hämta alla 350k spel.

Prestandan loggas i `stats.json` som genereras i output-katalogen.
