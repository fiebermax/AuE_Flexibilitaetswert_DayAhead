# Schnittstellen zwischen den Teilpaketen

Jede Übergabe ist eine **CSV-Datei** mit festen Spalten und Einheiten (Details: `docs/codebook.md`). Öffnen mit `pd.read_csv(...)` oder in Excel. Ändert sich eine Schnittstelle: Nachbarpaket informieren und Eintrag A-xxx im Projekttagebuch.

| Von → an | Datei | Spalten (Einheit) | Prüfung |
| --- | --- | --- | --- |
| R1 → alle | `params.yaml` | Annahmen, Zeiträume, Kosten | Review im Team |
| R2 → R3 | `data/preise_clean.csv` | eine Zeile je UTC-Stunde; Schlüssel `ts_utc`; Spalten und Einheiten in `docs/codebook.md` | `tests/test_cleaning.py` grün |
| R2 → R3 | `data/last_synth.csv` | `datum`, `mwh_gesamt` (180 MWh/Tag, Praxiskontakt), `mwh_flexibel` (8 MWh Reinigung in der Nacht ab `datum` 22 Uhr) | `tests/test_pipeline.py` |
| R2 → alle | `r2/ergebnisse/cleaning_log.md`, `r2/ergebnisse/data_quality.md`, `r2/ergebnisse/*.csv` | Bereinigungsschritte mit Zählung, Kennzahlen, Grafiken | Grundlage Bericht Kap. 3 (K2) |
| R3 → R4 | `ergebnisse/blockkosten_nacht.csv` | je Nacht × 2-h-Block: `nacht`, `wochentag_nacht`, `saison`, `n_stunden_nacht`, `pos`, `start_lokal`, `start_utc`, `preis_eur_mwh` (€/MWh), `sonntag_h`, `feiertag_h` (Stunden des Blocks) | `tests/test_merkmale.py` (Abgleich mit R2) |
| R3 → R4 | `ergebnisse/backtest_naechte.csv` | je Nacht × Strategie: `periode`, `woche`, `nacht`, `strategie`, `start_lokal`, `start_utc`, `preis_eur_mwh`, `mwh`, `kosten_eur` (nur Strom), `sonntag_h`, `feiertag_h` | `pruefen()` in `src/04_strategien.py` |
| R3 → R4 | `ergebnisse/backtest_wochen.csv` | `periode`, `woche` (Montag), `kosten_A`, `kosten_D`, `kosten_D_saison`, `kosten_B`, `kosten_B_ohne_wochentag`, `kosten_C` (EUR, nur Strom; C = Oracle; leer, wenn eine Strategie nicht alle 7 Nächte plant) | Wochensumme = Summe der Nächte, `pruefen()` |
| R3 → R4 | `ergebnisse/ki_strategien.csv` | Ersparnis gegenüber A je `strategie`, `periode` (training, test_1_stunde, test_2_viertel, test_gesamt, stresstest), `vertrag` (band/proportional), `faktor`, `n_wochen`, `mittel_eur_woche`, `ki_unten`, `ki_oben` (95 % t), `boot_unten`, `boot_oben` (Block-Bootstrap), `eur_jahr`, `anteil_oracle` (EUR, nur Strom) | Seed 42, 5 000 Wiederholungen, Tests in `tests/test_strategien.py` |
| R3 → R4, R1 | `ergebnisse/hypothesentests.csv` | H0b, H0c (Kipppunkt `untere_schranke` = m*), K3-Vergleiche je Periode: `shapiro_p`, `t`, `p_t`, `p_wilcoxon`, `schwelle`, `h0_verworfen`, `robust`, `konfirmatorisch` | Entscheidung nur `test_gesamt` (`docs/hypothesen.md`) |
| R3 → alle | `ergebnisse/fehleranalyse_b.csv` | Bedauern von B (B − C) und B − D in €/Nacht, Trefferquote, je Periode × Saison bzw. Wochentag | explorativ |
| R4 → R1 | `ergebnisse/wirtschaftlichkeit.csv` | `szenario`, `ersparnis_eur_jahr`, `umstellungskosten_eur`, `break_even` | Review R1 |

## Schnellstart mit pandas

```python
import pandas as pd
preise = pd.read_csv("data/preise_clean.csv")
preise.groupby("stunde_lokal")["preis_eur_mwh"].median()                    # typischer Preis je Uhrzeit
preise[preise["in_betriebszeit"]].groupby(["saison", "stunde_lokal"])["preis_eur_mwh"].median()
```

## Hinweise

- **Begriffe:** **Status quo A** = Reinigung 22–24 Uhr Ortszeit, direkt nach Produktionsende (Tatsache, vom Praxispartner bestätigt am 10.11.2026, K-012; `last.status_quo_start_h`). Die Reinigung (2 h, `last.blocklaenge_h`) darf nur im **Reinigungsfenster** 22–06 Uhr liegen (`last.fenster_start_h`, `last.fenster_ende_h`). Die Faustregel D (fester Block in der Nacht) legt R3 im Backtest fest; 22–24 Uhr heißt nie „Faustregel“. Untersucht wird nur die Reinigung; Kälte und Kontrastfall T sind Nichtziel (E-043).
- **Nacht über die Wochengrenze (A-010):** Die Nacht von Sonntag auf Montag gehört zum Sonntag der Zielwoche, ihre Stunden 00–06 Uhr liegen aber schon in der Folgewoche und fehlen in `w.zielwoche` (Mo 00:00 bis So 24:00). Entschieden (E-044): Die Sonntagsnacht wird mitgewertet; die Kosten der Nächte kommen aus der Blockkosten-Matrix von `src/03_merkmale.py`, die die Stunden bis Montag 06:00 enthält.
- **Mehrkosten-Rückblick:** `src/fensteranalyse.py` bewertet Nächte als Folge echter Stunden; die Funktion `fenster_je_tag(df, 22, 6, 2, 22)` kann R3 für die Bewertung je Nacht wiederverwenden.
- **Schlüssel ist `ts_utc`.** In UTC gibt es keine doppelten oder fehlenden Stunden. Die lokale Zeit (`ts_lokal`, `stunde_lokal`) ist Zusatz: Am Oktober-Umstellungssonntag kommt 02:00 Uhr zweimal vor (zwei UTC-Stunden, zwei Preise), im März fehlt 02:00. Beides liegt außerhalb der Betriebszeit 06–22 Uhr, aber **im Reinigungsfenster 22–06 Uhr**: Diese Nächte haben 7 bzw. 9 echte Stunden (E-036).
- **Nur Stundenpreise**; ab 01.10.2025 der SMARD-Stundenwert (Mittel der vier Viertelstunden).
- **`flag_outlier` nie für die Planung nutzen** (Look-ahead, siehe Codebook).
- **Kosten:** R3 rechnet nur Stromkosten, R4 die Personalkosten mit Zuschlägen (A-017). Für die Zuschläge zählt der Kalendertag der Stunde (Spalten `sonntag`, `feiertag`, A-016).
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

## Rückblick-Kennzahl R2

- „Mehrkosten Status quo A (Reinigung 22–24 Uhr) gegenüber billigstem 2-h-Fenster in 22–06 Uhr“ (`src/fensteranalyse.py`, Tabellen `r2/ergebnisse/reinigungsfenster_*.csv`): beschreibend, keine Strategie.
- Präsentationsfolien entstehen am Ende mit Claude, nicht per Skript im Repo (E-039).
