# Projekttagebuch

Ein Eintrag pro Entscheidung, Problem, Meilenstein, Absprache oder KI-Einsatz. Neueste Einträge oben. Jeder Eintrag wird von der Person committet, die ihn verfasst. Entscheidungen aus dem WhatsApp-Chat werden innerhalb von 24 Stunden hier eingetragen.

Eintragsarten: **E** Entscheidung · **P** Problem/Konflikt · **M** Meilensteinprotokoll · **A** Absprache/Schnittstelle · **K** KI-Einsatz und Rückkopplung

---

## 10.11.2026

### P-011 · PR #10 ohne Review gemergt (auf Anweisung von Max)
- **Problem:** Laut P-003 Merge nach `main` nur nach Review des Paarpartners; PR #10 (Code zurück nach `src/`, E-040) hat niemand geprüft.
- **Angesprochen von:** Claude, 10.11.2026
- **Entscheidung:** Max verlangt den Merge ausdrücklich („merge bitte alles“). Vorher geprüft: Pipeline läuft, `preise_clean.csv` bitgleich zu `main`, 51 Tests grün.
- **Ergebnis:** PR #10 am 10.11.2026 gemergt; nachträgliches Review durch Susan offen (zusammen mit P-010).

### E-040 · Aller Code in `src/`, `r2/` nur Dokumente und Ergebnisse (korrigiert E-038)
- **Person:** Max (R2)
- **Entscheidung:** Die Programme `01_download.py`, `02_synthetisch.py`, `cleaning.py`, `fensteranalyse.py`, `build_board.py` liegen wieder in `src/`, neben allem anderen Code. `r2/` enthält nur `ergebnisse/` und `docs/` von R2. Gemeint war in E-038 von Anfang an: was alle brauchen (und Code gehört dazu, weil `run_all.py` ihn für alle ausführt), bleibt in `src/`.
- **Verworfen:** Code in `r2/src/` (zweiter Code-Ordner, Importe über zwei Ordner, für das Team verwirrend).
- **Beleg:** `README.md` („Wo was liegt“), `src/run_all.py`; Pipeline gelaufen, `preise_clean.csv` bitgleich zu `main`, 51 Tests grün.

### P-010 · PR #9 auf Anweisung von Max gemergt, spätere Commits ohne Review
- **Problem:** Laut P-003 Merge nach `main` nur nach Review des Paarpartners. Susan hat den Branch bis Commit `a0185cb` geprüft (A-012); die späteren Commits (Kommentare, Diagramme, Board, Umzug nach `r2/`, Vereinfachung E-038, E-039) hat sie nicht gesehen.
- **Angesprochen von:** Claude, 10.11.2026
- **Entscheidung:** Max verlangt den Merge ausdrücklich. Vorher geprüft: jeder in Doku und Code genannte Pfad existiert (automatische Prüfung; offen sind nur geplante Ergebnisdateien von R2 bis R4), `python src/run_all.py` läuft für alle R2-Schritte durch (Abbruch erst im leeren Gerüst `03_merkmale.py` von R3, gewollt), 51 Tests grün, Daten bitgleich.
- **Ergebnis:** PR #9 am 10.11.2026 gemergt; nachträgliches Review der Commits nach `a0185cb` durch Susan offen.

### E-039 · Repo radikal vereinfacht: weniger Dateien, flache Ordner, keine Folien per Skript
- **Person:** Max (R2), nach Rückmeldung von Susan und A-013 (Umfang wird nicht bewertet)
- **Entscheidung:**
  - **Gelöscht:** `docs/ki-nutzung.md` (KI-Einsatz steht laut Katalog 6.5 im Projekttagebuch, die K-Einträge reichen; Regel in `CLAUDE.md` angepasst), `docs/projektanweisung.md` (steht am Ende von `docs/kickoff.md`), `docs/gespraech-praxispartner.md` (leerer Leitfaden, Antworten in K-005, K-008); aus dem Kickoff der 1,0-Blueprint, die Abgabeübersicht und die Sperrkriterien (jetzt kurz in `docs/belegmatrix.md`, 635 → 333 Zeilen).
  - **PowerPoint raus:** `r2/src/build_presentation.py`, `r2/output/`, `r2/pptx_kit/`, Paket `python-pptx`. Folien macht das Team am Ende mit Claude.
  - **Flache Ordner:** `config/params.yaml` → `params.yaml`; `data/processed/*.csv` → `data/*.csv`; `data/raw/smard/4169/hour/*.json` → `data/raw/*.json`, Manifest → `data/raw/manifest.csv` (`SOURCES.md` und `MANIFEST.md` entfallen, doppelt zum Manifest); `r2/reports/{tables,figures}` → `r2/ergebnisse/`; leere Ordner `results/`, `notebooks/` weg.
  - **Endergebnis:** eine einzige Analyseseite wie der Notebook-Prototyp von Max (linear von Parametern über Daten, Backtest, Tests, Sensitivität bis zur Empfehlung an die Betriebsleitung).
- **Verworfen:** tiefe Ordner nach SMARD-Filter und Auflösung (es gibt nur einen Filter und nur Stundenwerte, E-021); Folien per Skript (606 Zeilen Code für etwas, das am Ende einmal gebraucht wird); eigene KI-Liste neben dem Tagebuch.
- **Hinweis:** Ältere Einträge nennen die alten Pfade; gemeint sind die gleichnamigen Dateien an den neuen Orten (Tabelle oben).
- **Beleg:** `README.md` („Wo was liegt“); nach dem Umzug: Download offline ohne neue Dateien, Manifest unverändert, `preise_clean.csv` und `last_synth.csv` bitgleich, 51 Tests grün.

### A-013 · Prof: Umfang und Werkzeug sind frei, auch eine Excel-Liste ist gleichwertig
- **Von → an:** Prof → Team; weitergegeben von Max (R2) an Claude Code, 10.11.2026
- **Was:** Laut Prof gibt eine Lösung als Excel-Liste theoretisch dieselbe Note. Das deckt sich mit dem Kriterienkatalog (7.3: nicht bewertet werden der Umfang der Abgabe und die Schwierigkeit der Werkzeugwahl; 1.4: begründete, einfache Verfahren stehen über komplexen).
- **Folge:** So wenig Dokumente wie nötig. `docs/belegmatrix.md` ist jetzt die eine Übersicht nach dem Original-Katalog: Pflichtabgaben (1.3), Bewertungsmodell und Sperrkriterien (2), Stufe 5 je Kriterium mit unserem Stand. Weitere Zusammenlegungen von Dokumenten entscheidet das Team (Vorschlag offen).
- **Beleg:** `docs/belegmatrix.md`; Kriterienkatalog Stand 28.09.2026 (nicht im Repo)

### E-038 · Eigener Ordner `r2/` für alles, was nur R2 betrifft (revidiert E-023)
- **Person:** Max (R2), auf Rückmeldung von Susan („viel zu unübersichtlich, zu komplex“)
- **Entscheidung:** Nur R2-eigene Dateien wandern nach `r2/`: `r2/src/` (`01_download.py`, `02_synthetisch.py`, `cleaning.py`, `fensteranalyse.py`, `build_board.py`, `build_presentation.py`), `r2/reports/` (vorher `reports/`), `r2/docs/` (`architektur.md`, `datenaufbereitung.md`, `datenkatalog.md`, `sensitivitaet_plan.md`), `r2/output/`, `r2/pptx_kit/`. Für alle bleiben oben: `data/processed/`, `config/`, `src/` (`preisabfrage.py`, `datenzugriff.py`, `gemeinsam.py`, `run_all.py`, Gerüste R3/R4), `docs/` (Tagebuch, Schnittstellen, Codebook, Kickoff, Belegmatrix, KI-Nutzung), `tests/`. Leere Platzhalter (`notebooks/`, `.gitkeep` in `data/`) entfernt. README beginnt jetzt mit einer Tabelle „welche Datei, was steht drin, wer braucht sie“.
- **Verworfen:** alles in `src/` und `docs/` lassen (für das Team nicht zu überblicken); Rollenordner für alle vier Rollen (Grund aus E-023 gilt weiter: zusätzliche Struktur ohne Nutzen für die anderen).
- **Hinweis:** Ältere Tagebucheinträge nennen die alten Pfade (`src/cleaning.py`, `reports/…`, `docs/datenaufbereitung.md`); gemeint sind jetzt die gleichnamigen Dateien unter `r2/`.
- **Beleg:** `README.md` (Abschnitt „Wo was liegt“), `src/run_all.py`, `config/params.yaml` (`cleaning.reports: r2/reports`); 51 Tests grün nach dem Umzug; `preise_clean.csv` unverändert.

### K-011 · KI-Einsatz: Kommentare, Diagramme, Board, Aufräumen
- **Werkzeug:** Claude Code
- **Zweck:** Erklärende Kommentare an den schwierigen Stellen in `cleaning.py`, `datenzugriff.py`, `fensteranalyse.py`, `01_download.py` (Verhalten unverändert); Diagramm-Dokument `r2/docs/architektur.md` (Workflow, Bereinigung, Reinigungsfenster, Planungsfreitag, Dateien; Begriffe aus dem Statistischen Grundlagenwerk Teil 4: deskriptive Analytik, DMAIC-Phase Measure, Workflow-Knoten); Board `r2/reports/board.html`, erzeugt von `r2/src/build_board.py` aus den Repo-Daten; Umzug nach `r2/` (E-038).
- **Wie geprüft:** `pytest tests/`: 51 grün nach jedem Schritt; `preise_clean.csv` nach dem erneuten Lauf bitgleich; Pipeline-Schritte aus den neuen Pfaden ausgeführt.
- **Offen:** Max geht `r2/docs/architektur.md` mit dem Code durch (Sperrkriterium Erklärbarkeit); `r2/src/build_presentation.py` nur bei den Pfaden angepasst, inhaltlich weiter alter Stand.

### A-012 · Review durch Susan: PR #6 bis #8 und Branch vom 10.11.2026
- **Von → an:** Susan → Max (R2); weitergegeben von Max im Chat mit Claude Code
- **Was:** Susan hat die ohne Review gemergten PRs #6, #7 und #8 nachträglich geprüft und den aktuellen Stand des Branches `claude/friendly-ramanujan-6ej4do` (Reinigungsfall, Preisabfrage, Commits `a57ec82` bis `a0185cb`) gegengeprüft („double checked“). Damit sind die offenen Reviews aus P-006, P-007 und P-008 erledigt.
- **Kanal und Datum:** mündlich bzw. Chat Susan → Max, 10.11.2026
- **Beleg:** bisher nur diese Angabe von Max. Damit das Review belegt ist (Kickoff: „Was nur im Chat steht, ist kein Beleg“), hinterlässt Susan auf dem Pull Request des Branches ein Approve bzw. einen Kommentar; Funde und Änderungen trägt sie hier nach.
- **Offen:** Susans Rolle ist noch nicht in der Rollentabelle eingetragen (P-003 verlangt das Review des Paarpartners); Funde aus dem Review: keine genannt.

### K-010 · KI-Einsatz: einfache Preisabfrage
- **Werkzeug:** Claude Code
- **Zweck:** `src/preisabfrage.py` (`tag`, `tage`, `letzte_monate`, Aufruf im Terminal), `tests/test_preisabfrage.py` (9 Tests), Abschnitte in `README.md` und `docs/schnittstellen.md`, Einträge A-011 und K-010 im Auftrag von Max.
- **Wie geprüft:** `pytest tests/`: 51 Tests grün; Preis einer Stunde gegen `preise_clean.csv` verglichen (Test); Umstellungstage mit 23 und 25 Stunden; Wochentag gegen `datum.dt.weekday`; Stichprobe `python src/preisabfrage.py 2026-10-15` (Donnerstag, 24 Zeilen).
- **Offen:** Susan probiert die Abfrage aus und meldet, ob Spalten oder Aufruf fehlen.

### A-011 · Wunsch Susan: einfacher Zugriff auf einzelne Tage und die letzten Monate
- **Von → an:** Susan (über Max, R2) → R2
- **Was (Datei, Spalten, Einheit):** Methode, um auf die letzten Monate bzw. einzelne Tage zuzugreifen und direkt mit Variablen wie Preis, Uhrzeit, Datum und Wochentag zu arbeiten. Umgesetzt als `src/preisabfrage.py`: `tag("JJJJ-MM-TT")`, `tage(von, bis)`, `letzte_monate(n, wochentag=...)`; Spalten `datum`, `wochentag` (deutsch), `uhrzeit` ("14:00"), `stunde`, `preis` (€/MWh), `saison`, `werktag`, `zeit`. Bewusst getrennt von `datenzugriff.py`: freie Sicht auf die Vergangenheit, deshalb nicht für Strategien (Look-ahead).
- **Verworfen:** Funktion in `datenzugriff.py` (würde den Look-ahead-Schutz verwässern); nur README-Beispiele mit `preise_clean.csv` (Spaltennamen wie `stunde_lokal`, Wochentag als Zahl 0–6 sind für das Team umständlicher).
- **Kanal und Datum:** Wunsch von Susan an Max, weitergegeben im Chat mit Claude Code, 10.11.2026
- **Bis:** erledigt 10.11.2026; Rückmeldung Susan offen
- **Nachricht an Susan:** WhatsApp, formuliert am 10.11.2026, Versand durch Max: Funktionen `tag`, `tage`, `letzte_monate`, `alle_preise` mit Beispielen; Code liegt auf dem Branch `claude/friendly-ramanujan-6ej4do` (noch nicht auf `main`); Hinweis: nur zum Anschauen, nicht für Strategien; Bitte um Rückmeldung.
- **Änderung, nachgezogen von:** `README.md`, `docs/schnittstellen.md`, K-010

### K-009 · KI-Einsatz: Umstellung auf den Reinigungsfall
- **Werkzeug:** Claude Code
- **Zweck:** Prüfung der Praxisangaben aus K-008 (Widerspruch P-009, Ortsname des zentralen Einkaufs, der den Praxispartner identifiziert, Konflikt D1 mit E-021, Zeitumstellung im Nachtfenster); erste Schätzung im Rückblick; Umstellung von `config/params.yaml`, `src/02_synthetisch.py`, `src/gemeinsam.py` (`fensterstunden`), `src/fensteranalyse.py` (Fenster über Mitternacht, echte Stunden, Jahrestabellen, eigener Aufruf), `src/run_all.py`; 7 neue bzw. geänderte Tests; Doku (README, Kickoff, Codebook, Schnittstellen, Datenaufbereitung, Sensitivitätsplan, `docs/ki-nutzung.md`); diese Einträge im Auftrag von Max.
- **Wie geprüft:** Entscheidungen vorab von Max (E-031 bis E-034); `pytest tests/`: 42 Tests grün; Gegenprobe: Zuordnung der Nacht zum Vortag absichtlich entfernt → 4 Tests rot; erste Schätzung (Scratchpad-Skript `nacht.py`) mit dem Repo-Code nachgerechnet, Abweichungen nur in den Umstellungsnächten (das Skript hatte sie falsch gruppiert); `preise_clean.csv` gegen den letzten Commit verglichen: nur `last_mwh_tag` und `last_mwh_flexibel_tag` geändert.
- **Was wir geändert haben:** In der ersten Schätzung stand für 2026 eine Jahressumme, obwohl 2026 nur 303 Nächte hat (bis 31.10.); jetzt eigene Spalte `vollstaendig` und Hochrechnung auf 365 Nächte. `src/build_presentation.py` auf Anweisung von Max nicht angefasst: Folien erst am Ende, zuerst muss der Code stehen.
- **Offen:** Max erklärt `fenster_je_tag` (Nacht über Mitternacht, echte Stunden) selbst.

### A-010 · Schnittstelle R2 → R3: Reinigungsfall, Nacht über die Wochengrenze
- **Von → an:** R2 (Max) → R3
- **Was (Datei, Spalten, Einheit):** `last_synth.csv`: `mwh_gesamt` jetzt 180 MWh, `mwh_flexibel` 8 MWh; der Wert am Datum d gilt für die Reinigung in der Nacht d 22:00 bis d+1 06:00. Neue Schalter in `params.yaml`: `last.fenster_start_h` 22, `last.fenster_ende_h` 6, `last.status_quo_start_h` 22, `last.blocklaenge_h` 2, Block `kaelte` für T, Block `vertrag`, neue Zuschläge. Zum Wiederverwenden: `fensteranalyse.fenster_je_tag(df, 22, 6, 2, 22)` bewertet jede Nacht mit echten Stunden. **Achtung:** Die Sonntagsnacht der Zielwoche reicht bis Montag 06:00 der Folgewoche; diese Stunden fehlen in `w.zielwoche`. R3 entscheidet: mitwerten (Preise bis Montag 06:00 nachladen) oder Sonntagsnacht weglassen. Dazu die drei offenen Fragen aus A-007.
- **Kanal und Datum:** Nachricht vorbereitet am 10.11.2026, Versand durch Max
- **Bis:** Fr 13.11.2026
- **Antwort R3:** offen
- **Änderung, nachgezogen von:** `docs/schnittstellen.md`

### E-037 · R2-Kennzahl neu: Mehrkosten der Reinigung 22–24 Uhr gegenüber dem billigsten 2-h-Fenster der Nacht (revidiert E-030)
- **Person:** Max (R2), umgesetzt von Claude
- **Entscheidung:** Je Nacht (benannt nach dem Tag, an dem sie um 22 Uhr beginnt): Mittelpreis des Status quo 22–24 Uhr minus Mittelpreis des billigsten 2-h-Blocks in 22–06 Uhr, je Saison Median und IQR in €/MWh und %, häufigste Startzeit; je Jahr Mittel, Median und € bei 8 MWh je Nacht (Summe und Hochrechnung auf 365 Nächte). Das Scratchpad-Skript `nacht.py` aus der ersten Schätzung ist als getestete Funktion in `src/fensteranalyse.py` aufgegangen (Aufruf `python src/fensteranalyse.py`, Schritt in `run_all.py`), statt als zweites Skript mit derselben Logik. Kennzeichnung: Rückblick mit bekannten Preisen, keine Strategie; € sind eine Obergrenze ohne Personal und Zuschläge und mit Annahme A3 „Band“.
- **Verworfen:** E-030 (08–14 Uhr gegen billigstes 6-h-Fenster am Tag) passt nicht mehr zum Fall; `nacht.py` als eigenes Skript (doppelte Logik, ungetestet, falsche Gruppierung in den Umstellungsnächten, Teiljahr 2026 als Jahressumme).
- **Ergebnis (Hypothese, kein Strategieergebnis):** 1 764 Nächte. Mehrkosten im Median Winter 16,2, Frühling 19,6, Sommer 29,6, Herbst 20,7 €/MWh; billigstes Fenster beginnt meist um 3 Uhr (38 %, 2 Uhr 27 %); genau 22–24 Uhr ist höchstens in 2,9 % der Nächte am billigsten. Obergrenze in €: 2023 rund 71 T€, 2024 58 T€, 2025 59 T€, 2026 hochgerechnet 78 T€, Krisenjahr 2022 163 T€. Bei proportionaler Bewertung (A3) rund 30 % davon.
- **Offen:** Folien und `pptx_kit/` zeigen noch E-030; `src/build_presentation.py` bricht mit den neuen Parametern ab. Umstellung erst am Ende, wenn der Code steht (Anweisung Max).
- **Beleg:** `src/fensteranalyse.py`, `reports/tables/reinigungsfenster_saison.csv`, `reports/tables/reinigungsfenster_jahr.csv`, Tests in `tests/test_fensteranalyse.py`

### E-036 · Zeitumstellung liegt jetzt im Reinigungsfenster (revidiert E-018 und Sensitivitätsvariante V1)
- **Person:** Max (R2), Hinweis von Claude
- **Entscheidung:** Die Umstellung (02–03 Uhr) liegt nicht mehr außerhalb des Falls, sondern mitten im Reinigungsfenster 22–06 Uhr. Gerechnet wird mit echten Stunden (UTC, E-026): Die März-Nacht hat 7, die Oktober-Nacht 9 Stunden; ein 2-h-Block sind immer 2 echte Stunden und 8 MWh und darf in der Oktober-Nacht beide „02:00“-Stunden nutzen. Das betrifft 10 von 1 764 Nächten.
- **Verworfen:** E-018 („kostenneutral, weil außerhalb der Betriebszeit“) gilt für die Reinigung nicht mehr; nach Ortszeit rechnen (die doppelte Stunde wäre mehrdeutig, die fehlende ein Loch im Block).
- **Beleg:** Tests `test_umstellungsnaechte_mit_echten_stunden`, `test_block_darf_beide_oktober_zwei_uhr_stunden_nutzen`; `docs/sensitivitaet_plan.md` (V1)

### E-035 · Weitere Parameter aus dem Termin vom 10.11.: Zuschläge, Stundensatz, Vertrag, Planungszeit
- **Person:** Max (R2), nach K-008
- **Entscheidung:** In `config/params.yaml`: Sonntagszuschlag 50 % (Bandbreite 30–50 %) und Feiertagszuschlag 100 % (geschätzt, P14, P15); Nachtzuschlag 25 % (P13, Bandbreite 25–30 %); Stundensatz 35 €/h (A7, 30–45 €/h, statt 30 €/h); 3 Personen (A6, 2–4); Festpreis 85 €/MWh (P4, statt `null`); neuer Block `vertrag` mit Spot-Anteil 30 % und Bewertung `band` (A3, Alternative `proportional` als Sensitivität V8); Planung Freitag 08:00 statt 12:00 (P11; die Datengrenze bleibt Freitag 23:00, weil die Samstagspreise erst gegen 12:45 kommen). E-021 bleibt: nur Stundenwerte; Zeile D1 der Praxistabelle („15-min ab 01.10.2025“) ist damit korrigiert. Der Standort des zentralen Einkaufs (P16) wird als „zentraler Einkauf des Konzerns“ anonymisiert.
- **Verworfen:** 15-min-Preise für Blockstarts in Viertelstunden (E-021, Zeit); Ortsnamen im Repo (identifiziert den Praxispartner).
- **Offen:** `kosten.nachtstunden` unverändert 23–06 Uhr. Gilt schon 22–23 Uhr als Nacht, hätte der Status quo zwei statt einer zuschlagspflichtigen Stunde (Sensitivität V9). Beim Kontakt klären.
- **Beleg:** `config/params.yaml` (`kosten`, `vertrag`, `planung`), `docs/sensitivitaet_plan.md` (V8, V9)

### E-034 · Fragestellung: „verschiebbarer Last“ statt „verschiebbarer Produktionslast“
- **Person:** Max (R2)
- **Entscheidung:** Neue Formulierung: „Inwiefern lässt sich der Flexibilitätswert verschiebbarer Last eines bayerischen Werks einer international tätigen Großmolkerei am Day-Ahead-Strommarkt DE-LU durch eine wöchentliche Schichtplanung realisieren, und wie verändert die Umstellung auf den Viertelstundenhandel im Oktober 2025 diesen Wert?“ Die Reinigung ist keine Produktion, aber personalgebunden und wöchentlich geplant. H0a, H0b, H0c und Bonferroni (E-005, E-006) bleiben unverändert.
- **Verworfen:** „Produktionslast“ beibehalten (fachlich falsch für die Reinigung).
- **Begründung:** Die Änderung erfolgt vor jeder Auswertung (es gibt noch keinen Backtest), sie passt die Frage nicht an ein Ergebnis an.
- **Beleg:** `README.md`, `docs/kickoff.md`

### E-033 · Fälle: Reinigung S1 als Hauptfall, Kälte als Kontrastfall T, S2 nur Ausblick
- **Person:** Max (R2), nach K-008
- **Entscheidung:** Hauptfall S1 ist die Reinigung (CIP): 4 MW für 2 h = 8 MWh pro Nacht, verschiebbar innerhalb der Nebenzeit 22–06 Uhr, an jedem Tag. Kontrastfall T ist die Kälteversorgung (1 MW, Vorkühlung 2 h, Annahme A1), die automatisch läuft und täglich mit bekannten Day-Ahead-Preisen gesteuert werden kann. S2 (Produktionsblock verschieben) nur als Ausblick, wegen der Grenze Rohmilch (P9) und der Zuschläge. In `params.yaml`: `last.mwh_pro_tag` 8,0 (statt Platzhalter 2,0), `last.blocklaenge_h` 2 (statt 6), neu `last.prozess`, `last.fenster_start_h` 22, `last.fenster_ende_h` 6; neuer Block `kaelte`. `02_synthetisch` prüft, dass das Fenster nicht in der Produktion liegt und der Block hineinpasst.
- **Verworfen:** 2 MWh im 6-h-Block am Tag (Platzhalter ohne Praxisbezug); S2 als Hauptfall (größerer Hebel, aber Rohmilch, Lastspitze A4 und Zuschläge nicht in der Zeit zu modellieren); Kälte als Hauptfall (nicht personalgebunden, passt nicht zur wöchentlichen Schichtplanung).
- **Beleg:** `config/params.yaml` (`last`, `kaelte`), `src/02_synthetisch.py`, Tests `test_last_unsinnige_parameter_werden_abgelehnt`, `test_basisfall_reinigung_ist_gueltig`

### E-032 · Tagesverbrauch 180 MWh (löst P-009)
- **Person:** Max (R2)
- **Entscheidung:** `last.gesamtverbrauch_mwh_pro_tag` 180,0 (Praxiskontakt 10.11.2026, 65 GWh/a). Die 50 MWh aus K-005 waren ein Platzhalter und sind ersetzt.
- **Verworfen:** 50 MWh beibehalten (passt nicht zu 65 GWh/a).
- **Beleg:** `config/params.yaml`, `data/processed/last_synth.csv`, Spalte `last_mwh_tag` in `preise_clean.csv`

### E-031 · Status quo A: Reinigung 22–24 Uhr
- **Person:** Max (R2)
- **Entscheidung:** Status quo A ist die Reinigung direkt nach Produktionsende, 22–24 Uhr (`last.status_quo_start_h: 22`). **Annahme**, vom Praxiskontakt nicht bestätigt.
- **Verworfen:** 08–14 Uhr (Status quo des alten Falls, E-030); ein Status quo später in der Nacht (ohne Beleg; je später, desto kleiner der Flexibilitätswert).
- **Begründung:** Naheliegender Ablauf nach Produktionsende; Kipp-Annahme: Läuft die Reinigung heute schon um 2–4 Uhr, ist der Flexibilitätswert von S1 fast null. Beim Kontakt bestätigen lassen.
- **Beleg:** `config/params.yaml`, `src/02_synthetisch.py` (Prüfung Status quo im Fenster)

### P-009 · Widerspruch Tagesverbrauch: 50 MWh (K-005) gegen 180 MWh (K-008)
- **Problem:** Am 09.11. wurden 50 MWh pro Tag genannt (K-005), am 10.11. 180 MWh pro Tag bzw. 65 GWh pro Jahr (K-008). 65 GWh ÷ 365 = 178 MWh, der neue Wert ist also in sich stimmig. Der Spot-Anteil von 53 MWh pro Tag liegt nahe am alten Wert; vermutlich war am 09.11. der Spot-Anteil gemeint (Annahme, nicht bestätigt).
- **Angesprochen von:** Claude bei der Prüfung von K-008, 10.11.2026
- **Lösungsvorschlag:** 180 MWh pro Tag als Basis übernehmen; beim Kontakt kurz bestätigen lassen, ob 50 MWh der Spot-Anteil war.
- **Entscheidung:** Max, 10.11.2026: 180 MWh gelten (Praxiskontakt); die 50 MWh waren ein Platzhalter und werden ersetzt (E-032).
- **Ergebnis:** `config/params.yaml` und `last_synth.csv` umgestellt (E-032).

### K-008 · Termin mit dem Praxiskontakt: Zahlen, verschiebbare Lasten, Vertrag (ganzes Team)
- **Gesprächspartner:** Kontakt beim Praxispartner; Termin von ca. 15 Minuten mit dem ganzen Team, 10.11.2026
- **Aussagen (genannt):** Jahresverbrauch des Werks 65 GWh (P1); Tagesverbrauch 180 MWh (P2); davon rund 53 MWh pro Tag (ca. 30 %) am Day-Ahead-Markt (P3), rund 70 % zum Festpreis von 85 €/MWh, eingekauft im Januar für das Folgejahr (P4); Produktion 16 h pro Tag, 06–22 Uhr, nachts keine Volllast (P5); Reinigung (CIP) 4 MW für ca. 2 h, voll elektrisch (P6); Kälteversorgung 1 MW (P7); verschiebbar sind Kälte und Reinigung (P8); Rohmilch höchstens 36–48 h lagerfähig, muss sofort gekühlt werden (P9); nach höchstens 24 h Produktion muss gereinigt werden, laut Kontakt gesetzlich (P10); Schichtplanung Freitagmorgen für die Folgewoche (P11); Personal überwiegend Zeitarbeit, flexibel (P12); Entscheider sind der zentrale Einkauf des Konzerns und die Werksleitung (P16).
- **Aussagen (vom Kontakt geschätzt):** Nachtzuschlag 25 % (25–30 %) (P13); Sonntagszuschlag 50 % (30–50 %) (P14); Feiertagszuschlag bis 100 % (P15).
- **Abgeleitet (Team):** mittlere Last ca. 7,4 MW (B1); Spot-Volumen ca. 19 GWh pro Jahr (B2); Reinigungsenergie ca. 8 MWh pro Tag (B3); Prognosehorizont 3–9 Tage, weil am Freitagmorgen nur die Freitagspreise bekannt sind (B4); Nebenzeit 22–06 Uhr, davon 2 h Reinigung (B5).
- **Annahmen des Teams (noch zu belegen):** Kälteverschiebung (Vorkühlung) 2 h, Bandbreite 0–4 h (A1); Festpreis als Forward mit Abnahmepflicht (A2); Festanteil als Band, verschobene MWh also zu 100 % am Spot bewertet, Alternative proportional × 30 % (A3, Kipp-Annahme, beide Fälle rechnen); Jahreshöchstlast darf nicht steigen (A4); §19 StromNEV als Nichtziel (A5); 3 Personen an der Reinigung, 2–4 (A6); Zeitarbeit 35 €/h, 30–45 €/h (A7).
- **Szenarien:** S1 Basis: die Reinigung wandert innerhalb 22–06 Uhr. S2 Ausbau: der Produktionsblock verschiebt sich, z. B. in die Mittagsstunden (Grenze P9).
- **Was sich ändert (Vorschlag, noch nicht umgesetzt):** verschiebbarer Prozess und Menge (Reinigung 8 MWh pro Tag, 2-h-Block in der Nacht statt 2 MWh im 6-h-Block am Tag); Status quo A muss neu festgelegt werden; Planung Freitagmorgen statt Freitagmittag (ändert die Datengrenze nicht, die Samstagspreise kommen erst gegen 12:45); Zuschläge für Sonntag und Feiertag neu; Stundensatz 35 statt 30 €/h; Festpreis 85 €/MWh statt `null`. Kipp-Annahme Vertrag (Kickoff) ist damit teilweise geklärt: Das Werk kauft zu 30 % spot.
- **Offen:** Wann läuft die Reinigung heute (Status quo A)? Ist die Kälte personalgebunden oder automatisch (dann eher Tagessteuerung T)? Wie ist der Festpreisanteil vertraglich gestaltet (Band oder Profil, A3)? Bestätigung 50 gegen 180 MWh (P-009).
- **Hinweis:** Der Standort des zentralen Einkaufs wird im Repo nicht genannt, weil er den Praxispartner identifiziert (CLAUDE.md, Kickoff).

## 09.11.2026

### P-008 · PR #8 ohne Review gemergt (auf Anweisung von Max)
- **Problem:** Laut P-003 Merge nach `main` nur nach Review des Paarpartners; R3 ist noch nicht im Repo.
- **Angesprochen von:** Max (R2), 09.11.2026
- **Entscheidung:** Max verlangt den Merge ausdrücklich, damit die Folien R2 und `pptx_kit/` auf `main` liegen. Weiterarbeit mit Susan am 10.11.2026.
- **Ergebnis:** PR #8 am 09.11.2026 gemergt; nachträgliches Review durch Susan am 10.11.2026 erledigt (A-012).

### K-007 · KI-Einsatz Folien R2
- **Werkzeug:** Claude Code
- **Zweck:** `src/fensteranalyse.py`, `src/build_presentation.py`, Grafiken, vier Folien mit Sprechernotizen, `pptx_kit/defense_qa.md`, `pptx_kit/sources.md`.
- **Wie geprüft:** Bestandsaufnahme und Entscheidungen D1–D6 vor dem Bau (A-009); Ortszeit geprüft (Betriebszeit 06–22 Uhr = 04–20 UTC im Sommer, 05–21 UTC im Winter; neue Tests für beide); Zahlenprüfung im Build (eine absichtlich eingefügte Zahl wird erkannt); Folien über LibreOffice gerendert und gesichtet, Überlappung auf Folie 3 behoben; Notizen 57–64 s.
- **Offen:** Max erklärt Folien und Kennzahl selbst; Probelauf.

### E-030 · Kennzahl „Mehrkosten des Status quo A“ statt „Anteil 08–14“
- **Person:** Max (R2)
- **Entscheidung:** Für Folie c: Mehrkosten des Status-quo-Fensters 08–14 Uhr gegenüber dem billigsten 6-h-Fenster innerhalb 06–22 Uhr (Ortszeit), je Tag als Differenz der Mittelpreise, je Saison Median und IQR in €/MWh und %; dazu die Verteilung der Startzeit des billigsten Fensters. „Genau 08–14 Uhr an unter 1 % der Tage“ nur als Nebeninfo. Prozent nur für Tage mit positivem billigsten Preis (sonst nicht definiert). Ausdrücklich gekennzeichnet: Rückblick mit bekannten Preisen, keine Strategie.
- **Verworfen:** (a) Anteil der Tage, an denen 08–14 genau das billigste Fenster ist (fast immer null, sagt nichts über die Größenordnung); (b) Anteil der Tage, an denen die billigste Einzelstunde in 08–14 liegt (passt nicht zum 6-h-Block).
- **Ergebnis:** Median-Mehrkosten Winter 9,0, Frühling 19,3, Sommer 22,3, Herbst 15,4 €/MWh; billigstes Fenster beginnt meist um 10 oder 11 Uhr. Prozentwerte im Frühling und Sommer breit gestreut (Preise nahe null), deshalb Kernaussage in €/MWh.
- **Beleg:** `src/fensteranalyse.py`, `pptx_kit/key_figures.json`, Tests `tests/test_fensteranalyse.py`

### A-009 · Auftrag Folien R2: Bestandsaufnahme und Entscheidungen
- **Von → an:** Max (R2) → Claude Code
- **Was:** PowerPoint für Teil R2 per Skript, mit `pptx_kit/` (Kennzahlen, Grafiken, Prüferfragen, Quellen). Erst Bestandsaufnahme, dann Freigabe. Entscheidungen von Max: D1 Kennzahl Mehrkosten (E-030) nach vorheriger Prüfung der Ortszeit; D2 08–14 Uhr = Status quo A, einheitlich benannt; D3 keine Vorlage, Design-Konstanten oben im Skript; D4 Folien und Kit committen; D5 Zahlenprüfung, ausgenommen Bezeichner und Foliennummern; D6 keine Titelfolie. Verschiebbare Menge 2,0 MWh/Tag als ANNAHME, Frage „Warum 2,0 MWh?“ in `defense_qa.md`.
- **Kanal und Datum:** Chat mit Claude Code, 09.11.2026
- **Änderung, nachgezogen von:** E-030, K-007; `docs/schnittstellen.md` (Begriff Status quo A)

### P-007 · PR #7 ohne Review gemergt (auf Anweisung von Max)
- **Problem:** Laut P-003 Merge nach `main` nur nach Review des Paarpartners; R3 ist noch nicht im Repo.
- **Angesprochen von:** Max (R2), 09.11.2026
- **Entscheidung:** Max verlangt den Merge ausdrücklich, damit das Team die bereinigten Daten auf `main` hat. Review durch R3 nachträglich.
- **Ergebnis:** PR #7 am 09.11.2026 gemergt; nachträgliches Review durch Susan am 10.11.2026 erledigt (A-012).

### K-006 · KI-Einsatz Datenbereinigung
- **Werkzeug:** Claude Code
- **Zweck:** Plan der Bereinigung, `src/cleaning.py`, `tests/test_cleaning.py`, `reports/`, `docs/codebook.md`, `data/raw/MANIFEST.md`; Recherche der SDAC-Preisgrenzen und des Umstellungstermins auf 15 Minuten (Quellen in `docs/datenaufbereitung.md`).
- **Wie geprüft:** Plan vor dem Code von Max freigegeben (A-008); 24 Tests grün; Gegenprobe: eine Stunde gelöscht und ein Preis auf 6 000 €/MWh gesetzt → 3 Tests rot; Umstellungstage von Hand nachgesehen (26.10.2025: beide 02:00-Stunden mit 3,19 und 2,02 €/MWh erhalten). Commits mit Präfix `cleaning:` und Trailer `Co-Authored-By: Claude Code`.
- **Offen:** Max erklärt `src/cleaning.py` selbst (Sperrkriterium Erklärbarkeit) bis Fr 13.11.

### E-029 · Bereinigung als eigenes Skript mit Log, Berichten und Codebook
- **Person:** Max (R2), umgesetzt von Claude
- **Entscheidung:** `src/cleaning.py` ersetzt `src/02_aufbereitung.py` (Schritt 02 in `run_all.py`, nach `02_synthetisch`). Jeder Schritt wird mit Zeilenzahl vorher/nachher in `reports/cleaning_log.md` protokolliert; Kennzahlen je Monat und Saison (Mittel, Median, IQR, Anteil negativ) und drei Grafiken in `reports/`; jede Spalte in `docs/codebook.md`; `data/raw/MANIFEST.md` je Rohdatei. Plausibilitätsgrenzen −500 bis +5 000 €/MWh (SDAC; das Maximum lag 2022–2026 zwischen +3 000 und +5 000, daher der weiteste Wert).
- **Verworfen:** Bereinigung ohne Log (nicht nachvollziehbar, K2/K5); Plausibilitätsgrenze +4 000 (galt nicht im ganzen Zeitraum).
- **Beleg:** `src/cleaning.py`, `reports/cleaning_log.md`, Commits `b6bdf86`, `461a29d`

### E-028 · Aggregationsregel ab 01.10.2025: SMARD-Stundenwert
- **Person:** Max (R2)
- **Entscheidung:** Ab der Umstellung der Day-Ahead-Kopplung auf 15-Minuten-Produkte (Handelstag 30.09.2025, Lieferung ab 01.10.2025, NEMO Committee 2025) nutzen wir den Stundenwert, den SMARD veröffentlicht. Er entspricht dem Mittel der vier Viertelstunden (früher geprüft: höchstens 0,005 €/MWh Abweichung über 9 505 Stunden, Commit `b68dfdb`).
- **Verworfen:** 15-min-Daten erneut laden und selbst mitteln (aufwendiger; bei Blöcken zur vollen Stunde kostengleich; Vereinfachung nach E-021).
- **Beleg:** `reports/cleaning_log.md` Schritt 4, `docs/datenaufbereitung.md`

### E-027 · Nur CSV, kein Parquet
- **Person:** Max (R2)
- **Entscheidung:** Alle bereinigten Dateien als CSV (`preise_clean.csv`, `last_synth.csv`, `reports/tables/*.csv`). Zeitstempel als Text mit UTC-Kennung (`ts_utc`) bzw. UTC-Versatz (`ts_lokal`).
- **Verworfen:** Parquet (im Arbeitsauftrag vorgesehen; erhält Datentypen, ist aber nicht in Excel zu öffnen und für das Team eine Hürde, E-022).
- **Beleg:** `docs/codebook.md`, Test `test_spalten_und_typen`

### E-026 · UTC als Schlüssel, nichts mitteln (revidiert E-010 und E-011)
- **Person:** Max (R2)
- **Entscheidung:** Schlüssel ist `ts_utc`. In UTC gibt es keine doppelten oder fehlenden Stunden; die doppelte Oktober-Stunde sind zwei verschiedene UTC-Stunden und bleiben beide mit eigenem Preis erhalten. Lokale Zeit nur als Zusatzspalte; lokale Tage haben 23, 24 oder 25 Stunden.
- **Verworfen:** die bisherige Lösung, die doppelte Stunde zu mitteln (E-010): Sie verwirft eine echte Beobachtung. Ortszeit als Schlüssel: mehrdeutig.
- **Begründung:** keine stille Bereinigungsentscheidung; Umstellung liegt 02–03 Uhr, außerhalb der Betriebszeit 06–22 Uhr, ändert also keine Kosten.
- **Beleg:** Tests `test_oktober_hat_25_lokale_stunden_ohne_mitteln`, `test_lokale_tage_23_24_25_stunden`

### E-025 · Auffällige Preise nur markieren (`flag_outlier`), nie löschen
- **Person:** Max (R2)
- **Entscheidung:** Modifizierter z-Wert (Median, MAD; Iglewicz & Hoaglin 1993) innerhalb Jahr × Monat × Stunde, Betrag > 3,5 → `flag_outlier`. Ergebnis: 1 827 Stunden (4,3 %), rund 70 % davon ungewöhnlich niedrig (Wochenende, Nacht), die ungewöhnlich hohen vor allem mittags. Keine Zeile gelöscht oder verändert. Die Spalte ist nur zur Beschreibung; `src/datenzugriff.py` entfernt sie (Look-ahead).
- **Verworfen:** ±3 Standardabweichungen oder IQR als Löschregel, Kappen/Winsorisieren: Day-Ahead-Preise sind Auktionsergebnisse; Extremwerte sind echt und gerade die günstigen Stunden tragen den Flexibilitätswert (Janczura et al. 2013; Weron 2014). Mittelwert und SD werden zudem von den Ausreißern selbst verschoben (Leys et al. 2013).
- **Beleg:** `reports/tables/ausreisser.csv`, `docs/datenaufbereitung.md` Abschnitt 4, Test `test_ausreisser_nur_markiert_nichts_veraendert`

### E-024 · Produktion an jedem Tag inkl. Feiertage, Betrieb 06–22 Uhr
- **Person:** Max (R2), nach Interview K-005
- **Entscheidung:** `last.produktionstage: taeglich`, Betriebszeit 06–22 Uhr, Verbrauch 50 MWh pro Tag. Der verschiebbare 6-Stunden-Block muss in der Betriebszeit liegen (Prüfung in `02_synthetisch`). Verschiebbarer Anteil bleibt Platzhalter (2,0 MWh), bis Prozess und Menge feststehen.
- **Verworfen:** Produktion nur Mo–Fr ohne Feiertage (bisherige Annahme; bleibt als Sensitivitätsvariante V4).
- **Beleg:** `config/params.yaml` (`last`), `data/processed/last_synth.csv`

### A-008 · Arbeitsauftrag Datenbereinigung: Plan und Freigabe
- **Von → an:** Max (R2) → Claude Code
- **Was:** Auftrag „Datenbereinigung Strompreis-/Lastdaten“ (UTC, Auflösung, Vollständigkeit, Dubletten, Plausibilität, Beschreibung, Join, kein Look-ahead, Tests, Log, Berichte, Codebook, Manifest). Claude legte zuerst einen Plan mit sechs offenen Entscheidungen vor; Max gab frei: alles als CSV, Verbrauch 50 MWh täglich inkl. Feiertage, sonst wie empfohlen; Aggregation über den SMARD-Stundenwert (E-028).
- **Kanal und Datum:** Chat mit Claude Code, 09.11.2026
- **Änderung, nachgezogen von:** E-024 bis E-029, K-006

### K-005 · Interview mit dem Praxiskontakt: Verbrauch, Betriebszeit, flexible Prozesse
- **Gesprächspartner:** Kontakt beim Praxispartner, direktes Interview durch Max, 09.11.2026
- **Aussagen:** Stromverbrauch des Werks rund **50 000 kWh (50 MWh) pro Tag**, **an jedem Tag, auch an Feiertagen**; Produktion **06–22 Uhr** (16 h). Gut verschiebbar („hochflexibel“): **Kälteerzeugung mit Eisspeicher** (Kompressoren bei billigem Strom, Eis auf Vorrat), **Becherherstellung** (Kunststoff-Tiefziehen, von der Milch entkoppelt, über Lager planbar), **Druckluft und Stickstoff** (Kompressoren mit Puffertanks), **Abwasserreinigung** (Belüftung und Pumpen einige Stunden drosseln oder hochfahren).
- **Was wir geändert haben:** `params.yaml` und `last_synth.csv` (50 MWh täglich, 06–22 Uhr), E-024.
- **Offen:** Welcher Prozess ist unser verschiebbarer Fall, mit welcher Menge pro Tag? Fachlich passt die **Becherherstellung** am besten zur Fragestellung (personalgebunden, wöchentlich planbar); Kälte, Druckluft und Abwasser laufen automatisch und täglich steuerbar, passen also eher zum Kontrastfall Tagessteuerung T (Kickoff). Entscheidung im Team.

### P-006 · PR #6 ohne Review gemergt (auf Anweisung von Max)
- **Problem:** Laut P-003 wird nach `main` nur nach Review des Paarpartners gemergt; R3 ist noch nicht im Repo, das Review von PR #6 steht aus.
- **Angesprochen von:** Max (R2), 09.11.2026
- **Entscheidung:** Max verlangt den Merge ausdrücklich, damit das Team die CSV-Daten auf `main` hat. Review durch R3 nachträglich.
- **Ergebnis:** PR #6 am 09.11.2026 gemergt; nachträgliches Review durch Susan am 10.11.2026 erledigt (A-012).

### M-001 · Teamtreffen: gemeinsame Einrichtung und Durchsprache, 09.11.2026
- **Teilnehmende:** alle vier Teammitglieder (u. a. Max, Susan)
- **Inhalte:**
  - VS Code bei allen eingerichtet und das GitHub-Repository darin eingebunden
  - GitHub-Struktur gemeinsam durchgegangen (Ordner `src/`, `data/`, `docs/`, `config/`), `README.md` gelesen
  - Coding Agents eingerichtet: Claude Code (Anthropic) und Codex (OpenAI), siehe K-004
  - Anforderungen besprochen (Kriterienkatalog K1–K10, Abgaben, Termine)
  - Theorie besprochen: Day-Ahead-Markt, Testdesign (jeden Freitag nachspielen, nur damals bekanntes Wissen), Strategien A–D, C, T, Hypothesen H0a–H0c
  - Probleme bei der Einrichtung gemeinsam gelöst, siehe P-005
- **Stand je Paket:**

| Paket | Stand | Rückstand | Maßnahme | Owner | bis |
| --- | --- | --- | --- | --- | --- |
| R1 | Rahmen, Kickoff | Problem Statement, Folien 1–2 | im Team verteilen | R1 | Pitch |
| R2 | Daten fertig als CSV (`data/processed/`), Datenzugriff für R3 | Datenfolie, Code erklären können | Max | R2 | Di 10.11. / Fr 13.11. |
| R3 | Testdesign besprochen | Merkmale, Backtest | Datenzugriff aus `docs/schnittstellen.md` nutzen | R3 | vor 13.11. |
| R4 | Testdesign besprochen | Kostenannahmen | Recherche Umstellungskosten | R4 | vor 13.11. |

### P-005 · Probleme bei der Einrichtung
- **Problem:** Beim Einrichten von VS Code, Repository-Anbindung und Coding Agents traten Probleme auf. [Konkrete Probleme ergänzen, z. B. Anmeldung, Zugriffsrechte, Installation]
- **Angesprochen von:** Team, 09.11.2026
- **Lösungsvorschlag:** gemeinsam im Treffen Schritt für Schritt durchgehen
- **Entscheidung:** im Team gelöst
- **Ergebnis:** alle können auf das Repository zugreifen und mit den Agents arbeiten

### K-004 · Coding Agents für das Team (Claude Code, OpenAI Codex)
- **Werkzeug:** Claude Code (Anthropic), Codex (OpenAI), jeweils in VS Code
- **Zweck:** Unterstützung beim Programmieren und Dokumentieren in den Teilpaketen
- **Wie geprüft:** Jeder Einsatz wird in `docs/ki-nutzung.md` eingetragen (Werkzeug, Zweck, Prüfung); Dateikopf `# KI: …` und Commit-Trailer `AI-Assisted: …`; wer KI-Code committet, muss ihn in der Verteidigung erklären können (Sperrkriterium).

### E-023 · Rollenordner wieder entfernt
- **Person:** Max (R2)
- **Entscheidung:** Der Ordner `rollen/` (R1–R4) wird entfernt; Aufgaben und Zuständigkeiten stehen im Kickoff (`docs/kickoff.md`) und im Tagebuch.
- **Verworfen:** Rollenordner beibehalten (zusätzliche Struktur, die das Team eher verwirrt als entlastet).
- **Begründung:** Repo übersichtlich halten, damit sich alle schnell zurechtfinden (siehe E-022).

### K-003 · Rückkopplung Praxiskontakt: Produktion läuft 16 Stunden am Tag
- **Gesprächspartner:** Kontakt beim Praxispartner (Elektrik), Rücksprache durch Max, 09.11.2026
- **Aussage:** Die Produktion läuft 16 Stunden am Tag.
- **Was wir geändert haben:** `params.yaml`: `last.betrieb_h_pro_tag: 16`, `last.betrieb_start_h: null` (offen). Folge für R3: Der verschiebbare 6-Stunden-Block muss innerhalb der 16 Betriebsstunden liegen; ein Nachtblock außerhalb der Betriebszeit ist nicht zulässig.
- **Offen:** Wann beginnen die 16 Stunden (z. B. 06–22 Uhr)? Welcher Prozess ist verschiebbar, mit welcher Leistung? Betriebsruhe 24./31.12.? Nächste Rückfrage durch Max.

### E-022 · Übergabe als CSV statt Parquet; README gekürzt
- **Person:** Max (R2), umgesetzt von Claude
- **Entscheidung:** `preise_h.csv` und `last_synth.csv` statt Parquet; zusätzliche Spalten `datum` und `stunde` in `preise_h.csv`, damit `groupby("stunde")` ohne Datumsbehandlung geht. Die CSV-Dateien und `results/tables/*.csv` liegen im Repo, damit das Team sie ohne Pipeline-Lauf öffnen kann. `README.md` beginnt jetzt mit „Daten ansehen“; `data/interim/` entfällt (wurde nicht mehr gebraucht).
- **Verworfen:** Parquet beibehalten (kompakter und typsicher, aber nicht in Excel zu öffnen und für Teammitglieder ohne Python-Erfahrung eine Hürde).
- **Begründung:** Das ganze Team (u. a. Susan) soll die Daten mit pandas oder Excel direkt analysieren können (K9, K10). Schnittstelle zu R3 geändert, siehe `docs/schnittstellen.md`.
- **Beleg:** `README.md`, `docs/schnittstellen.md`, Test `test_spalten_laut_schnittstelle`

### E-021 · Nur Stundenpreise, keine 15-Minuten-Daten
- **Person:** Max (R2)
- **Entscheidung:** Wir arbeiten durchgehend mit Stundenpreisen. Ab 01.10.2025 nutzen wir den Stundenwert, den SMARD aus den vier Viertelstunden bildet. Die 15-min-Rohdaten (57 Wochendateien) und `preise_15min` sind gestrichen, ebenso die Sensitivitätsvariante V5. Die Spalte `regime` (Stunden- vs. Viertelstundenhandel) bleibt, damit Test 1 und Test 2 weiter verglichen werden können (H0c).
- **Verworfen:** Eigene Stundenmittel aus 15-min-Daten und eine Variante mit Blockstart in 15-min-Schritten (zu komplex für die verbleibenden 10 Tage; bei Blöcken zur vollen Stunde ohnehin rechnerisch gleich, E-012).
- **Begründung:** Vereinfachung, damit das Team die Daten versteht und nutzen kann. Grenze im Bericht: Ab 10/2025 verschenkt eine Planung im Stundenraster mögliches Potenzial der Viertelstunden (Ausblick).
- **Beleg:** `src/02_aufbereitung.py`, `config/params.yaml` (`daten.aufloesungen`), `docs/sensitivitaet_plan.md`

### A-007 · Datenzugriff für R3 bereitgestellt, offene Punkte
- **Von → an:** R2 (Max) → R3
- **Kanal und Datum:** WhatsApp, Nachricht am 09.11.2026 formuliert, Versand durch Max
- **Was:** `src/datenzugriff.py` liefert je Freitag `historie` (nur bekannte Preise), `zielwoche` (echte Preise der geplanten Woche) und `last`; Nutzung in `docs/schnittstellen.md`.
- **Fragen an R3:** (1) Passt die Planungsuhrzeit Freitag 12:00 (`planung.planungsuhrzeit`)? (2) Neben B mit 4 Wochen auch ein Fenster von 2 Jahren als Variante (Vorschlag von Max)? Dafür reicht `historie_wochen=104`. (3) Stresstest 2022: In den ersten Wochen gibt es kaum Historie, weil die Daten am 01.01.2022 beginnen. Sollen wir ab Dezember 2021 laden (`daten.aufloesungen.hour`), oder bewertet der Stresstest nur Strategien, die auf dem Training gelernt haben?
- **Bis:** Antwort bis Fr 13.11.2026
- **Antwort R3:** offen
- **Änderung, nachgezogen von:** offen

### E-020 · Datenzugriff je Freitag als eigenes Modul mit Look-ahead-Schutz
- **Person:** Max (R2), umgesetzt von Claude
- **Entscheidung:** Neues Modul `src/datenzugriff.py`. Es liefert für jeden Planungsfreitag einer Periode die bis dahin bekannten Preise (`historie`), die echten Preise der geplanten Woche (`zielwoche`) und die Last dieser Woche. Rollierender Ursprung: Jeden Freitag rückt der Stichtag eine Woche weiter, die vergangene Woche gehört ab dann zur Historie. Ein Datensatz für alles, kein neues Einlesen pro Woche. Neue Schalter in `params.yaml`, Block `planung`: Planung freitags 12:00, also bekannt bis Freitag 23:00, weil die Samstagspreise erst gegen 12:45 veröffentlicht werden; nur volle Wochen je Periode.
- **Verworfen:** (a) Jede Woche einen neuen Datensatz einlesen: gleiches Ergebnis, aber viele Dateien und mehr Fehlerquellen. (b) Datumslogik in jeder Strategie selbst schreiben (R3): Jede Strategie könnte die Grenze anders ziehen, ein Look-ahead fiele nicht auf. (c) Wochen über Periodengrenzen mitwerten: Die Woche 29.09.–05.10.2025 hätte Stunden- und Viertelstundenregime gemischt (H0c).
- **Begründung:** K4 Stufe 3 („Validierung korrekt: rollierender Ursprung, Test nie fürs Entwickeln benutzt“), K5 Stufe 5 (automatisierte Prüfung „kein Look-ahead“, dokumentierte Schnittstelle). 38 Freitage in Test 1, 51 in Test 2.
- **Beleg:** `src/datenzugriff.py`, Tests `test_kein_look_ahead_in_allen_planungswochen`, `test_look_ahead_wird_erkannt`, `docs/schnittstellen.md`

### A-006 · Abgleich des Verständnisses von Fragestellung und Testdesign (Susan, Max)
- **Von → an:** Susan Jaturat (Rolle noch nicht eingetragen) → Team, Antwort von Max (R2)
- **Kanal und Datum:** WhatsApp, 09.11.2026, 20:59 und 21:04; Antwort von Max formuliert am 09.11.2026
- **Was (Susans Zusammenfassung):** Produktion läuft 24/7, energieintensive Aufgaben werden auf wahrscheinlich günstige Zeiten gelegt; der Day-Ahead-Preis ist am Vortag bekannt, der Personalplan steht aber freitags für die ganze Woche, deshalb eine Prognose; Vergangenheit nachspielen; ein Monat ab einem Freitag, vier Wochenwerte aufaddieren und mit dem Festpreis vergleichen; „8–14 Uhr billigster Strom wegen Solar“.
- **Bestätigt:** Kern des Testdesigns (Freitag nachspielen, nur Wissen bis zu diesem Freitag, mit echten Day-Ahead-Preisen nachrechnen); Grund für die Prognose (Wochenplanung des Personals); nur der energieintensive Prozess wird verschoben.
- **Korrigiert:** (1) 08–14 Uhr ist der Status quo A (`last.status_quo_start_h: 8`), nicht die günstigste Zeit; dass mittags günstiger ist, ist eine Prototyp-Hypothese, kein Ergebnis. (2) Nicht ein Monat, sondern jeder Freitag in Test 1 (01–09/2025) und Test 2 (10/2025–09/2026); Kennzahl ist die mittlere Ersparnis pro Woche mit 95-%-Konfidenzintervall, keine Summe von vier Werten. (3) Hauptvergleich ist Status quo A mit denselben Day-Ahead-Preisen; Spot gegen Festpreis ist ein eigener Vergleich (R1, R4). (4) Strategie B nutzt die letzten 4 Wochen (`strategien.historie_wochen: 4`), nicht nur die Vorwoche.
- **Antwort Susan:** offen
- **Änderung, nachgezogen von:** keine Änderung an Code oder Annahmen. Hinweis für den Pitch (K9): Testdesign so erklären, dass diese Missverständnisse nicht entstehen.

## 07.11.2026

### A-004 · Regel: Kommunikation immer im Tagebuch dokumentieren
- **Von → an:** Max (R2) → Claude (KI-Assistenz); gilt für alle Absprachen von R2
- **Was:** Jede Kommunikation zwischen Rollen (Nachrichten, Fragen, Antworten, Absprachen) wird sofort mit Datum als A-, P-, K- oder M-Eintrag festgehalten, Antworten werden im bestehenden Eintrag nachgetragen. Festgeschrieben in `CLAUDE.md`, damit jede künftige KI-Sitzung die Regel befolgt.
- **Bis:** ab sofort
- **Änderung, nachgezogen von:** Claude, 07.11.2026 (`CLAUDE.md`, dieser Eintrag)

### K-002 · KI-Einsatz bei Download, Aufbereitung und synthetischem Lastgang
- **Werkzeug:** Claude
- **Zweck:** Code für `src/01_download.py`, `src/02_aufbereitung.py`, `src/02_synthetisch.py`, `src/gemeinsam.py`, erklärende Kommentare, Erweiterung von `tests/test_datenannahmen.py` (jetzt 24 Tests); Vorschläge zur Zeitumstellung mit Alternativen; Entwurf `docs/sensitivitaet_plan.md`; Formulierung und Eintragen der Tagebucheinträge E-008 bis E-018, A-002, A-003, P-002, P-003 und K-002 im Auftrag von Max, inklusive Belege (Commits `b68dfdb`, `9ce870e`, `38765e1`, `38e0516`).
- **Wie geprüft:** (1) `pytest tests/`: 24 Tests grün. (2) Gegenprobe: eine Rohdatei von Hand geändert → Download bricht mit Meldung ab, Integritätstest rot; in `preise_h` einen Preis gelöscht und Samstage als Werktag markiert → drei Tests rot. (3) Nachgerechnet: 26.10.2025 02:00 Uhr = (3,19 + 2,015) / 2 = 2,6025 €/MWh; 29.03.2026 ohne 02:00 Uhr; Stundenzahl 1 765 Tage × 24 − 5 = 42 355. (4) Zweiter Lauf ohne Internet: 0 Dateien geladen. (4b) Kommentare nachträglich ergänzt und Werktagsregel verschoben: Ausgabedateien per SHA256 vorher/nachher bit-gleich. (4c) Last: Feiertagsvariante nur für die Last umgestellt → Abgleichstest rot. (5) Erklären des Codes durch Max: **offen**, vor dem Zwischenreview Fr 13.11. nachholen (Sperrkriterium Erklärbarkeit). Kommentare im Code dafür ergänzt (Commit `9ce870e`).
- **Was wir geändert haben:** Nach Rückmeldung von Max: Kommentare auf Englisch und pro Abschnitt statt Zeile für Zeile; ENTSO-E-Abgleich gestrichen (E-015); Firmenname des Praxispartners im öffentlichen Repo anonymisiert. Die Einträge wurden von Claude formuliert und von Max zur Prüfung freigegeben; Abweichung von der Regel „jeder committet seine Einträge selbst“ hiermit offengelegt.

### P-003 · PR #3 ohne Review gemergt
- **Problem:** Laut Kickoff prüfen sich die Review-Paare per Pull Request. PR #3 (Download, Aufbereitung, Lastgang) wurde am 07.11.2026 gemergt, bevor R3 ihn gesehen hat; R3 war noch kein Collaborator im Repo, deshalb konnte niemand als Reviewer eingetragen werden.
- **Angesprochen von:** Max (R2), 07.11.2026
- **Lösungsvorschlag:** R3 reviewt nachträglich und kommentiert auf GitHub; Fehler werden in einem neuen PR behoben. Ab jetzt: kein Merge nach `main` ohne Review des Paarpartners.
- **Entscheidung:** angenommen (Max); Zustimmung des Teams über A-003 angefragt
- **Ergebnis:** offen

### P-002 · Sensitivitätsschwelle vor dem Rechnen festlegen
- **Problem:** Ohne vorab festgelegte Schwelle könnte man im Nachhinein jede Änderung als „klein“ deklarieren.
- **Angesprochen von:** Max (R2), 07.11.2026
- **Lösungsvorschlag:** Relevant, wenn sich die mittlere Netto-Ersparnis um mehr als 5 % ändert oder sich eine Entscheidung zu H0a/H0b/H0c umkehrt. Beschluss, bevor R3 den ersten Testlauf sieht.
- **Entscheidung:** offen; Vorschlag an R3 über A-003, Teambeschluss bis Fr 13.11.2026
- **Ergebnis:** offen

### E-018 · Zeitumstellung ist im Basisszenario kostenneutral
- **Person:** Max (R2)
- **Entscheidung:** Die Varianten V1 (Oktober: erste/zweite statt Mittel) und V2 (März: Stunde füllen) werden im Basisszenario nicht durchgerechnet. Grund: Die Zeitumstellung ist immer am letzten Sonntag im März bzw. Oktober; Sonntage sind keine Werktage, die Last ist dort 0 MWh. Geprüft für alle 10 Umstellungstage 2022–2026. Ein Test stellt sicher, dass das so bleibt.
- **Verworfen:** V1 und V2 voll durch den Backtest schicken: Das Ergebnis wäre zwangsläufig 0 % und damit eine Scheinprüfung, die nur Rechenzeit und Seiten kostet.
- **Begründung:** Analytisch und per Test belegt statt gerechnet. Relevant wird die Frage erst bei Wochenendproduktion (anderes Lastszenario); dann werden V1/V2 aktiviert. Wirkt weiterhin auf beschreibende Statistiken (Preisprofile, Boxplots), dort ist sie vernachlässigbar (1 von 8 760 Stunden pro Jahr).
- **Beleg:** Test `test_zeitumstellung_nur_an_lastfreien_tagen`, `docs/sensitivitaet_plan.md`

### A-003 · Übergabe R2 → R3: Preise und Last bereit, Vorschläge zum Backtest
- **Von → an:** R2 (Max) → R3; Review-Paar R2 ↔ R3 laut Kickoff
- **Kanal und Datum:** WhatsApp, Nachricht am 07.11.2026 formuliert (Text: Commit dieses Eintrags), Versand durch Max. Laut Kickoff ist der Chat kein Beleg, deshalb dieser Eintrag.
- **Was (Datei, Spalten, Einheit):**
  - `data/processed/preise_h.parquet`: `zeit` (Europe/Berlin, Stundenbeginn), `preis_eur_mwh` (EUR/MWh), `regime` (stunde/viertel), `werktag` (bool); 2022-01-01 bis 2026-10-31, 42 355 Stunden, 0 Lücken.
  - `data/processed/last_synth.parquet`: `datum`, `mwh` (MWh pro Tag); 2,0 an Werktagen, sonst 0 (Platzhalter).
  - `data/processed/preise_15min.parquet`: wie `preise_h`, 15 min ab 01.10.2025.
  - Stolperfallen in `docs/schnittstellen.md`.
- **Fünf Punkte mit Vorschlag von R2:**
  1. *23-Stunden-Tag im März:* keine Änderung nötig. Alle Umstellungstage sind Sonntage, die Last ist dort 0 (E-018, Test). Blockkosten nur für Werktage bilden.
  2. *Backtest als Funktion:* `backtest(preise_h, last, params) -> DataFrame` mit den Spalten von `backtest_wochen.csv`; liest und schreibt keine Dateien, Seed aus `params`; `main()` macht nur Einlesen, Aufruf, Speichern. Skizze in `docs/schnittstellen.md`.
  3. *15-min-Blockstart (V5, H0c):* neuer Schalter `strategien.blockstart_raster_min` (60 = Basis, 15 = Variante), nur Testperiode 2, mit `preise_15min.parquet`; ein Block = `blocklaenge_h` × 4 Viertelstunden; Oracle C und T im selben Raster. Kontrolle: Raster 60 auf 15-min-Preisen muss exakt das Basisergebnis liefern.
  4. *Review:* R3 schickt den GitHub-Namen, Max lädt als Collaborator ein und füllt `CODEOWNERS`; R3 kommentiert PR #3 nachträglich; ab jetzt wird jeder PR nach `main` erst nach Review des Paarpartners gemergt.
  5. *Relevanzschwelle Sensitivität:* relevant, wenn sich die mittlere Netto-Ersparnis um mehr als 5 % ändert oder eine Entscheidung zu H0a/H0b/H0c kippt; Beschluss mit Datum, bevor R3 den ersten Testlauf sieht (P-002).
- **Bis:** Antwort R3 bis Mo 09.11.2026; Backtest-Funktion vor dem Zwischenreview Fr 13.11.2026.
- **Antwort R3:** offen
- **Änderung, nachgezogen von:** offen

### E-017 · Eine Werktagsregel für Preise und Last
- **Person:** Max (R2)
- **Entscheidung:** Die Funktion `werktage()` liegt in `src/gemeinsam.py` und wird von `02_aufbereitung` (Spalte `werktag`) und `02_synthetisch` (Last) benutzt. Ein Test prüft, dass beide an denselben Tagen Werktag sagen.
- **Verworfen:** Die Regel in beiden Skripten getrennt (könnte auseinanderlaufen; dann verbrauchte R3 an einem Feiertag Strom, für den kein Werktagspreis vorgesehen ist).
- **Begründung:** Gegenprobe: Feiertagsvariante nur für die Last umgestellt → Test rot.
- **Beleg:** Test `test_last_und_preise_gleiche_werktage`, Commit `38765e1`

### E-016 · Synthetischer Lastgang deterministisch
- **Person:** Max (R2)
- **Entscheidung:** `src/02_synthetisch.py` schreibt `last_synth.parquet` (`datum`, `mwh`): an jedem Werktag `last.mwh_pro_werktag` (Platzhalter 2,0 MWh), sonst 0 MWh; ein Eintrag je Kalendertag im Preiszeitraum, rund 500 MWh pro Jahr. Ohne Zufall. Alle Werte sind Platzhalter, vom Praxiskontakt zu plausibilisieren.
- **Verworfen:** (a) Zufällige Schwankung der Tagesmenge mit festem Seed: Sie träfe jede Strategie in derselben Woche gleich (gepaarter Vergleich), änderte also nicht, welche Strategie günstiger ist, brächte aber einen Parameter (Schwankungsbreite), den niemand gegen die Realität prüfen kann. (b) Nur Werktage als Zeilen: Ein fehlender Tag wäre nicht von einer echten Lücke zu unterscheiden; mit 0 MWh ist „keine Produktion“ ausdrücklich.
- **Begründung:** Einfach, reproduzierbar, erklärbar. Die Unsicherheit über die Menge wird über die Sensitivität (V6 Menge, V7 Blocklänge) gezeigt statt über künstliches Rauschen. Der Text in `last.werktage` wird geprüft; ändert ihn jemand, bricht das Skript ab, statt still Mo–Fr weiterzurechnen.
- **Beleg:** `src/02_synthetisch.py`, `docs/datenkatalog.md`, Tests `test_last_*`, Commit `38765e1`

### E-015 · Kein Abgleich mit ENTSO-E; K2 Stufe 5 über die Sensitivitätsrechnung
- **Person:** Max (R2)
- **Entscheidung:** Wir gleichen die SMARD-Preise nicht mit der ENTSO-E Transparency Platform ab. K2 Stufe 5 („Datenqualität aktiv geprüft“) belegen wir mit einer Sensitivitätsrechnung: Wie stark ändert sich die Ersparnis, wenn wir Zeitumstellung, Feiertagskalender, Zeitauflösung und die synthetischen Parameter anders wählen?
- **Verworfen:** Abgleich SMARD gegen ENTSO-E (so im Kickoff noch vorgesehen). SMARD bezieht die Day-Ahead-Preise von ENTSO-E, beide sind also keine unabhängigen Quellen; ein Abgleich fände höchstens Übertragungsfehler. Diese Prüfung haben wir innerhalb von SMARD schon (eigenes Stundenmittel gegen SMARD-Stundenwert, max. 0,005 €/MWh). Der Aufwand (Konto, API-Schlüssel) brächte für K2 nichts dazu.
- **Begründung:** Die Katalogformulierung nennt die Sensitivitätsrechnung ausdrücklich als Weg zu Stufe 5; sie prüft zudem die synthetischen Daten, die sich gegen keine Quelle prüfen lassen.
- **Beleg:** `docs/sensitivitaet_plan.md`, später `results/tables/sensitivitaet.csv`; Commit `38e0516`

### A-002 · Neue Parameter und Dateien von R2
- **Von → an:** R2 → R1 (Owner `config/`), R3
- **Was:** `params.yaml`: neue Einträge `markt.regimewechsel`, `markt.zeitzone`, Block `daten` (URL, Download-Zeiträume, Pfade, Retry). Neue Dateien `preise_15min.parquet`, `zeitumstellung.csv`, `datenqualitaet.csv` in `docs/schnittstellen.md` eingetragen. `preise_h.parquet` unverändert laut Schnittstelle.
- **Bis:** 07.11.2026, Review durch R1 und R3 per Pull Request
- **Änderung, nachgezogen von:** Review durch R1 (`params.yaml`) und R3 offen, angefragt über A-003; PR #3 wurde vorher gemergt (P-003).

### E-014 · Werktage: gesetzliche Feiertage Bayern, Mariä Himmelfahrt als Variante
- **Person:** Max (R2)
- **Entscheidung:** Werktag = Montag bis Freitag und kein gesetzlicher Feiertag in Bayern (Paket `holidays`, `subdiv="BY"`). Mariä Himmelfahrt (15.08.) gilt nur in überwiegend katholischen Gemeinden; Schalter `feiertagsvariante_mariae_himmelfahrt` in `params.yaml` (Standard: false).
- **Verworfen:** Feiertagsliste von Hand (fehleranfällig); 24./31.12. als arbeitsfrei (keine gesetzlichen Feiertage; Betriebsruhe ist eine offene Frage an den Praxiskontakt, ggf. Variante V4).
- **Beleg:** Test `test_werktage_bayern_und_variante`

### E-013 · Echte Lücken sichtbar lassen; negative Preise behalten
- **Person:** Max (R2)
- **Entscheidung:** Liefert SMARD für eine Stunde keinen Wert, bleibt die Zeile mit leerem Preis stehen und der Test `test_keine_luecken` schlägt an. Negative Preise und Nullpreise bleiben unverändert drin. Stand 07.11.2026: 0 Lücken, 0 doppelte Zeitstempel, 1 877 Stunden mit negativem Preis (2022–10/2026).
- **Verworfen:** Lückenzeilen löschen (Lücke unsichtbar, Wochen hätten weniger Stunden); negative Preise auf 0 setzen oder entfernen (sind echte Auktionsergebnisse, genau dort liegt Flexibilitätswert; K3 S5 „Ausreißer als Information“).
- **Beleg:** `results/tables/datenqualitaet.csv`, Test `test_preisbereich`

### E-012 · Viertelstunden zu Stundenmitteln; 15-min-Daten separat
- **Person:** Max (R2)
- **Entscheidung:** Ab 01.10.2025 ist der Stundenpreis das arithmetische Mittel der vier Viertelstunden, nur wenn alle vier vorhanden sind. Die 15-min-Werte liegen zusätzlich in `preise_15min.parquet`.
- **Verworfen:** (a) Die Stundenwerte von SMARD direkt übernehmen: SMARD rechnet sie selbst und rundet auf zwei Nachkommastellen; wir nutzen sie stattdessen als Prüfung (max. Abweichung 0,005 €/MWh bei 9 505 Stunden). (b) Median oder letzter Wert: entspricht nicht den Kosten. (c) Mittel auch bei fehlenden Viertelstunden: würde eine Lücke still füllen.
- **Begründung:** Bei gleichmäßiger Leistung innerhalb der Stunde gilt exakt: Kosten = Mittelpreis × Energie. Das Mitteln glättet Spitzen (Maximum 2026: 697 €/MWh Stunde gegen 747 €/MWh Viertelstunde); wie viel Ersparnis das kostet, zeigt die Sensitivität 15 statt 60 min (K2, K3).
- **Einschränkung:** Der Abgleich mit dem SMARD-Stundenwert prüft nur auf Rechen- und Übertragungsfehler, er ist keine unabhängige Quelle (siehe E-015).
- **Beleg:** `results/tables/datenqualitaet.csv` (Spalten `abw_smard_stunde_*`), Test `test_stundenmittel_passt_zu_viertelstunden`, Commit `b68dfdb`

### E-011 · Zeitumstellung März: fehlende Stunde markieren, nicht füllen
- **Person:** Max (R2)
- **Entscheidung:** Am letzten Sonntag im März gibt es 02:00 Uhr nicht. Der Tag hat 23 Zeilen; die Tage stehen in `zeitumstellung.csv` und in `datenqualitaet.csv`.
- **Verworfen:** Interpolieren oder Vorwärtsfüllen: erfindet einen Preis für eine Stunde, in der niemand Strom verbraucht; ein Block über 02:00 Uhr bekäme Kosten für eine nicht existierende Stunde.
- **Begründung:** Keine stillen Annahmen in den Daten; R3 ist über `docs/schnittstellen.md` informiert. Kostenwirkung im Basisszenario null, weil Sonntag (E-018).
- **Beleg:** Test `test_maerz_fehlende_stunde_wird_nicht_aufgefuellt`, `test_stunden_pro_tag`

### E-010 · Zeitumstellung Oktober: doppelte Stunde mitteln
- **Person:** Max (R2)
- **Entscheidung:** Am letzten Sonntag im Oktober gibt es 02:00–03:00 Uhr zweimal (25 Stunden). Beide Preise werden gemittelt und als eine Zeile 02:00 Uhr abgelegt, der Tag hat 24 Zeilen. Fehlt einer der beiden Werte, bleibt das Ergebnis leer.
- **Verworfen:** (a) Beide Stunden behalten (25 Zeilen): ohne Informationsverlust, aber die Blockkosten-Matrix Tag × Startstunde (R3) braucht genau einen Wert je Uhrzeit. (b) Nur die erste oder zweite Stunde nehmen: willkürlich, wirft einen echten Preis weg. (c) Durchgehend in UTC rechnen: Schichten richten sich nach der Uhr im Werk; in UTC verschöbe sich der Block halbjährlich um eine Stunde.
- **Begründung:** Betrifft 1 Nachtstunde pro Jahr (5 im ganzen Zeitraum); Tagesblöcke wie 08–14 Uhr nie. Mittel = Kosten bei gleichmäßigem Verbrauch über beide Stunden, halbiert auf eine Stunde. Die Umstellungstage sind immer Sonntage, also keine Werktage; im Basisszenario fällt dort keine Last an, die Wahl ändert die Kosten nicht (E-018).
- **Beleg:** `src/02_aufbereitung.py::zu_ortszeit`, `data/processed/zeitumstellung.csv`, Test `test_oktober_doppelte_stunde_wird_gemittelt`

### E-009 · Integrität der Rohdaten über SHA256
- **Person:** Max (R2)
- **Entscheidung:** Je Datei URL, Abrufzeitpunkt, SMARD-Erstellzeitpunkt, Größe und SHA256 in `manifest.csv`. Jeder Lauf und ein Test prüfen, dass sich keine Rohdatei geändert hat. Wurde eine Woche geladen, bevor sie vorbei war, und fehlen deshalb Werte, wird sie neu geladen; die alte Datei bleibt als `*.veraltet-<datum>.json` liegen.
- **Verworfen:** Nur ein Abrufdatum in `SOURCES.md` (eine veränderte Datei fiele nicht auf); unvollständige Dateien überschreiben (verletzt „Rohdaten nie überschreiben“).
- **Begründung:** Prüfbare Herkunft (Sperrkriterium Datenherkunft); Gegenprobe: eine von Hand geänderte Zahl wird sofort gemeldet.
- **Beleg:** `tests/test_datenannahmen.py::test_rohdaten_unveraendert`, Commit `b68dfdb`

### E-008 · Rohdaten: SMARD-JSON wochenweise, unverändert, im Repo versioniert
- **Person:** Max (R2)
- **Entscheidung:** `src/01_download.py` lädt die SMARD-Wochendateien (Filter 4169, DE-LU, `hour` ab 2022-01-01, `quarterhour` ab 2025-10-01, bis Datenstand) als Original-Bytes nach `data/raw/smard/4169/<auflösung>/`. Vorhandene Dateien werden nicht neu geladen; der Schritt läuft dann offline. Die Rohdaten (ca. 2 MB, 310 Dateien) liegen im Repo.
- **Verworfen:** (a) CSV-Export von smard.de per Hand: nicht reproduzierbar, kein Skript. (b) Bei jedem Lauf neu laden: SMARD korrigiert nachträglich, Ergebnisse würden sich ohne unser Zutun ändern; ohne Internet läuft nichts. (c) Rohdaten nicht ins Repo: Dritte müssten neu laden und bekämen eventuell andere Werte. CC BY 4.0 erlaubt die Weitergabe mit Namensnennung.
- **Begründung:** Sperrkriterium Reproduzierbarkeit, K5 Stufe 5 (neue Daten: nur `datenstand` ändern), K2 (Herkunft je Datei belegbar).
- **Beleg:** `src/01_download.py`, `data/raw/smard/manifest.csv`, `data/raw/SOURCES.md`, Commit `b68dfdb` (PR #3, Merge `e56aeb1`)

### E-007 · Abgrenzung auf Day-Ahead, kein Intraday
- **Person:** Max
- **Entscheidung:** Analyse nur mit Day-Ahead-Preisen DE-LU.
- **Verworfen:** Intraday-Preise einbeziehen.
- **Begründung:** Schichtplan steht eine Woche vorher fest, Intraday-Preise sind erst Stunden vorher bekannt; Spotverträge orientieren sich üblicherweise am Day-Ahead-Preis (Annahme, belegen); Intraday braucht aktives Trading. Intraday als Ausblick.
- **Beleg:** `config/params.yaml` (markt.produkt)

### E-006 · Mehrfachtest-Korrektur
- **Person:** Max
- **Entscheidung:** Bonferroni, α = 0,05 / 3 ≈ 0,017 je Hypothese.
- **Verworfen:** α = 0,05 je Test (Risiko eines Zufallstreffers über drei Tests fast 15 %).
- **Beleg:** `config/params.yaml` (statistik)

### E-005 · Fragestellung und Nullhypothesen festgelegt (vor jeder Auswertung)
- **Person:** Max (Vorschlag), Team (Bestätigung offen)
- **Entscheidung:** Fragestellung und H0a, H0b, H0c wie im README.
- **Verworfen:** Ja/Nein-Frage „Senkt ein Betrieb … seine Energiekosten?“ (nicht offen, kein Rahmen, keine Methode erkennbar); Fokus auf Kälteerzeugung (täglich automatisch steuerbar, Wochenplanung wäre unbegründet; bleibt Kontrastfall T).
- **Begründung:** Analysefrage mit räumlichem, zeitlichem und thematischem Rahmen; Begriffe operationalisiert (siehe Kickoff-Dokument).

### E-004 · Praxisfall Großmolkerei
- **Person:** Max
- **Entscheidung:** Szenario angelehnt an ein bayerisches Werk eines realen Praxispartners; im Bericht „Großmolkerei in Bayern“, Name nur mit schriftlicher Freigabe.
- **Verworfen:** fiktive Galvanik (keine Rückkopplung möglich); Siemens Energy (kaum flexible Last, Vertraulichkeit).
- **Begründung:** Max hat einen Kontakt im Werk (Elektriker) für die Rückkopplung (K1 Stufe 5).

### E-003 · Daten: echt, wo möglich, synthetisch, wo nötig
- **Person:** Max
- **Entscheidung:** Preise echt von SMARD; Lastgang, Kosten und Betriebsdaten synthetisch mit festem Seed.
- **Verworfen:** Preise generieren (Prüfungen fänden nur, was wir hineinstecken; entwertet K2 und K6).
- **Grundlage:** Der Prof hat die Nutzung generierter Daten in der Vorlesung am **[Datum eintragen]** erlaubt; Max war anwesend. **[Folie oder Moodle-Link eintragen, falls vorhanden]**

### P-001 · Unklar, ob generierte Daten erlaubt sind
- **Problem:** Erlaubnis zunächst nur aus dem Gruppenchat bekannt, Quelle unklar; Sperrkriterium Datenherkunft.
- **Angesprochen von:** Max, 07.11.2026
- **Lösungsvorschlag:** Prof direkt fragen.
- **Ergebnis:** Gelöst. Max bestätigt, dass der Prof es in der Vorlesung erlaubt hat (siehe E-003).

### E-002 · Prototyp nur als Machbarkeitsnachweis
- **Person:** Max
- **Entscheidung:** Der vorhandene Notebook-Prototyp gilt als Machbarkeitsnachweis. Seine Zahlen sind Hypothesen, keine Ergebnisse. Jedes Paket wird vom Owner neu aufgebaut.
- **Verworfen:** Prototyp direkt übernehmen (Eigenanteil je Person nicht nachweisbar).

### K-001 · KI-Einsatz bei Themenfindung und Planung
- **Werkzeug:** Claude
- **Zweck:** Prototyp-Notebook (SMARD-Download, Backtest), Kickoff-Dokument, Abgleich mit dem Kriterienkatalog, Formulierung der Fragestellung.
- **Prüfung:** Abgleich mit Kriterienkatalog und Kursmaterial durch das Team; Prototyp-Zahlen ausdrücklich nicht als Ergebnis übernommen.

### E-001 · Rollen und Teilpakete
- **Person:** Team
- **Entscheidung:** Vier Rollen R1 bis R4 mit zusammengelegten Teilpaketen (Katalog 1.2), Vertretungen R1↔R4, R2↔R3. Personen: **[eintragen]**.

### A-001 · Termine
- Case- und Rollen-Pitch: **[Datum eintragen]**
- Analyse fertig: So 15.11.2026
- Endpräsentation: ab 16.11.2026, Termin **[eintragen]**
- Abgabe Bericht: **[eintragen]**
- Praxisgespräch: Sonntag 08.11. oder Montag 09.11.2026

---

## Vorlagen

### E-xxx · Titel
- **Person:**
- **Entscheidung:**
- **Verworfen:**
- **Begründung:**
- **Beleg:** (Commit, Datei, Berichtsseite)

### P-xxx · Titel
- **Problem:**
- **Angesprochen von:** (Person, Datum)
- **Lösungsvorschlag:**
- **Entscheidung:**
- **Ergebnis:**

### M-xxx · Meilenstein: Titel, Datum
| Paket | Stand | Rückstand | Maßnahme | Owner | bis |
| --- | --- | --- | --- | --- | --- |
| R1 | | | | | |
| R2 | | | | | |
| R3 | | | | | |
| R4 | | | | | |

### A-xxx · Absprache/Schnittstelle
- **Von → an:**
- **Was (Datei, Spalten, Einheit):**
- **Bis:**
- **Änderung, nachgezogen von:**

### K-xxx · KI-Einsatz oder Rückkopplung
- **Werkzeug bzw. Gesprächspartner:**
- **Zweck bzw. Aussage:**
- **Wie geprüft bzw. was wir geändert haben:**
