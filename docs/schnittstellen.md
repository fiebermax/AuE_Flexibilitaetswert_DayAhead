# Schnittstellen zwischen den Teilpaketen

Jede Übergabe ist eine **CSV-Datei** mit festen Spalten und Einheiten (Details: `docs/codebook.md`). Öffnen mit `pd.read_csv(...)` oder in Excel. Ändert sich eine Schnittstelle: Nachbarpaket informieren und Eintrag A-xxx im Projekttagebuch.

| Von → an | Datei | Spalten (Einheit) | Prüfung |
| --- | --- | --- | --- |
| R1 → alle | `config/params.yaml` | Annahmen, Zeiträume, Kosten | Review im Team |
| R2 → R3 | `data/processed/preise_clean.csv` | eine Zeile je UTC-Stunde; Schlüssel `ts_utc`; Spalten und Einheiten in `docs/codebook.md` | `tests/test_cleaning.py` grün |
| R2 → R3 | `data/processed/last_synth.csv` | `datum`, `mwh_gesamt` (50 MWh/Tag, Praxiskontakt), `mwh_flexibel` (Platzhalter) | `tests/test_pipeline.py` |
| R2 → alle | `reports/cleaning_log.md`, `reports/data_quality.md`, `reports/tables/*.csv` | Bereinigungsschritte mit Zählung, Kennzahlen, Grafiken | Grundlage Bericht Kap. 3 (K2) |
| R3 → R4 | `results/tables/backtest_wochen.csv` | `woche`, `periode`, `kosten_A` … `kosten_T` (EUR), `oracle` (EUR) | Summen gegen Tageswerte geprüft |
| R3 → R4 | `results/tables/ki_strategien.csv` | `strategie`, `periode`, `mittel_eur_woche`, `ki_unten`, `ki_oben`, `anteil_oracle` | Seed, Bootstrap-n |
| R4 → R1 | `results/tables/wirtschaftlichkeit.csv` | `szenario`, `ersparnis_eur_jahr`, `umstellungskosten_eur`, `break_even` | Review R1 |

## Schnellstart mit pandas

```python
import pandas as pd
preise = pd.read_csv("data/processed/preise_clean.csv")
preise.groupby("stunde_lokal")["preis_eur_mwh"].median()                    # typischer Preis je Uhrzeit
preise[preise["in_betriebszeit"]].groupby(["saison", "stunde_lokal"])["preis_eur_mwh"].median()
```

## Hinweise

- **Begriffe:** **Status quo A** = festes Fenster 08–14 Uhr Ortszeit (Kickoff-Definition, `last.status_quo_start_h`). Die Faustregel D (fester Block, vermutlich mittags) legt R3 im Backtest fest; 08–14 Uhr heißt nie „Faustregel“.
- **Schlüssel ist `ts_utc`.** In UTC gibt es keine doppelten oder fehlenden Stunden. Die lokale Zeit (`ts_lokal`, `stunde_lokal`) ist Zusatz: Am Oktober-Umstellungssonntag kommt 02:00 Uhr zweimal vor (zwei UTC-Stunden, zwei Preise), im März fehlt 02:00. Beides liegt außerhalb der Betriebszeit 06–22 Uhr.
- **Nur Stundenpreise**; ab 01.10.2025 der SMARD-Stundenwert (Mittel der vier Viertelstunden).
- **`flag_outlier` nie für die Planung nutzen** (Look-ahead, siehe Codebook).
- **Last:** 50 MWh pro Tag an jedem Tag (Praxiskontakt); verschiebbarer Anteil `mwh_flexibel` ist noch ein Platzhalter.

## Datenzugriff je Freitag: `src/datenzugriff.py` (für R3)

Für den Backtest, damit keine Daten aus der Zukunft benutzt werden:

```python
import datenzugriff as dz
preise, last = dz.lade_preise(), dz.lade_last()
for w in dz.planungswochen(preise, last, "test_1_stunde", historie_wochen=4):   # None = alle Daten bis zum Freitag
    w.historie     # Preise, die am Freitag bekannt waren
    w.zielwoche    # echte Preise der geplanten Woche (Mo bis So), zum Nachrechnen
    w.last         # Last dieser Woche (mwh_gesamt, mwh_flexibel)
```

- Perioden aus `zeitraeume` in `params.yaml`: `training` (104 Freitage), `test_1_stunde` (38), `test_2_viertel` (51), `stresstest` (51).
- Planung freitags 12:00: bekannt sind Preise bis Freitag 23:00 (die Samstagspreise kommen erst gegen 12:45).
- Nur volle Wochen je Periode; bricht mit `LookAheadFehler` ab, wenn Zukunftsdaten in die Historie geraten.

## Folien und Kennzahlen R2: `src/build_presentation.py`

- `python src/build_presentation.py` erzeugt `output/R2_Datenanalyse.pptx` und `pptx_kit/` (Kennzahlen, Grafiken, Prüferfragen, Quellen).
- `pptx_kit/key_figures.json` ist die einzige Quelle für Zahlen auf den Folien (je Kennzahl: Wert, Einheit, Zeitraum, Skript, Commit, Status ERGEBNIS / HYPOTHESE / ANNAHME).
- Rückblick-Kennzahl „Mehrkosten Status quo A gegenüber billigstem 6-h-Fenster“ (`src/fensteranalyse.py`): beschreibend, keine Strategie.
