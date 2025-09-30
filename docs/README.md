# IGDB Game Recommendation System - Dokumentation

Detta är huvuddokumentationen för IGDB Game Recommendation System. Här hittar du en översikt över projektet, dess struktur och hur du navigerar i dokumentationen.

## Dokumentationsstruktur

Dokumentationen är organiserad i följande kategorier:

### 1. Projektöversikt
- [**Projektspecifikation**](./igdb-project-spec.md) - Detaljerad beskrivning av projektets mål, arkitektur och komponenter
- [**Framstegsrapport**](./progress.md) - Aktuell status och uppnådda milstolpar
- [**Handlingsplan**](./handlingsplan.md) - Detaljerad plan för projektets genomförande med tidslinjer

### 2. Teknisk Dokumentation
- [**GCP Setup**](./gcp-setup.md) - Guide för konfigurering av Google Cloud Platform
- [**Datarensningsplan**](./data-cleaning-plan.md) - Strategi och implementation för datarensning

### 3. Utvecklingsguider
- [Lokal utvecklingsmiljö](./development-guides/local-setup.md) *(planerad)*
- [CI/CD Pipeline](./development-guides/ci-cd.md) *(planerad)*
- [Testning](./development-guides/testing.md) *(planerad)*

### 4. Arkitekturdokumentation
- [Systemarkitektur](./architecture/system-overview.md)
- [Datamodell](./architecture/data-model.md)
- [Rekommendationssystem](./architecture/recommendation-system.md)
- [API-dokumentation](./architecture/api-docs.md) *(planerad)*

## Aktuell Projektstatus

Projektet är för närvarande i **Fas 5: ML Pipeline** och har slutfört följande huvudmilstolpar:

- ✅ Projektstruktur och grundläggande setup
- ✅ Terraform foundation
- ✅ IGDB API integration
- ✅ Lokal utvecklingsmiljö
- ✅ CI/CD pipeline grundstruktur
- ✅ Web app prototyp
- ✅ GCP setup
- ✅ Datainsamling och analys
- ✅ Datarensning och datamodellering
- ✅ Implementation av infrastruktur i molnet
- ✅ Integration av datarensningspipeline med ETL-process

Nästa steg är att implementera rekommendationssystemet med feature extraction och similarity search.

## Viktiga Resurser

- [IGDB API Dokumentation](https://api-docs.igdb.com/)
- [GCP Konsol](https://console.cloud.google.com/home/dashboard?project=igdb-pipeline-v3)
- [GitHub Repository](https://github.com/JohanEnstam/igdb-game-recommender)
