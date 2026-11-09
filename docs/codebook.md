# Codebook

Alle Spalten der bereinigten Dateien. Erzeugt von `src/cleaning.py` bzw. `src/02_synthetisch.py`. Öffnen mit `pd.read_csv(...)` oder Excel.

## `data/processed/preise_clean.csv` (eine Zeile je UTC-Stunde, 42 360 Zeilen)

| Spalte | Bedeutung | Einheit / Format | Quelle | Typ | Wertebereich |
| --- | --- | --- | --- | --- | --- |
| `ts_utc` | **Schlüssel.** Beginn der Stunde in UTC | `2025-10-26T01:00:00Z` | SMARD (Unix-ms → UTC) | Zeitstempel, eindeutig | 31.12.2021 23:00Z bis 31.10.2026 22:00Z, lückenlos stündlich |
| `ts_lokal` | dieselbe Stunde in deutscher Zeit mit UTC-Versatz | `2025-10-26 02:00:00+01:00` | abgeleitet aus `ts_utc` | Zeitstempel | +01:00 (Winter) oder +02:00 (Sommer) |
| `datum_lokal` | Kalendertag in deutscher Zeit | `JJJJ-MM-TT` | abgeleitet | Text | 2022-01-01 bis 2026-10-31 |
| `stunde_lokal` | Uhrzeit (Stundenbeginn) in deutscher Zeit | Stunde | abgeleitet | ganze Zahl | 0–23; am Oktober-Umstellungstag kommt 2 zweimal vor, im März fehlt 2 |
| `wochentag` | Wochentag | 0 = Montag … 6 = Sonntag | abgeleitet | ganze Zahl | 0–6 |
| `saison` | meteorologische Jahreszeit | Winter (Dez–Feb), Fruehling (Mär–Mai), Sommer (Jun–Aug), Herbst (Sep–Nov) | abgeleitet | Text | 4 Werte |
| `preis_eur_mwh` | Day-Ahead-Großhandelspreis DE-LU | €/MWh, 2 Nachkommastellen | Bundesnetzagentur \| SMARD.de, Filter 4169, CC BY 4.0 | Kommazahl | geprüft −500 bis +5 000; tatsächlich −500 bis 936,28; negative Werte gültig |
| `regime` | Handelsregime der Day-Ahead-Auktion | `stunde` bis 30.09.2025, `viertel` ab 01.10.2025 | SDAC 15-min-MTU, Lieferung ab 01.10.2025 | Text | 2 Werte |
| `werktag` | Mo–Fr und kein gesetzlicher Feiertag in Bayern | True/False | Paket `holidays` (BY); Mariä Himmelfahrt schaltbar | bool | — |
| `in_betriebszeit` | Stunde liegt in der Betriebszeit des Werks | True/False | Praxiskontakt: 06–22 Uhr (K-003, K-005) | bool | 16 von 24 Stunden je Tag |
| `last_mwh_tag` | Stromverbrauch des Werks an diesem Tag | MWh pro Tag | **Praxiskontakt, Interview 09.11.2026** (K-005): 50 MWh an jedem Tag inkl. Feiertage | Kommazahl | 50,0 |
| `last_mwh_flexibel_tag` | davon zeitlich verschiebbar | MWh pro Tag | **synthetisch, Platzhalter** bis der Prozess feststeht | Kommazahl | 2,0 |
| `imputed` | Wert wurde ergänzt | True/False | `src/cleaning.py` | bool | immer False (keine Imputation) |
| `flag_outlier` | auffälliger Preis: Betrag des modifizierten z-Werts > 3,5 im Vergleich mit gleichem Jahr, Monat und Stunde | True/False | `src/cleaning.py` (Iglewicz & Hoaglin 1993) | bool | ca. 4 % True |

**Achtung `flag_outlier`:** nur zur Beschreibung. Der Vergleich nutzt den ganzen Monat, also auch spätere Stunden. Eine Planungsstrategie darf die Spalte nie verwenden (Look-ahead); `src/datenzugriff.py` entfernt sie deshalb.

## `data/processed/last_synth.csv` (eine Zeile je Kalendertag, 1 765 Zeilen)

| Spalte | Bedeutung | Einheit | Quelle | Typ | Wertebereich |
| --- | --- | --- | --- | --- | --- |
| `datum` | Kalendertag (deutsche Zeit) | `JJJJ-MM-TT` | — | Text | 2022-01-01 bis 2026-10-31 |
| `mwh_gesamt` | Stromverbrauch des Werks | MWh pro Tag | Praxiskontakt (K-005) | Kommazahl | 50,0 an jedem Tag |
| `mwh_flexibel` | davon verschiebbar | MWh pro Tag | synthetisch, Platzhalter (`last.mwh_pro_tag`) | Kommazahl | 2,0 |

## Berichtstabellen `reports/tables/`

| Datei | Inhalt |
| --- | --- |
| `kennzahlen_monat.csv` | je Jahr und Monat: Stunden, Mittel, Median, Q25, Q75, IQR, Min, Max, Anteil negativer Stunden (%) |
| `kennzahlen_saison.csv` | dasselbe je Jahr und Saison |
| `tagesprofil_saison.csv` | dasselbe je Saison und Uhrzeit (über alle Jahre) |
| `zeitumstellung.csv` | lokale Tage mit 23 bzw. 25 Stunden |
| `luecken.csv` | Lücken mit Beginn (UTC) und Länge in Stunden (derzeit leer) |
| `ausreisser.csv` | alle Stunden mit `flag_outlier` und ihrem z-Wert |
