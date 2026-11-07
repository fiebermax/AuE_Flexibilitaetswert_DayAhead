# Schnittstellen zwischen den Teilpaketen

Jede Übergabe ist eine Datei mit festen Spalten und Einheiten. Ändert sich eine Schnittstelle: Nachbarpaket informieren und Eintrag A-xxx im Projekttagebuch.

| Von → an | Datei | Spalten (Einheit) | Prüfung |
| --- | --- | --- | --- |
| R1 → alle | `config/params.yaml` | Annahmen, Zeiträume, Kosten | Review im Team |
| R2 → R3 | `data/processed/preise_h.parquet` | `zeit` (Europe/Berlin, Stundenbeginn), `preis_eur_mwh`, `regime` (stunde/viertel), `werktag` (bool) | `tests/test_datenannahmen.py` grün |
| R2 → R3 | `data/processed/preise_15min.parquet` | wie `preise_h`, `zeit` = Beginn der Viertelstunde; nur ab 01.10.2025 | für die Sensitivität 15 statt 60 min; Stundenmittel = `preise_h` (Test) |
| R2 → alle | `data/processed/zeitumstellung.csv` | `aufloesung`, `datum`, `zeitpunkte_roh`, `zeitpunkte_aufbereitet`, `art` | Liste der Umstellungstage |
| R2 → alle | `results/tables/datenqualitaet.csv` | je `aufloesung`, `jahr`, `regime`: Zeitpunkte, Lücken, Duplikate, Umstellungstage, negative Preise, Min/Mittel/Max (EUR/MWh), Abweichung Stundenmittel gegen SMARD-Stundenwert (EUR/MWh) | Grundlage Qualitätsbericht (K2) |
| R2 → R3 | `data/processed/last_synth.parquet` | `datum`, `mwh` | Seed aus `params.yaml` |
| R3 → R4 | `results/tables/backtest_wochen.csv` | `woche`, `periode`, `kosten_A` … `kosten_T` (EUR), `oracle` (EUR) | Summen gegen Tageswerte geprüft |
| R3 → R4 | `results/tables/ki_strategien.csv` | `strategie`, `periode`, `mittel_eur_woche`, `ki_unten`, `ki_oben`, `anteil_oracle` | Seed, Bootstrap-n |
| R4 → R1 | `results/tables/wirtschaftlichkeit.csv` | `szenario`, `ersparnis_eur_jahr`, `umstellungskosten_eur`, `break_even` | Review R1 |

## Hinweise zu `preise_h.parquet` (R2 → R3)

- **Zeitumstellung März:** Der Tag hat 23 Zeilen, 02:00 Uhr fehlt (existiert nicht). Ein Block über 02:00 Uhr umfasst an diesem Tag nur 5 echte Stunden.
- **Zeitumstellung Oktober:** 02:00 Uhr ist das Mittel der beiden 02:00-Stunden; der Tag hat 24 Zeilen.
- **Ab 01.10.2025:** `preis_eur_mwh` ist das Mittel der vier Viertelstunden (nur wenn alle vier vorhanden sind).
- **Echte Lücken** stünden als Zeile mit leerem Preis drin; Stand Abruf 07.11.2026: keine.
