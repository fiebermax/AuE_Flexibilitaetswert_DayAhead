# R2 · Datenanalyse & IT

Arbeitsbereich der Rolle. **Code, Daten und Ergebnisse bleiben in `src/`, `data/`, `results/`**, damit die Pipeline mit einem Befehl läuft (K5). Hier steht, was davon zu dieser Rolle gehört, plus Notizen und der Entwurf des Verantwortungsnachweises.

| | |
| --- | --- |
| Person | Max |
| Kernfrage | Sind die Daten sauber, und läuft alles auf Knopfdruck? |
| Führt | Datenquellen & Qualität; Pipeline, Repo, Tests; Aggregation 15 → 60 min; Sensitivitätsrechnung; Empfehlung zur künftigen Datenerhebung; Repo-Onboarding fürs Team |
| Wirkt mit | Datenaufbereitung (R3) |
| Kriterien | K2, K5, Aggregation in K3 |
| Vertretung | R3 |

## Meine Dateien im Repo

- `src/01_download.py`: SMARD-Download mit Cache, Retry, SHA256 (Commit `b68dfdb`)
- `src/02_aufbereitung.py`: Zeitzone, Zeitumstellung, 15 → 60 min, Werktage, Datenqualität (`b68dfdb`, Kommentare `9ce870e`)
- `src/02_synthetisch.py`: synthetischer Lastgang (`38765e1`)
- `src/datenzugriff.py`: Zugriff für R3 je Freitag, ohne Blick in die Zukunft (E-020)
- `src/gemeinsam.py`, `src/run_all.py`
- `tests/test_datenannahmen.py` (25 Tests)
- `data/raw/` mit `SOURCES.md` und `smard/manifest.csv`
- `docs/datenkatalog.md`, `docs/schnittstellen.md`, `docs/sensitivitaet_plan.md`, `docs/ki-nutzung.md`
- `results/tables/datenqualitaet.csv`

## Schnittstellen (Details in `docs/schnittstellen.md`)

**Erhält:**
- Von R1: Annahmen in `config/params.yaml`
- Vom Praxiskontakt (über Max): Lastmenge, Blocklänge, Betriebsruhe 24./31.12.

**Übergibt:**
- An R3: `data/processed/preise_h.parquet`, `preise_15min.parquet`, `last_synth.parquet` (Spalten in `docs/schnittstellen.md`)
- An R1: `results/tables/datenqualitaet.csv` für Bericht Kap. 3

## Offene Aufgaben (Stand 09.11.2026)

- [ ] Antwort R3 auf A-003 eintragen (Backtest-Funktion, 15-min-Raster, Schwelle)
- [ ] Relevanzschwelle im Team beschließen (P-002), dann Schalter V3–V7 und `src/06_sensitivitaet.py`
- [ ] Code selbst erklären können (K-002, Sperrkriterium Erklärbarkeit) bis Fr 13.11.
- [ ] Reproduktionstest durch eine Person außerhalb von R2 am 16.11. organisieren
- [ ] Empfehlung zur künftigen Datenerhebung (Bericht)

**Review-Regel:** Kein Merge ohne Review durch R3 (Review-Paar R2 ↔ R3, Tagebuch P-003).

## Verantwortungsnachweis (2–3 Seiten, Gliederung laut Kickoff)

1. a) Aufgabenstellung des eigenen Pakets
2. b) Problematik im Paket
3. c) Methode: getroffene Entscheidungen und begründete Alternativen (Verweise auf Tagebuch-E-Einträge)
4. d) Beitrag zum Gesamterfolg, Schnittstellen (erhält von, übergibt an)
5. Eigene Fehler und verworfene Wege (K9 Stufe 5)
6. Belegliste: Commits, Tagebucheinträge, Berichtsseiten

## Notizen

*(Arbeitsnotizen, Ideen, offene Fragen. Entscheidungen und Absprachen gehören zusätzlich ins `docs/projekttagebuch.md`.)*
