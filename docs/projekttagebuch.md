# Projekttagebuch

Ein Eintrag pro Entscheidung, Problem, Meilenstein, Absprache oder KI-Einsatz. Neueste Einträge oben. Jeder Eintrag wird von der Person committet, die ihn verfasst. Entscheidungen aus dem WhatsApp-Chat werden innerhalb von 24 Stunden hier eingetragen.

Eintragsarten: **E** Entscheidung · **P** Problem/Konflikt · **M** Meilensteinprotokoll · **A** Absprache/Schnittstelle · **K** KI-Einsatz und Rückkopplung

---

## 11.11.2026

### P-014 · Branch `claude/great-pasteur-p9emmq` ohne Review nach `main` gemergt (auf Anweisung von Max)
- **Problem:** Laut P-003 Merge nach `main` nur nach Review des Paarpartners. Susan (R3) hat die Phasen 1–5, die Analyseseite und Review-Phase 1 nicht reviewt; ihre Bestätigungen (K-013 bis K-015, E-056) und die von Caro und Chiara (E-045) sind offen.
- **Angesprochen von:** Claude, 11.11.2026
- **Entscheidung:** Max verlangt den Merge ausdrücklich („merge alles“), damit das Team für die Präsentation (12.11.2026) mit dem Stand auf `main` arbeiten kann. Vorher geprüft: `pytest tests/` 80 grün, `python src/run_all.py` komplett, Zahlen des Hauptfalls bitgleich (K-019).
- **Offen:** Review-Phase 2–5 (Zuordnung der Hypothesen, Quellenabgleich, Planungsskripte, Control-Seite, Prüfung) folgt auf einem neuen Branch; nachträgliches Review durch Susan auf dem Pull Request.

### K-019 · KI-Einsatz Review Phase 1 (Vertrag, Konsistenz)
- **Werkzeug:** Claude Code, Sitzung von Max nach dem Review-Prompt (Phasen 0–5)
- **Zweck:** Vertrag auf Faktor 1,0 (A-018), Umbenennung `test_2` (E-059), Abschnitt Spot gegen Festpreis gekürzt, B_16 als „nicht signifikant“, Rollen (E-057), „2–4 Uhr“ angeglichen.
- **Wie geprüft:** `pytest tests/`: 80 grün; `python src/run_all.py` komplett (10 Schritte, 3:42 min); alle bisherigen Zahlen für Faktor 1,0 bitgleich (netto_tests, ki_strategien, kipppunkte, wirtschaftlichkeit, backtest_wochen, sensitivitaet), nur die Zeilen des 30-%-Falls entfallen; Analyseseite neu ausgeführt.

### P-013 · Folien widersprechen dem Repo an drei Stellen
- **Problem:** (1) Folie 3 nennt H0a = feste Uhrzeit, H0b = Wochenplanung (16 Wochen) gegen 22–24 Uhr, H0c = Rücktest; vorab festgelegt sind andere H0a–H0c (`docs/hypothesen.md`, `7a63c15`). (2) Folie 3, Rahmen: „Reinigung heute 22–24 Uhr ist Annahme“; laut K-012 vom Partner bestätigt. (3) Folie 4 nennt R2 „Datenanalyse & IT“ und R3 „Energieeinkauf“; Teamdokument und Review: „Datenerhebung & IT“, „Modellierung & Statistik“.
- **Angesprochen von:** Claude beim Abgleich mit der Präsentation (Projektvorstellung 12.11.2026), 11.11.2026
- **Lösung:** (1) nach E-056 (Variante 1); (2) und (3) Folie anpassen. Folien liegen nicht im Repo; Änderung durch R1.
- **Offen:** Chiara passt Folie 3 und 4 an.

### E-059 · Benennung: `test_2` statt `test_2_viertel`, Empfehlung „fest 3 Uhr (3–5 Uhr)“, B_16 „nicht signifikant“
- **Person:** Max (R2), nach Review (Punkt F)
- **Entscheidung:** Periode `test_2_viertel` heißt überall `test_2` (Code, `params.yaml`, Ergebnisdateien, Notebook, Doku), weil die Viertelstunde Nichtziel ist (E-043). Die Empfehlung lautet einheitlich „fest 3 Uhr (3–5 Uhr)“; „2–4 Uhr“ in Erklärzettel und Ishikawa ersetzt (dort war das Preistal gemeint, jetzt „meist 2–5 Uhr“). B_16 gegen D heißt im Text „+10 € pro Woche, nicht signifikant (p = 0,019 > 0,017)“. Die Spalte `regime` in `preise_clean.csv` bleibt (Marktfakt).
- **Verworfen:** auch `test_1_stunde` umbenennen (nicht verlangt; auf Wunsch in Phase 5).

### E-058 · Zweite Preisquelle: Energy-Charts, teilweise unabhängig (revidiert den Sensitivitätsplan)
- **Person:** Max (R2), nach Review (Punkt D)
- **Entscheidung:** Abgleich SMARD gegen Energy-Charts (Fraunhofer ISE), gleicher Zeitraum, UTC-Stunden; Kennzeichnung „teilweise unabhängig (gleiche EPEX-Auktion, eigene Aufbereitung)“. Umsetzung in Phase 3.
- **Verworfen:** ENTSO-E Transparency (braucht API-Token, ebenfalls dieselbe Auktion); kein Abgleich wie im Sensitivitätsplan (K2 Stufe 5 verlangt eine zweite Quelle, der Übertragungsfehler-Check ist genau ihr Wert).
- **Revidiert:** `r2/docs/sensitivitaet_plan.md`, Abschnitt „Kein Abgleich mit ENTSO-E“.

### A-019 · IT-Aufwand für die Automatisierung an R4
- **Von → an:** Max (R2) → Caro (R4)
- **Was:** Aufwand für den n8n-Workflow (baut Max selbst; Claude liefert `src/plan_woche.py`, `src/soll_ist.py`, Tests, `n8n/README.md`): **3–6 Personentage, Tagessatz 700 € (Bandbreite 500–900 €)**, Teamannahme. Damit einmalige Umstellungskosten 1 500–5 400 €, Mitte 3 150 € (4,5 PT × 700 €). R4 rechnet den Break-even damit neu (Phase 4).
- **Kanal und Datum:** Chat Max mit Claude Code, 11.11.2026

### E-057 · Rollen nach Review: Process Map bei R4, Control bei R2 (abweichend vom Teamdokument)
- **Person:** Max (R2) für das Team
- **Entscheidung:** Rollennamen wie im Teamdokument: R1 Projektleitung & Controlling (Chiara), R2 Datenerhebung & IT (Max), R3 Modellierung & Statistik (Susan), R4 Produktion & Schichtplanung (Caro). Abweichend vom Teamdokument gehört die Process Map zu R4 und Control (Kennzahl, Rücknahmeregel, Planungsskripte, Control-Seite) zu R2.
- **Verworfen:** Process Map und Control bei R1 (Teamdokument): R4 kennt den Ablauf der Nacht, R2 baut die Skripte und die Kennzahl.
- **Beleg:** `docs/kickoff.md` (Rollentabelle), `docs/annahmen.md` (Rollen); revidiert E-050 (Process Map bei R1).

### E-056 · Hypothesen: Variante 1 (vorab festgelegte H0a–H0c bleiben konfirmatorisch)
- **Person:** Max (R2), Entscheidung über Variante 1; Susan (R3) bestätigt hier
- **Entscheidung:** Konfirmatorisch sind nur die vorab festgelegten H0a–H0c (`7a63c15`), α = 0,05/3. FS1–FS3 aus dem Teamdokument stehen daneben als Teamfragen mit Zuordnung und sind explorativ. Folie 3 wird darauf umgestellt (P-013). Umsetzung (Abschnitt „Zuordnung“ in `docs/hypothesen.md`, Notebook) in Phase 2.
- **Verworfen:** Variante 2 (FS1–FS3 zusätzlich konfirmatorisch, α = 0,05/6): nicht zulässig, weil das Teamdokument nach der Berechnung der Testzeiträume entstand (E-055).
- **Offen:** Bestätigung durch Susan.

### E-055 · Teamdokument nach den Testergebnissen: FS1–FS3 und B_16 sind explorativ
- **Person:** Max (R2)
- **Befund:** Das Teamdokument „AuE_Projekt_gruppeF“ (16 Wochen, FS1–FS3) entstand am 11.11.2026 **nach** der Berechnung der Testzeiträume. Zeitfolge laut git (UTC): Regeln eingefroren 13:36 (`1d59427`), Testzeiträume gerechnet 13:45 (`f6a06df`), B_16 und FS1–FS3 ergänzt 13:55 (`1ef4baa`).
- **Entscheidung:** FS1–FS3 und B_16 werden überall als **explorativ** gekennzeichnet. Die Empfehlung (fest 3 Uhr) hängt nicht daran: Sie stützt sich auf die vorab festgelegten H0a und H0b.
- **Verworfen:** „Fragen vorab festgelegt, nur Code später“ (trifft nicht zu).

### A-018 · Vertrag: Reinigung zu 100 % am Day-Ahead (verbindlich, Owner R1)
- **Von → an:** Max (R2) nach Review → alle; Owner R1 (Chiara)
- **Was:** Die 70 % Festpreis decken den Grundverbrauch des Werks und werden immer voll verbraucht. Die Reinigung liegt obendrauf und wird zu 100 % am Day-Ahead gekauft. Vertragsfaktor 1,0 ist der einzige Hauptfall. Faktor 0,3 ist aus Fazit, Kernaussagen, Netto-Tests, Kipppunkten und Break-even entfernt und bleibt nur als Sensitivität V8 („falls der Festpreis nicht voll verbraucht wird“). Der Abschnitt Spot gegen Festpreis ist auf eine Einordnung gekürzt (entscheidet nicht über die Uhrzeit); Grafik g6 entfällt, die Zahlen bleiben in `ergebnisse/spot_festpreis.csv`.
- **Kanal und Datum:** Review, weitergegeben von Max, 11.11.2026
- **Änderung, nachgezogen von:** `params.yaml` (`vertrag`), `docs/annahmen.md` (Nr. 8, 9), `src/04_strategien.py` (`VERTRAEGE`), `src/05_bewertung.py`, `src/06_sensitivitaet.py` (V8), `src/07_bericht.py`, `analyse.ipynb`; revidiert die Kipp-Annahme A3 (E-035) und die Zweifall-Rechnung aus M-004.
- **Ergebnis:** Keine Zahl des Hauptfalls ändert sich (bitgleich); es entfallen nur die Zeilen des 30-%-Falls (z. B. 18 770 €/Jahr, Kipppunkt 0,4 h).

### E-054 · Acht weitere Grafiken nach Vorschlägen aus einer Claude-Sitzung (über Max)
- **Person:** Max (R2), Vorschläge aus einer separaten Claude-Sitzung, die nur `analyse.html` gelesen hatte
- **Entscheidung:** Neu in `src/07_bericht.py` und auf der Analyseseite: g8 Heatmap Stunde × Monat (Abweichung vom Monatsmittel), g9 Heatmap Startwahl je Strategie, g10 Verteilung der Wochenersparnis (Box plus Einzelwochen), g11 Differenz B − D als Histogramm und QQ-Plot (H0b, Normalität), g12 Wasserfall vom Oracle zur Netto-Ersparnis, g13 Kalender-Heatmap der Wochenersparnis, g14 Pareto der C&E-Matrix, g15 jede Nacht Preis 22 Uhr gegen 3 Uhr. Daten der Heatmap g8 zusätzlich als Tabelle 14 in `ergebnisse/daten_fuer_grafiken.md`.
- **Abweichend vom Vorschlag:** Tornado (g4) und rollierende Linie (g3) gab es schon. Das Pareto zeigt die kumulierten Prozent als Beschriftung statt auf einer zweiten y-Achse (zwei Skalen in einer Grafik verworfen). Erster Titel von g8 („2–5 Uhr ganzjährig günstig“) war falsch, weil die Nacht im Sommer über dem Monatsmittel liegt; korrigiert und nachgeprüft (3 Uhr ist in jedem Monat 19–46 €/MWh billiger als 22 Uhr).
- **Beleg:** `ergebnisse/grafiken/g8`–`g15`, `ergebnisse/analyse.html`; jede Grafik gerendert und angesehen.

### E-053 · Finale Analyseseite im Design des Notebook-Prototyps
- **Person:** Max (R2), nach Vorlage seines Notebook-Prototyps (`prototype.html`, nicht im Repo)
- **Entscheidung:** `analyse.ipynb` ist die eine Analyseseite (Ziel aus E-039): linear von den Parametern über Daten, Preistal, Backtest, Ergebnisse FS1–FS3, Tests, Fehleranalyse, Personalkosten und Wirtschaftlichkeit, C&E, Sensitivität, Spot gegen Festpreis bis zur Empfehlung, Owner je Abschnitt. Sie rechnet nichts neu, sondern liest die Ergebnisdateien; die Interpretationstexte setzen ihre Zahlen beim Ausführen selbst ein (Zellen mit Tag `remove_input`, auf der Seite nur als Text). `src/08_board.py` führt das Notebook als letzten Schritt von `run_all.py` aus und exportiert `ergebnisse/analyse.html` im JupyterLab-Stil. Neue Pakete in `requirements.txt` (nbformat, nbclient, nbconvert, mistune 3.0.2 wegen Unverträglichkeit mit nbconvert 7.16, ipykernel). Neue Grafik g7 (kumulierte Ersparnis im Test).
- **Verworfen:** Zahlen fest in den Text schreiben (veralten beim nächsten Lauf); Berechnungen im Notebook wiederholen (zweite Rechnung neben der getesteten Pipeline); das R2-Board erweitern (anderes Design als der Prototyp).
- **Beleg:** `analyse.ipynb`, `src/08_board.py`, `ergebnisse/analyse.html`; im Browser gerendert und Abschnitt für Abschnitt angesehen, keine Fehlerausgabe.

### E-052 · Grafiken entstehen in Claude aus einer Datendatei; Repo liefert nur die Daten
- **Person:** Max (R2), 11.11.2026
- **Entscheidung:** Die Grafiken für Bericht und Folien baut das Team später in Claude. Das Repo liefert dafür **alle Daten in einer Datei**: `ergebnisse/daten_fuer_grafiken.md` (Kernaussagen und 13 Tabellen: Preistal, Ersparnis je Strategie, Netto und H0a, alle Tests, Kennzahl je Monat, Sensitivität, Break-even, Kipppunkte, Spot gegen Festpreis, C&E, Fehleranalyse, R2-Kennzahlen). Sie wird von `src/07_bericht.py` bei jedem `run_all.py` neu erzeugt, also nie von Hand gepflegt. Die sechs PNG aus K-018 bleiben nur als Entwurf.
- **Verworfen:** Grafiken fertig im Repo per Skript (Folien entstehen ohnehin in Claude, E-039); Zahlen von Hand in ein Dokument kopieren (veraltet beim nächsten Lauf).
- **Beleg:** `ergebnisse/daten_fuer_grafiken.md`, `src/07_bericht.py`

### E-051 · Energie der Reinigung: 8 MWh pro Nacht (löst den offenen Punkt aus E-049)
- **Person:** Max (R2), 11.11.2026
- **Entscheidung:** Die Reinigung braucht 8 MWh pro Nacht (4 MW × 2 h), wie im Interview genannt (K-008 P6). Das „8 MW für 2 h“ im Teamdokument ist als 8 MWh zu lesen; das Teamdokument wird entsprechend korrigiert. Alle bisherigen Ergebnisse gelten unverändert, weil sie schon mit 8 MWh gerechnet sind.
- **Verworfen:** 16 MWh (8 MW × 2 h): widerspricht dem Interview. Bleibt als Sensitivität V6c im Bericht (Euro-Beträge doppelt, Entscheidung gleich, M-005).
- **Beleg:** `params.yaml` (`last.mwh_pro_tag`), `docs/annahmen.md` Nr. 6

### K-018 · KI-Einsatz Phase 6 (R1), Zwischenstand: Grafiken und Spot gegen Festpreis
- **Werkzeug:** Claude Code, Sitzung von Max (E-045)
- **Zweck:** `src/07_bericht.py` (letzter Schritt in `run_all.py`): sechs Grafiken nach einem Standard in `ergebnisse/grafiken/` (Titel = Kernaussage, eine y-Achse, Quelle unten, Farben nach Rolle, farbenblind geprüft mit dem Palettenprüfer, direkte Beschriftung) und `ergebnisse/spot_festpreis.csv` (mittlerer Day-Ahead-Preis im Lastprofil des Werks je Jahr gegen 85 €/MWh: 2022 247, 2023 100, 2024 82, 2025 91, 2026 bis Okt. 111 €/MWh).
- **Wie geprüft:** jede Grafik gerendert und angesehen; abgeschnittene Titel und überlappende Beschriftungen (g2, g3, g4, g5, g6) behoben; zwei Titel an die Daten angepasst (g6 behauptete zuerst „nahe am Festpreis“, 2026 liegt aber bei 111 €/MWh); `pytest tests/` grün.
- **Offen:** Problem Statement, Process Map, Berichtsgliederung nach DMAIC, Text Spot gegen Festpreis, Tests für `07_bericht.py`, Erklärzettel Phase 6; Bestätigung durch Chiara (R1). Lastprofil für Spot gegen Festpreis ist eine Annahme (180 MWh/Tag, Reinigung 22–24 Uhr, Rest gleichmäßig 06–22 Uhr).

### M-005 · Sensitivitätsrechnung gerechnet (Phase 5, K2 Stufe 5)
- **Stand:** `src/06_sensitivitaet.py`, zwölf Varianten (V2, V3, V4, V6a–c, V7a–c, V8, V9, V10) gegen die Basis, Schwelle 5 % vorab festgelegt (E-044). Keine Testentscheidung kippt (H0a verworfen, H0b nicht verworfen in allen Varianten); Anteil am Oracle 92–95 %. Euro-Beträge stark abhängig von Menge (−50 % bis +100 %), Vertrag (−70 %), Produktionstagen (−36 %) und Blocklänge (+34 % bis −40 %). Ohne Nächte mit auffälligen Preisen −11 %, Anteil gleich.
- **Neu:** V6c = 16 MWh aus dem Teamdokument (E-049).
- **Abweichung vom Plan:** Varianten, die die Regeln nicht berühren, werden auf den gewählten Blöcken nachgerechnet statt `cleaning`/`02_synthetisch` neu laufen zu lassen; nur V7 rechnet R3s eingefrorene Regeln neu (als Funktion `backtest_periode`, damit ist die Absprache aus Planpunkt 5 erledigt).
- **Beleg:** `r2/ergebnisse/sensitivitaet.csv`, Tabelle in `r2/docs/sensitivitaet_plan.md`, `tests/test_sensitivitaet.py`, Erklärzettel Phase 5

### K-017 · KI-Einsatz Phase 5 (Sensitivität R2)
- **Werkzeug:** Claude Code, Sitzung von Max (E-045)
- **Zweck:** `src/06_sensitivitaet.py`, `tests/test_sensitivitaet.py`, Schritt in `src/run_all.py`, Ergebnis im Sensitivitätsplan, Erklärzettel Phase 5.
- **Wie geprüft:** `pytest tests/`: 80 grün; Basis gleich R4 (1 199,05 €/Woche); V3 und V10 zunächst verdächtig (fast 0): von Hand nachvollzogen, Feiertags- und Wochenendzuschläge treffen A und D symmetrisch; jede Variante ändert nachweislich ihren Schalter (Test); V6 linear (Test).
- **Offen:** Max geht Erklärzettel Phase 5 durch (eigenes Paket, Verteidigung).

### M-004 · Bewertung R4 gerechnet (Phase 4): H0a verworfen, Kipppunkt ist das Personal
- **Stand:** `src/05_bewertung.py`; `python src/run_all.py` läuft erstmals komplett durch. Test gesamt, D gegen A nach Personalkosten: netto 1 199 €/Woche (KI 1 061–1 337), 62 400 €/Jahr bei Faktor 1,0; 361 €/Woche, 18 800 €/Jahr bei Faktor 0,3. **H0a verworfen** (p < 0,001, Wilcoxon gleich). In keiner der 244 Wochen 2022–2026 war D teurer als 22–24 Uhr.
- **Kipppunkte:** Zuschläge fast ohne Wirkung (Personal-Mehrkosten −2 €/Woche, weil 22–06 Uhr ganz Nacht ist). Die Verschiebung kippt, wenn jede Person je Nacht mehr als 1,3 h (Faktor 1,0) bzw. 0,4 h (Faktor 0,3) zusätzlich bezahlt werden muss, z. B. Warten von 22 bis 3 Uhr. Break-even bei 25 000 € Umstellungskosten: 4,8 bzw. 16 Monate.
- **Empfehlung (Entwurf für R1):** fest 3 Uhr, ohne Prognose, nur mit eigener Reinigungsschicht ohne bezahlte Wartezeit; Kennzahl rollierende 13-Wochen-Netto-Ersparnis; Rücknahme auf 22 Uhr, wenn sie unter null fällt; jährlich die feste Uhrzeit neu bestimmen.
- **Beleg:** `ergebnisse/netto_tests.csv`, `wirtschaftlichkeit.csv`, `kipppunkte.csv`, `kpi_rollierend.csv`, `ce_matrix.csv`, `docs/ishikawa.md`, `docs/erklaerzettel.md` Phase 4
- **Rückstand:** Caro bestätigt Erklärzettel, C&E-Gewichte (E-044) und die Basisannahmen der Zuschläge beim Partner (A-017); Frage an den Partner: Würde die Reinigungsmannschaft bei 3 Uhr warten oder als eigene Schicht kommen?

### E-050 · C&E-Gewichte (Vorschlag) und Process Map bei R1
- **Person:** Claude als Vorschlag für Caro (R4); Max (R2) für die Zuordnung
- **Entscheidung:** C&E-Matrix mit fünf Kriterien, alle so formuliert, dass hoch = gut: Steuerbarkeit im Wochenplan 5, kein Produktrisiko 5, personalgebunden 4, verschiebbare Leistung 3, Datenlage 2; Skala 0/1/3/9; Begründung je Gewicht und Zeile im Code (`CE_KRITERIEN`, `CE_BEWERTUNG`). Ergebnis Reinigung 153 (62 %), Produktion 51, Kälte 43. Die Process Map macht R1 (Teamdokument), nicht R4 wie im Prompt.
- **Verworfen:** Leistung (MW) am höchsten gewichten (dann läge die Produktion vorn, obwohl sie wegen Rohmilch nicht verschiebbar ist); Kriterien mit „hoch = schlecht“ (Risiko, Personalbedarf) mischen (die gewichtete Summe wäre nicht mehr lesbar).
- **Offen:** Caro bestätigt oder ändert die Gewichte.

### K-016 · KI-Einsatz Phase 4 (R4) und Abgleich mit dem Teamdokument
- **Werkzeug:** Claude Code, Sitzung von Max (E-045)
- **Zweck:** `src/05_bewertung.py`, `tests/test_bewertung.py`, `docs/ishikawa.md`, Erklärzettel Phase 4, Schnittstellen; vorher `docs/annahmen.md`, B_16 und FS1–FS3 (E-049).
- **Wie geprüft:** `pytest tests/`: 75 grün; eine Freitagnacht von Hand (A 262,50 €, D 315,00 €); Netto = Strom × Faktor − Personal an einem Zahlenbeispiel; unvollständige Wochen zählen nicht; `python src/run_all.py` komplett; bisherige Strategien nach B_16 bitgleich.
- **Offen:** Caro bestätigt den Erklärzettel Phase 4.

### E-049 · Abgleich mit dem Teamdokument: Annahmenliste, Wochenende, B_16, Fragestellungen FS1–FS3
- **Person:** Max (R2), nach Abgleich mit dem Teamdokument „Analyse und Entscheidungsprojekt“ (Gruppe F)
- **Entscheidung:** (1) `docs/annahmen.md` ist die eine Annahmenliste (Leitfrage, FS1–FS3, Rahmenbedingungen mit Quelle und `params.yaml`-Schlüssel, Nichtziele, Rollen). (2) Wochenendzuschlag 50 % gilt für Samstag **und** Sonntag (`kosten.wochenendzuschlag`, vorher nur Sonntag). (3) Die Team-Regel aus FS2 kommt als Strategie **B_16** dazu: je Wochentag das Mittel der letzten 16 gleichen Nächte. (4) FS1 (D gegen A), FS2 (B_16 gegen A) und FS3 (B_16 gegen A im letzten Jahr = Test 2) stehen in `ergebnisse/hypothesentests.csv`. (5) Process Map laut Teamdokument bei R1 (Phase 6), nicht bei R4.
- **Offenlegung:** B_16 und FS1–FS3 kamen **nach** dem Einfrieren (`1d59427`) und nach Sicht der Testergebnisse dazu. Sie sind deshalb als „nicht konfirmatorisch“ markiert; die vorab festgelegten H0a–H0c bleiben unverändert. Die Regel B_16 stammt aus dem Teamdokument, wurde also nicht nach den Ergebnissen gewählt. Die bisherigen Strategien sind bitgleich (geprüft gegen den Stand von Phase 3).
- **Ergebnis (Test gesamt, 89 Wochen, nur Strom):** FS1: D spart 1 197 €/Woche (KI 1 059–1 336). FS2: B_16 spart 1 207 €/Woche (KI 1 071–1 344, 93,8 % des Oracle). FS3 (letztes Jahr): B_16 spart 1 281 €/Woche (KI 1 062–1 499). Alle p < 0,001. B_16 gegen D: +10 €/Woche (KI 0,6–19, p = 0,019 > α/3; im Training −14): praktisch gleich gut.
- **Nebenbei behoben:** Anteil am Oracle wurde bei Strategien mit fehlenden Wochen (B in 2022) gegen das Oracle aller Wochen gerechnet; jetzt auf denselben Wochen (B im Stresstest 90,8 % statt 94,8 %).
- **Offen:** ~~Energie der Reinigung~~ erledigt am 11.11.2026: 8 MWh (E-051).
- **Verworfen:** B (4 Wochen, Median) durch B_16 ersetzen (würde die eingefrorene Regel nachträglich ändern); FS1–FS3 als konfirmatorisch zählen (nachträglich, und es wären sechs statt drei Tests für Bonferroni).

### M-003 · Backtest und Tests von R3 gerechnet (Phase 3)
- **Stand:** Alle vier Zeiträume gerechnet mit den eingefrorenen Regeln (`1d59427`). Test 2025–2026 (89 Wochen, nur Strom, Faktor 1,0): D 1 197 €/Woche (95-%-KI 1 059–1 336, 93,0 % des Oracle), B 1 179 (91,6 %), C 1 288. Faktor 0,3: D rund 18 700 €/Jahr.
- **H0b nicht verworfen** (B − D = −18 €/Woche, p_t = 0,99, Wilcoxon gleich): Eine wöchentliche Prognose bringt nichts gegenüber der festen Regel 3 Uhr. **H0c:** C − B = 109 €/Woche, Kipppunkt m\* = 91 €/Woche. **H0a** offen bis Phase 4 (Personalkosten R4).
- **Gegenproben:** Test 1, Test 2 und Stresstest 2022 einzeln mit gleicher Richtung; Bootstrap-Intervalle rund 50 % breiter als die t-Intervalle, gleiche Entscheidung; Shapiro-Wilk lehnt Normalverteilung ab, Wilcoxon gleich.
- **Beleg:** `ergebnisse/ki_strategien.csv`, `ergebnisse/hypothesentests.csv`, `ergebnisse/fehleranalyse_b.csv`, `docs/erklaerzettel.md` Phase 3
- **Rückstand:** Bestätigung durch Susan (Phasen 1–3).

### P-012 · Code-Fehler nach dem Einfrieren: leere Historie im Stresstest
- **Problem:** Im ersten Lauf des Stresstests 2022 stürzte B ab: Die Historie der ersten Woche ist leer (Daten beginnen am 01.01.2022), `blockkosten` gab dann eine Tabelle ohne Spalten zurück. Laut E-044 soll B in diesen Wochen nicht planen.
- **Angesprochen von:** Claude, 11.11.2026
- **Lösung:** `src/03_merkmale.py` gibt auch ohne vollständige Nacht feste Spalten zurück; Test in `tests/test_merkmale.py`. Keine Regel geändert (die Regeln in `src/04_strategien.py` sind seit `1d59427` unverändert, Trainingszahlen bitgleich).
- **Nebenbefund:** Für B entfallen 2022 fünf statt vier Wochen (E-044 nannte vier): Die vierte bekannte Freitagnacht gibt es erst am Planungsfreitag der sechsten Woche.

### K-015 · KI-Einsatz Phase 3 (Statistik R3)
- **Werkzeug:** Claude Code, Sitzung von Max (E-045)
- **Zweck:** Statistik in `src/04_strategien.py` (t-Test, Wilcoxon, Shapiro-Wilk, Block-Bootstrap, Fehleranalyse), drei Ergebnisdateien, Erklärzettel Phase 3, Schnittstellen.
- **Wie geprüft:** `pytest tests/`: 70 grün, darunter t-Wert, p-Wert und untere Schranke gegen Handformel, Bootstrap reproduzierbar mit Seed, Vertragsfaktor; Trainingszahlen bitgleich mit dem eingefrorenen Stand; `git diff 1d59427` zeigt keine Änderung an den Regelfunktionen; `python src/run_all.py` läuft bis Schritt 05.
- **Offen:** Susan bestätigt den Erklärzettel Phase 3.

### M-002 · Strategien eingefroren (Commit `1d59427`)
- **Stand:** Regeln A, D (3 Uhr), D_saison (3 Uhr in jeder Saison), B (Median der letzten 4 gleichen Wochentage), B_ohne_wochentag (letzte 28 Nächte), C (Oracle) in `src/04_strategien.py`, entwickelt nur auf dem Training 2023–2024. Hash: `1d594271f1c9f2a2dfccecc3faf1b114baa3e8d4`.
- **Regel ab jetzt:** Keine Änderung an den Regeln mehr. Test 1, Test 2 und Stresstest 2022 laufen erst in Phase 3. Ein Code-Fehler wird behoben und hier offen dokumentiert, die Regel selbst bleibt (`docs/hypothesen.md`).
- **Rückstand:** Susan hat die Regeln noch nicht bestätigt (E-045, E-046); eingefroren auf Anweisung von Max („weiter“).

### E-048 · Kalendermerkmale verbessern die Strategien im Training nicht (Befund, K3)
- **Person:** Claude als Befund für Susan (R3)
- **Befund (Training, 104 Wochen, nur Strom, Faktor 1,0):** Ersparnis gegenüber A: D 1 162 €/Woche (93,4 % des Oracle), D_saison 1 162 (93,4 %), B 1 132 (91,0 %), B_ohne_wochentag 1 139 (91,6 %), C 1 244. Saison bringt 0 €, gleicher Wochentag −7 €/Woche. B ist im Training schlechter als die feste Regel D, wobei D im Training gelernt und deshalb geschönt ist.
- **Folge:** K3 Stufe 5 („Merkmal verbessert das Ergebnis messbar“) ist mit diesen beiden Merkmalen nicht belegt. Beide Ergebnisse werden als negative Ergebnisse berichtet. Eine weitere Merkmalssuche nach Sicht der Ergebnisse ist verworfen (p-Hacking). Ob ein anderer K3-Beleg kommt (z. B. „Nacht als Einheit über Mitternacht“ statt Kalendertag, R2), entscheidet das Team.
- **Beleg:** `ergebnisse/backtest_wochen.csv` (Periode training), `docs/erklaerzettel.md` Phase 2

### K-014 · KI-Einsatz Phase 2 (Strategien R3)
- **Werkzeug:** Claude Code, Sitzung von Max (E-045)
- **Zweck:** `src/04_strategien.py`, `tests/test_strategien.py`, Erklärzettel Phase 2, Schnittstellen `backtest_naechte.csv` und `backtest_wochen.csv`.
- **Wie geprüft:** `pytest tests/`: 67 grün. Beim ersten Lauf schlug die Prüfung „Oracle nie teurer“ an: Der Montag war als „Freitag + 72 h“ berechnet und verschob in Wochen mit Zeitumstellung die Woche um eine Nacht; behoben mit Kalendertagen und Test. Woche ab 04.03.2024 von Hand aus den Stundenpreisen nachgerechnet (A 3 682,24 €, D 3 199,52 €, C 3 163,32 €, gleich). Look-ahead-Test: verfälschte Zukunftspreise ändern den Plan von B nicht.
- **Offen:** Susan bestätigt den Erklärzettel Phase 2.

### E-047 · Haupttest t-Test, keine Regression (ändert `docs/hypothesen.md` vom selben Tag)
- **Person:** Max (R2) für das Team, 11.11.2026
- **Entscheidung:** Über H0a–H0c entscheidet der gepaarte t-Test, einseitig, p < α/3. Shapiro-Wilk wird vorher berichtet, Wilcoxon läuft als Gegenprobe, ein Block-Bootstrap-Intervall nur als Grenze. Die Regression (Ersparnis je Nacht gegen die Nachtspreizung) und die Regressionsvariante B′ entfallen.
- **Verworfen:** Block-Bootstrap als Haupttest (Fassung `7a63c15`): erklärt sich in der Verteidigung schwerer, und der t-Test steht im Kickoff und im Kursmaterial. Regression: kein Beitrag zu H0a–H0c.
- **Testdaten gesehen?** Nein. Bisher sind nur Trainingsnächte ausgewertet (Phase 1).
- **Grenze:** Wochen derselben Saison hängen zusammen; der t-Test kann die Unsicherheit dann unterschätzen. Das Bootstrap-Intervall zeigt, wie stark.

### K-013 · KI-Einsatz Phase 0 und Phase 1 (R2-Ergänzung, Hypothesen, Merkmale R3)
- **Werkzeug:** Claude Code, Sitzung von Max nach dem Prompt aus E-045
- **Zweck:** Phase-0-Antworten umgesetzt (Commits `a73df08`, `49ac435`); `docs/hypothesen.md` (`7a63c15`); `src/03_merkmale.py`, `tests/test_merkmale.py`, `docs/erklaerzettel.md` (Phase 1).
- **Wie geprüft:** `pytest tests/`: 60 grün; Blockkosten-Matrix gegen R2-Funktion `fenster_je_tag` über alle 1 764 Nächte (gleicher Status-quo-Preis und billigster Block, Abweichung < 10⁻⁹); Zeitumstellungsnächte mit 6 bzw. 8 Blöcken einzeln geprüft; `preise_clean.csv` nach der R2-Ergänzung in allen alten Spalten bitgleich; `python src/run_all.py` läuft bis Schritt 03.
- **Offen:** Susan liest den Erklärzettel Phase 1, prüft eine Nacht von Hand nach und bestätigt hier (Datum, was geprüft).

### E-046 · Saisonaler Block bringt im Training nichts; K3-Nachweis über B (Vorschlag)
- **Person:** Claude als Befund für Susan (R3); Entscheidung offen
- **Befund (Training 2023–2024, kein Testergebnis):** Der beste feste Start ist 3 Uhr in jeder Saison und an jedem Wochentag (`ergebnisse/saisonaler_block.csv`). D_saison ist damit identisch mit D, das Merkmal Saison verbessert die feste Regel um 0 €.
- **Vorschlag:** D_saison bleibt im Backtest und wird als negatives Ergebnis berichtet. Der K3-Nachweis in € kommt stattdessen aus dem Kalendermerkmal „gleicher Wochentag“ in B: B (Median der letzten 4 gleichen Wochentage) gegen B ohne Wochentag (Median der letzten 28 Nächte), verglichen auf dem Training, bevor eingefroren wird.
- **Verworfen (vorgeschlagen):** Den saisonalen Block weglassen (dann fehlt das negative Ergebnis, das H0b stützt); ein neues Merkmal nur suchen, bis eines wirkt (Gefahr des p-Hacking, deshalb nur dieser eine vorab benannte Vergleich).
- **Offen:** Susan entscheidet vor Phase 2.

### E-045 · Arbeitsweise: KI baut R1, R3, R4 in Phasen, Max committet, Owner prüfen und erklären
- **Person:** Max (R2), nach Einwand von Susan (R3) gegen die Aufteilung „jeder baut sein Paket selbst“
- **Entscheidung:** Die fehlenden Pakete entstehen mit Claude Code nach einem festen Prompt in Phasen (0: Bestand, 1–3: R3, 4: R4, 5: R2, 6: R1). Nach jeder Phase hält Claude an, schreibt einen Erklärzettel für den Owner (was, warum, verworfen, drei Prüferfragen) und wartet auf „weiter“. Git-Autor ist Max (er committet alles); jeder Commit trägt den Trailer `Owner: R<x>` und `AI-Assisted: Claude`, Dateiköpfe nennen den Owner.
- **Verworfen:** (a) Jeder baut und committet sein Paket selbst unter eigenem Account (Kickoff, Risiko 1): von Susan abgelehnt. (b) Die Person der Rolle als Git-Autor eintragen, obwohl sie nicht an der Sitzung beteiligt war: wäre eine falsche Angabe zum Eigenanteil.
- **Risiko und Maßnahme:** Im Git-Verlauf steht nur Max. Der Eigenanteil der anderen muss deshalb anders belegt werden: Jeder Owner bestätigt sein Paket im Tagebuch (Nachtrag am Phaseneintrag) oder per Kommentar am Pull Request und erklärt es im Probelauf mit Kreuzfragen. Ohne diese Bestätigung gilt das Paket als nicht verantwortet (Sperrkriterium Erklärbarkeit).
- **Ändert:** Kickoff „Eigenanteil sichtbar machen“ und Risiko 1 (Verweis dort ergänzt).
- **Offen:** Zustimmung von Chiara (R1) und Caro (R4) zu dieser Arbeitsweise.

### E-044 · Offene Fragen aus A-007, A-010, E-035 und dem Sensitivitätsplan entschieden
- **Person:** Max (R2), Phase 0 am 11.11.2026
- **Entscheidung:** (1) Die Sonntagsnacht wird mitgewertet; ihre Stunden bis Montag 06:00 kommen aus der Blockkosten-Matrix (echte Preise, nur zur Bewertung). (2) Stresstest 2022 nur mit Regeln, die im Training gelernt wurden; für B entfallen die ersten 4 Wochen 2022 mangels Historie, im Bericht als Grenze genannt. (3) Umstellungskosten als Break-even-Kurve statt Punktwert (keine belastbare Quelle). (4) Schwelle der Sensitivität 5 % (`statistik.sensitivitaet_schwelle_pct`). (5) Gewichte der C&E-Matrix schlägt Claude begründet vor, Caro (R4) bestätigt in Phase 4.
- **Verworfen:** (1) Sonntagsnacht weglassen: jede Woche fehlte eine Nacht, ausgerechnet die mit Sonntagszuschlag. (2) Preise ab 12/2021 nachladen: ändert den Datenstand und alle Prüfsummen für vier Wochen Stresstest. (3) Punktschätzung der Umstellungskosten ohne Quelle.
- **Beleg:** `params.yaml`, `docs/schnittstellen.md`, `r2/docs/sensitivitaet_plan.md`

### A-017 · Kosten: R3 rechnet Strom, R4 Personal; Basisannahmen der Zuschläge
- **Von → an:** Max (R2) → R3 (Susan), R4 (Caro)
- **Was:** R3 liefert in `ergebnisse/backtest_wochen.csv` nur Stromkosten. R4 rechnet Personalkosten mit Zuschlägen. Basisannahmen: 22–06 Uhr gilt komplett als Nacht (`kosten.nachtstunden` jetzt 22–05); für die Stunden 0–6 Uhr zählt der Kalendertag der Stunde (Sa 22 Uhr = Samstag, So 02 Uhr = Sonntag); trifft Nacht auf Sonntag oder Feiertag, gilt nur der höchste Zuschlag (`kosten.zuschlag_regel: hoechster`). Sensitivität: V9 Nacht erst ab 23 Uhr, V10 Zuschläge addiert.
- **Kanal und Datum:** Chat Max mit Claude Code, 11.11.2026
- **Offen:** Caro bestätigt die drei Basisannahmen beim Praxispartner, wenn möglich; Antwort hier nachtragen.
- **Änderung, nachgezogen von:** `params.yaml`, `docs/schnittstellen.md`, `r2/docs/sensitivitaet_plan.md` (V9 umgedreht, V10 neu); E-035 „Offen“ damit erledigt.

### A-016 · Schnittstelle R2 → R4: Spalten `sonntag` und `feiertag`
- **Von → an:** R2 (Max) → R4 (Caro)
- **Was (Datei, Spalten, Einheit):** `data/preise_clean.csv` hat zwei neue Spalten: `sonntag` und `feiertag` (gesetzlicher Feiertag Bayern), beide True/False und bezogen auf den Kalendertag der Stunde. Vorher gab es nur `werktag`, in dem Samstag, Sonntag und Feiertag zusammenfallen; R4 braucht sie getrennt, weil die Zuschläge verschieden sind (50 % / 100 %).
- **Kanal und Datum:** Repo, 11.11.2026
- **Beleg:** Commit `a73df08`; `src/gemeinsam.py` (`feiertage_bayern`), `src/cleaning.py`, Test `test_sonntag_und_feiertag_gelten_fuer_den_kalendertag_der_stunde`; alle bisherigen Spalten bitgleich, 52 Tests grün; `docs/codebook.md`.

### E-043 · Gegenstand nur die Reinigung; Kälte gestrichen, Viertelstunde Nichtziel
- **Person:** Max (R2)
- **Entscheidung:** Untersucht wird nur die Reinigung (CIP). Kälte (Kontrastfall T), Produktion, Viertelstunden, Netzentgelte und Intraday sind Nichtziele und werden im Bericht im Kapitel „Abgrenzung“ begründet. Gelöscht: Block `kaelte` und `strategien.tagessteuerung` in `params.yaml`, T in `docs/schnittstellen.md` und `r2/docs/architektur.md`; der Kickoff bekommt nur einen Verweis. Test 2 (10/2025–09/2026) bleibt als zweiter Testzeitraum mit Stundenwerten, ohne eigene Hypothese. Der Tagesplanungsfall steckt im Oracle C: Die Preise einer Nacht sind am Vortag um 12:45 vollständig bekannt.
- **Verworfen:** T als „nicht verwendet“ markiert stehen lassen (toter Ballast, verwirrt); Test 2 streichen (verschenkt den Strukturbruch als Gegenprobe, K6).
- **Revidiert:** E-033 (Kälte als Kontrastfall T).

### E-042 · Neue Nullhypothesen H0a–H0c (revidiert E-034 und Kickoff)
- **Person:** Max (R2)
- **Entscheidung:** H0a: Ersparnis D gegen A nach Kosten ≤ 0. H0b: Ersparnis B ≤ Ersparnis D. H0c: (Ersparnis C − Ersparnis B) − Mehrkosten Tagesplanung ≤ 0, berichtet als Kipppunkt des Aufpreises für kurzfristig gebuchtes Personal. Bonferroni α = 0,05/3. Testrichtung, Test und Entscheidungsregel stehen in `docs/hypothesen.md`, separat committet vor jeder Auswertung.
- **Verworfen:** alte H0c (Stunden- gegen Viertelstundenregime): Viertelstunde ist Nichtziel (E-043); alte H0b (Prognose gegen „eine feste Zeitregel“) ohne Festlegung, welche.
- **Begründung:** Fokus nur auf die Reinigung. Es ist noch nichts ausgewertet (kein Backtest), die Hypothesen werden also nicht an ein Ergebnis angepasst.

### A-015 · Rollen R1 und R4 besetzt
- **Von → an:** Max (R2) → Team
- **Was:** R1 Projektleitung & Controlling: Chiara. R4 Produktion & Schichtplanung: Caro. Damit sind alle vier Rollen besetzt (R2 Max, R3 Susan, A-014). Review-Paare nach Kickoff: R2 ↔ R3, R1 ↔ R4.
- **Kanal und Datum:** Chat Max mit Claude Code, 11.11.2026
- **Beleg:** Rollentabelle in `docs/kickoff.md`

### K-012 · Praxisrückkopplung: Reinigung läuft heute 22–24 Uhr
- **Gesprächspartner:** Ansprechpartner beim Praxispartner, Interview am 10.11.2026 (weitergegeben von Max am 11.11.2026)
- **Aussage:** Die Reinigung (CIP) läuft heute direkt nach Produktionsende von 22 bis 24 Uhr.
- **Was wir geändert haben:** Der Status quo A ist keine Annahme mehr, sondern eine Tatsache. Geändert an sieben Stellen: E-031 (Nachtrag), K-008 (offene Frage erledigt), `params.yaml`, `docs/schnittstellen.md`, `README.md`, `src/fensteranalyse.py`, `src/build_board.py`. Die stärkste Kipp-Annahme des Falls (E-031) entfällt.
- **Offen:** Die Aussage stand nicht in K-008; Max prüft, ob sie in den Notizen vom 10.11. steht, und ergänzt sie dort.

### A-014 · Rolle R3: Susan
- **Von → an:** Max (R2) → Team; weitergegeben im Chat mit Claude Code, 11.11.2026
- **Was:** Susan übernimmt R3 Energieeinkauf (Merkmale inkl. saisonalem Block, Strategien A bis D im Backtest, Regression, gepaarter Test, Bootstrap; K3, K4). Damit ist sie Paarpartnerin von R2 für die Reviews nach P-003; der offene Punkt aus A-012 ist erledigt.
- **Beleg:** Rollentabelle in `docs/kickoff.md`
- **Offen:** Susan bestätigt die Rolle selbst (Commit oder Kommentar im Repo).

### E-041 · Abgrenzung R2/R3: beschreibende Kennzahlen bei R2, schließende Statistik und Merkmale bei R3
- **Person:** Max (R2), nach Rückfrage, ob Median, Quartile usw. Susans Teil sind
- **Entscheidung:** Kennzahlen, die die Daten beschreiben (Mittel, Median, Quartile, Min/Max, Anteil negativer Preise je Monat, Saison und Uhrzeit; Rückblick-Kennzahl der Reinigungsnacht), gehören zur Datenexploration und zum Qualitätsbericht und bleiben bei R2 (Kickoff Schritt 2, K2). Alles, was eine Regel begründet oder prüft (Merkmale, saisonaler Block, Strategien, Tests, Konfidenzintervalle, Euro-Nachweis für K3/K4), macht R3. Grenzfall `r2/ergebnisse/tagesprofil_saison.csv`: bleibt rein beschreibend; R3 darf es als Startpunkt nutzen, leitet den saisonalen Block aber selbst her und bewertet ihn in Euro.
- **Verworfen:** die beschreibenden Kennzahlen an R3 abgeben (Qualitätsbericht und Datenexploration sind laut Kickoff R2-Aufgabe; R3 hätte doppelte Arbeit ohne eigenen K3/K4-Beitrag).
- **Beleg:** `src/cleaning.py` (Kennzahlen), `src/fensteranalyse.py` (Rückblick, keine Strategie, E-037), `docs/kickoff.md` (Rollentabelle, Schritt 2 und 3)

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
- **Nachtrag 11.11.2026:** Susan ist R3 (A-014), Rollentabelle ergänzt.

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
- **Nachtrag 11.11.2026:** Basisannahme jetzt 22–06 Uhr komplett Nacht (A-017); V9 prüft 23–06 Uhr.
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
- **Nachtrag 11.11.2026:** Vom Praxispartner im Interview am 10.11.2026 bestätigt (K-012); keine Annahme mehr.
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
- **Offen:** ~~Wann läuft die Reinigung heute (Status quo A)?~~ erledigt: 22–24 Uhr (K-012). Ist die Kälte personalgebunden oder automatisch (dann eher Tagessteuerung T)? Wie ist der Festpreisanteil vertraglich gestaltet (Band oder Profil, A3)? Bestätigung 50 gegen 180 MWh (P-009).
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
