# R3 · Energieeinkauf

Arbeitsbereich der Rolle. **Code, Daten und Ergebnisse bleiben in `src/`, `data/`, `results/`**, damit die Pipeline mit einem Befehl läuft (K5). Hier steht, was davon zu dieser Rolle gehört, plus Notizen und der Entwurf des Verantwortungsnachweises.

| | |
| --- | --- |
| Person | offen |
| Kernfrage | Welche Regel ist am billigsten, und braucht es eine Prognose? |
| Führt | Merkmale inklusive saisonalem Block; Strategien A bis D im Backtest; Regression, gepaarter Test, Bootstrap; Methodenfrage „braucht es eine Prognose?“ |
| Wirkt mit | Datenquellen (R2) |
| Kriterien | K3, K4 |
| Vertretung | R2 |

## Meine Dateien im Repo

- `src/03_merkmale.py`: Blockkosten-Matrix, saisonaler Block, Kalendermerkmale
- `src/04_strategien.py`: Backtest A, B, B′, C, D, T; Look-ahead-Asserts; gepaarter Test; Block-Bootstrap
- Validierungsprotokoll, Merkmalsdoku

## Schnittstellen (Details in `docs/schnittstellen.md`)

**Erhält:**
- Von R2: Zugriff je Freitag über `src/datenzugriff.py` (`planungswochen(...)`, siehe `docs/schnittstellen.md`)
- Von R2: `data/processed/preise_h.csv` (`zeit`, `datum`, `stunde`, `preis_eur_mwh`, `regime`, `werktag`), `last_synth.csv` (`datum`, `mwh`); Hinweise in `docs/schnittstellen.md`

**Übergibt:**
- An R4: `results/tables/backtest_wochen.csv` (`woche`, `periode`, `kosten_A` … `kosten_T`, `oracle`), `results/tables/ki_strategien.csv`
- An R2: Backtest als Funktion `backtest(preise_h, last, params)` für die Sensitivitätsrechnung (Vorschlag A-003)

## Offene Aufgaben (Stand 09.11.2026)

- [ ] Antwort auf A-003 (5 Punkte) an R2
- [ ] Review von PR #3 und PR #4
- [ ] GitHub-Namen an Max (Collaborator, `CODEOWNERS`)
- [ ] Strategien vor dem ersten Blick auf Test 1 einfrieren (Testdesign im Kickoff)

**Review-Regel:** Kein Merge ohne Review durch R2 (Review-Paar R2 ↔ R3).

## Verantwortungsnachweis (2–3 Seiten, Gliederung laut Kickoff)

1. a) Aufgabenstellung des eigenen Pakets
2. b) Problematik im Paket
3. c) Methode: getroffene Entscheidungen und begründete Alternativen (Verweise auf Tagebuch-E-Einträge)
4. d) Beitrag zum Gesamterfolg, Schnittstellen (erhält von, übergibt an)
5. Eigene Fehler und verworfene Wege (K9 Stufe 5)
6. Belegliste: Commits, Tagebucheinträge, Berichtsseiten

## Notizen

*(Arbeitsnotizen, Ideen, offene Fragen. Entscheidungen und Absprachen gehören zusätzlich ins `docs/projekttagebuch.md`.)*
