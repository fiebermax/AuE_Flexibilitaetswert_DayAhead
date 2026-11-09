# R3 · Energieeinkauf

Arbeitsbereich der Rolle: alle Aufgaben mit Status und Beleg. **Code, Daten und Ergebnisse liegen in `src/`, `data/`, `results/`** (Pipeline mit einem Befehl, K5); die Links unten führen direkt zu den Dateien.

Status: ✅ erledigt · 🟨 in Arbeit · ⬜ offen. Stand 09.11.2026.

| | |
| --- | --- |
| Person | offen |
| Kernfrage | Welche Regel ist am billigsten, und braucht es eine Prognose? |
| Führt | Merkmale inklusive saisonalem Block; Strategien A bis D im Backtest; Regression, gepaarter Test, Bootstrap; Methodenfrage „braucht es eine Prognose?“ |
| Wirkt mit | Datenquellen (R2) |
| Kriterien | K3, K4 |
| Vertretung | R2 |
| Review-Partner | R2 (kein Merge nach `main` ohne dessen Review) |

## Aufgaben (0 von 12 erledigt)

| # | Aufgabe | Ergebnis / Datei | Termin | Status | Beleg / Hinweis |
| --- | --- | --- | --- | --- | --- |
| 1 | Antwort an R2 zu den 5 Punkten (Backtest-Funktion, 15-min-Raster, Schwelle …) | Tagebuch A-003 | Mo 09.11. | ⬜ |  |
| 2 | GitHub-Namen an Max; Review von PR #3 und #4 | Kommentare auf GitHub | Fr 13.11. | ⬜ | P-003, P-004 |
| 3 | Eigene Rolle im Format a) bis d) | Folie 5 | Mo 09.11. | ⬜ |  |
| 4 | Folie zum Vorgehen (Phasen, Strategien A–D) | Folie 4 | Di 10.11. | ⬜ |  |
| 5 | **Schritt 03:** Blockkosten-Matrix Tag × Blockstart, saisonaler Block, Kalendermerkmale | [`src/03_merkmale.py`](../../src/03_merkmale.py) | nach dem Pitch | ⬜ | K3 S5 |
| 6 | **Schritt 04:** Strategien A, B, B′, C, D, T als Funktion `backtest(preise_h, last, params)` | [`src/04_strategien.py`](../../src/04_strategien.py) | nach dem Pitch | ⬜ | Vorschlag in `docs/schnittstellen.md` |
| 7 | Look-ahead-Asserts; Strategien vor Test 1 einfrieren | Code, Tagebuch | vor Test 1 | ⬜ | K4 S3 |
| 8 | Saisonalen Block in Euro bewerten (mit/ohne Merkmal) | Tabelle | vor 14.11. | ⬜ | K3 S5 |
| 9 | Bootstrap und gepaarter Test, 95-%-KI | `results/tables/ki_strategien.csv` | Sa 14.11. | ⬜ | K4 |
| 10 | Validierungsprotokoll | Datei in `docs/` | Sa 14.11. | ⬜ |  |
| 11 | Bericht Kap. 4 (Merkmale) und Kap. 5 (Methode) | Bericht | bis Abgabe | ⬜ |  |
| 12 | Verantwortungsnachweis | diese Datei, Abschnitt unten | bis Abgabe | ⬜ |  |

## Schnittstellen (Details in `docs/schnittstellen.md`)

**Erhält:**
- Von R2: `data/processed/preise_h.parquet`, `last_synth.parquet`, `preise_15min.parquet` (Hinweise in `docs/schnittstellen.md`)

**Übergibt:**
- An R4: `results/tables/backtest_wochen.csv`, `results/tables/ki_strategien.csv`
- An R2: Backtest als Funktion für die Sensitivitätsrechnung (A-003)

## Verantwortungsnachweis (2–3 Seiten, Gliederung laut Kickoff)

1. a) Aufgabenstellung des eigenen Pakets
2. b) Problematik im Paket
3. c) Methode: getroffene Entscheidungen und begründete Alternativen (Verweise auf Tagebuch-E-Einträge)
4. d) Beitrag zum Gesamterfolg, Schnittstellen (erhält von, übergibt an)
5. Eigene Fehler und verworfene Wege (K9 Stufe 5)
6. Belegliste: Commits, Tagebucheinträge, Berichtsseiten

## Notizen

*(Arbeitsnotizen, Ideen, offene Fragen. Entscheidungen und Absprachen gehören zusätzlich ins `docs/projekttagebuch.md`.)*
