# Datenkatalog

| Merkmal | Quelle | Echt/synthetisch | Einheit | Skalenniveau | Auflösung | Zeitraum | Lücken (Anzahl) | Bekannte Fallstricke |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Day-Ahead-Preis DE-LU | SMARD 4169 | echt | EUR/MWh | Verhältnis (auch negativ) | 60 min, ab 01.10.2025 15 min | 2022–10/2026 | 0 (Abruf 07.11.2026, `results/tables/datenqualitaet.csv`) | Zeitumstellung, Zonenwechsel 2018, Anzeigeprobleme bis 09.10.2025, nachträgliche Korrekturen |
| Lastgang (`last_synth.parquet`: `datum`, `mwh`) | `src/02_synthetisch.py`, deterministisch | **synthetisch** | MWh pro Tag | Verhältnis | Tag | wie Preise (2022-01-01 bis Datenstand) | 0 | **Annahme:** `last.mwh_pro_werktag` = 2,0 MWh an jedem Werktag (Mo–Fr ohne Feiertage BY), 0 sonst; Leistung konstant 2,0 MWh / `blocklaenge_h` 6 h = 0,33 MW; rund 500 MWh/Jahr. Platzhalter, **vom Praxiskontakt zu plausibilisieren**. Nicht gegen Realität prüfbar, deshalb Sensitivität über Menge und Blocklänge |
| Werktag/Feiertag | Paket holidays (BY) | abgeleitet | – | nominal | Tag | wie Preise | 0 | Mariä Himmelfahrt nur regional |
| Stunde, Wochentag, Saison | abgeleitet | abgeleitet | – | ordinal/nominal | – | – | 0 | – |

Stichprobenumfang: Anzahl Testwochen je Periode eintragen; Wochen sind abhängig, effektive Stichprobe ist kleiner.
Keine personenbezogenen Daten.
