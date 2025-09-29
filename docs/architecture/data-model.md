# Datamodell - IGDB Game Recommendation System

## Översikt

Detta dokument beskriver datamodellen för IGDB Game Recommendation System, med fokus på den rensade och strukturerade datan som används för rekommendationer.

## Datamodell för Rensad Data

Datamodellen är utformad för att hantera dubbletter, versioner och relationer mellan spel på ett effektivt sätt. Den består av fyra huvudtabeller:

### 1. Games

Huvudtabellen som innehåller information om varje unikt spel.

```sql
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
```

#### Nyckelattribut:
- **game_id**: Unik identifierare för spelet (från IGDB)
- **canonical_name**: Normaliserat namn utan versionsmarkörer
- **display_name**: Originalnamnet för visning
- **quality_score**: Beräknad poäng baserad på datakvalitet (0-100)

### 2. Game Relationships

Definierar relationer mellan spel, som dubbletter, versioner och uppföljare.

```sql
CREATE TABLE game_relationships (
  source_game_id STRING NOT NULL,
  target_game_id STRING NOT NULL,
  relationship_type STRING NOT NULL,  -- "duplicate_of", "version_of", "sequel_to", etc.
  confidence_score FLOAT64,
  created_at TIMESTAMP
);
```

#### Relationstyper:
- **duplicate_of**: Exakt samma spel (olika plattformar)
- **version_of**: Olika versioner av samma spel (remasters, utgåvor)
- **sequel_to**: Uppföljare/föregångare i en serie

### 3. Game Groups

Grupperar relaterade spel i meningsfulla samlingar.

```sql
CREATE TABLE game_groups (
  group_id STRING NOT NULL,
  group_type STRING NOT NULL,  -- "version_group", "series", "franchise"
  canonical_name STRING NOT NULL,
  representative_game_id STRING,
  game_count INT64,
  created_at TIMESTAMP
);
```

#### Grupptyper:
- **version_group**: Olika versioner av samma spel
- **series**: Spel i samma serie (t.ex. "Final Fantasy")

### 4. Game Group Members

Kopplingstabell mellan spel och grupper.

```sql
CREATE TABLE game_group_members (
  group_id STRING NOT NULL,
  game_id STRING NOT NULL,
  is_primary BOOL,
  created_at TIMESTAMP
);
```

## Relationsdiagram

```
+-------------+       +---------------------+       +-------------+
|   Games     |       | Game Relationships  |       | Game Groups |
+-------------+       +---------------------+       +-------------+
| game_id     |<----->| source_game_id     |       | group_id    |<---+
| canonical_  |       | target_game_id     |       | group_type  |    |
| display_name|       | relationship_type  |       | canonical_  |    |
| release_date|       | confidence_score   |       | representat.|    |
| summary     |       | created_at         |       | game_count  |    |
| rating      |       +---------------------+       | created_at  |    |
| cover_url   |                                    +-------------+    |
| has_complete|                                                      |
| quality_    |                                                      |
| created_at  |       +---------------------+                        |
| updated_at  |<----->| Game Group Members  |<-----------------------+
+-------------+       +---------------------+
                      | group_id           |
                      | game_id            |
                      | is_primary         |
                      | created_at         |
                      +---------------------+
```

## Dataflöde

1. **Rådata från IGDB API** → Sparas i JSON-format
2. **Datarensningspipeline** → Extraherar kanoniska namn och identifierar relationer
3. **Transformation** → Skapar strukturerad datamodell med spel, relationer och grupper
4. **Laddning** → Sparas i BigQuery med optimerat schema

## Användningsområden

### Rekommendationer

Datamodellen möjliggör flera typer av rekommendationer:
- Rekommendera andra versioner av ett spel
- Rekommendera uppföljare/föregångare i samma serie
- Rekommendera spel med liknande egenskaper

### Sökning

- Effektiv sökning baserad på kanoniska namn
- Gruppering av sökresultat för att undvika dubbletter
- Prioritering av spel med högre kvalitetspoäng

## Statistik från Datarensningen

- **Bearbetade spel**: 328,924 spel
- **Identifierade relationer**: 85,466 totalt
  - Exakta dubbletter: 17,986 (21.0%)
  - Versioner av samma spel: 17,967 (21.0%)
  - Uppföljare/föregångare: 49,513 (57.9%)
- **Skapade grupper**: 16,800 totalt
  - Versionsgrupper: 4,929 (29.3%)
  - Spelserier: 11,871 (70.7%)
  - Genomsnittlig gruppstorlek: 5.0 spel
  - Största grupp: 901 spel

## Nästa Steg

1. **Implementera BigQuery-schema** baserat på denna datamodell
2. **Optimera för frågeeffektivitet** med partitionering och indexering
3. **Utveckla inkrementell uppdateringslogik** för kontinuerlig synkronisering

## Relaterade Dokument

- [Datarensningsplan](../data-cleaning-plan.md)
- [ETL-process](./etl-process.md) *(planerad)*
