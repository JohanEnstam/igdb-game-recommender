# Optimeringsresultat - Feature Extraction

## Sammanfattning

Jag har genomfört initial optimering av feature extraction för rekommendationssystemet på ett mellanstort dataset med ~25,000 spel.

## Dataset

- **Storlek**: 24,997 spel
- **Metod**: Stratifierat urval baserat på quality_score
- **Distribution**:
  - Spel med summary: 21,415 (85.7%)
  - Spel med genres: 20,846 (83.4%)
  - Spel med platforms: 19,776 (79.1%)
  - Spel med themes: 14,034 (56.1%)
- **Quality Score**: Min: 22.22, Max: 100.00, Medel: 75.80

## Optimeringsresultat (Snabb optimering)

Testade 6 parameterkombinationer:

### Bästa Resultat

- **Text Weight**: 0.60
- **Max Text Features**: 5,000
- **Min Document Frequency**: 5
- **N-gram Range**: (1, 2)
- **Average Similarity**: 0.6245
- **Extraction Time**: 4.83s
- **Total Features**: 5,213 (5,000 text + 213 kategoriska)

### Alla Resultat (sorterade efter similarity)

| Text Weight | Max Features | Min DF | N-gram | Avg Similarity | Time (s) | Total Features |
|------------|--------------|--------|--------|---------------|----------|----------------|
| 0.60 | 5000 | 5 | (1,2) | **0.6245** | 4.83 | 5213 |
| 0.60 | 3000 | 5 | (1,2) | 0.4279 | 4.23 | 3213 |
| 0.80 | 3000 | 5 | (1,2) | 0.3941 | 4.32 | 3213 |
| 0.70 | 3000 | 5 | (1,2) | 0.3719 | 4.96 | 3213 |
| 0.70 | 5000 | 5 | (1,2) | 0.3127 | 4.19 | 5213 |
| 0.80 | 5000 | 5 | (1,2) | 0.2852 | 4.37 | 5213 |

### Observationer

1. **Text Weight 0.60 är bäst**: Lägre text-vikt (0.60) ger bättre resultat än högre (0.70-0.80)
   - Detta indikerar att kategoriska features (genres, platforms, themes) är mycket viktiga
   - En balans mellan text och kategoriska features ger bäst resultat

2. **Fler text features är bättre**: 5,000 features > 3,000 features
   - Större vokabulär fångar fler nyanser i spelsammanfattningar
   - Marginellt längre extraction time (4.83s vs 4.23s) men värt det för bättre kvalitet

3. **Extraction Time**: Alla parametrar ger snabb extraction (4-5 sekunder)
   - Mycket snabba iterationer möjliga
   - Skalbart för större dataset

## Demo-tester

### The Witcher: Adventure Game
Top rekommendationer visar blandade resultat:
- ✅ **Bra**: Archeland, Bravely Default (RPG/Strategy spel)
- ❌ **Mindre bra**: Pokemon-spel (för olika tema)
- ⚠️ **Problem**: Vissa spel med kinesiska titlar (佣兵战歌) - språkbarriär

### Portal
Mycket bättre resultat:
- ✅ **Utmärkta**: Cr4ckr, Orthoiso, Ringognir (alla puzzle-spel)
- ✅ **Bra**: Chronon, Breaking Box: Rush! (puzzle/indie)
- ✅ **Konsistent tema**: Nästan alla rekommendationer är puzzle/indie-spel

## Nästa Steg

### 1. Validera Rekommendationskvalitet (Pågående)

**Manuell Bedömning**:
- [ ] Testa med 20-30 populära spel
- [ ] Utvärdera top 10 rekommendationer för varje
- [ ] Dokumentera kvalitet (Relevant/Inte Relevant)
- [ ] Beräkna precision@10

**Testspel att inkludera**:
- AAA-spel: The Witcher 3, Dark Souls, Skyrim, Portal 2
- Indie-spel: Hollow Knight, Celeste, Stardew Valley
- Olika genrer: FPS, RPG, Puzzle, Strategy, Adventure

### 2. Förbättra Parametrar

**Full Optimering** (inte snabb):
- Text weights: [0.5, 0.55, 0.60, 0.65, 0.70]
- Max text features: [5000, 7000, 10000]
- Min df: [3, 5, 10]
- N-gram ranges: [(1, 1), (1, 2), (1, 3), (2, 2)]

**Förväntad tidsåtgång**: ~1-2 timmar för 60 kombinationer

### 3. Skala upp till Hela Datasetet

När optimala parametrar är hittade:
- [ ] Extrahera features för alla 328,924 spel
- [ ] Mät extraction time och minnesanvändning
- [ ] Bygga Faiss-index
- [ ] Benchmark query performance
- [ ] Spara features och index för senare användning

**Förväntad extraction time**: ~3-5 minuter (baserat på 5s för 25k spel)

### 4. Implementera Förbättringar

**Potentiella förbättringar**:
- **Språkfiltrering**: Filtrera bort eller separera spel på icke-engelska
- **Genre-weights**: Ge olika vikt åt olika genres
- **Platform-filtrering**: Optional filtrering efter platform
- **Hybrid approach**: Kombinera content-based med popularity/ratings

## Tekniska Detaljer

### Feature Extraction

```python
# TF-IDF Text Features
- Vocabulary: 5,000 mest frekventa ord (efter stop words)
- N-grams: (1, 2) - unigramm och bigramm
- Min DF: 5 - ord måste förekomma i minst 5 dokument

# Categorical Features
- Genres: ~50 unika genres
- Platforms: ~120 unika platformar
- Themes: ~40 unika teman
- Encoding: Multi-label binarization (one-hot)

# Kombination
- Text features: 60% weight
- Categorical features: 40% weight
- Normalisering: L2-normalisering av båda
```

### Similarity Search

```python
# Faiss Index
- Type: IndexFlatIP (Inner Product)
- Distance: Cosine similarity (efter L2-normalisering)
- Size: 24,997 vektorer × 5,213 dimensioner
- Query time: ~100-200ms (inklusive index build)
```

## Slutsats

Initial optimering visar lovande resultat:
- ✅ Snabb feature extraction (4-5 sekunder)
- ✅ Goda similarity scores (0.62 för bästa parametrar)
- ✅ Relevanta rekommendationer för puzzle-spel (Portal)
- ⚠️ Blandade resultat för RPG-spel (Witcher)
- ⚠️ Språkbarriär för icke-engelska spel

**Rekommendation**: Fortsätt med manuell validering och full optimering innan skalning till hela datasetet.
