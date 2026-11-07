# Tagebuch-Entwürfe R2

Entwürfe von Claude für [Name R2]. **Nicht das Projekttagebuch.** R2 prüft jeden Eintrag, passt ihn an und trägt ihn selbst in `docs/projekttagebuch.md` ein; danach kann diese Datei gelöscht werden. Platzhalter in eckigen Klammern erst ausfüllen, wenn die Aussage stimmt.

## 07.11.2026

### E-008 · Rohdaten: SMARD-JSON wochenweise, unverändert, im Repo versioniert
- **Person:** [Name R2]
- **Entscheidung:** `src/01_download.py` lädt die SMARD-Wochendateien (Filter 4169, DE-LU, `hour` ab 2022-01-01, `quarterhour` ab 2025-10-01, bis Datenstand) als Original-Bytes nach `data/raw/smard/4169/<auflösung>/`. Vorhandene Dateien werden nicht neu geladen; der Schritt läuft dann offline. Die Rohdaten (ca. 2 MB, 310 Dateien) liegen im Repo.
- **Verworfen:** (a) CSV-Export von smard.de per Hand: nicht reproduzierbar, kein Skript. (b) Bei jedem Lauf neu laden: SMARD korrigiert nachträglich, Ergebnisse würden sich ohne unser Zutun ändern; ohne Internet läuft nichts. (c) Rohdaten nicht ins Repo: Dritte müssten neu laden und bekämen eventuell andere Werte. CC BY 4.0 erlaubt die Weitergabe mit Namensnennung.
- **Begründung:** Sperrkriterium Reproduzierbarkeit, K5 Stufe 5 (neue Daten: nur `datenstand` ändern), K2 (Herkunft je Datei belegbar).
- **Beleg:** `src/01_download.py`, `data/raw/smard/manifest.csv`, `data/raw/SOURCES.md`, Commit [hash]

### E-009 · Integrität der Rohdaten über SHA256
- **Person:** [Name R2]
- **Entscheidung:** Je Datei URL, Abrufzeitpunkt, SMARD-Erstellzeitpunkt, Größe und SHA256 in `manifest.csv`. Jeder Lauf und ein Test prüfen, dass sich keine Rohdatei geändert hat. Wurde eine Woche geladen, bevor sie vorbei war, und fehlen deshalb Werte, wird sie neu geladen; die alte Datei bleibt als `*.veraltet-<datum>.json` liegen.
- **Verworfen:** Nur ein Abrufdatum in `SOURCES.md` (eine veränderte Datei fiele nicht auf); unvollständige Dateien überschreiben (verletzt „Rohdaten nie überschreiben“).
- **Begründung:** Prüfbare Herkunft (Sperrkriterium Datenherkunft); Gegenprobe: eine von Hand geänderte Zahl wird sofort gemeldet.
- **Beleg:** `tests/test_datenannahmen.py::test_rohdaten_unveraendert`, Commit [hash]

### E-010 · Zeitumstellung Oktober: doppelte Stunde mitteln
- **Person:** [Name R2]
- **Entscheidung:** Am letzten Sonntag im Oktober gibt es 02:00–03:00 Uhr zweimal (25 Stunden). Beide Preise werden gemittelt und als eine Zeile 02:00 Uhr abgelegt, der Tag hat 24 Zeilen. Fehlt einer der beiden Werte, bleibt das Ergebnis leer.
- **Verworfen:** (a) Beide Stunden behalten (25 Zeilen): ohne Informationsverlust, aber die Blockkosten-Matrix Tag × Startstunde (R3) braucht genau einen Wert je Uhrzeit. (b) Nur die erste oder zweite Stunde nehmen: willkürlich, wirft einen echten Preis weg. (c) Durchgehend in UTC rechnen: Schichten richten sich nach der Uhr im Werk; in UTC verschöbe sich der Block halbjährlich um eine Stunde.
- **Begründung:** Betrifft 1 Nachtstunde pro Jahr (5 im ganzen Zeitraum); Tagesblöcke wie 08–14 Uhr nie. Mittel = Kosten bei gleichmäßigem Verbrauch über beide Stunden, halbiert auf eine Stunde. Wirkung wird in der Sensitivitätsrechnung (K2 S5) beziffert. [offen]
- **Beleg:** `src/02_aufbereitung.py::zu_ortszeit`, `data/processed/zeitumstellung.csv`, Test `test_oktober_doppelte_stunde_wird_gemittelt`

### E-011 · Zeitumstellung März: fehlende Stunde markieren, nicht füllen
- **Person:** [Name R2]
- **Entscheidung:** Am letzten Sonntag im März gibt es 02:00 Uhr nicht. Der Tag hat 23 Zeilen; die Tage stehen in `zeitumstellung.csv` und in `datenqualitaet.csv`.
- **Verworfen:** Interpolieren oder Vorwärtsfüllen: erfindet einen Preis für eine Stunde, in der niemand Strom verbraucht; ein Block über 02:00 Uhr bekäme Kosten für eine nicht existierende Stunde.
- **Begründung:** Keine stillen Annahmen in den Daten; R3 ist über `docs/schnittstellen.md` informiert.
- **Beleg:** Test `test_maerz_fehlende_stunde_wird_nicht_aufgefuellt`, `test_stunden_pro_tag`

### E-012 · Viertelstunden zu Stundenmitteln; 15-min-Daten separat
- **Person:** [Name R2]
- **Entscheidung:** Ab 01.10.2025 ist der Stundenpreis das arithmetische Mittel der vier Viertelstunden, nur wenn alle vier vorhanden sind. Die 15-min-Werte liegen zusätzlich in `preise_15min.parquet`.
- **Verworfen:** (a) Die Stundenwerte von SMARD direkt übernehmen: SMARD rechnet sie selbst und rundet auf zwei Nachkommastellen; wir nutzen sie stattdessen als Prüfung (max. Abweichung 0,005 €/MWh bei 9 505 Stunden). (b) Median oder letzter Wert: entspricht nicht den Kosten. (c) Mittel auch bei fehlenden Viertelstunden: würde eine Lücke still füllen.
- **Begründung:** Bei gleichmäßiger Leistung innerhalb der Stunde gilt exakt: Kosten = Mittelpreis × Energie. Das Mitteln glättet Spitzen (Maximum 2026: 697 €/MWh Stunde gegen 747 €/MWh Viertelstunde); wie viel Ersparnis das kostet, zeigt die Sensitivität 15 statt 60 min (K2, K3).
- **Einschränkung:** Der Abgleich mit dem SMARD-Stundenwert prüft nur auf Rechen- und Übertragungsfehler, er ist keine unabhängige Quelle (siehe E-015).
- **Beleg:** `results/tables/datenqualitaet.csv` (Spalten `abw_smard_stunde_*`), Test `test_stundenmittel_passt_zu_viertelstunden`

### E-013 · Echte Lücken sichtbar lassen; negative Preise behalten
- **Person:** [Name R2]
- **Entscheidung:** Liefert SMARD für eine Stunde keinen Wert, bleibt die Zeile mit leerem Preis stehen und der Test `test_keine_luecken` schlägt an. Negative Preise und Nullpreise bleiben unverändert drin. Stand 07.11.2026: 0 Lücken, 0 doppelte Zeitstempel, 1 877 Stunden mit negativem Preis (2022–10/2026).
- **Verworfen:** Lückenzeilen löschen (Lücke unsichtbar, Wochen hätten weniger Stunden); negative Preise auf 0 setzen oder entfernen (sind echte Auktionsergebnisse, genau dort liegt Flexibilitätswert; K3 S5 „Ausreißer als Information“).
- **Beleg:** `results/tables/datenqualitaet.csv`, Test `test_preisbereich`

### E-014 · Werktage: gesetzliche Feiertage Bayern, Mariä Himmelfahrt als Variante
- **Person:** [Name R2]
- **Entscheidung:** Werktag = Montag bis Freitag und kein gesetzlicher Feiertag in Bayern (Paket `holidays`, `subdiv="BY"`). Mariä Himmelfahrt (15.08.) gilt nur in überwiegend katholischen Gemeinden; Schalter `feiertagsvariante_mariae_himmelfahrt` in `params.yaml` (Standard: false).
- **Verworfen:** Feiertagsliste von Hand (fehleranfällig); 24./31.12. als arbeitsfrei (keine gesetzlichen Feiertage; Betriebsruhe mit dem Kontakt klären [offen]).
- **Beleg:** Test `test_werktage_bayern_und_variante`

### A-002 · Neue Parameter und Dateien von R2
- **Von → an:** R2 → R1 (Owner `config/`), R3
- **Was:** `params.yaml`: neue Einträge `markt.regimewechsel`, `markt.zeitzone`, Block `daten` (URL, Download-Zeiträume, Pfade, Retry). Neue Dateien `preise_15min.parquet`, `zeitumstellung.csv`, `datenqualitaet.csv` in `docs/schnittstellen.md` eingetragen. `preise_h.parquet` unverändert laut Schnittstelle.
- **Bis:** 07.11.2026, Review durch R1 und R3 per Pull Request
- **Änderung, nachgezogen von:** [R3 bestätigt Umgang mit 23-Stunden-Tagen in der Blockkosten-Matrix]

### E-015 · Kein Abgleich mit ENTSO-E; K2 Stufe 5 über die Sensitivitätsrechnung
- **Person:** [Name R2]
- **Entscheidung:** Wir gleichen die SMARD-Preise nicht mit der ENTSO-E Transparency Platform ab. K2 Stufe 5 („Datenqualität aktiv geprüft“) belegen wir mit einer Sensitivitätsrechnung: Wie stark ändert sich die Ersparnis, wenn wir Zeitumstellung, Feiertagskalender, Zeitauflösung und die synthetischen Parameter anders wählen?
- **Verworfen:** Abgleich SMARD gegen ENTSO-E (so im Kickoff noch vorgesehen). SMARD bezieht die Day-Ahead-Preise von ENTSO-E, beide sind also keine unabhängigen Quellen; ein Abgleich fände höchstens Übertragungsfehler. Diese Prüfung haben wir innerhalb von SMARD schon (eigenes Stundenmittel gegen SMARD-Stundenwert, max. 0,005 €/MWh). Der Aufwand (Konto, API-Schlüssel) brächte für K2 nichts dazu.
- **Begründung:** Die Katalogformulierung nennt die Sensitivitätsrechnung ausdrücklich als Weg zu Stufe 5; sie prüft zudem die synthetischen Daten, die sich gegen keine Quelle prüfen lassen.
- **Beleg:** `docs/sensitivitaet_plan.md`, später `results/tables/sensitivitaet.csv`

### E-016 · Synthetischer Lastgang deterministisch
- **Person:** [Name R2]
- **Entscheidung:** `src/02_synthetisch.py` schreibt `last_synth.parquet` (`datum`, `mwh`): an jedem Werktag `last.mwh_pro_werktag` (Platzhalter 2,0 MWh), sonst 0 MWh; ein Eintrag je Kalendertag im Preiszeitraum, rund 500 MWh pro Jahr. Ohne Zufall. Alle Werte sind Platzhalter, vom Praxiskontakt zu plausibilisieren.
- **Verworfen:** (a) Zufällige Schwankung der Tagesmenge mit festem Seed: Sie träfe jede Strategie in derselben Woche gleich (gepaarter Vergleich), änderte also nicht, welche Strategie günstiger ist, brächte aber einen Parameter (Schwankungsbreite), den niemand gegen die Realität prüfen kann. (b) Nur Werktage als Zeilen: Ein fehlender Tag wäre nicht von einer echten Lücke zu unterscheiden; mit 0 MWh ist „keine Produktion“ ausdrücklich.
- **Begründung:** Einfach, reproduzierbar, erklärbar. Die Unsicherheit über die Menge wird über die Sensitivität (V6 Menge, V7 Blocklänge) gezeigt statt über künstliches Rauschen. Der Text in `last.werktage` wird geprüft; ändert ihn jemand, bricht das Skript ab, statt still Mo–Fr weiterzurechnen.
- **Beleg:** `src/02_synthetisch.py`, `docs/datenkatalog.md`, Tests `test_last_*`

### E-017 · Eine Werktagsregel für Preise und Last
- **Person:** [Name R2]
- **Entscheidung:** Die Funktion `werktage()` liegt in `src/gemeinsam.py` und wird von `02_aufbereitung` (Spalte `werktag`) und `02_synthetisch` (Last) benutzt. Ein Test prüft, dass beide an denselben Tagen Werktag sagen.
- **Verworfen:** Die Regel in beiden Skripten getrennt (könnte auseinanderlaufen; dann verbrauchte R3 an einem Feiertag Strom, für den kein Werktagspreis vorgesehen ist).
- **Begründung:** Gegenprobe: Feiertagsvariante nur für die Last umgestellt → Test rot.
- **Beleg:** Test `test_last_und_preise_gleiche_werktage`

### A-003 · Backtest als Funktion (für die Sensitivitätsrechnung)
- **Von → an:** R2 → R3
- **Was:** Für `src/06_sensitivitaet.py` muss R3s Backtest als Funktion aufrufbar sein, z. B. `backtest(preise: DataFrame, last: DataFrame, params: dict) -> DataFrame` (Spalten wie `backtest_wochen.csv`), ohne selbst Dateien zu lesen. Außerdem Hinweis zu V5: Mit Blöcken zur vollen Stunde sind 15-min- und Stundenkosten exakt gleich; nur Blockstarts in 15-min-Schritten zeigen einen Unterschied (wichtig für H0c).
- **Bis:** [Datum, vor 13.11.]
- **Änderung, nachgezogen von:** [R3]

### P-002 · Sensitivitätsschwelle vor dem Rechnen festlegen
- **Problem:** Ohne vorab festgelegte Schwelle könnte man im Nachhinein jede Änderung als „klein“ deklarieren.
- **Angesprochen von:** [Name R2], 07.11.2026
- **Lösungsvorschlag:** Relevant, wenn sich die mittlere Ersparnis um mehr als 5 % ändert oder sich eine Entscheidung zu H0a/H0b/H0c umkehrt.
- **Entscheidung:** [Team, Datum]
- **Ergebnis:** [offen]

### K-002 · KI-Einsatz bei Download, Aufbereitung und synthetischem Lastgang
- **Werkzeug:** Claude
- **Zweck:** Code für `src/01_download.py`, `src/02_aufbereitung.py`, `src/02_synthetisch.py`, `src/gemeinsam.py`, erklärende Kommentare, Erweiterung von `tests/test_datenannahmen.py` (jetzt 24 Tests); Vorschläge zur Zeitumstellung mit Alternativen; Entwurf `docs/sensitivitaet_plan.md`; diese Tagebuch-Entwürfe.
- **Wie geprüft:** (1) `pytest tests/`: 24 Tests grün. (2) Gegenprobe: eine Rohdatei von Hand geändert → Download bricht mit Meldung ab, Integritätstest rot; in `preise_h` einen Preis gelöscht und Samstage als Werktag markiert → drei Tests rot. (3) Nachgerechnet: 26.10.2025 02:00 Uhr = (3,19 + 2,015) / 2 = 2,6025 €/MWh; 29.03.2026 ohne 02:00 Uhr; Stundenzahl 1 765 Tage × 24 − 5 = 42 355. (4) Zweiter Lauf ohne Internet: 0 Dateien geladen. (4b) Kommentare nachträglich ergänzt und Werktagsregel verschoben: Ausgabedateien per SHA256 vorher/nachher bit-gleich. (4c) Last: Feiertagsvariante nur für die Last umgestellt → Abgleichstest rot. (5) [Name R2] hat den Code Zeile für Zeile gelesen und kann ihn erklären. [erst eintragen, wenn das stimmt]
- **Was wir geändert haben:** [eigene Änderungen nach dem Review eintragen]
