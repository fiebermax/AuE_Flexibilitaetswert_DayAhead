# R2 · Datenanalyse & IT

Arbeitsbereich der Rolle: alle Aufgaben mit Status und Beleg. **Code, Daten und Ergebnisse liegen in `src/`, `data/`, `results/`** (Pipeline mit einem Befehl, K5); die Links unten führen direkt zu den Dateien.

Status: ✅ erledigt · 🟨 in Arbeit · ⬜ offen. Stand 09.11.2026.

| | |
| --- | --- |
| Person | Max |
| Kernfrage | Sind die Daten sauber, und läuft alles auf Knopfdruck? |
| Führt | Datenquellen & Qualität; Pipeline, Repo, Tests; Aggregation 15 → 60 min; Sensitivitätsrechnung; Empfehlung zur künftigen Datenerhebung; Repo-Onboarding fürs Team |
| Wirkt mit | Datenaufbereitung (R3) |
| Kriterien | K2, K5, Aggregation in K3 |
| Vertretung | R3 |
| Review-Partner | R3 (kein Merge nach `main` ohne dessen Review) |

## Aufgaben (9 von 22 erledigt)

| # | Aufgabe | Ergebnis / Datei | Termin | Status | Beleg / Hinweis |
| --- | --- | --- | --- | --- | --- |
| 1 | Repo anlegen: Struktur, README, Gerüst `src/` 01–05 | [`README.md`](../../README.md) | Sa 07.11. | ✅ | Commit `0ccf808` |
| 2 | **Schritt 01:** SMARD-Download (Filter 4169, DE-LU), Cache, Retry, SHA256-Manifest | [`src/01_download.py`](../../src/01_download.py) | nach dem Pitch | ✅ | Commit `b68dfdb`; Tagebuch E-008, E-009 |
| 3 | **Schritt 02:** Aufbereitung: Zeitzone, Zeitumstellung, Lücken, Werktage Bayern | [`src/02_aufbereitung.py`](../../src/02_aufbereitung.py) | nach dem Pitch | ✅ | Commit `b68dfdb`; E-010, E-011, E-013, E-014, E-018 |
| 4 | Aggregation 15 → 60 min, 15-min-Daten separat | [`src/02_aufbereitung.py`](../../src/02_aufbereitung.py) | nach dem Pitch | ✅ | Commit `b68dfdb`; E-012 |
| 5 | Euro-Effekt der Aggregation (Variante V5) | [`docs/sensitivitaet_plan.md`](../../docs/sensitivitaet_plan.md) | Sa 14.11. | ⬜ | braucht R3s Backtest (A-003) |
| 6 | **Schritt 02b:** synthetischer Lastgang, deterministisch | [`src/02_synthetisch.py`](../../src/02_synthetisch.py) | Di 10.11. | ✅ | Commit `38765e1`; E-016, E-017 |
| 7 | Automatisierte Tests der Datenannahmen (25 Tests) | [`tests/test_datenannahmen.py`](../../tests/test_datenannahmen.py) | laufend | ✅ | Commits `b68dfdb`, `38765e1`, `9e85d28` |
| 8 | Datenherkunft und Lizenz je Datei | [`data/raw/SOURCES.md`](../../data/raw/SOURCES.md) | laufend | ✅ | `data/raw/smard/manifest.csv` |
| 9 | Datenkatalog mit synthetischen Größen | [`docs/datenkatalog.md`](../../docs/datenkatalog.md) | nach dem Pitch | 🟨 | Stichprobenumfang (Anzahl Testwochen) fehlt noch |
| 10 | Qualitätsbericht v1 | [`results/tables/datenqualitaet.csv`](../../results/tables/datenqualitaet.csv) | nach dem Pitch | 🟨 | Tabelle fertig, Text für Bericht Kap. 3 offen |
| 11 | Schnittstellen dokumentieren | [`docs/schnittstellen.md`](../../docs/schnittstellen.md) | laufend | ✅ | A-002, A-003 |
| 12 | Code mit Kommentaren, selbst erklären können | Kommentare in `src/` | Fr 13.11. | 🟨 | Kommentare `9ce870e`; Erklären offen (K-002, Sperrkriterium) |
| 13 | Sensitivitätsrechnung: Plan | [`docs/sensitivitaet_plan.md`](../../docs/sensitivitaet_plan.md) | — | ✅ | Commit `38e0516`; E-015 |
| 14 | Sensitivitätsrechnung: Schwelle beschließen, umsetzen, rechnen | `src/06_sensitivitaet.py` | Sa 14.11. | ⬜ | P-002, A-003 |
| 15 | Datenfolie für den Pitch | Folie 3 | Di 10.11. | ⬜ |  |
| 16 | Eigene Rolle im Format a) bis d) | Folie 5 | Mo 09.11. | ⬜ |  |
| 17 | Repo-Onboarding: Rollenordner, Collaborators, CODEOWNERS | [`rollen/README.md`](../../rollen/README.md) | Fr 13.11. | 🟨 | Rollenordner `77b2eb0`; Einladungen offen (GitHub-Namen fehlen), A-005 |
| 18 | Kontakt zum Praxispartner (Max, über die Rolle hinaus, K10) | Gesprächsprotokoll im Tagebuch | bis Fr 13.11. | ⬜ | Lastmenge, Blocklänge, Betriebsruhe klären |
| 19 | Reproduktionstest durch eine Person außerhalb von R2 | Testprotokoll | Mo 16.11. | ⬜ | K5 S5 |
| 20 | Empfehlung zur künftigen Datenerhebung | Bericht | bis Abgabe | ⬜ |  |
| 21 | Bericht Kap. 3 (Daten) und Kap. 9 (Reproduzierbarkeit, KI) | Bericht | bis Abgabe | ⬜ |  |
| 22 | Verantwortungsnachweis | diese Datei, Abschnitt unten | bis Abgabe | ⬜ |  |

## Schnittstellen (Details in `docs/schnittstellen.md`)

**Erhält:**
- Von R1: Annahmen in `config/params.yaml`
- Vom Praxiskontakt (über Max): Lastmenge, Blocklänge, Betriebsruhe 24./31.12.

**Übergibt:**
- An R3: `data/processed/preise_h.parquet`, `preise_15min.parquet`, `last_synth.parquet`
- An R1: `results/tables/datenqualitaet.csv` für Bericht Kap. 3

## Verantwortungsnachweis (2–3 Seiten, Gliederung laut Kickoff)

1. a) Aufgabenstellung des eigenen Pakets
2. b) Problematik im Paket
3. c) Methode: getroffene Entscheidungen und begründete Alternativen (Verweise auf Tagebuch-E-Einträge)
4. d) Beitrag zum Gesamterfolg, Schnittstellen (erhält von, übergibt an)
5. Eigene Fehler und verworfene Wege (K9 Stufe 5)
6. Belegliste: Commits, Tagebucheinträge, Berichtsseiten

## Notizen

*(Arbeitsnotizen, Ideen, offene Fragen. Entscheidungen und Absprachen gehören zusätzlich ins `docs/projekttagebuch.md`.)*
