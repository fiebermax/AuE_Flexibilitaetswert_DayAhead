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
2. *„Warum ist die Prognose schlechter als eine feste Uhrzeit?“* Das Preistal liegt fast immer bei 2–4 Uhr. B reagiert auf Zufallsschwankungen der letzten 4 Wochen und verlässt 3 Uhr in rund der Hälfte der Nächte, ohne dass das im Mittel etwas bringt.
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
