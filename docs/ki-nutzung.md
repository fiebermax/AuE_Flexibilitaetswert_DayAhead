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
| 07.11.2026 | Max (R2) | Claude | `src/01_download.py`, `src/02_aufbereitung.py`, `src/02_synthetisch.py`, `src/gemeinsam.py`, Tests, Sensitivitätsplan, Tagebucheinträge E-008 bis K-002 |
| 09.11.2026 | Max (R2) | Claude | `src/datenzugriff.py` (Datenzugriff für den Backtest), 4 Tests, Schnittstellendoku | pytest (29 Tests), Gegenprobe mit absichtlich falscher Datumsgrenze, Stichproben (Feiertag 06.01.2025 = 0 MWh, März-Umstellungswoche 167 h) | Tagebuch E-020 | pytest (18 Tests), Gegenprobe mit absichtlich eingebauten Fehlern, Nachrechnen der Umstellungstage | Tagebuch K-002 |
