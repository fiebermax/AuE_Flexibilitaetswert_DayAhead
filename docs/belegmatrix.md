# Belegmatrix

Wir führen den Bewertungsbogen des Prüfers (Katalog 7.1) selbst. Ziel: Stufe 5 in jedem Kriterium. Eine Stufe ohne Beleg wird nicht vergeben (Katalog 6.1). Vor der Abgabe muss jede Zeile einen Beleg haben.

Status: ⬜ offen · 🟨 in Arbeit · ✅ belegt

| K | Kriterium (Gewicht) | Stufe-5-Anforderung (Kurzform) | Beleg (Seite, Commit, Tagebuch) | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| K1 | Fragestellung (10) | Rückkopplung mit Praxispartner; Entscheider und Zeitpunkt; Nullhypothesen | Tagebuch E-005, Gesprächsprotokoll, Bericht Kap. 2 | R1 | 🟨 |
| K2 | Datenqualität (12) | Datenqualität aktiv geprüft (Sensitivitätsrechnung) | Qualitätsbericht, Sensitivitätstabelle | R2 | ⬜ |
| K3 | Aufbereitung (12) | Eigene Merkmalskonstruktion verbessert das Ergebnis in Euro; Ausreißer als Information | Merkmalsdoku, Tabelle mit/ohne saisonalem Block | R3, R2 | ⬜ |
| K4 | Methode (12) | Methodenklasse mit Daten hinterfragt (braucht es eine Prognose?) | Validierungsprotokoll, Ergebnistabelle | R3 | ⬜ |
| K5 | Umsetzung (10) | Datentests, Schnittstellen dokumentiert, Dritte wenden es auf neue Daten an | `tests/`, `docs/schnittstellen.md`, Reproduktionsprotokoll | R2 | 🟨 |
| K6 | Interpretation (12) | Gegenbelege: anderer Zeitraum, Kipppunkte, Scheinkorrelation; negatives Ergebnis klar | Ergebniskapitel, Kipppunkt-Tabelle | R4 | ⬜ |
| K7 | Verwertung (10) | Empfehlung im Prozess: wer, Grundlage, was anders, Kennzahl, nachsteuern, Rücknahme | Prozesstabelle, Wirtschaftlichkeitsrechnung | R4, R1 | ⬜ |
| K8 | Visualisierung (8) | Für die Werksleitung ohne Vorlesungswissen verständlich; interaktiv nur mit Nutzen | Abbildungen, Break-even-Rechner | R1 | ⬜ |
| K9 | Kommunikation (8) | Schnittstellen erklären, Team vertreten, Fehler und verworfene Wege offen | Probelauf, Kapitel „Verworfene Wege“ | alle | ⬜ |
| K10 | Teamarbeit (6) | Über das eigene Paket hinaus: roter Faden, Konflikte moderieren, einspringen, befähigen | Tagebuch P- und M-Einträge, Reviews, Peer | jede Person | 🟨 |

## Sperrkriterien

| Sperrkriterium | Absicherung | Status |
| --- | --- | --- |
| Reproduzierbarkeit | `run_all.py`, fester Seed, Tests, Reproduktionstest durch Dritte | ⬜ |
| Datenherkunft und Datenschutz | `data/raw/SOURCES.md`, synthetische Daten gekennzeichnet, keine personenbezogenen Daten | 🟨 |
| Kennzeichnung fremder Beiträge | `docs/ki-nutzung.md`, Dateiköpfe, Commit-Trailer | 🟨 |
| Erklärbarkeit in der Verteidigung | Probelauf mit Kreuzfragen | ⬜ |
