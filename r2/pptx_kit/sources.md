# Quellen und KI-Einsatz (R2)

Erzeugt von `src/build_presentation.py`.

## Daten

| Quelle | Inhalt | Lizenz | Beleg |
| --- | --- | --- | --- |
| Bundesnetzagentur | SMARD.de | Day-Ahead-Großhandelspreis DE-LU, Filter 4169, 01.01.2022–31.10.2026, abgerufen 07.11.2026 | CC BY 4.0, Namensnennung „Bundesnetzagentur \| SMARD.de“ | `data/raw/MANIFEST.md` |
| Praxiskontakt (anonymisiert) | Verbrauch 50 MWh/Tag, Betriebszeit 06–22 Uhr, flexible Prozesse; Interview 09.11.2026 | Nutzung nur aggregiert, Name nur mit Freigabe | Tagebuch K-005 |
| eigene Annahme | verschiebbarer Anteil 2,0 MWh/Tag (Platzhalter) | — | `config/params.yaml` |

## Fakten zum Markt

- ACER (2026): Decision 02/2026, Annex I, harmonisierte Höchst- und Mindestclearingpreise SDAC. https://www.acer.europa.eu/sites/default/files/documents/Individual%20Decisions_annex/ACER-Decision-02-2026-AnnexI.pdf
- EPEX SPOT (2022): Harmonised maximum clearing price for SDAC to be set to +4,000 EUR/MWh from 10th May 2022. https://www.epexspot.com/en/news/harmonised-maximum-clearing-price-sdac-be-set-4000-eurmwh-10th-may-2022
- EXAA (2022): Harmonised maximum clearing price for SDAC to be set to +5,000 EUR/MWh from 20th September. https://www.exaa.at/uber-exaa/neuigkeiten/harmonised-maximum-clearing-price-for-sdac-to-be-set-to-5-000-eur-mwh/
- NEMO Committee (2025): 15-minute MTU in SDAC was implemented (Lieferung ab 01.10.2025). https://nemo-committee.eu/assets/files/15-minute-mtu-in-sdac-was-implemented.pdf

## Methodische Literatur

Siehe `docs/datenaufbereitung.md` (Wang & Strong 1996; Tukey 1977; Hampel 1974; Iglewicz & Hoaglin 1993; Leys et al. 2013; Janczura et al. 2013; Weron 2014).

## KI-Einsatz

**Wofür Claude Code genutzt wurde:** Programmcode (`src/01_download.py`, `src/02_synthetisch.py`, `src/cleaning.py`, `src/datenzugriff.py`, `src/fensteranalyse.py`, `src/build_presentation.py`), Tests, Dokumentation (Codebook, Aufbereitungsprotokoll, Schnittstellen), Quellenrecherche zu Preisgrenzen und zur Viertelstunden-Umstellung, Entwürfe für Tagebucheinträge, diese Folien.

**Was ich (Max, R2) entschieden und geprüft habe:**
- Pläne vor jedem größeren Schritt freigegeben (Tagebuch A-008, A-009).
- Fachliche Entscheidungen: nur Stundenpreise (E-021), CSV statt Parquet (E-027), UTC als Schlüssel (E-026), Ausreißer nur markieren (E-025), Produktion täglich (E-024), Kennzahl Mehrkosten des Status quo statt „Anteil 08–14“ (E-030).
- Praxisangaben selbst im Interview erhoben (K-005).
- Prüfung: 35 automatische Tests grün; Gegenproben mit absichtlich eingebauten Fehlern; gerenderte Folien gesichtet.
- Offen: den Code Abschnitt für Abschnitt selbst erklären (Sperrkriterium Erklärbarkeit).

Kennzeichnung im Repo: Dateikopf `# KI: Claude …`, Commit-Trailer, `docs/ki-nutzung.md`.
