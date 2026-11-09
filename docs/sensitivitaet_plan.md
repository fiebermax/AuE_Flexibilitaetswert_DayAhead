# Plan: Sensitivitätsrechnung (K2 Stufe 5)

Stand 07.11.2026, Owner R2. Abgestimmt mit R3 über Tagebuch A-003 (Antwort offen). **Nur Plan, noch nicht gerechnet**: Es fehlt der Backtest von R3 (`src/04_strategien.py`).

## Ziel

K2 Stufe 5 verlangt, die Datenqualität aktiv zu prüfen statt sie nur zu beschreiben. Wir zeigen das mit einer Sensitivitätsrechnung: Wie stark hängt das Ergebnis von unseren Aufbereitungsentscheidungen und den synthetischen Annahmen ab? Zielaussage je Variante: „Die mittlere Ersparnis ändert sich um weniger als x %“ oder eben nicht.

**Kein Abgleich mit ENTSO-E.** SMARD bezieht die Day-Ahead-Preise von ENTSO-E. Ein Abgleich beider wäre keine unabhängige Quelle und würde nur Übertragungsfehler finden. Den Rechen- und Übertragungsfehler-Check innerhalb von SMARD haben wir schon: das eigene Stundenmittel gegen SMARDs Stundenwert, maximal 0,005 €/MWh Abweichung (`results/tables/datenqualitaet.csv`).

## Vorab festlegen (vor dem ersten Rechenlauf, mit Datum ins Tagebuch)

1. **Basis** ist der Stand in `params.yaml` zum Zeitpunkt des Eintrags.
2. **Kennzahl:** mittlere Netto-Ersparnis gegenüber A in €/Woche, je Strategie und Testperiode, dazu der Anteil am Oracle-Wert C.
3. **Schwelle:** Eine Variante gilt als relevant, wenn sich die mittlere Ersparnis um mehr als 5 % ändert **oder** sich eine Testentscheidung zu H0a, H0b oder H0c umkehrt. *Die Schwelle ist ein Vorschlag, das Team muss sie festlegen.*
4. Alle Varianten werden berichtet, auch die ohne Wirkung. Das schützt gegen den Vorwurf, nur passende Varianten gezeigt zu haben.

Die Varianten sind keine neuen Hypothesentests. Es entstehen keine zusätzlichen p-Werte, die Bonferroni-Korrektur bleibt bei drei Tests.

## Varianten

| ID | Was | Basis | Variante(n) | Schalter in `params.yaml` | Betroffen | Erwartung (Annahme) |
| --- | --- | --- | --- | --- | --- | --- |
| V1 | Zeitumstellung Oktober | doppelte Stunde gemittelt | erste Stunde · zweite Stunde | `daten.zeitumstellung_oktober: mittel \| erste \| zweite` | `02_aufbereitung.zu_ortszeit` | **im Basisszenario 0**: Umstellung immer sonntags, Last 0 (Tagebuch E-018, Test). Nur bei Wochenendproduktion rechnen |
| V2 | Zeitumstellung März | 02:00 fehlt, Tag hat 23 h | fehlende Stunde mit Preis der Vorstunde gefüllt (nur als Sensitivität!) | `daten.zeitumstellung_maerz: fehlt \| vorstunde` | `02_aufbereitung.baue_tabelle` | **im Basisszenario 0**, wie V1 (E-018) |
| V3 | Feiertagskalender | ohne Mariä Himmelfahrt | mit Mariä Himmelfahrt (15.08.) | `last.feiertagsvariante_mariae_himmelfahrt` (**existiert schon**) | Preise (`werktag`) und Last zugleich; ein Test erzwingt Gleichlauf | klein: 1 Werktag pro Jahr weniger |
| V4 | Betriebsruhe 24./31.12. | Werktag | arbeitsfrei | `last.zusaetzlich_frei: ["12-24", "12-31"]` | `gemeinsam.werktage` | klein; **nur falls der Praxiskontakt das bestätigt** |
| V6 | Lastmenge (synthetisch) | 2,0 MWh/Werktag | 1,0 · 4,0 | `last.mwh_pro_werktag` | `02_synthetisch` | €/Woche skaliert linear, Anteil am Oracle bleibt gleich (rechnerisch, als Kontrolle) |
| V7 | Blocklänge (synthetisch) | 6 h | 4 h · 8 h | `last.blocklaenge_h` | R3 (Blockkosten-Matrix) | nicht trivial: kurze Blöcke treffen das Preistal besser |

V6 und V7 sind laut Kickoff Pflicht für K2 Stufe 5: Synthetische Daten lassen sich nicht gegen die Wirklichkeit prüfen, also prüfen wir, wie stark das Ergebnis von ihren Parametern abhängt.

## Gestrichen: V5 (15 min statt Stunde)

Nur Stundenpreise (Tagebuch E-021). Bei Blöcken zur vollen Stunde wären 15-min- und Stundenkosten ohnehin rechnerisch gleich; ein Unterschied entstünde erst bei Blockstarts in 15-min-Schritten, das ist für den Zeitrahmen zu aufwendig. Im Bericht als Grenze und Ausblick nennen.

## Technische Umsetzung

1. **Neue Schalter in `params.yaml`** (Standardwert = heutiges Verhalten, Ergebnis bleibt bit-gleich):
   ```yaml
   daten:
     zeitumstellung_oktober: "mittel"   # mittel | erste | zweite
     zeitumstellung_maerz: "fehlt"      # fehlt | vorstunde   (nur für Sensitivität)
   last:
     zusaetzlich_frei: []               # z. B. ["12-24", "12-31"], nach Praxisgespräch
   ```
2. **Variantenliste in `params.yaml`**, jede Variante überschreibt einzelne Schalter:
   ```yaml
   sensitivitaet:
     schwelle_pct: 5
     varianten:
       V1a: {daten.zeitumstellung_oktober: "erste"}
       V1b: {daten.zeitumstellung_oktober: "zweite"}
       V2:  {daten.zeitumstellung_maerz: "vorstunde"}
       V3:  {last.feiertagsvariante_mariae_himmelfahrt: true}
       V6a: {last.mwh_pro_werktag: 1.0}
       V6b: {last.mwh_pro_werktag: 4.0}
       V7a: {last.blocklaenge_h: 4}
       V7b: {last.blocklaenge_h: 8}
   ```
3. **Umbau der Schritte, damit Varianten nichts überschreiben:** `02_aufbereitung.main()` und `02_synthetisch.main()` bekommen die optionalen Argumente `params` und `ausgabe_ordner`. Ohne Argumente verhalten sie sich wie heute. Varianten schreiben nach `data/processed/sensitivitaet/<ID>/` (in `.gitignore`).
4. **Neues Skript `src/06_sensitivitaet.py` (R2):** je Variante Parameter kopieren, Schalter setzen, Schritte 02 und 02b ausführen, R3s Backtest aufrufen, Kennzahlen sammeln. Ausgabe `results/tables/sensitivitaet.csv` mit den Spalten `variante`, `schalter`, `wert`, `strategie`, `periode`, `mittel_eur_woche`, `delta_eur`, `delta_pct`, `anteil_oracle`, `h0_entscheidung_gleich`, `relevant`. Der Bootstrap braucht denselben Seed wie die Basis, damit Unterschiede nicht vom Zufall kommen.
5. **Absprache mit R3 (A-xxx, jetzt nötig):** Der Backtest muss als Funktion aufrufbar sein, z. B. `backtest(preise: DataFrame, last: DataFrame, params: dict) -> DataFrame`. Er darf selbst keine Dateien lesen, sonst kann `06_sensitivitaet.py` keine Varianten einspeisen.
6. **Tests:**
   - Die Basis-Variante reproduziert die Basis-Ergebnisse exakt.
   - Jede Variante ändert ihren Schalter tatsächlich, sonst wäre sie eine stille Nullvariante.
   - V6 skaliert die €/Woche linear und lässt den Anteil am Oracle gleich, als Plausibilitätskontrolle.
   - Zeitumstellungstage sind lastfrei (`test_zeitumstellung_nur_an_lastfreien_tagen`); schlägt der Test fehl, V1/V2 aktivieren.

## Zeitplan und Aufwand (Schätzung)

| Schritt | Wann | Aufwand |
| --- | --- | --- |
| Schwelle und Basis im Team festlegen, Tagebuch | vor 13.11. | 15 min |
| Absprache Backtest-Funktion mit R3 | sofort | 15 min |
| Schalter V1, V2, V4 in `02_aufbereitung` und `gemeinsam` | sobald Schwelle steht | 2 h inkl. Tests |
| `06_sensitivitaet.py` | sobald R3s Backtest als Funktion steht | 2–3 h |
| Lauf, Tabelle, ein Satz je Variante für Bericht Kap. 3 | Sa 14.11. | 1 h |

## Wo es belegt wird

Bericht Kapitel 3 (Datenqualität) mit der Sensitivitätstabelle, `results/tables/sensitivitaet.csv` mit Commit, Tagebucheintrag mit der vorab festgelegten Schwelle und Datum, Verteidigung R2.
