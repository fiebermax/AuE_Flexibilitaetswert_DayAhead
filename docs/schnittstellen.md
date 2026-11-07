# Schnittstellen zwischen den Teilpaketen

Jede Übergabe ist eine Datei mit festen Spalten und Einheiten. Ändert sich eine Schnittstelle: Nachbarpaket informieren und Eintrag A-xxx im Projekttagebuch.

| Von → an | Datei | Spalten (Einheit) | Prüfung |
| --- | --- | --- | --- |
| R1 → alle | `config/params.yaml` | Annahmen, Zeiträume, Kosten | Review im Team |
| R2 → R3 | `data/processed/preise_h.parquet` | `zeit` (Europe/Berlin, Stundenbeginn), `preis_eur_mwh`, `regime` (stunde/viertel), `werktag` (bool) | `tests/test_datenannahmen.py` grün |
| R2 → R3 | `data/processed/last_synth.parquet` | `datum`, `mwh` | Seed aus `params.yaml` |
| R3 → R4 | `results/tables/backtest_wochen.csv` | `woche`, `periode`, `kosten_A` … `kosten_T` (EUR), `oracle` (EUR) | Summen gegen Tageswerte geprüft |
| R3 → R4 | `results/tables/ki_strategien.csv` | `strategie`, `periode`, `mittel_eur_woche`, `ki_unten`, `ki_oben`, `anteil_oracle` | Seed, Bootstrap-n |
| R4 → R1 | `results/tables/wirtschaftlichkeit.csv` | `szenario`, `ersparnis_eur_jahr`, `umstellungskosten_eur`, `break_even` | Review R1 |
