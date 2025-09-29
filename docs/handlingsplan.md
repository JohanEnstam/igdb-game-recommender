# Handlingsplan - IGDB Game Recommendation System

## Övergripande Strategi

Vi har valt en hybridapproach för att effektivt gå vidare med projektet:

1. **Validera kritiska antaganden först** - Testa IGDB API-prestanda och datakvalitet lokalt
2. **Bygga infrastruktur parallellt** - Sätta upp nödvändig GCP-infrastruktur för att stödja dataflödet
3. **Implementera inkrementellt** - Fokusera på en komponent i taget för att snabbt få värdefull feedback

Denna approach ger oss det bästa av båda världar - vi validerar snabbt våra antaganden om API:et samtidigt som vi bygger en solid grund för framtida automatisering.

## Detaljerad Handlingsplan

### Fas 1: Validera IGDB API-antaganden (Slutförd)

**Mål:** Bekräfta att vi kan hämta alla spel på cirka 15 minuter och förstå datastrukturen.

1. **Implementera bulk_fetch.py** ✅
   - Utvecklat skript som använder vår IGDB-klient för att hämta alla spel
   - Implementerat loggning av tidsåtgång och datamängd
   - Sparat rådata lokalt för analys

2. **Validera prestanda** ✅
   - Mätt faktisk tid för att hämta alla spel: **12 minuter och 5 sekunder**
   - Analyserat rate limiting och optimerat för maximal throughput
   - Dokumenterat resultat och insikter i progress.md

3. **Analysera datakvalitet** ✅
   - Undersökt datastruktur och innehåll med analyze_data.py
   - Identifierat nödvändiga transformationer för BigQuery
   - Planerat schema för staging och production tables

**Resultat:**
- Totalt antal spel i IGDB: **328,924** (mindre än de uppskattade 350k)
- Genomsnittlig hämtningshastighet: **453 spel per sekund**
- Datakvalitet varierar mellan fält:
  - Spel med betyg: 32,226 (9.8%)
  - Spel med sammanfattning: 281,462 (85.6%)
  - Spel med omslagsbild: 262,394 (79.8%)
  - Spel med utgivningsdatum: 239,307 (72.8%)

### Fas 2: Grundläggande Infrastruktur

**Mål:** Sätta upp nödvändig infrastruktur för att lagra och bearbeta IGDB-data.

1. **GitHub Actions secrets** ✅
   - Lagt till nödvändiga secrets för CI/CD:
     - `GCP_PROJECT_ID`: igdb-pipeline-v3
     - `GCP_SA_KEY`: Base64-encodad service account-nyckel
     - `TF_STATE_BUCKET`: igdb-terraform-state
     - `CF_SERVICE_ACCOUNT`: cf-igdb-ingest@igdb-pipeline-v3.iam.gserviceaccount.com
     - `CLOUD_RUN_SERVICE_ACCOUNT`: cloud-run-igdb-api@igdb-pipeline-v3.iam.gserviceaccount.com
     - `GCP_REGION`: europe-west1

2. **Terraform för storage och BigQuery**
   - Implementera Terraform-moduler för:
     - GCS buckets för rådata
     - BigQuery dataset och tabeller
     - Åtkomstbehörigheter

3. **Skapa och validera infrastruktur**
   - Köra `terraform apply` för att skapa resurser
   - Validera att resurserna skapats korrekt
   - Dokumentera infrastrukturstatus

### Fas 3: Data Pipeline

**Mål:** Implementera automatiserad datainhämtning och bearbetning.

1. **Cloud Function för IGDB API**
   - Implementera Cloud Function för att hämta data från IGDB API
   - Konfigurera Cloud Scheduler för daglig synkronisering
   - Testa och validera funktionen

2. **ETL-process**
   - Implementera ETL Cloud Function för att transformera data
   - Skapa MERGE-logik för staging till production
   - Implementera data quality checks

3. **Event-driven arkitektur**
   - Konfigurera Pub/Sub topics och subscriptions
   - Implementera event-baserad triggering av funktioner
   - Testa end-to-end dataflöde

### Fas 4: Slutföra CI/CD-pipeline

**Mål:** Säkerställa att alla komponenter kan deployas automatiskt.

1. **Terraform deployment**
   - Testa och validera automatisk deployment via GitHub Actions
   - Implementera terraform plan/apply workflow
   - Sätta upp branch protection rules

2. **Cloud Functions deployment**
   - Konfigurera automatisk deployment av Cloud Functions
   - Implementera versionshantering av funktioner
   - Testa deployment-pipeline

3. **Monitoring och alerting**
   - Konfigurera Cloud Monitoring dashboards
   - Implementera alerting för kritiska fel
   - Sätta upp loggning för felsökning

## Tidslinje och Prioriteringar

1. **Högsta prioritet (Närmaste dagarna)**
   - ✅ Implementera och testa bulk_fetch.py
   - ✅ Analysera dubbletter och relaterade spel
   - ✅ Implementera datarensningspipeline enligt [datarensningsplanen](./data-cleaning-plan.md)
   - ✅ Utveckla datamodell för spel, relationer och grupper
   - ✅ Köra datarensningspipelinen på hela IGDB-databasen
   - ✅ Sätta upp GitHub Actions secrets

2. **Medelhög prioritet (Inom en vecka)**
   - Implementera Terraform för storage och BigQuery
   - Skapa optimerat BigQuery-schema baserat på datarensning

3. **Medelhög prioritet (Inom två veckor)**
   - Implementera Cloud Function för IGDB API
   - Skapa ETL-process med datarensningslogik
   - Konfigurera Pub/Sub

4. **Lägre prioritet (Efter grundläggande funktionalitet)**
   - Slutföra CI/CD-pipeline
   - Implementera monitoring och alerting
   - Optimera prestanda

## Mätbara Mål

1. **Kortsiktiga mål**
   - ✅ Bekräfta att vi kan hämta alla spel inom 20 minuter (Uppnått: 12 min 5 sek för 328,924 spel)
   - ✅ Identifiera dubbletter och relaterade spel i databasen
   - ✅ Implementera datarensningspipeline med minst 90% precision i dubblettidentifiering
   - ✅ Framgångsrikt bearbeta och rensa hela IGDB-databasen (328,924 spel)
   - ✅ Konfigurera GitHub Secrets för CI/CD-pipeline
   - Lagra rensad data i BigQuery med optimerat schema

2. **Medellånga mål**
   - Reducera redundans i databasen med minst 20% genom datarensning
   - Automatisera hela dataflödet från IGDB till BigQuery med datarensning
   - Implementera inkrementell synkronisering som bevarar relationer
   - Skapa grundläggande rekommendationslogik baserad på spelrelationer

3. **Långsiktiga mål**
   - Komplett end-to-end demo med 200 nya spel och korrekt relationsmappning
   - Fullt automatiserad ML-pipeline som utnyttjar rensad data
   - Produktionsklar web-app med rekommendationer baserade på spelrelationer
