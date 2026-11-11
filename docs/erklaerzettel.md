# Erklärzettel je Phase (für die Owner, zur Vorbereitung der Verteidigung)

<!-- KI: Claude, Zweck: Erklärzettel nach E-045, je Phase höchstens eine Seite, geprüft von den jeweiligen Ownern -->

Eine Phase = ein Abschnitt. Der Owner liest ihn, prüft ihn am Code nach und bestätigt im Tagebuch (E-045).

## Phase 1 · R3 (Susan): Hypothesen und Merkmale

**Was gebaut wurde**
- `docs/hypothesen.md` (Commit `7a63c15`): H0a–H0c, einseitig, α = 0,05/3, Haupttest Block-Bootstrap, t-Test und Wilcoxon als Robustheit. Festgelegt, bevor irgendein Testzeitraum gerechnet wurde.
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
