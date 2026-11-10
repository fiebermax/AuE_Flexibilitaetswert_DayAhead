# Cleaning-Log

Erzeugt von `r2/src/cleaning.py`. Eingabe: `data/raw/` (unverändert), `data/last_synth.csv`. Ausgabe: `data/preise_clean.csv`.

| Schritt | Regel | N vorher | N nachher | betroffene Zeilen | Begründung |
| --- | --- | --- | --- | --- | --- |
| 0 Rohdaten prüfen | SHA-256 jeder Rohdatei = Wert im Manifest | 253 | 253 | 0 | Rohdaten unverändert, Herkunft belegt (data/raw/manifest.csv) |
| 1 Einlesen | alle Wochendateien untereinander, Zeitstempel UTC | 42504 | 42504 | 0 | Wochendateien von SMARD (Mo 00:00 bis So 24:00 deutscher Zeit) |
| 2 Dubletten | exakt: einer bleibt; widersprüchlich: Abbruch | 42504 | 42504 | 0 | 0 exakte, 0 widersprüchliche Dubletten |
| 3 Zeitraum | 01.01.2022 00:00 bis 31.10.2026 24:00 deutscher Zeit | 42504 | 42360 | 144 | Randtage der ersten und letzten Wochendatei liegen außerhalb des Untersuchungszeitraums |
| 4 Auflösung | Abstand aufeinanderfolgender Zeitstempel = 60 min | 42360 | 42360 | 0 | SMARD-Stundenwerte; ab 01.10.2025 Mittel der 4 Viertelstunden (SDAC 15-min-MTU, Lieferung ab 01.10.2025) |
| 5 Vollständigkeit | erwartetes UTC-Stundenraster; fehlende Stunden als leere Zeile, Flag imputed | 42360 | 42360 | 0 | 0 Lücken; keine Imputation ohne Rückfrage |
| 6 Zeitumstellung | lokale Zeit aus UTC; 23-/25-Stunden-Tage auflisten, nichts mitteln | 42360 | 42360 | 10 | die doppelte Oktober-Stunde sind zwei verschiedene UTC-Stunden, keine Dubletten |
| 7 Plausibilität | -500 <= Preis <= 5000 EUR/MWh (SDAC-Preisgrenzen) | 42360 | 42360 | 0 | negative Preise und Spitzen sind gültig und bleiben |
| 8 Auffällige Werte | Betrag modifizierter z-Wert > 3.5 je Jahr x Monat x Stunde | 42360 | 42360 | 1827 | nur markiert (flag_outlier), nichts gelöscht; nur zur Beschreibung, nicht für die Planung |
| 9 Join Last | Schlüssel: lokales Datum aus UTC-Zeitstempel; last_synth.csv (synthetisch) | 42360 | 42360 | 0 | 0 Preisstunden ohne Last, 0 Lasttage ohne Preis |
