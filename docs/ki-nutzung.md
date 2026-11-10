# KI-Nutzung

Der Einsatz von KI-Werkzeugen ist erlaubt und kennzeichnungspflichtig (Katalog 6.5). Bewertet wird, ob wir die Ausgabe fachlich beurteilen können.

## Regeln
- Jede Datei mit KI-Anteil bekommt diesen Kopf:
  ```python
  # KI: Claude, Zweck: <wofür>, geprüft von <Name> durch <Test/Review/Nachrechnen>
  ```
- Commits mit KI-Anteil enden mit `AI-Assisted: Claude`.
- Wer KI-Code committet, muss ihn in der Verteidigung Zeile für Zeile erklären können.

## Einsätze

| Datum | Person | Werkzeug | Zweck | Wie geprüft | Datei/Commit |
| --- | --- | --- | --- | --- | --- |
| 06.–07.11.2026 | Max | Claude | Prototyp-Notebook, Kickoff-Dokument, Kriterienabgleich, Fragestellung, Repo-Gerüst | Abgleich mit Kriterienkatalog und Kursmaterial; Prototyp-Zahlen nur als Hypothesen | Tagebuch K-001 |
| 07.11.2026 | Max (R2) | Claude | `src/01_download.py`, `src/02_aufbereitung.py`, `src/02_synthetisch.py`, `src/gemeinsam.py`, Tests, Sensitivitätsplan, Tagebucheinträge E-008 bis K-002 | pytest (18 Tests), Gegenprobe mit absichtlich eingebauten Fehlern, Nachrechnen der Umstellungstage | Tagebuch K-002 |
| 09.11.2026 | Max (R2) | Claude | `src/datenzugriff.py` (Datenzugriff für den Backtest), 4 Tests, Schnittstellendoku | pytest (29 Tests), Gegenprobe mit absichtlich falscher Datumsgrenze, Stichproben (Feiertag 06.01.2025 = 0 MWh, März-Umstellungswoche 167 h) | Tagebuch E-020 |
| 09.11.2026 | Max (R2) | Claude | Vereinfachung: nur Stundenpreise, CSV statt Parquet, kürzere README, Tests angepasst | pytest (24 Tests), Stichproben Umstellungstage in `preise_h.csv` | Tagebuch E-021, E-022 |
| 09.11.2026 | Team | Claude Code, OpenAI Codex | Coding Agents im Teamtreffen eingerichtet (VS Code) | Einsatz je Aufgabe wird hier und im Tagebuch einzeln eingetragen | Tagebuch K-004 |
| 09.11.2026 | Max (R2) | Claude Code | `src/cleaning.py`, `tests/test_cleaning.py`, Berichte, Codebook, Manifest; Quellenrecherche Preisgrenzen und 15-min-Umstellung | Plan vorab freigegeben; 24 Tests grün; Gegenprobe (gelöschte Stunde, Preis 6 000 €/MWh → 3 Tests rot); Quellen verlinkt | Tagebuch K-006 |
| 09.11.2026 | Max (R2) | Claude Code | `src/fensteranalyse.py`, `src/build_presentation.py`, Folien R2, `pptx_kit/` | Plan und Entscheidungen D1–D6 von Max; 35 Tests grün; Zahlenprüfung im Skript (Gegenprobe: erfundene Zahl wird erkannt); Folien gerendert und gesichtet | Tagebuch K-007
| 10.11.2026 | Max (R2) | Claude Code | Prüfung der Praxisangaben (K-008, P-009); Umstellung auf den Reinigungsfall: `config/params.yaml`, `src/02_synthetisch.py`, `src/gemeinsam.py`, `src/fensteranalyse.py` (Fenster über Mitternacht, Jahrestabellen), `src/run_all.py`, 7 neue Tests, Doku; Tagebucheinträge E-031 bis E-037, A-010, K-009 | Entscheidungen von Max vorab; 42 Tests grün; erste Schätzung (Skript im Scratchpad) mit dem Repo-Code nachgerechnet; nur Lastspalten in `preise_clean.csv` geändert (Diff geprüft) | Tagebuch K-009 |
