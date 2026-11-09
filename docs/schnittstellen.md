# Schnittstellen zwischen den Teilpaketen

Jede Übergabe ist eine **CSV-Datei** mit festen Spalten und Einheiten. Öffnen mit `pd.read_csv(...)` oder in Excel. Ändert sich eine Schnittstelle: Nachbarpaket informieren und Eintrag A-xxx im Projekttagebuch.

| Von → an | Datei | Spalten (Einheit) | Prüfung |
| --- | --- | --- | --- |
| R1 → alle | `config/params.yaml` | Annahmen, Zeiträume, Kosten | Review im Team |
| R2 → R3 | `data/processed/preise_h.csv` | `zeit` (Stundenbeginn, deutsche Zeit mit UTC-Versatz, z. B. `2025-01-06 08:00:00+01:00`), `datum` (JJJJ-MM-TT), `stunde` (0–23), `preis_eur_mwh` (EUR/MWh), `regime` (`stunde` bis 30.09.2025, `viertel` ab 01.10.2025), `werktag` (True/False) | `tests/test_datenannahmen.py` grün |
| R2 → R3 | `data/processed/last_synth.csv` | `datum` (JJJJ-MM-TT), `mwh` (MWh pro Tag) | deterministisch aus `last.*` in `params.yaml`; gleiche Werktage wie `preise_h.csv` (Test) |
| R2 → alle | `data/processed/zeitumstellung.csv` | `datum`, `stunden_roh`, `stunden_aufbereitet`, `art` | Liste der Umstellungstage |
| R2 → alle | `results/tables/datenqualitaet.csv` | je `jahr`: Stunden, Lücken, negative Preise, Min/Mittel/Max (EUR/MWh) | Grundlage Bericht Kap. 3 (K2) |
| R3 → R4 | `results/tables/backtest_wochen.csv` | `woche`, `periode`, `kosten_A` … `kosten_T` (EUR), `oracle` (EUR) | Summen gegen Tageswerte geprüft |
| R3 → R4 | `results/tables/ki_strategien.csv` | `strategie`, `periode`, `mittel_eur_woche`, `ki_unten`, `ki_oben`, `anteil_oracle` | Seed, Bootstrap-n |
| R4 → R1 | `results/tables/wirtschaftlichkeit.csv` | `szenario`, `ersparnis_eur_jahr`, `umstellungskosten_eur`, `break_even` | Review R1 |

## Schnellstart mit pandas

```python
import pandas as pd
preise = pd.read_csv("data/processed/preise_h.csv")
preise.groupby("stunde")["preis_eur_mwh"].mean()          # Durchschnittspreis je Uhrzeit
preise[preise["werktag"]].groupby("stunde")["preis_eur_mwh"].mean()   # nur Werktage
last = pd.read_csv("data/processed/last_synth.csv")
```

## Hinweise zu den Preisen

- **Nur Stundenpreise** (Tagebuch E-021). Ab 01.10.2025 ist das der Stundenwert, den SMARD aus den vier Viertelstunden bildet.
- **Zeitumstellung:** Im März hat ein Tag 23 Zeilen (02:00 fehlt), im Oktober ist 02:00 das Mittel der beiden 02:00-Stunden. Beides ist immer sonntags, also ohne Last (E-018).
- **Lücken** stünden als Zeile mit leerem Preis drin; Stand Abruf 07.11.2026: keine.

## Hinweise zur Last

- Ein Eintrag je Kalendertag; an Nicht-Werktagen `mwh = 0`.
- Nur die Tagesmenge. Wann sie verbraucht wird, entscheidet die Strategie (R3).
- Platzhalter: 2,0 MWh pro Werktag im 6-Stunden-Block. Laut Praxiskontakt läuft die Produktion 16 Stunden am Tag (K-003); der Block muss innerhalb dieser Betriebszeit liegen. Wann die 16 Stunden beginnen, ist noch offen (`last.betrieb_start_h`).

## Datenzugriff je Freitag: `src/datenzugriff.py` (für R3)

Für den Backtest, damit keine Daten aus der Zukunft benutzt werden:

```python
import datenzugriff as dz
preise, last = dz.lade_preise(), dz.lade_last()
for w in dz.planungswochen(preise, last, "test_1_stunde", historie_wochen=4):   # None = alle Daten bis zum Freitag
    w.historie     # Preise, die am Freitag bekannt waren
    w.zielwoche    # echte Preise der geplanten Woche (Mo bis So), zum Nachrechnen
    w.last         # Last dieser Woche
```

- Perioden aus `zeitraeume` in `params.yaml`: `training` (104 Freitage), `test_1_stunde` (38), `test_2_viertel` (51), `stresstest` (51).
- Planung freitags 12:00: bekannt sind Preise bis Freitag 23:00 (die Samstagspreise kommen erst gegen 12:45).
- Nur volle Wochen je Periode; bricht mit `LookAheadFehler` ab, wenn Zukunftsdaten in die Historie geraten.
