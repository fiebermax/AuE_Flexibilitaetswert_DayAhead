# Projekttagebuch

Ein Eintrag pro Entscheidung, Problem, Meilenstein, Absprache oder KI-Einsatz. Neueste Einträge oben. Jeder Eintrag wird von der Person committet, die ihn verfasst. Entscheidungen aus dem WhatsApp-Chat werden innerhalb von 24 Stunden hier eingetragen.

Eintragsarten: **E** Entscheidung · **P** Problem/Konflikt · **M** Meilensteinprotokoll · **A** Absprache/Schnittstelle · **K** KI-Einsatz und Rückkopplung

---

## 09.11.2026

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
