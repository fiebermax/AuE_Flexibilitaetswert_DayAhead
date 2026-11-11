# Hypothesen und Entscheidungsregeln (vor jeder Auswertung fixiert)

<!-- KI: Claude, Zweck: Präregistrierung der Tests nach E-042, geprüft von Susan (R3) und Caro (R4) -->

Owner: R3 (Susan), H0a und die Kostenseite von H0c mit R4 (Caro). Festgelegt am 11.11.2026, **bevor** ein Testzeitraum ausgewertet wurde (E-042). Jede spätere Änderung braucht einen eigenen Commit und einen E-Eintrag, der sagt, ob die Testdaten zu diesem Zeitpunkt schon angesehen waren.

## Gegenstand und Einheit

- Nur die Reinigung (CIP): 8 MWh pro Nacht als 2-h-Block im Fenster 22–06 Uhr (E-043).
- **Beobachtungseinheit: eine Planungswoche** (Mo–So, 7 Nächte inklusive der Sonntagsnacht bis Montag 06:00, E-044). Grund: Die Entscheidung fällt einmal pro Woche am Freitag; Nächte derselben Woche hängen über denselben Plan zusammen.
- **Ersparnis** einer Strategie X in € pro Woche = Stromkosten A − Stromkosten X, mit 8 MWh × mittlerer Preis des gewählten Blocks. Basis: jede verschobene MWh läuft über die Börse (Faktor 1,0, Annahme A3 „Band“); Untergrenze Faktor 0,3 („proportional“). Der Faktor skaliert alle Ersparnisse gleich, die Testentscheidungen sind deshalb in beiden Fällen dieselben; die Euro-Beträge werden für beide ausgewiesen.
- Strategien: A Status quo 22–24 Uhr, D fester Block aus dem Training, D_saison ein Block je Saison, B Prognose aus den letzten 4 Wochen (keine Regressionsvariante B′, E-047), C Oracle (= Tagesplanung, weil die Preise einer Nacht am Vortag 12:45 vollständig bekannt sind).

## Stichproben

| Zweck | Zeitraum | Wochen (ca.) | Rolle |
| --- | --- | --- | --- |
| Entwickeln, Lernen | Training 2023–2024 | 104 | darf beliebig oft angesehen werden |
| **Konfirmatorischer Test** | **Test 1 + Test 2 gemeinsam** (01/2025–09/2026) | 89 | einzige Stichprobe mit Testentscheidung |
| Gegenprobe Strukturbruch | Test 1 und Test 2 einzeln | 38 / 51 | nur Konfidenzintervalle, keine Testentscheidung |
| Stresstest | 2022 | 51 (B: 47, E-044) | nur Konfidenzintervalle, keine Testentscheidung |

Warum gemeinsam: Viertelstunden sind Nichtziel (E-043), beide Zeiträume liefern Stundenpreise. Getrennt getestet wären es sechs Tests statt drei, mit entsprechend schärferer Bonferroni-Schwelle und weniger Wochen je Test. Die getrennten Intervalle zeigen trotzdem, ob das Ergebnis nach 10/2025 kippt (K6).

## Die drei Nullhypothesen

Signifikanzniveau je Test: **α = 0,05 / 3 ≈ 0,0167** (Bonferroni, `statistik` in `params.yaml`). Alle Tests einseitig.

| | H0 | H1 | Differenz je Woche *d* | Wer rechnet |
| --- | --- | --- | --- | --- |
| **H0a** | Die Ersparnis von D gegenüber A nach Personalkosten ist ≤ 0 | > 0 | (Strom A − Strom D) − (Personal D − Personal A) | R3 Strom, R4 Personal |
| **H0b** | Die Ersparnis von B ist ≤ der Ersparnis von D | B spart mehr als D | Strom D − Strom B | R3 |
| **H0c** | (Ersparnis C − Ersparnis B) − Mehrkosten Tagesplanung ≤ 0 | > 0 | Strom B − Strom C − *m* | R3 Strom, R4 *m* |

- **H0a, „nach Kosten“:** Personalkosten mit Nacht-, Sonntags- und Feiertagszuschlag nach A-017 (22–06 Uhr Nacht, Kalendertag der Stunde, nur der höchste Zuschlag). Umstellungskosten sind einmalig bzw. jährlich und gehen nicht in den Wochentest ein; sie bewertet R4 als Break-even-Kurve (E-044).
- **H0b** vergleicht nur Stromkosten: Beide Strategien liegen komplett in der Nacht, Personal und Nachtzuschlag sind gleich; Unterschiede entstehen nur über Sonntags- und Feiertagsstunden, die R4 als Netto-Variante ausweist. Das ist die Kernfrage K4: Braucht es eine Prognose?
- **H0c** ist ein **Kipppunkt**, kein Ja/Nein: *m* (Mehrkosten pro Woche für kurzfristig gebuchtes Personal bei Tagesplanung) ist unbekannt. Da C nie teurer ist als B, wäre der Test für *m* = 0 trivial. Berichtet wird deshalb *m\** = untere einseitige (1 − α/3)-Schranke des t-Intervalls für das Mittel von (Strom B − Strom C): Für jeden Aufpreis *m* < *m\** wird H0c verworfen, Tagesplanung lohnt sich dann. R4 rechnet *m\** in € pro Personalstunde um (geteilt durch 7 Nächte × `kosten.mitarbeiter` × `last.blocklaenge_h`).

## Entscheidungsregel (für alle drei gleich)

Geändert am 11.11.2026 (E-047), vor jeder Auswertung: Haupttest ist der t-Test, keine Regression.

1. **Haupttest: gepaarter t-Test, einseitig**, auf den Wochendifferenzen *d* (je Woche Strategie gegen Vergleichsstrategie). H0 wird verworfen, wenn **p < α/3 ≈ 0,0167**.
2. **Voraussetzung prüfen:** Shapiro-Wilk auf *d* wird vorher berichtet. Bei rund 89 Wochen trägt der t-Test auch bei leichter Abweichung von der Normalverteilung (zentraler Grenzwertsatz). Als Gegenprobe läuft der Wilcoxon-Vorzeichen-Rang-Test mit derselben Schwelle. Widersprechen sich beide, heißt das Ergebnis „nicht robust“ und wird so berichtet.
3. **Effektgröße immer mit:** Mittel in €/Woche und €/Jahr mit zweiseitigem 95-%-Konfidenzintervall, Anteil am Oracle = Ersparnis X ÷ Ersparnis C. Das Intervall zusätzlich per Block-Bootstrap (4 Wochen, 5 000 Wiederholungen, Seed 42), weil Wochen derselben Saison zusammenhängen: Ist das Bootstrap-Intervall deutlich breiter als das des t-Tests, wird das als Grenze des t-Tests berichtet.
4. **Signifikanz ist nicht Relevanz:** Ob eine signifikante Ersparnis sich lohnt, entscheidet R4 gegen die Umstellungskosten (Break-even).
5. **H0c als Kipppunkt:** *m\** = untere einseitige (1 − α/3)-Schranke des t-Intervalls für das Mittel von (Strom B − Strom C).

## Explorativ, ohne Testentscheidung (keine weiteren p-Werte für Bonferroni)

- **K3-Nachweis:** D_saison gegen D und B gegen B_ohne_wochentag (Median der letzten 28 Nächte, ergänzt nach E-046, nur Trainingsdaten gesehen), je Mittel der Wochendifferenz mit 95-%-Intervall.
- **Fehleranalyse:** Bedauern (Regret) von B = Strom B − Strom C je Nacht, nach Saison, Wochentag und Periode.
- Faktor 0,3, Gegenprobe Test 1 / Test 2, Stresstest 2022.

## Ablauf, der die Regeln schützt

1. Diese Datei wird **separat committet**, bevor eine Strategie gerechnet wird.
2. Strategien werden nur auf dem Training entwickelt. Danach Commit „Strategien eingefroren“, Hash ins Tagebuch.
3. Erst dann laufen Test 1, Test 2 und 2022. Danach ändert sich keine Regel mehr; Fehler im Code werden behoben und offen dokumentiert, die Regel selbst bleibt.
4. Negative Ergebnisse werden gleichrangig berichtet.
