# Schnittstellen zwischen den Teilpaketen

Jede Übergabe ist eine **CSV-Datei** mit festen Spalten und Einheiten (Details: `docs/codebook.md`). Öffnen mit `pd.read_csv(...)` oder in Excel. Ändert sich eine Schnittstelle: Nachbarpaket informieren und Eintrag A-xxx im Projekttagebuch.

| Von → an | Datei | Spalten (Einheit) | Prüfung |
| --- | --- | --- | --- |
| R1 → alle | `config/params.yaml` | Annahmen, Zeiträume, Kosten | Review im Team |
| R2 → R3 | `data/processed/preise_clean.csv` | eine Zeile je UTC-Stunde; Schlüssel `ts_utc`; Spalten und Einheiten in `docs/codebook.md` | `tests/test_cleaning.py` grün |
| R2 → R3 | `data/processed/last_synth.csv` | `datum`, `mwh_gesamt` (180 MWh/Tag, Praxiskontakt), `mwh_flexibel` (8 MWh Reinigung in der Nacht ab `datum` 22 Uhr) | `tests/test_pipeline.py` |
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

- **Begriffe:** **Status quo A** = Reinigung 22–24 Uhr Ortszeit, direkt nach Produktionsende (Annahme, E-031; `last.status_quo_start_h`). Die Reinigung (2 h, `last.blocklaenge_h`) darf nur im **Reinigungsfenster** 22–06 Uhr liegen (`last.fenster_start_h`, `last.fenster_ende_h`). Die Faustregel D (fester Block in der Nacht) legt R3 im Backtest fest; 22–24 Uhr heißt nie „Faustregel“. **Kontrastfall T** ist die Kälte (Block `kaelte`), täglich mit bekannten Preisen gesteuert.
- **Nacht über die Wochengrenze (A-010):** Die Nacht von Sonntag auf Montag gehört zum Sonntag der Zielwoche, ihre Stunden 00–06 Uhr liegen aber schon in der Folgewoche und fehlen in `w.zielwoche` (Mo 00:00 bis So 24:00). R3 entscheidet, ob die Sonntagsnacht mitgewertet wird (dann Preise bis Montag 06:00 nachladen) oder entfällt.
- **Mehrkosten-Rückblick:** `src/fensteranalyse.py` bewertet Nächte als Folge echter Stunden; die Funktion `fenster_je_tag(df, 22, 6, 2, 22)` kann R3 für die Bewertung je Nacht wiederverwenden.
- **Schlüssel ist `ts_utc`.** In UTC gibt es keine doppelten oder fehlenden Stunden. Die lokale Zeit (`ts_lokal`, `stunde_lokal`) ist Zusatz: Am Oktober-Umstellungssonntag kommt 02:00 Uhr zweimal vor (zwei UTC-Stunden, zwei Preise), im März fehlt 02:00. Beides liegt außerhalb der Betriebszeit 06–22 Uhr, aber **im Reinigungsfenster 22–06 Uhr**: Diese Nächte haben 7 bzw. 9 echte Stunden (E-036).
- **Nur Stundenpreise**; ab 01.10.2025 der SMARD-Stundenwert (Mittel der vier Viertelstunden).
- **`flag_outlier` nie für die Planung nutzen** (Look-ahead, siehe Codebook).
- **Last:** 180 MWh pro Tag an jedem Tag (Praxiskontakt, K-008); verschiebbar ist die Reinigung mit 8 MWh pro Nacht (4 MW × 2 h).

## Einfache Abfrage einzelner Tage: `src/preisabfrage.py` (für alle, A-011)

`tag("2026-10-15")`, `tage("2026-08-01", "2026-08-31")`, `letzte_monate(3, wochentag="Samstag")` liefern je Stunde die Spalten `datum`, `wochentag` (Montag … Sonntag), `uhrzeit` ("14:00"), `stunde` (14), `preis` (€/MWh), `saison`, `werktag` und `zeit` (eindeutiger Zeitstempel mit UTC-Versatz). Nur zum Anschauen und für Grafiken; **nie** als Eingabe einer Planungsstrategie, dafür gibt es `datenzugriff.py` mit Look-ahead-Schutz.

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
- Planung Freitagmorgen 08:00 (K-008 P11): bekannt sind Preise bis Freitag 23:00 (die Samstagspreise kommen erst gegen 12:45). Gegenüber 12:00 ändert sich die Datengrenze nicht.
- Nur volle Wochen je Periode; bricht mit `LookAheadFehler` ab, wenn Zukunftsdaten in die Historie geraten.

## Folien und Kennzahlen R2: `src/build_presentation.py`

- `python src/build_presentation.py` erzeugt `output/R2_Datenanalyse.pptx` und `pptx_kit/` (Kennzahlen, Grafiken, Prüferfragen, Quellen).
- `pptx_kit/key_figures.json` ist die einzige Quelle für Zahlen auf den Folien (je Kennzahl: Wert, Einheit, Zeitraum, Skript, Commit, Status ERGEBNIS / HYPOTHESE / ANNAHME).
- Rückblick-Kennzahl „Mehrkosten Status quo A (Reinigung 22–24 Uhr) gegenüber billigstem 2-h-Fenster in 22–06 Uhr“ (`src/fensteranalyse.py`, Tabellen `reports/tables/reinigungsfenster_*.csv`): beschreibend, keine Strategie.
- **Stand 10.11.2026:** Das Folienskript ist noch nicht auf den Reinigungsfall umgestellt und bricht mit den neuen Parametern ab; `output/R2_Datenanalyse.pptx` und `pptx_kit/` zeigen den alten Fall (08–14 Uhr). Folien werden erst am Ende neu gebaut, wenn der Code steht (E-037).
