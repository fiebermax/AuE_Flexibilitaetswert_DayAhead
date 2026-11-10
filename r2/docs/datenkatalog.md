# Datenkatalog

| Merkmal | Quelle | Echt/synthetisch | Einheit | Skalenniveau | Auflösung | Zeitraum | Lücken (Anzahl) | Bekannte Fallstricke |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Day-Ahead-Preis DE-LU (`preis_eur_mwh`) | SMARD 4169 | echt | EUR/MWh | Verhältnis (auch negativ) | 60 min; ab 01.10.2025 SMARD-Stundenwert aus 4 Viertelstunden | 2022–10/2026, 42 360 UTC-Stunden | 0 (`r2/ergebnisse/cleaning_log.md`) | Zeitumstellung (UTC als Schlüssel), Zonenwechsel 2018, Umstellung auf 15 min am 01.10.2025, nachträgliche Korrekturen (eingefrorene Rohdaten) |
| Stromverbrauch Werk (`mwh_gesamt`) | Praxiskontakt, Interview 09.11.2026 (K-005) | Praxisangabe | MWh pro Tag | Verhältnis | Tag | wie Preise | 0 | 50 MWh an jedem Tag inkl. Feiertage; Betrieb 06–22 Uhr; Einzelangabe, nicht gemessen |
| verschiebbarer Anteil (`mwh_flexibel`) | `r2/src/02_synthetisch.py` | **synthetisch** | MWh pro Tag | Verhältnis | Tag | wie Preise | 0 | **Platzhalter 2,0 MWh**, Prozess und Menge noch festzulegen; Sensitivität über Menge und Blocklänge |
| Werktag/Feiertag | Paket holidays (BY) | abgeleitet | – | nominal | Tag | wie Preise | 0 | Mariä Himmelfahrt nur regional |
| Stunde, Wochentag, Saison | abgeleitet | abgeleitet | – | ordinal/nominal | – | – | 0 | – |

Stichprobenumfang: Test 1 = 38 Wochen, Test 2 = 51 Wochen, Stresstest 2022 = 51 Wochen, Training = 104 Wochen (`src/datenzugriff.py`, nur volle Wochen). Wochen sind abhängig (Saison, Preisniveau), die effektive Stichprobe ist kleiner; deshalb Block-Bootstrap (R3).
Keine personenbezogenen Daten.
