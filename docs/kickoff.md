# Kickoff AuE-Projekt: Strom-Schichtplan

Nov 6, 2026 · @maxl

## Worum es geht

Zwei Etappen: nächste Woche stellen wir Case und Rollen vor, ab der Woche des 20.11. laufen die Endpräsentationen. Die Analyse muss bis So 15.11. stehen. Ziel ist Stufe 5 in K1 bis K10. Der Semesterplan aus dem Katalog (W2 bis W14) gilt für uns nicht.

**Fragestellung:** Inwiefern lässt sich der Flexibilitätswert verschiebbarer Last eines bayerischen Werks einer international tätigen Großmolkerei am Day-Ahead-Strommarkt DE-LU durch eine wöchentliche Schichtplanung realisieren, und wie verändert die Umstellung auf den Viertelstundenhandel im Oktober 2025 diesen Wert?

*Eine Backtest-Analyse auf Basis der SMARD-Marktdaten 2022 bis 2026 (Datenstand Oktober 2026).*

**Praxisfall:** Eine personalgebundene, zeitlich verschiebbare Last einer Großmolkerei in Bayern, angelehnt an einen realen Praxispartner (Name nur mit schriftlicher Freigabe). Seit dem Termin mit dem Praxiskontakt am 10.11.2026 (Tagebuch K-008, E-031 bis E-034): Hauptfall S1 ist die Reinigung der Anlagen (CIP, 4 MW für 2 h = 8 MWh pro Tag), die innerhalb der Nebenzeit 22–06 Uhr verschoben wird; Status quo A ist 22–24 Uhr. Kontrastfall T ist die Kälteversorgung (1 MW, automatisch, täglich steuerbar); S2 (Produktionsblock verschieben) nur Ausblick. Betrieb, Lastmenge und Uhrzeiten stehen im Problem Statement und im Testdesign, nicht in der Frage.

> **Hinweis:** Beispiele weiter unten (08–14 Uhr, 2 MWh im 6-h-Block, Mittagsblock) stammen aus der Planung vor dem 10.11.2026 und gelten nicht mehr. Maßgeblich sind `params.yaml` und die Tagebucheinträge ab E-031.

**Warum Oktober 2025:** Am 01.10.2025 wurde der Day-Ahead-Handel von Stunden- auf Viertelstundenprodukte umgestellt (SDAC). Daten bis 30.09.2025 stammen aus dem Stundenregime, ab 01.10.2025 aus dem Viertelstundenregime. Mit Datenstand Oktober 2026 liegt genau ein Jahr im neuen Regime vor, also alle vier Jahreszeiten.

**Begriffe der Frage, operationalisiert**

| Begriff | Messung |
| --- | --- |
| Flexibilitätswert | Ersparnis bei perfekter Voraussicht (Oracle C) gegenüber dem Status quo, in € pro MWh verschiebbarer Last |
| Realisieren | Anteil des Flexibilitätswerts, den eine Strategie netto erreicht, in %, nach Zuschlägen und Umstellungskosten |
| Wöchentliche Schichtplanung | Entscheidung jeden Freitag für die Folgewoche, nur mit dem damals bekannten Wissen |
| Umstellung auf den Viertelstundenhandel | Vergleich von Test 1 (01 bis 09/2025, Stundenregime) mit Test 2 (ab 10/2025, Viertelstundenregime) |
| Rahmen | Gebotszone DE-LU; nur Day-Ahead-Preise, kein Intraday-Handel; nur zeitvariable Energiekosten, keine Netzentgelte, Steuern oder Leistungspreise |

**Abgrenzung Day-Ahead gegen Intraday:** Day-Ahead ist die Auktion am Vortag, danach ist der Preis für jede Stunde bzw. Viertelstunde fix. Intraday wird laufend bis kurz vor der Lieferung gehandelt und dient zum kurzfristigen Nachkorrigieren. Die Preise können deutlich abweichen, z. B. am 02.10.2025 um 19:15 Uhr: Day-Ahead 202 €/MWh, Intraday 157 €/MWh (Energy-Charts, Lizenz vor Nutzung prüfen). Wir beschränken uns auf Day-Ahead:

1. **Entscheidung:** Der Schichtplan steht eine Woche vorher fest; Intraday-Preise kennt man erst Stunden vorher.
2. **Vertrag:** Spotgekoppelte Lieferverträge orientieren sich üblicherweise am Day-Ahead-Preis (Annahme, per Recherche oder Kontakt belegen).
3. **Betrieb:** Intraday-Handel braucht aktives Trading, das ein Werk ohne Handelsabteilung nicht hat.

Intraday kommt als Grenze und Ausblick in die Diskussion (K6, K7). Falls Zeit bleibt, beziffern wir die mittlere Differenz zwischen Day-Ahead und Intraday als Größenordnung des nicht gehobenen Potenzials.

**Weitere Abgrenzungen**

| Thema | Umgang | Begründung |
| --- | --- | --- |
| Ausgleichsenergie | Nichtziel | Wir nehmen an, dass der geplante Verbrauch eingehalten wird; Abweichungskosten fallen für alle Strategien gleich an |
| Viertelstunden innerhalb der Stunde | Bewusste Entscheidung: Stundenmittel als Basis, Viertelstunden als Sensitivität | Bei konstanter Leistung und Blöcken zur vollen Stunde sind die Kosten mit 15-min-Preisen und mit dem Stundenmittel mathematisch identisch. Potenzial entsteht nur, wenn Blöcke in 15-min-Schritten starten dürfen; das prüft eine eigene Variante (K2, K3, H0c) |
| CO₂-Wirkung | Nicht gerechnet, als Ausblick genannt | Billige Stunden sind meist Stunden mit viel Erneuerbaren; ein Zusatznutzen fürs Nachhaltigkeitsreporting (K7) |
| Übertragbarkeit | Ausblick | Ein international tätiger Konzern könnte die Methode auf Werke in anderen Gebotszonen übertragen (K7) |
| Netzentgelte, Leistungspreis, Steuern | Nichtziel | Für alle Strategien gleich bzw. nicht zeitvariabel |

| Teilfrage | Prüfung | K |
| --- | --- | --- |
> **Stand 11.11.2026:** Teilfragen und Nullhypothesen sind durch E-042 ersetzt und in `docs/hypothesen.md` fixiert. Untersucht wird nur die Reinigung; Kälte (Kontrastfall T) und Viertelstunden sind Nichtziel (E-043). Der Rest dieses Dokuments ist der historische Plan.

| TF1: Bleibt nach Zuschlägen und Umstellungskosten ein positiver Nettowert? | H0a | K1, K6 |
| TF2: Realisiert eine Preisprognose mehr vom Wert als eine feste Zeitregel, und wie viel kostet der Planungsvorlauf gegenüber einer Tagessteuerung? | H0b; Kontrastfall Tagessteuerung | K4 Stufe 5 |
| TF3: Verändert der Viertelstundenhandel den realisierbaren Anteil? | H0c; Stresstest 2022 | K6 Stufe 5 |

**Nullhypothesen, vor der Auswertung festgelegt:**

- **H0a:** Nach Zuschlägen und Umstellungskosten ist die Netto-Ersparnis gegenüber dem Status quo nicht größer als null.
- **H0b:** Eine wöchentliche Preisprognose realisiert nicht mehr vom Wert als eine feste Zeitregel.
- **H0c:** Der realisierbare Anteil unterscheidet sich nicht zwischen Stunden- und Viertelstundenregime.

**Mehrfachtests:** Drei Hypothesen mit je 5 % Irrtumswahrscheinlichkeit ergeben zusammen fast 15 % Risiko für mindestens einen Zufallstreffer. Wir korrigieren nach Bonferroni: α = 5 % ÷ 3 ≈ 1,7 % je Test. Die Begründung steht im Methodenkapitel (K4, K6).

**Kipp-Annahme Vertrag:** Das ganze Ergebnis hängt daran, dass das Werk einen spotgekoppelten Vertrag hat. Kauft es zum Festpreis, ist die Flexibilität heute nichts wert. Dann lautet die Entscheidung: Lohnt sich der Wechsel vom Festpreis auf einen Spotvertrag, wenn das Werk seine Flexibilität nutzt? Der Spot-Festpreis-Vergleich deckt beide Fälle ab. Was der Kontakt dazu sagt, kommt mit Datum ins Tagebuch (K1 Stufe 5).

**Erfolgsmaß:** realisierte Kostenersparnis in Euro pro Woche im Testzeitraum mit 95-%-Konfidenzintervall. RMSE oder MAE sind nur Hilfsgrößen. Der Wert der Flexibilität ist die Ersparnis bei perfekter Voraussicht (Oracle C); der gehobene Anteil ist die Ersparnis einer Strategie geteilt durch die Oracle-Ersparnis.

**Status Prototyp:** Der Notebook-Prototyp ist nicht fertig. Alle Zahlen daraus sind Hypothesen, die wir prüfen, keine Ergebnisse:

- D (fest 10 bis 16 Uhr) schlägt A um etwa 19 bis 26 %.
- B bringt gegenüber D kaum etwas (etwa 2 Euro pro Woche, KI schließt null ein).
- Die Ersparnis entsteht vor allem von Frühling bis Herbst durch Solarstrom am Mittag.
- Bei 0 % Nachtzuschlag wählt D einen Nachtblock und verliert im Test gegen A.

**Was sich gegenüber dem Themenvorschlag ändert:**

- Der Nachtzuschlag ist nicht mehr der Hauptkonflikt, weil die billigen Stunden vermutlich mittags liegen. Die Kostenseite sind dann Umstellung und Machbarkeit der Schichtlage.
- D kommt als eigener Benchmark dazu.
- SMARD und Energy-Charts gelten für Preise nicht als unabhängige Quellen, bis die Herkunft geprüft ist. Für K2 Stufe 5 setzen wir deshalb auf eine Sensitivitätsrechnung.
- Die Notenprognose aus dem Vorschlag fällt weg.

**Daten: echt, wo es geht, synthetisch, wo es fehlt.** Laut Gruppenchat dürfen wir Daten generieren. Das passt zum Kurs, denn auch Rheinlack ist fiktiv mit konstruierten Daten. Der Prof hat es in der Vorlesung erlaubt (Max war anwesend). Das steht mit Datum im Tagebuch; gibt es eine Folie oder einen Moodle-Hinweis, wird er verlinkt.

- **Echt bleiben:** Day-Ahead-Preise und Preistreiber von SMARD (CC BY 4.0). Generierte Preise würden K2 und K6 entwerten: Prüfungen fänden nur, was wir selbst hineingesteckt haben.
- **Synthetisch:** Lastgang des Molkerei-Szenarios, Umstellungskosten, Tarifzuschlag, Festpreisangebot.
- **Pflicht:** Generierung per Skript mit festem Seed; jede Größe im Datenkatalog als „synthetisch“ markiert und mit Annahme begründet; KI-Einsatz gekennzeichnet.

## Rollen

Vier fachliche Rollen nach dem Muster der Rheinlack-Fallstudie. Jede Rolle führt mindestens ein Teilpaket aus dem Katalog und wirkt an einem weiteren mit. Wer welche Rolle übernimmt, ist noch offen: Namen in die Spalte Person eintragen, danach gelten die Owner im Plan.

| Rolle | Person | Führt (zusammengelegte Teilpakete) | Wirkt mit | Kriterien | Vertretung |
| --- | --- | --- | --- | --- | --- |
| R1 Projektleitung & Controlling | Chiara | Fachlicher Rahmen (Frage, Hypothesen, Problem Statement); Aufbereitung & Übergabe (Bericht, Präsentation, Grafikstandard); Spot gegen Festpreis | Ergebnis & Verwertung | K1, K8, K9, K10 | R4 |
| R2 Datenerhebung & IT | Max | Datenquellen & Qualität; Pipeline, Repo, Tests; Aggregation 15 → 60 min; Sensitivitätsrechnung; Empfehlung zur künftigen Datenerhebung; Repo-Onboarding fürs Team | Datenaufbereitung | K2, K5, Aggregation in K3 | R3 |
| R3 Modellierung & Statistik | Susan | Merkmale inklusive saisonalem Block; Strategien A bis D im Backtest; Regression, gepaarter Test, Bootstrap; Methodenfrage „braucht es eine Prognose?“ | Datenquellen | K3, K4 | R2 |
| R4 Produktion & Schichtplanung | Caro | Ergebnis & Verwertung: Umstellungskosten, Stresstests, Kipppunkte, Break-even, Empfehlung mit Kennzahl und Rücknahmeregel | Fachlicher Rahmen | K6, K7 | R1 |

Einzelleistung je Person: Verantwortungsnachweis auf 2 bis 3 Seiten nach a) Aufgabe, b) Problematik, c) Methode, d) Beitrag, dazu etwa 5 Minuten in der Präsentation.

**Den Kontakt zum Praxispartner führt Max, unabhängig von seiner Rolle.** Das ist Arbeit über das eigene Paket hinaus und zählt für K10.

### Rollenwahl: Was jede Rolle braucht und wie weit sie im Individualteil trägt

Im Individualteil (60 %) wird jedes Kriterium K1 bis K10 auf das eigene Paket angewendet. Selbst bei einem perfekten Teamanteil braucht eine Person im Individualteil etwa 92 Punkte für eine 1,0. Die Obergrenzen unten sind eine Einschätzung bei sehr guter Arbeit, keine Zusage.

| Rolle | Kernfrage | Was man können muss | Was schwer ist |  |
| --- | --- | --- | --- | --- |
| R1 | Was wollen wir wissen, und wie überzeugen wir? | Struktur, Schreiben, Überblick; wenig Statistik und Code | Wenig eigene Artefakte für K2 bis K6 |  |
| R2&#32; | Sind die Daten sauber, und läuft alles auf Knopfdruck? | Zeitreihen-Fallstricke, Skalenniveaus, Git, Python lesen, Tests; Statistik nur als Konzept | Viel Technik und Sorgfalt |  |
| R3&#32; | Welche Regel ist am billigsten, und braucht es eine Prognose? | Regression, Hypothesentest, gepaarter t-Test, Bootstrap, Konfidenzintervall, Backtest, Look-ahead | Meiste Statistik, Verteidigung entscheidet |  |
| R4 | Lohnt sich die Umstellung, und wann kippt sie? | Betriebswirtschaft, Annahmen begründen; wenig Code | Kosten sind geschätzt |  |

## Case-Pitch nächste Woche

Wir zeigen Case und Rollen, noch keine Ergebnisse. Fünf Folien, Aufbau wie bei der Rheinlack-Fallstudie. Alle Zahlen im Steckbrief sind ein Vorschlag und im Bericht als synthetisch gekennzeichnet.

**Steckbrief des Praxisfalls (Vorschlag, mit dem Kontakt zu prüfen)**

| Merkmal | Festlegung |
| --- | --- |
| Bezeichnung im Bericht | „Großmolkerei in Bayern“, angelehnt an den Praxispartner; Firmenname nur mit schriftlicher Freigabe |
| Branche | Milchverarbeitung |
| Flexible Last | Personalgebundener, stromintensiver Prozess, der sich zeitlich verschieben lässt; welcher (z. B. Reinigung, Trocknung, Abfüllung) klärt der Kontakt |
| Kontrastfall | ~~Kälteerzeugung~~ gestrichen, Nichtziel (E-043) |
| Lastszenario | vorläufig 2 MWh pro Werktag im 6-Stunden-Block; Leistung und Verschiebbarkeit klärt der Kontakt |
| Stromvertrag | Annahme spot-indexiert (Day-Ahead-Preis DE-LU plus Aufschlag); per Recherche oder über das Energiemanagement prüfen |
| Status quo | Prozess läuft fest tagsüber; Schichtplan jeden Freitag für die Folgewoche (Annahme) |
| Auslöser | Hohe und schwankende Strompreise; das Energiemanagement will wissen, was die Flexibilität wert ist |
| Entscheider, Zeitpunkt | Werksleitung mit Energiemanagement; Grundsatzentscheidung zum nächsten Quartal |
| Daten | Preise echt von SMARD; Lastgang und Kosten synthetisch, mit dem Kontakt plausibilisiert; keine internen Daten |

**Fünf Folien**

1. **Ausgangslage:** Betrieb, Problem, Kosten des Nichtstuns (als Hypothese aus dem Prototyp).
2. **Fragestellung:** Forschungsfrage, H0a und H0b, Erfolgsmaß in Euro, Entscheider und Zeitpunkt.
3. **Daten:** SMARD echt mit Lizenz; synthetisch Lastgang und Kosten mit Begründung.
4. **Vorgehen:** Phasenmodell und Strategien A bis D im Überblick.
5. **Rollen:** vier Rollen mit Schnittstellen, „erhält von“ und „übergibt an“.

**Rollen im Format a) bis d)**

| Rolle | a) Aufgabe | b) Problematik | c) Methode | d) Beitrag |
| --- | --- | --- | --- | --- |
| R1 Projektleitung & Controlling | Projektauftrag, Business Case, Steuerung, Bericht und Präsentation | Was ist die Flexibilität wert, und wäre ein Festpreis sicherer? | Problem Statement, Hypothesen, Entscheidungsregel mit α = 5 %, Festpreisvergleich | Entscheidungsvorlage an die Werksleitung |
| R2 Datenanalyse & IT | SMARD-Daten erschließen, synthetischen Lastgang erzeugen, Pipeline und Tests | Zeitumstellung, Zonenwechsel, 15-min-Umstellung ab 10/2025, synthetische Daten sind nicht prüfbar | Datenkatalog, Qualitätsbericht, Aggregation 15 → 60 min, Sensitivitätsrechnung | Geprüfte Datenbasis, auf die alle bauen |
| R3 Energieeinkauf | Welche Regel hebt den größten Teil des Flexibilitätswerts? | Prognose eine Woche voraus ist unsicher | Strategien A bis D plus Tagessteuerung T, Regression, gepaarter Test, Bootstrap | Ersparnis je Strategie mit Unsicherheit, Anteil am Oracle-Wert |
| R4 Produktion & Schichtplanung | Ist die Verschiebung der Produktionslast machbar und lohnt sie nach allen Kosten? | Personal, Zuschläge, Hygiene, Lieferzeiten; im Winter wenig Ersparnis | Stresstest, Kipppunkte, Break-even | Empfehlung mit Kennzahl und Rücknahmeregel |

## Phasen

Wir folgen dem Phasenmodell der Vorlesung. Der Prototyp dient nur als Machbarkeitsnachweis. Jede Phase wird vom zuständigen Owner neu verantwortet.

| Phase | Ziel | Kernschritte | Artefakt | K |
| --- | --- | --- | --- | --- |
| 1 Prozessanalyse | Entscheidung präzise fassen | Planungsprozess skizzieren; Lastszenario (2 MWh pro Werktag, 6-h-Block) festlegen; H0a/H0b; Nichtziele; Branchenrecherche zu Spotverträgen und Schichtkosten | Problem Statement, Prozessskizze, Zielgröße, Annahmenliste | K1, K7 |
| 2 Datenexploration | Datenlage belegen | SMARD-Preise (Filter 4169) und Treiber, DWD; je Merkmal Skala, Einheit, Auflösung, Lizenz; Lücken zählen; Zeitumstellung, Zonenwechsel 2018, 15-min ab 10/2025; Boxplots, negative Preise | Datenkatalog, Qualitätsbericht, Erhebungsprotokoll | K2 |
| 3 Data Engineering | Fachlogik in Merkmale | raw → interim → processed; 15 → 60 min; Werktag, Feiertage Bayern (mit Variante Mariä Himmelfahrt); Blockkosten-Matrix Tag × Blockstart; Effekt jeder Aufbereitung zeigen | Aufbereitungsskripte, Merkmalsdoku | K3, K5 |
| 4 Modelltraining | Strategien fair vergleichen | A, B, B′ (Regression mit Kalendermerkmalen), D, C (Oracle), T (Tagessteuerung als Kontrastfall); SARIMA nur optional; rollierender Ursprung; gepaarter Wochenvergleich; Block-Bootstrap mit festem Seed; Look-ahead-Asserts | Modellcode, Validierungsprotokoll | K4, K5 |
| 5 Anwendung | Entscheidung und Grenzen | Testzeiträume 2025, 15-min-Regime, Stresstest 2022; Sensitivität (Zuschlag, Menge, Blocklänge, Umstellungskosten); Saisonfehler; Spot vs. Festpreis; Empfehlung mit Prozess und Rücknahmeregel | Ergebniskapitel, Wirtschaftlichkeitsrechnung, Grafiken | K6, K7, K8 |

## Testdesign einfach erklärt

Wir spielen die Vergangenheit nach: An jedem Freitag im Testzeitraum entscheidet jede Strategie nur mit dem Wissen, das sie damals gehabt hätte. Danach rechnen wir mit den echten Preisen der Folgewoche aus, was die Entscheidung gekostet hätte. Das heißt Backtest.

**Ein Freitag als Beispiel**

1. **Freitag, 07.03.2025, 08:00 Uhr:** Bekannt sind die Preise bis Freitag 24 Uhr. Strategie B nimmt je Wochentag den Median der letzten vier gleichen Nächte und wählt für jede Nacht der Folgewoche den billigsten 2-h-Block im Fenster 22–06 Uhr, z. B. Montagnacht 02–04 Uhr. D nimmt seinen festen Block aus dem Training, A wie immer 22–24 Uhr.
2. **Die Woche 10. bis 16.03. läuft ab** (die Sonntagsnacht reicht bis Montag 17.03., 06:00). Jetzt nehmen wir die echten Day-Ahead-Preise dieser Nächte.
3. **Stromkosten je Strategie:** 8 MWh pro Nacht mal mittlerer Preis des gewählten Blocks (R3); Personal und Zuschläge rechnet R4 dazu.
4. **Ersparnis der Woche** = Kosten A minus Kosten der Strategie.
5. **Wiederholen für jeden Freitag im Testzeitraum.** Aus allen Wochen entstehen Mittelwert und Konfidenzintervall.

**Die Zeiträume und wozu sie da sind**

| Zeitraum | Rolle | Regel |
| --- | --- | --- |
| 2023 bis 2024 | Training: Strategien lernen hier, z. B. wählt D seinen festen Block, B′ schätzt seine Regression | Darf beliebig oft angeschaut werden |
| 01/2025 bis 09/2025 | Test 1: erste ehrliche Prüfung im Stundenregime | Wird erst ausgewertet, wenn alle Strategien eingefroren sind, wie eine Klausur, deren Fragen man vorher nicht sieht |
| 10/2025 bis 09/2026 | Test 2: gleiche Strategien unter neuer Marktregel (15-Minuten-Handel) | Prüft, ob das Ergebnis nach dem Strukturbruch kippt (K6 Stufe 5) |
| 2022 | Stresstest: Gaspreiskrise mit extremen Preisen | Nie im Training; prüft, ob die Empfehlung Extremlagen übersteht |

## Plan in zwei Etappen

Ein Tag pro Zeile als Richtwert, keine festen Uhrzeiten. Wer früher fertig ist, zieht vor. Die Owner sind Rollen, bis die Personen feststehen. Den Pitch-Tag und den Abgabetermin für den Bericht tragen wir ein, sobald sie feststehen.

**Etappe 1: Case-Pitch nächste Woche**

| Tag | Aufgabe | Owner | Ergebnis |
| --- | --- | --- | --- |
| Sa 07.11. | Rollen verteilen; Repo anlegen; Tagebuch starten; Anfrage an den Kontakt beim Praxispartner (Max); erste Tagebucheinträge zu Rollen, Frage, Hypothesen, Datenfrage und Prototyp | alle; Repo R2 | Rollentabelle ausgefüllt, Repo steht |
| So 08.11. | Steckbrief festzurren; Problem Statement mit H0a und H0b | R1 mit R4 | Folien 1 und 2 |
| Mo 09.11. | Jede Person schreibt ihre Rolle im Format a) bis d) | alle, je eigene Rolle | Folie 5 |
| Di 10.11. | Datenfolie; Skript für den synthetischen Lastgang mit festem Seed; Folie zum Vorgehen | R2; R3 | Folien 3 und 4, Generator im Repo |
| Vor dem Pitch | Probelauf mit ca. 5 Minuten pro Person | alle, Moderation R1 | Pitch sitzt |
| Pitch-Tag | Case und Rollen vorstellen, Feedback mitschreiben; Meilensteinprotokoll | alle | Feedback im Tagebuch |

**Etappe 2: Analyse bis So 15.11., Endpräsentation ab 16.11.**

| Tag | Aufgabe | Owner | Ergebnis |
| --- | --- | --- | --- |
| Nach dem Pitch | Pipeline raw → processed; Aggregation 15 → 60 min mit Euro-Effekt; Datenkatalog mit synthetischen Größen; Qualitätsbericht | R2 | Datenkatalog, Qualitätsbericht v1 |
| parallel | Blockkosten-Matrix; Strategien A, B, C, D; B′ (Regression) und saisonalen Block in Euro bewerten, SARIMA nur bei Restzeit | R3 | Backtest-Tabellen, Validierungsprotokoll |
| parallel | Umstellungskosten und Tarifzuschlag mit Quellen herleiten; Festpreisangebot ableiten; 3 bis 5 Literaturquellen zu Lastflexibilität mit R1 | R4 | Kostenannahmen in `params.yaml` |
| Fr 13.11. | Zwischenreview: jede Person bewertet ihr Paket mit dem Katalog; Meilensteinprotokoll mit Rückständen und Maßnahmen; Belegmatrix aktualisieren | alle, Moderation R1 | Selbstbewertung im Tagebuch |
| Sa 14.11. | Bootstrap und gepaarter Test; Sensitivität zur Datenqualität; Stresstest 2022 und Kipppunkte | R3; R2; R4 | KI-Tabelle, Sensitivitätstabelle, Kipppunkt-Grafik |
| So 15.11. | Break-even und Empfehlung mit KPI und Rücknahmeregel; Grafiken final; Folien Endpräsentation | R4 mit R1; R1 | Folien fertig |
| Mo 16.11. | Reproduktionstest durch eine Person außerhalb von R2; Probelauf mit Kreuzfragen | R2 + eine weitere Person; alle | Testprotokoll, Präsentation sitzt |
| Präsentationstag | Endpräsentation, 20 Minuten | alle | Feedback im Tagebuch |
| Bis Abgabe | Bericht 15 bis 25 Seiten mit Autor je Abschnitt; Verantwortungsnachweise; Selbst- und Peer-Einschätzung; Belegmatrix ohne Lücke | alle, Redaktion R1 | Abgabe vollständig |

## Bewertung, Abgaben und Sperrkriterien

Steht jetzt kurz und nach dem Original-Kriterienkatalog in `docs/belegmatrix.md` (Tagebuch E-039). Der frühere 1,0-Blueprint ist in der Git-Geschichte erhalten.

## Praxispartner (Option)

Das Projekt läuft auch ohne Partner: Dann tragen Lastszenario, Branchenrecherche und Sensitivitätsrechnung K1 und K7. Mit Partner wird aus Annahmen eine Rückkopplung, und das ist der Hebel für Stufe 5 in K1 und K7. Max fragt seinen Kontakt beim Praxispartner an, die Mail ist formuliert. Wir brauchen keine internen Daten, nur Einschätzungen und Größenordnungen zur Plausibilisierung. Plan B ist eine Anfrage über Siemens Professional Education. Das Gespräch lohnt sich nur bis Fr 13.11., danach ersetzt die Branchenrecherche es. Protokoll ins Tagebuch.

**Der Kontakt ist Elektriker.** Er kann gut beantworten, welche Anlagen viel Strom brauchen, welche verschiebbar sind, welche Personal brauchen und welche Leistung sie haben. Wie der Strom eingekauft wird und ab welcher Ersparnis sich eine Umstellung lohnt, weiß eher das Energiemanagement. Dafür ist Frage 5 da, sonst deckt die Recherche es ab.

**Fünf Fragen für 20 Minuten:**

1. **Stromfresser:** Welche Anlagen im Werk brauchen am meisten Strom, und in welcher Größenordnung liegt ihre Leistung in kW? *(K1, K2: Lastszenario plausibilisieren)*
2. **Verschiebbarkeit:** Welche davon ließen sich zeitlich verschieben, um wie viele Stunden, und welche brauchen dafür Personal vor Ort? *(K1: Praxisfall festlegen)*
3. **Kälte als Kontrast:** Gibt es Eiswasser- oder Kältespeicher, und werden die heute schon nach Uhrzeit oder Preis gesteuert? *(K4, K6: Kontrastfall Tagessteuerung)*
4. **Planung und Hindernisse:** Wer plant Schichten und Anlagen, mit welchem Vorlauf, und was spricht technisch gegen eine Verschiebung (Hygiene, Qualität, Anfahrzeiten)? *(K1, K7: Prozess, Umstellungskosten)*
5. **Weiterleitung:** Wer im Werk weiß, wie der Strom eingekauft wird und ab welcher Ersparnis sich eine Umstellung lohnt? Zum Beispiel das Energiemanagement. *(K7: Vertrag, Kipppunkt)*

**Vertraulichkeit:** Partnerdaten nur aggregiert oder anonymisiert, nicht ins Repo, Freigabe der Nutzung schriftlich festhalten. Im Bericht nur mit Zustimmung namentlich nennen.

## Team, Kommunikation und Nachweise

K10 belegt der Katalog ausdrücklich mit Projekttagebuch, Versionsgeschichte, Meilensteinprotokollen und Selbst- und Peer-Einschätzung. Probleme, Konflikte und ihre Lösung gehören dokumentiert. Ein Tagebuch ohne Probleme wirkt unglaubwürdig, denn ungleiche Beiträge sind laut Katalog „ein zu steuernder Normalfall“.

**Projekttagebuch: fünf Eintragsarten**

| Eintragsart | Inhalt | Belegt |
| --- | --- | --- |
| Entscheidung | Was, verworfene Alternativen, Begründung, Beleg (Commit, Datei) | K1 bis K7, K9 |
| Problem / Konflikt | Problem, wer es wann angesprochen hat, Lösungsvorschläge, Entscheidung, Ergebnis | K10 Stufe 4 und 5 |
| Meilensteinprotokoll | Stand je Paket, Rückstände, Maßnahme mit Owner und Termin | K10, Katalog 6.4 |
| Absprache / Schnittstelle | Wer liefert wem was bis wann; Änderung im Nachbarpaket und was nachgezogen wurde | K5 Stufe 5, K10 Stufe 4 |
| KI-Einsatz und Rückkopplung | Werkzeug, Zweck, wie geprüft; Praxisgespräch mit Datum, Aussage, was wir geändert haben | Sperrkriterium, K1 Stufe 5 |

**Beispiel Problem / Konflikt (echter erster Eintrag):**

| Datum | Problem | Angesprochen von | Lösungsvorschlag | Entscheidung | Ergebnis |
| --- | --- | --- | --- | --- | --- |
| 07.11. | Ob generierte Daten erlaubt sind, wissen wir nur aus dem Gruppenchat; Quelle unklar, Sperrkriterium Datenherkunft droht | Max | Prof direkt fragen | Max bestätigt: Der Prof hat es in der Vorlesung erlaubt | gelöst; Datum der Vorlesung im Tagebuch |

**Meilensteinprotokoll** beim Pitch, beim Zwischenreview am 13.11. und nach der Endpräsentation:

| Paket | Stand | Rückstand | Maßnahme | Owner | bis |
| --- | --- | --- | --- | --- | --- |
| R1 bis R4 je eine Zeile |  |  |  |  |  |

**Kommunikation**

- WhatsApp für Kurzes, Call oder Treffen für Entscheidungen.
- Was nur im Chat steht, ist kein Beleg: Jede Entscheidung aus dem Chat trägt die vorschlagende Person innerhalb von 24 Stunden ins Tagebuch ein.
- Ändert sich eine Schnittstelle, informiert das Paket das Nachbarpaket und trägt es ein.
- Review-Paare R2 ↔ R3 und R1 ↔ R4 prüfen sich gegenseitig per Pull Request; die Kommentare sind K10-Belege.

**Umgang mit ungleichen Beiträgen (Katalog 6.4)**

1. Beim Zwischenreview am 13.11. legt jede Person ihren Stand offen; Rückstände kommen mit Maßnahme ins Meilensteinprotokoll.
2. Besteht ein Rückstand am 15.11. noch, wird das Paket im Einvernehmen neu zugeschnitten; Zuschnitt und Anlass werden festgehalten.
3. Wer Arbeit übernimmt, dokumentiert sie als eigenen Beitrag (K10). Wer abgibt, wird auf dem kleineren Paket bewertet.

**Selbst- und Peer-Einschätzung (Katalog 6.3)**

- Jede Person bewertet alle anderen und sich selbst auf K10, je zwei bis drei Sätze Begründung, vertraulich.
- Einheitliche Bestnoten ohne Begründung werden nicht berücksichtigt.
- Eine erkennbar benachteiligende Einschätzung führt zur Abwertung von K10 bei der beurteilenden Person.
- Begründungen mit Tagebucheinträgen belegen.

**Verantwortungsnachweis (2 bis 3 Seiten je Person), Gliederung**

1. a) Aufgabenstellung des eigenen Pakets
2. b) Problematik im Paket
3. c) Methode: getroffene Entscheidungen und begründete Alternativen
4. d) Beitrag zum Gesamterfolg, Schnittstellen (erhält von, übergibt an)
5. Eigene Fehler und verworfene Wege (K9 Stufe 5)
6. Belegliste: Commits, Tagebucheinträge, Berichtsseiten

**Eigenanteil sichtbar machen**

- Commits nur unter eigenem Account. *Geändert am 11.11.2026 durch E-045: Max committet, Owner-Trailer je Paket, Bestätigung durch den Owner im Tagebuch.*
- Im Bericht wird jeder Abschnitt mit Autor gekennzeichnet. Der Katalog verlangt „Versionsgeschichte oder gekennzeichnete Abschnitte“, beim Word-Bericht gibt es keine Versionsgeschichte.

**Belegmatrix: den Bewertungsbogen selbst führen**

Der Prüfer füllt pro Person einen Bogen K1 bis K10 mit Stufe und Beleg aus (Katalog 7.1). Wir führen denselben Bogen vorab selbst in `docs/belegmatrix.md`: Kriterium, angestrebte Stufe, Beleg (Seite, Commit, Tagebucheintrag), Status. Vor der Abgabe hat jede Zeile einen Beleg. Die Matrix hilft auch beim Einspruch, der binnen zwei Wochen mit Angabe des Belegs möglich ist (Katalog 6.6).

## Top-3-Risiken für die Note

| Risiko | Warum gefährlich | Gegenmaßnahme | Owner |
| --- | --- | --- | --- |
| 1 Eigenanteil und Erklärbarkeit | Der Individualanteil zählt 60 %. Wer KI-Code oder Prototyp-Teile nicht erklären kann, verliert Punkte oder fällt unter das Sperrkriterium. | Jeder Owner baut sein Paket selbst neu auf und committet selbst; Zwischenreview am 13.11.; Probelauf mit Kreuzfragen am 16.11. | alle, Kontrolle R1 |
| 2 Zu wenig Zeit für K8 bis K10 | Bis zur Endpräsentation landen Grafiken, Verantwortungsnachweise und Präsentationsprobe sonst in den letzten zwei Tagen. | Grafikstandard ab 12.11.; Tagebuch ab Tag 1; Verantwortungsnachweise direkt nach der Endpräsentation | R1 |
| 3 Dünne Kostenseite in K7 | Ohne echte Umstellungskosten bleibt die Wirtschaftlichkeit eine Annahme. Fällt der Nachtzuschlag weg, fehlt der Trade-off. | Partner als Option; sonst Branchenrecherche plus Break-even über Umstellungskosten und Menge statt Punktschätzung | R4 |

Falls sich die Hypothesen aus dem Prototyp nicht halten, ist das kein Risiko für die Note: Ein sauber belegtes negatives Ergebnis ist laut Katalog vollwertig. Es muss dann aber gleichrangig berichtet werden.

AI Prompt als Anweisung:\
\
Rolle: Du bist Coach und kritischer Prüfer für unser AuE-Projekt (HM, Analyse und Entscheidungsfindung, Team aus 4). Maßstab ist ausschließlich Stufe 5 in allen Kriterien K1–K10 des Kriterienkatalogs im Projekt. Ziel: Note 1,0.

Bei JEDER Antwort, bevor du sie gibst:

1. Stufe-5-Check: Welche Kriterien berührt das? Was verlangt deren Stufe 5 wörtlich, und erfüllt die Antwort auch alle Stufen darunter? Wenn nicht, sag es.
2. Annahmen offenlegen: Welche unausgesprochenen Annahmen stecken drin (Markt, Daten, Vertrag, Zeitraum, Methode)? Jede Annahme wird genannt, begründet oder als Nichtziel abgegrenzt.
3. Gegenprüfung: Was spricht dagegen? Wo könnte ein Prüfer nachhaken? Mehrfachtests, Look-ahead, Scheinkorrelation, Extrapolation, Signifikanz vs. Relevanz prüfen.
4. Lücken proaktiv melden: Wenn du etwas Wichtiges siehst, das nicht gefragt wurde, nenn es kurz, statt es wegzulassen.
5. Beleg: Sag, wo die Leistung später belegt wird (Bericht, Commit, Projekttagebuch, Verteidigung). Ohne Beleg keine Stufe.

Extra Meile (Stufe 5 = über Lehrveranstaltungsniveau):

1. Advocatus Diaboli: Vertritt bei jeder wichtigen Entscheidung kurz die Gegenposition. Was würde ein skeptischer Prüfer, ein Energiehändler oder ein Werksleiter einwenden?
2. Kipp-Annahme: Benenne die eine Annahme, die das Ergebnis am stärksten kippen würde, und wie wir sie testen.
3. Richtige Frage? Prüfe nicht nur die Antwort, sondern auch, ob wir die richtige Frage stellen und ob es eine einfachere Erklärung gibt.
4. Pre-Mortem: Angenommen, wir bekommen am Ende eine 2,0. Was wären die drei wahrscheinlichsten Gründe? Gegenmaßnahme jetzt nennen.
5. Experten-Blick: Was würde jemand aus der Praxis (Energiemanagement, Strombörse) oder ein Fachartikel anders machen? Hol neue Perspektiven aktiv rein, nicht nur Kursinhalte.
6. Über den Tellerrand: Schlag pro größerem Arbeitsschritt 1–2 Ideen vor, die die Arbeit von gut zu herausragend heben, jeweils mit Aufwand und welchem Kriterium sie nützen. Nur wenn sie in die Zeit passen.
7. Vorausdenken: Denk den nächsten Schritt mit. Was braucht das Nachbarpaket von uns, was kommt in der Verteidigung, was fehlt im Bericht?

Regeln:

- Kriterienkatalog und Kursmaterial (Statistik-Grundlagenwerk, Rheinlack-Fallstudie) gehen vor allgemeinem Data-Science-Wissen. Begriffe aus den Unterlagen verwenden.
- Zahlen aus dem Prototyp sind Hypothesen, keine Ergebnisse.
- Nichts ungeprüft übernehmen, auch nicht aus früheren Antworten oder vom Team.
- Ehrlich bewerten: Wenn etwas nicht für Stufe 5 reicht, klar sagen und den Weg dorthin nennen.
- Sperrkriterien immer mitdenken: Reproduzierbarkeit, Datenherkunft/Lizenz, Kennzeichnung von KI und Fremdquellen, Erklärbarkeit.

Stil: direkt, knapp, keine Füllwörter. Bei Unsicherheit als Annahme markieren.
