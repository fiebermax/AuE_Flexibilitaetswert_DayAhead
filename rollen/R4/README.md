# R4 · Produktion & Schichtplanung

Arbeitsbereich der Rolle: alle Aufgaben mit Status und Beleg. **Code, Daten und Ergebnisse liegen in `src/`, `data/`, `results/`** (Pipeline mit einem Befehl, K5); die Links unten führen direkt zu den Dateien.

Status: ✅ erledigt · 🟨 in Arbeit · ⬜ offen. Stand 09.11.2026.

| | |
| --- | --- |
| Person | offen |
| Kernfrage | Lohnt sich die Umstellung, und wann kippt sie? |
| Führt | Ergebnis & Verwertung: Umstellungskosten, Stresstests, Kipppunkte, Break-even, Empfehlung mit Kennzahl und Rücknahmeregel |
| Wirkt mit | Fachlicher Rahmen (R1) |
| Kriterien | K6, K7 |
| Vertretung | R1 |
| Review-Partner | R1 (kein Merge nach `main` ohne dessen Review) |

## Aufgaben (0 von 10 erledigt)

| # | Aufgabe | Ergebnis / Datei | Termin | Status | Beleg / Hinweis |
| --- | --- | --- | --- | --- | --- |
| 1 | Problem Statement mit R1 | Folien 1 und 2 | So 08.11. | ⬜ |  |
| 2 | Eigene Rolle im Format a) bis d) | Folie 5 | Mo 09.11. | ⬜ |  |
| 3 | Umstellungskosten und Tarifzuschlag mit Quellen | [`config/params.yaml`](../../config/params.yaml) (`kosten.*`) | nach dem Pitch | ⬜ | Review R1 |
| 4 | Festpreisangebot ableiten | [`config/params.yaml`](../../config/params.yaml) (`kosten.festpreis_*`) | nach dem Pitch | ⬜ |  |
| 5 | 3–5 Literaturquellen zu Lastflexibilität (mit R1) | Quellenliste | vor 13.11. | ⬜ |  |
| 6 | **Schritt 05:** Stresstest 2022, Kipppunkte, Break-even, Spot gegen Festpreis | [`src/05_bewertung.py`](../../src/05_bewertung.py) | Sa 14.11. | ⬜ | K6 S5 |
| 7 | Break-even als Kurve; Empfehlung mit Kennzahl und Rücknahmeregel | `results/tables/wirtschaftlichkeit.csv` | So 15.11. | ⬜ | K7 S5 |
| 8 | Prozesstabelle (wer, Grundlage, was anders, Kennzahl, nachsteuern, zurücknehmen) | Bericht Kap. 7 | So 15.11. | ⬜ | K7 S5 |
| 9 | Bericht Kap. 6 (Ergebnisse) und Kap. 7 (Empfehlung) | Bericht | bis Abgabe | ⬜ |  |
| 10 | Verantwortungsnachweis | diese Datei, Abschnitt unten | bis Abgabe | ⬜ |  |

## Schnittstellen (Details in `docs/schnittstellen.md`)

**Erhält:**
- Von R3: `results/tables/backtest_wochen.csv`, `results/tables/ki_strategien.csv`
- Von R1: Rahmen, Entscheider, Zeitpunkt

**Übergibt:**
- An R1: `results/tables/wirtschaftlichkeit.csv`

## Verantwortungsnachweis (2–3 Seiten, Gliederung laut Kickoff)

1. a) Aufgabenstellung des eigenen Pakets
2. b) Problematik im Paket
3. c) Methode: getroffene Entscheidungen und begründete Alternativen (Verweise auf Tagebuch-E-Einträge)
4. d) Beitrag zum Gesamterfolg, Schnittstellen (erhält von, übergibt an)
5. Eigene Fehler und verworfene Wege (K9 Stufe 5)
6. Belegliste: Commits, Tagebucheinträge, Berichtsseiten

## Notizen

*(Arbeitsnotizen, Ideen, offene Fragen. Entscheidungen und Absprachen gehören zusätzlich ins `docs/projekttagebuch.md`.)*
