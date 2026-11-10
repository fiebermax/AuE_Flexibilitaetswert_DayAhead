# Plan: Sensitivitätsrechnung (K2 Stufe 5)

Stand 07.11.2026, aktualisiert 10.11.2026 auf den Reinigungsfall (E-033), Owner R2. Abgestimmt mit R3 über Tagebuch A-003 (Antwort offen). **Nur Plan, noch nicht gerechnet**: Es fehlt der Backtest von R3 (`src/04_strategien.py`).

## Ziel

K2 Stufe 5 verlangt, die Datenqualität aktiv zu prüfen statt sie nur zu beschreiben. Wir zeigen das mit einer Sensitivitätsrechnung: Wie stark hängt das Ergebnis von unseren Aufbereitungsentscheidungen und den synthetischen Annahmen ab? Zielaussage je Variante: „Die mittlere Ersparnis ändert sich um weniger als x %“ oder eben nicht.

**Kein Abgleich mit ENTSO-E.** SMARD bezieht die Day-Ahead-Preise von ENTSO-E. Ein Abgleich beider wäre keine unabhängige Quelle und würde nur Übertragungsfehler finden. Den Rechen- und Übertragungsfehler-Check innerhalb von SMARD haben wir schon: das eigene Stundenmittel gegen SMARDs Stundenwert, maximal 0,005 €/MWh Abweichung (`ergebnisse/datenqualitaet.csv`).

## Vorab festlegen (vor dem ersten Rechenlauf, mit Datum ins Tagebuch)

1. **Basis** ist der Stand in `params.yaml` zum Zeitpunkt des Eintrags.
2. **Kennzahl:** mittlere Netto-Ersparnis gegenüber A in €/Woche, je Strategie und Testperiode, dazu der Anteil am Oracle-Wert C.
3. **Schwelle:** Eine Variante gilt als relevant, wenn sich die mittlere Ersparnis um mehr als 5 % ändert **oder** sich eine Testentscheidung zu H0a, H0b oder H0c umkehrt. *Die Schwelle ist ein Vorschlag, das Team muss sie festlegen.*
4. Alle Varianten werden berichtet, auch die ohne Wirkung. Das schützt gegen den Vorwurf, nur passende Varianten gezeigt zu haben.

Die Varianten sind keine neuen Hypothesentests. Es entstehen keine zusätzlichen p-Werte, die Bonferroni-Korrektur bleibt bei drei Tests.

## Varianten

| ID | Was | Basis | Variante(n) | Schalter in `params.yaml` | Betroffen | Erwartung (Annahme) |
| --- | --- | --- | --- | --- | --- | --- |
| V1 | Zeitumstellung | — | **entfällt** | — | — | Mit `ts_utc` als Schlüssel wird nichts gemittelt oder aufgefüllt (E-026). Die Umstellung liegt im Reinigungsfenster 22–06 Uhr; gerechnet wird mit echten Stunden (7 bzw. 9 h je Nacht, E-036), keine Variante nötig |
| V2 | Auffällige Preise | alle Stunden | Auswertung ohne Stunden mit `flag_outlier` (Daten bleiben unverändert) | Filter in `06_sensitivitaet.py` | Auswertung | zeigt, ob das Ergebnis an wenigen Extremstunden hängt (E-025) |
| V3 | Feiertagskalender | ohne Mariä Himmelfahrt | mit Mariä Himmelfahrt (15.08.) | `last.feiertagsvariante_mariae_himmelfahrt` | nur Spalte `werktag` der Preise (Produktion läuft täglich) | voraussichtlich 0 für die Kosten; nur relevant für Strategien, die `werktag` nutzen |
| V4 | Produktionstage | täglich (Praxiskontakt) | Mo–Fr ohne Feiertage | `last.produktionstage` | `02_synthetisch` | zeigt, wie stark das Ergebnis an der Wochenendproduktion hängt |
| V6 | verschiebbare Menge (Reinigung) | 8,0 MWh/Tag (4 MW × 2 h) | 4,0 · 12,0 | `last.mwh_pro_tag` | `02_synthetisch` | €/Woche skaliert linear, Anteil am Oracle bleibt gleich (rechnerisch, als Kontrolle) |
| V7 | Dauer der Reinigung | 2 h | 1 h · 3 h · 4 h (Energie bleibt 8 MWh) | `last.blocklaenge_h` | R3 (Blockkosten-Matrix) | nicht trivial: kurze Blöcke treffen das Preistal besser |
| V8 | Bewertung der verschobenen Menge (Kipp-Annahme A3) | Band: 100 % zum Spotpreis | proportional: 30 % (`vertrag.spot_anteil`) | `vertrag.bewertung_verschiebung` | R3, R4 | Ersparnis in € sinkt auf 30 %; ob H0a kippt, hängt an den Personal- und Zuschlagskosten |
| V9 | Nachtstunden des Zuschlags | 23–06 Uhr | 22–06 Uhr | `kosten.nachtstunden` | R3, R4 | Status quo 22–24 Uhr hätte dann zwei statt einer zuschlagspflichtigen Stunde (offen, E-035) |

V6 und V7 sind laut Kickoff Pflicht für K2 Stufe 5: Synthetische Daten lassen sich nicht gegen die Wirklichkeit prüfen, also prüfen wir, wie stark das Ergebnis von ihren Parametern abhängt.

## Gestrichen: V5 (15 min statt Stunde)

Nur Stundenpreise (Tagebuch E-021). Bei Blöcken zur vollen Stunde wären 15-min- und Stundenkosten ohnehin rechnerisch gleich; ein Unterschied entstünde erst bei Blockstarts in 15-min-Schritten, das ist für den Zeitrahmen zu aufwendig. Im Bericht als Grenze und Ausblick nennen.

## Technische Umsetzung

1. **Neue Schalter in `params.yaml`** (Standardwert = heutiges Verhalten, Ergebnis bleibt bit-gleich):
   ```yaml
   daten:
   last:
     produktionstage: "taeglich"        # Variante V4: "Mo-Fr ohne Feiertage Bayern"
   ```
2. **Variantenliste in `params.yaml`**, jede Variante überschreibt einzelne Schalter:
   ```yaml
   sensitivitaet:
     schwelle_pct: 5
     varianten:
       V2:  {auswertung.ohne_flag_outlier: true}
       V3:  {last.feiertagsvariante_mariae_himmelfahrt: true}
       V4:  {last.produktionstage: "Mo-Fr ohne Feiertage Bayern"}
       V6a: {last.mwh_pro_tag: 4.0}
       V6b: {last.mwh_pro_tag: 12.0}
       V7a: {last.blocklaenge_h: 1}
       V7b: {last.blocklaenge_h: 3}
       V7c: {last.blocklaenge_h: 4}
       V8:  {vertrag.bewertung_verschiebung: "proportional"}
       V9:  {kosten.nachtstunden: [22, 23, 0, 1, 2, 3, 4, 5]}
   ```
3. **Umbau der Schritte, damit Varianten nichts überschreiben:** `cleaning.main()` und `02_synthetisch.main()` bekommen die optionalen Argumente `params` und `ausgabe_ordner`. Ohne Argumente verhalten sie sich wie heute. Varianten schreiben nach `data/sensitivitaet/<ID>/` (in `.gitignore`).
4. **Neues Skript `src/06_sensitivitaet.py` (R2):** je Variante Parameter kopieren, Schalter setzen, Schritte 02 und 02b ausführen, R3s Backtest aufrufen, Kennzahlen sammeln. Ausgabe `ergebnisse/sensitivitaet.csv` mit den Spalten `variante`, `schalter`, `wert`, `strategie`, `periode`, `mittel_eur_woche`, `delta_eur`, `delta_pct`, `anteil_oracle`, `h0_entscheidung_gleich`, `relevant`. Der Bootstrap braucht denselben Seed wie die Basis, damit Unterschiede nicht vom Zufall kommen.
5. **Absprache mit R3 (A-xxx, jetzt nötig):** Der Backtest muss als Funktion aufrufbar sein, z. B. `backtest(preise: DataFrame, last: DataFrame, params: dict) -> DataFrame`. Er darf selbst keine Dateien lesen, sonst kann `06_sensitivitaet.py` keine Varianten einspeisen.
6. **Tests:**
   - Die Basis-Variante reproduziert die Basis-Ergebnisse exakt.
   - Jede Variante ändert ihren Schalter tatsächlich, sonst wäre sie eine stille Nullvariante.
   - V6 skaliert die €/Woche linear und lässt den Anteil am Oracle gleich, als Plausibilitätskontrolle.
   - Umstellungsnächte werden mit echten Stunden gerechnet (`test_umstellungsnaechte_mit_echten_stunden`).

## Zeitplan und Aufwand (Schätzung)

| Schritt | Wann | Aufwand |
| --- | --- | --- |
| Schwelle und Basis im Team festlegen, Tagebuch | vor 13.11. | 15 min |
| Absprache Backtest-Funktion mit R3 | sofort | 15 min |
| Schalter V2 (Filter) in `06_sensitivitaet.py`; V4 existiert schon | sobald Schwelle steht | 1 h inkl. Tests |
| `06_sensitivitaet.py` | sobald R3s Backtest als Funktion steht | 2–3 h |
| Lauf, Tabelle, ein Satz je Variante für Bericht Kap. 3 | Sa 14.11. | 1 h |

## Wo es belegt wird

Bericht Kapitel 3 (Datenqualität) mit der Sensitivitätstabelle, `ergebnisse/sensitivitaet.csv` mit Commit, Tagebucheintrag mit der vorab festgelegten Schwelle und Datum, Verteidigung R2.
