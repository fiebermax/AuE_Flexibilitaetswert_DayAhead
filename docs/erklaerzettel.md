# Erklärzettel je Phase (für die Owner, zur Vorbereitung der Verteidigung)

<!-- KI: Claude, Zweck: Erklärzettel nach E-045, je Phase höchstens eine Seite, geprüft von den jeweiligen Ownern -->

Eine Phase = ein Abschnitt. Der Owner liest ihn, prüft ihn am Code nach und bestätigt im Tagebuch (E-045).

## Phase 1 · R3 (Susan): Hypothesen und Merkmale

**Was gebaut wurde**
- `docs/hypothesen.md` (Commit `7a63c15`): H0a–H0c, einseitig, α = 0,05/3, Haupttest gepaarter t-Test, Wilcoxon als Gegenprobe (E-047), keine Regression. Festgelegt, bevor irgendein Testzeitraum gerechnet wurde.
- `src/03_merkmale.py`: die **Blockkosten-Matrix**. Für jede Nacht (benannt nach dem Tag, an dem sie um 22 Uhr beginnt) und jeden möglichen 2-h-Block der mittlere Preis in €/MWh. Normal 7 Blöcke je Nacht (Start 22, 23, 0 … 4), in der Märznacht 6, in der Oktobernacht 8. Dazu je Block die Stunden auf Sonntag und Feiertag (für R4) und als Kalendermerkmale Wochentag und Saison der Nacht.
- **Saisonaler Block:** der beste feste Start, gelernt nur aus den 731 Trainingsnächten 2023–2024, einmal fürs ganze Jahr und einmal je Saison (`ergebnisse/saisonaler_block.csv`).
- `tests/test_merkmale.py`: 8 Tests, darunter der Abgleich mit der getesteten R2-Funktion `fenster_je_tag` über alle 1 764 Nächte.

**Warum so**
- *Mittelpreis des Blocks:* Bei konstanter Leistung (4 MW) kostet jede MWh im Block den Durchschnitt der Stundenpreise.
- *Lange Tabelle (eine Zeile je Block):* In der Oktobernacht gibt es zweimal „2 Uhr“. Mit einer Spalte je Uhrzeit ginge ein Block verloren.
- *Startregel bei Zeitumstellung:* Eine Regel „Start 2 Uhr“ nimmt im März (2 Uhr fehlt) den 3-Uhr-Block und im Oktober den ersten 2-Uhr-Block.
- *Mittel statt Median für den festen Block:* Bezahlt wird die Summe über alle Nächte; die Summe ist am kleinsten beim kleinsten Mittel.
- *Nur Training:* Sonst hätte D die Testpreise schon gesehen (Look-ahead).

**Befund (Hypothese, Training, kein Testergebnis)**
- Der beste feste Start ist **3 Uhr, in jeder Saison und an jedem Wochentag**. Mittel im Training: 3 Uhr 70,8 €/MWh gegen 22 Uhr 91,4 €/MWh.
- Damit ist **D_saison = D**: Das Merkmal Saison verbessert die feste Regel um 0 €. Im Frühling liegt 2 Uhr nur 0,08 €/MWh hinter 3 Uhr.
- Für K3 Stufe 5 („Merkmal verbessert das Ergebnis messbar“) taugt der saisonale Block deshalb nicht. Das ist ein negatives Ergebnis und wird so berichtet.

**Verworfen**
- Breite Matrix mit einer Spalte je Uhrzeit (verliert den doppelten 2-Uhr-Block).
- Eigene Nachtlogik ohne Abgleich mit R2 (zwei Definitionen derselben Nacht könnten auseinanderlaufen; jetzt prüft ein Test, dass beide gleich sind).

**Drei Prüferfragen**
1. *„Warum wählt der saisonale Block überall 3 Uhr, und ist das Merkmal dann nutzlos?“* Das Preistal der Nacht liegt in jeder Saison zwischen 2 und 5 Uhr (Wind und niedrige Nachfrage). Eine feste Regel kann daraus nichts Saisonales gewinnen; Wert kann nur eine Regel haben, die sich an die einzelne Woche anpasst (B). Das negative Ergebnis zeigt, dass die einfache Regel reicht, solange B sie nicht schlägt (H0b).
2. *„Woher wissen Sie, dass Ihre Nächte richtig geschnitten sind?“* Test gegen die R2-Funktion: gleiche 1 764 Nächte, gleicher Preis des Status quo, gleicher billigster Block, Abweichung < 10⁻⁹.
3. *„Die Matrix enthält Testpreise. Ist das kein Look-ahead?“* Nein: Die Matrix dient nur zum Bewerten mit echten Preisen und, auf Trainingsnächte beschränkt, zum Lernen von D. B baut jeden Freitag eine eigene Matrix nur aus `w.historie` (Phase 2).

## Phase 2 · R3 (Susan): Strategien auf dem Training, eingefroren

**Was gebaut wurde**
- `src/04_strategien.py`: Jeden Freitag 08:00 plant jede Regel die 7 Nächte Mo–So der Folgewoche. Danach wird mit den echten Preisen nachgerechnet (Backtest, rollierender Ursprung).
  - **A** immer 22–24 Uhr. **D** fester Start aus dem Training (3 Uhr). **D_saison** je Saison (überall 3 Uhr, E-046).
  - **B** je Wochentag der Median der letzten 4 bekannten gleichen Nächte, dann der billigste Start.
  - **B_ohne_wochentag** Median der letzten 28 Nächte, ein Start für die Woche (nur für den K3-Vergleich).
  - **C** Oracle: billigster Block mit echten Preisen.
- Ausgaben: `ergebnisse/backtest_naechte.csv` (je Nacht und Strategie: Start, Preis, Kosten, Sonntags- und Feiertagsstunden für R4) und `ergebnisse/backtest_wochen.csv` (Stromkosten je Woche).
- `tests/test_strategien.py`: 7 Tests, u. a. „B sieht die Zielwoche nicht“ (alle Preise ab Samstag verfälscht, der Plan bleibt gleich) und eine Woche mit Zeitumstellung.

**Warum so**
- *B nur aus `w.historie`:* Der Datenzugriff von R2 bricht ab, sobald eine Stunde nach Freitag 24 Uhr hineinrutscht.
- *5 Wochen Historie für „letzte 4 gleiche Nächte“:* Die letzte Freitagnacht endet am Samstag und ist am Freitagmorgen noch nicht komplett bekannt; mit 4 Wochen hätte B für Freitag nur 3 Nächte.
- *Kalendertage statt Stunden:* „Freitag + 72 Stunden“ landet bei Zeitumstellung auf Sonntag 23 Uhr. Dieser Fehler trat beim ersten Lauf auf (eine Nacht doppelt), die Prüfung „Oracle nie teurer“ hat ihn gefunden; jetzt eigene Funktion `naechte_der_woche` mit Test.

**Befund Training 2023–2024 (104 Wochen, nur Strom, Faktor 1,0; Hypothese, kein Testergebnis)**

| Strategie | Ersparnis gegenüber A | Anteil am Oracle |
| --- | --- | --- |
| D (fest 3 Uhr) | 1 162 €/Woche | 93,4 % |
| D_saison | 1 162 €/Woche | 93,4 % |
| B (Prognose) | 1 132 €/Woche | 91,0 % |
| B ohne Wochentag | 1 139 €/Woche | 91,6 % |
| C (Oracle) | 1 244 €/Woche | 100 % |

- Die feste Regel „3 Uhr“ holt im Training schon 93 % des Werts. B ist **schlechter** als D. D ist hier allerdings im Training gelernt und deshalb geschönt; ehrlich ist erst der Test (Phase 3).
- Beide Kalendermerkmale bringen nichts: Saison 0 €, gleicher Wochentag −7 €/Woche. Für K3 ist das ein negatives Ergebnis.
- Nachgerechnet von Hand: Woche ab 04.03.2024 direkt aus den Stundenpreisen, A 3 682,24 €, D 3 199,52 €, C 3 163,32 €, auf den Cent gleich.

**Verworfen**
- B mit dem Mittel statt dem Median (einzelne Preisspitzen in den letzten 4 Wochen würden den Plan verschieben).
- Eine Suche nach weiteren Merkmalen, bis eines wirkt (p-Hacking; nur die vorab benannten Vergleiche).

**Drei Prüferfragen**
1. *„Woher wissen Sie, dass B nicht in die Zukunft schaut?“* Test `test_b_sieht_die_zielwoche_nicht`: Alle Preise ab Samstag werden verfälscht, der Plan bleibt gleich. Zusätzlich bricht `datenzugriff` mit `LookAheadFehler` ab.
2. *„Warum ist die Prognose schlechter als eine feste Uhrzeit?“* Das Preistal liegt meist zwischen 2 und 5 Uhr; fest 3 Uhr (3–5 Uhr) trifft es im Mittel am besten. B reagiert auf Zufallsschwankungen der letzten 4 Wochen und verlässt 3 Uhr in rund der Hälfte der Nächte, ohne dass das im Mittel etwas bringt.
3. *„D wurde auf denselben Daten gelernt, auf denen Sie es bewerten. Ist das fair?“* Im Training nicht, deshalb zählt nur der Test 2025–2026 (eingefroren, Phase 3).

## Phase 3 · R3 (Susan): Testzeiträume, Statistik, Fehleranalyse

**Was gebaut wurde**
- `src/04_strategien.py` rechnet jetzt alle vier Zeiträume. Die Regeln sind seit `1d59427` unverändert (Beleg: `git diff 1d59427 -- src/04_strategien.py` ändert nur `main` und fügt die Statistik an; die Trainingszahlen sind bitgleich).
- Statistik: gepaarter t-Test einseitig, Schwelle 0,05/3 ≈ 0,0167, nur in der gemeinsamen Teststichprobe (Test 1 + Test 2, 89 Wochen). Vorher Shapiro-Wilk, als Gegenprobe Wilcoxon, als Grenze ein Block-Bootstrap-Intervall.
- Ausgaben: `ergebnisse/ki_strategien.csv`, `ergebnisse/hypothesentests.csv`, `ergebnisse/fehleranalyse_b.csv`.

**Ergebnisse (Test 2025–2026, 89 Wochen, nur Strom)**

| Strategie | Ersparnis gegenüber 22–24 Uhr | 95-%-KI | €/Jahr (Faktor 1,0 / 0,3) | Anteil am Oracle |
| --- | --- | --- | --- | --- |
| D fest 3 Uhr | 1 197 €/Woche | 1 059 bis 1 336 | 62 300 / 18 700 | 93,0 % |
| B Prognose | 1 179 €/Woche | 1 040 bis 1 318 | 61 300 / 18 400 | 91,6 % |
| C Oracle | 1 288 €/Woche | 1 151 bis 1 424 | 67 000 / 20 100 | 100 % |

- **H0b wird nicht verworfen.** B spart im Mittel 18 € pro Woche **weniger** als D (p = 0,99; Wilcoxon gleich, also robust). Es braucht keine Prognose; die feste Regel „3 Uhr“ ist mindestens so gut. In Test 1, Test 2 und 2022 einzeln liegt B ebenfalls unter D.
- **H0c, Kipppunkt:** Die Tagesplanung (C) holt 109 €/Woche mehr als B, untere Schranke m\* = 91 €/Woche. Tagesplanung lohnt sich gegenüber B nur, wenn kurzfristiges Personal weniger als rund 91 € pro Woche mehr kostet, also etwa 2,20 € pro Personalstunde (91 € ÷ 7 Nächte ÷ 3 Personen ÷ 2 h; Umrechnung macht R4). Gegenüber D ist der Abstand noch kleiner (C − D ≈ 91 €/Woche).
- **H0a** braucht die Personalkosten und folgt in Phase 4 (R4).
- **Stresstest 2022:** Ersparnis D 2 943 €/Woche, Anteil 93 %. Das Ergebnis kippt nicht; B liegt auch hier unter D.
- **K3:** Saison 0 €, gleicher Wochentag −14 €/Woche (Intervall schließt 0 ein). Kein Merkmal verbessert die Regel.
- **Grenze t-Test:** Die Bootstrap-Intervalle sind rund 50 % breiter als die t-Intervalle (D: 984 bis 1 405 statt 1 059 bis 1 336). Benachbarte Wochen hängen zusammen; die Testentscheidungen ändern sich dadurch nicht. Shapiro-Wilk lehnt die Normalverteilung ab (p < 0,001), der Wilcoxon kommt aber zum selben Ergebnis.
- **Fehleranalyse B:** B trifft den billigsten Block nur in 24–50 % der Nächte. Am meisten verliert B gegenüber D in den Montagnächten (rund 9–11 € pro Nacht) und im Frühling 2026.

**Code-Fehler nach dem Einfrieren (P-012):** Im Stresstest war die Historie der ersten Woche leer. `blockkosten` gab dann eine Tabelle ohne Spalten zurück und B stürzte ab, statt „kein Plan“ zu melden. Behoben in `src/03_merkmale.py` (feste Spalten), Test ergänzt; an keiner Regel geändert. Für B fallen in 2022 dadurch 5 statt 4 Wochen weg: Die vierte Freitagnacht ist erst in Woche 6 bekannt.

**Drei Prüferfragen**
1. *„Sie haben 89 Wochen und einen t-Test. Sind die Wochen unabhängig?“* Nicht ganz, Wochen derselben Saison hängen zusammen. Deshalb zusätzlich das Block-Bootstrap-Intervall: rund 50 % breiter, gleiche Aussage.
2. *„Warum testen Sie Test 1 und Test 2 nicht getrennt?“* Sonst wären es sechs statt drei Tests mit schärferer Bonferroni-Schwelle. Die getrennten Intervalle zeigen trotzdem, dass das Ergebnis nach 10/2025 nicht kippt.
3. *„Die Daten sind nicht normalverteilt. Gilt der t-Test dann?“* Bei 89 Wochen trägt der zentrale Grenzwertsatz; der Wilcoxon, der keine Normalverteilung braucht, kommt zum selben Ergebnis.

## Phase 4 · R4 (Caro): Personalkosten, H0a, Break-even, Kipppunkte, C&E, Ishikawa, Empfehlung

**Was gebaut wurde**
- `src/05_bewertung.py`: Personalkosten je Reinigung = 3 Personen × 35 €/h × Summe über die 2 Stunden von (1 + Zuschlag). Zuschlag je Stunde: Nacht 25 % (22–06 Uhr), Wochenende 50 % (Sa und So), Feiertag 100 %, nur der höchste; maßgeblich ist der Kalendertag der Stunde (`docs/annahmen.md` Nr. 11–15).
- Ergebnisse: `netto_tests.csv` (H0a und Netto je Strategie), `wirtschaftlichkeit.csv` (Break-even-Kurve, Spalte `break_even` in Monaten), `kipppunkte.csv`, `kpi_rollierend.csv` (Kennzahl je Woche), `ce_matrix.csv`; dazu `docs/ishikawa.md`.
- `tests/test_bewertung.py`: 5 Tests, u. a. eine Freitagnacht von Hand (A 262,50 €, D 315,00 €, weil 3 Uhr schon Samstag ist).

**Warum so**
- *Nur die Differenz zu A zählt:* Gereinigt wird sowieso, nachts, mit denselben Leuten. Kosten entstehen nur, wenn die verschobene Stunde einen anderen Zuschlag hat.
- *Kalendertag der Stunde:* Die Freitagnacht wird ab Mitternacht zum Samstag (teurer), die Sonntagnacht zum Montag (billiger). Über die Woche gleicht sich das fast aus.
- *Break-even als Kurve:* Für Umstellungskosten gibt es keine Quelle (E-044). Die Kurve zeigt für 0 bis 100 000 € einmalig, nach wie vielen Monaten sie wieder drin sind.

**Ergebnisse (Test gesamt, 89 Wochen)**

| | Faktor 1,0 (Band) | Faktor 0,3 (proportional) |
| --- | --- | --- |
| Stromersparnis D | 1 197 €/Woche | 359 €/Woche |
| Personal-Mehrkosten D | −2 €/Woche | −2 €/Woche |
| **Netto D** | **1 199 €/Woche, 62 400 €/Jahr** (KI 1 061–1 337) | **361 €/Woche, 18 800 €/Jahr** (KI 319–403) |
| Break-even bei 25 000 € einmalig | 4,8 Monate (vorsichtig 5,4) | 16 Monate (vorsichtig 18) |

- **H0a wird verworfen** (p < 0,001, Wilcoxon gleich, robust): Die feste Regel 3 Uhr spart auch nach Zuschlägen. Gleiches Bild in Test 1, Test 2 und 2022 (netto 2 940 €/Woche). In keiner einzigen der 244 Wochen 2022–2026 wäre D teurer gewesen als 22–24 Uhr.
- **Die Zuschläge spielen kaum eine Rolle**, weil das ganze Fenster ohnehin Nacht ist.

**Kipppunkte (D, Test gesamt)**

| Annahme | kippt bei (Faktor 1,0) | kippt bei (Faktor 0,3) |
| --- | --- | --- |
| **Zusätzlich bezahlte Stunden je Person und Nacht** (Warten nach Produktionsende oder zweite Anfahrt) | **1,3 h** | **0,4 h** |
| Aufpreis je Personalstunde für die Verschiebung | 28,50 € | 8,60 € |
| Tagesplanung statt Wochenplan (H0c): Aufpreis kurzfristiges Personal | 2,16 € je h | 0,65 € je h |
| Vertragsfaktor, Preisspreizung | kein Kipppunkt (Personal-Mehrkosten ≈ 0) | ebenso |

Der eigentliche Hebel ist also **die Organisation des Personals**: Wartet die Reinigungsmannschaft nach 22 Uhr bis 3 Uhr und wird dafür bezahlt, frisst schon eine Stunde pro Person die Ersparnis. Mit einer Stunde Wartezeit wäre die Verschiebung in 43 von 196 rollierenden Quartalen ein Verlust gewesen.

**C&E-Matrix (Gewichte: Vorschlag, Caro bestätigt)**
Kriterien: Steuerbarkeit im Wochenplan (Gewicht 5), kein Produktrisiko (5), personalgebunden (4), verschiebbare Leistung in MW (3), Datenlage (2); Skala 0/1/3/9. Ergebnis: **Reinigung 153 Punkte (62 %)**, Produktion 51, Kälte 43. Die Reinigung ist der einzige Prozess, der im Wochenplan steuerbar ist, kein Produktrisiko trägt und vom Schichtplan abhängt; die Produktion hat zwar die meiste Leistung, scheidet aber an Rohmilch und fester Betriebszeit aus.

**Empfehlung an die Werksleitung (Entwurf für R1)**
1. **Was:** Reinigung fest um **3 Uhr** statt 22 Uhr einplanen (Regel D). Keine Preisprognose, keine wöchentliche Neuberechnung: Die bringt nichts Messbares (H0b, FS2).
2. **Bedingung:** Nur ohne bezahlte Wartezeit, also eigene Reinigungsschicht (Zeitarbeit nur für 03–05 Uhr) statt Warten nach Produktionsende. Sonst kippt es ab 1,3 h (Band) bzw. 0,4 h (proportional) pro Person und Nacht.
3. **Wer entscheidet:** Werksleitung (Schichtplan) mit dem zentralen Einkauf (Vertrag), K-008 P16.
4. **Kennzahl:** Netto-Ersparnis gegenüber 22–24 Uhr je Woche, rollierend über 13 Wochen, aus Stromrechnung (Day-Ahead-Preise 22–24 gegen 3–5 Uhr × 8 MWh) minus tatsächliche Personal-Mehrkosten laut Abrechnung (`kpi_rollierend.csv`).
5. **Nachsteuern:** einmal im Jahr die beste feste Uhrzeit mit den Preisen des Vorjahres neu bestimmen (wandert das Preistal, z. B. durch mehr Solar und Batterien).
6. **Rücknahmeregel:** Fällt die rollierende 13-Wochen-Kennzahl unter null, zurück auf 22 Uhr und Ursache klären. Mit den Kosten aus `params.yaml` wäre das 2022–2026 nie passiert (Minimum +626 €/Woche).

**Drei Prüferfragen**
1. *„Warum kosten die Zuschläge fast nichts?“* Weil 22–06 Uhr komplett Nacht ist (A-017). Unterschiede entstehen nur am Wochenende und an Feiertagen, und die gleichen sich über die Woche aus (Freitagnacht teurer, Sonntagnacht billiger).
2. *„Ihre Rücknahmeregel hat nie ausgelöst. Ist sie dann sinnlos?“* Mit unseren Kosten ja, weil die Ersparnis robust ist. Die Regel schützt gegen das, was wir nicht kennen: bezahlte Wartezeit, ein flacheres Preistal. Mit einer Stunde Wartezeit hätte sie in 43 von 196 Quartalen ausgelöst.
3. *„Wie sicher ist die C&E-Bewertung?“* Es ist eine Teamannahme mit Begründung je Zelle. Selbst wenn man die Leistung (MW) am höchsten gewichtet, bleibt die Produktion wegen Rohmilch (P9) und fester Betriebszeit unverschiebbar.

## Phase 5 · R2 (Max): Sensitivitätsrechnung

**Was gebaut wurde**
- `src/06_sensitivitaet.py` (läuft als letzter Schritt in `run_all.py`): zwölf Varianten aus `r2/docs/sensitivitaet_plan.md` gegen die Basis, je Strategie und Testzeitraum. Ergebnis: `r2/ergebnisse/sensitivitaet.csv`, Tabelle mit Lesart im Plan.
- `tests/test_sensitivitaet.py`: 5 Tests (Basis = Ergebnis R4, Menge wirkt linear und lässt den Anteil gleich, jede Variante ändert wirklich ihren Schalter, V4, Zuordnung auffälliger Stunden zur Nacht).

**Warum so**
- *Schwelle vorher festgelegt* (5 %, E-044) und *alle Varianten berichtet*, auch die ohne Wirkung: sonst könnte man nur passende Varianten zeigen.
- *Nachrechnen statt alles neu laufen lassen:* Die Regeln schauen nicht auf Menge, Personal, Feiertage oder Vertrag. Diese Größen wirken nur in der Bewertung. Nur die Blocklänge (V7) ändert die Wahl und läuft deshalb mit R3s eingefrorenen Regeln neu.

**Ergebnis**
- **Keine Testentscheidung kippt** in irgendeiner Variante (H0a verworfen, H0b nicht verworfen). Der Anteil am Oracle bleibt bei 92–95 %.
- **Die Euro-Beträge schwanken stark:** Menge (4 bis 16 MWh) −50 % bis +100 %, Vertrag 30 % −70 %, nur Mo–Fr −36 %, Blocklänge 1 bis 4 h +34 % bis −40 %. Deshalb im Bericht immer als Bandbreite.
- **Datenqualität (K2):** Ohne die 174 Nächte mit auffälligen Preisen sinkt die Ersparnis um 11 %, der Anteil bleibt gleich. Die Aussage hängt nicht an wenigen Extremstunden.
- Feiertagskalender und addierte Zuschläge wirken nicht (sie treffen A und D gleich).

**Verworfen**
- Abgleich mit ENTSO-E als „zweite Quelle“ (keine unabhängige Quelle, nur Übertragungsfehler; der Check innerhalb von SMARD liegt schon vor, E-028).
- `cleaning` und `02_synthetisch` für jede Variante neu laufen lassen (gleiches Ergebnis, viel mehr Code und Laufzeit).

**Drei Prüferfragen**
1. *„Woher wissen Sie, dass die Daten gut genug sind?“* Die Entscheidung bleibt in allen zwölf Varianten gleich, auch ohne die auffälligen Preise (−11 % in €, Anteil gleich). Dazu Lücken null, Stundenmittel gegen SMARD-Stundenwert höchstens 0,005 €/MWh Abweichung (E-028).
2. *„Warum ist ‚relevant‘ bei V6 und V8 ja, wenn das doch nur linear ist?“* Weil die Schwelle für die Euro-Beträge gilt. Dass es linear ist, prüft ein Test; für die Entscheidung zählt, dass die Tests nicht kippen.
3. *„Welche Annahme ist am kritischsten?“* Für die Euro-Beträge der Vertrag (Faktor 0,3) und die Menge (8 oder 16 MWh). Für die Entscheidung keine aus dieser Liste, sondern die bezahlte Wartezeit des Personals (Kipppunkt R4: 1,3 h bzw. 0,4 h).
