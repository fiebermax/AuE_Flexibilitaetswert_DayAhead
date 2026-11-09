# R4 · Produktion & Schichtplanung

Arbeitsbereich der Rolle. **Code, Daten und Ergebnisse bleiben in `src/`, `data/`, `results/`**, damit die Pipeline mit einem Befehl läuft (K5). Hier steht, was davon zu dieser Rolle gehört, plus Notizen und der Entwurf des Verantwortungsnachweises.

| | |
| --- | --- |
| Person | offen |
| Kernfrage | Lohnt sich die Umstellung, und wann kippt sie? |
| Führt | Ergebnis & Verwertung: Umstellungskosten, Stresstests, Kipppunkte, Break-even, Empfehlung mit Kennzahl und Rücknahmeregel |
| Wirkt mit | Fachlicher Rahmen (R1) |
| Kriterien | K6, K7 |
| Vertretung | R1 |

## Meine Dateien im Repo

- `src/05_bewertung.py`: Stresstest 2022, Kipppunkte, Break-even, Spot gegen Festpreis, Grafiken
- Kostenannahmen in `config/params.yaml` (`kosten.*`, mit Quellen; Review R1)
- Ergebniskapitel, Wirtschaftlichkeitsrechnung, Prozesstabelle

## Schnittstellen (Details in `docs/schnittstellen.md`)

**Erhält:**
- Von R3: `results/tables/backtest_wochen.csv`, `results/tables/ki_strategien.csv`
- Von R1: Rahmen, Entscheider, Zeitpunkt

**Übergibt:**
- An R1: `results/tables/wirtschaftlichkeit.csv` (`szenario`, `ersparnis_eur_jahr`, `umstellungskosten_eur`, `break_even`)

## Offene Aufgaben (Stand 09.11.2026)

- [ ] Umstellungskosten und Tarifzuschlag mit Quellen herleiten, Festpreisangebot ableiten
- [ ] 3–5 Literaturquellen zu Lastflexibilität (mit R1)
- [ ] Kipppunkte als Kurve statt Punktschätzung (Kickoff K7 Realismus)

**Review-Regel:** Kein Merge ohne Review durch R1 (Review-Paar R1 ↔ R4).

## Verantwortungsnachweis (2–3 Seiten, Gliederung laut Kickoff)

1. a) Aufgabenstellung des eigenen Pakets
2. b) Problematik im Paket
3. c) Methode: getroffene Entscheidungen und begründete Alternativen (Verweise auf Tagebuch-E-Einträge)
4. d) Beitrag zum Gesamterfolg, Schnittstellen (erhält von, übergibt an)
5. Eigene Fehler und verworfene Wege (K9 Stufe 5)
6. Belegliste: Commits, Tagebucheinträge, Berichtsseiten

## Notizen

*(Arbeitsnotizen, Ideen, offene Fragen. Entscheidungen und Absprachen gehören zusätzlich ins `docs/projekttagebuch.md`.)*
