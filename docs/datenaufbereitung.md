# Datenaufbereitung und Datenqualität (R2)

Stand 09.11.2026 · Owner R2 (Max) · Grundlage für Bericht Kapitel 3 (K2) und 4 (K3). Code: `src/01_download.py`, `src/02_aufbereitung.py`, `src/02_synthetisch.py`. Jede Entscheidung steht mit verworfener Alternative im Projekttagebuch (E-Nummer in Klammern).

> Begriffe aus dem Kursmaterial (Statistik-Grundlagenwerk, Rheinlack-Fallstudie) haben Vorrang. Vor dem Bericht prüfen, ob dort andere Bezeichnungen für Skalenniveaus, Ausreißer oder Datenqualität verwendet werden, und angleichen.

## 1. Vorgehen in einem Bild

```
SMARD (Rohdaten, JSON, 253 Wochen)
  │  Schritt 1: Erhebung       → unverändert speichern, Herkunft und Prüfsumme je Datei
  │  Schritt 2: Aufbereitung   → zusammenführen, Duplikate, Zeitzone, Zeitumstellung, Lücken, Kalender
  │  Schritt 3: Prüfung        → Plausibilität, Ausreißer markieren (nicht löschen), Qualitätskennzahlen
  ▼
preise_h.csv (42 355 Stunden)  +  last_synth.csv (synthetisch)  →  Backtest (R3)
```

Grundsatz: **Rohdaten bleiben unverändert; jede Veränderung geschieht im Code, ist begründet und nachvollziehbar.** Nichts wird von Hand bearbeitet (K3 Stufe 3).

## 2. Datenqualität nach Qualitätsdimensionen

Datenqualität wird nicht nur beschrieben, sondern je Dimension geprüft. Die Dimensionen folgen der verbreiteten Einteilung von Wang & Strong (1996).

| Dimension | Frage | Prüfung | Ergebnis (Abruf 07.11.2026) | Beleg |
| --- | --- | --- | --- | --- |
| **Herkunft / Integrität** | Stammen die Daten unverändert aus der Quelle? | SHA256-Prüfsumme je Rohdatei, Abrufzeitpunkt, URL | 253 Dateien, alle unverändert | `data/raw/smard/manifest.csv`, Test `test_rohdaten_unveraendert` (E-008, E-009) |
| **Vollständigkeit** | Fehlen Stunden? | Abgleich gegen das erwartete Stundenraster | 0 Lücken in 42 355 Stunden | `results/tables/datenqualitaet.csv`, Test `test_keine_luecken` (E-013) |
| **Eindeutigkeit** | Gibt es Stunden doppelt? | doppelte Zeitstempel zählen; widersprüchliche Werte → Abbruch | 0 Duplikate | Test `test_zeit_sortiert_eindeutig_volle_stunden` |
| **Konsistenz** | Passt die Struktur? | 24 Stunden je Tag (23 im März), volle Stunden, sortiert, Regime am 01.10.2025 | erfüllt | Tests `test_stunden_pro_tag`, `test_regime_am_wechsel` |
| **Plausibilität** | Liegen die Werte im möglichen Bereich? | Preisgrenzen der Day-Ahead-Auktion (−500 bis +4 000 €/MWh) | erfüllt; Minimum −500 (2023), Maximum 936 €/MWh (2024) | Test `test_preisbereich` |
| **Genauigkeit** | Wie genau sind die Werte? | Quelle und Rundung prüfen | Auktionsergebnisse, kein Mess- oder Schätzwert; auf 0,01 €/MWh gerundet. Ab 10/2025 Stundenwert = Mittel aus 4 Viertelstunden (SMARD) | E-012, E-021 |
| **Aktualität** | Wie aktuell, und ändern sich Werte nachträglich? | Datenstand in `params.yaml`; Erstellzeitpunkt je Datei | Datenstand 31.10.2026; nachträgliche Korrekturen durch eingefrorene Rohdaten abgefangen | `manifest.csv` (Spalte `smard_created_utc`) |
| **Ausreißer** | Gibt es auffällige Werte, und was bedeuten sie? | robuster z-Wert je Jahr × Monat × Stunde (Abschnitt 4) | 1 827 Stunden (4,3 %) markiert, keine gelöscht | `results/tables/ausreisser.csv`, Spalte `auffaellig` (E-025) |

**Unabhängige zweite Quelle:** bewusst nicht. SMARD bezieht die Day-Ahead-Preise von ENTSO-E; ein Abgleich wäre keine unabhängige Prüfung (E-015). Die aktive Prüfung der Datenqualität für K2 Stufe 5 erfolgt über die Sensitivitätsrechnung (`docs/sensitivitaet_plan.md`).

## 3. Aufbereitungsschritte

| # | Schritt | Methode | Begründung | Verworfene Alternative |
| --- | --- | --- | --- | --- |
| 1 | Erhebung | automatischer Abruf der SMARD-Wochendateien, Ablage als Original-Bytes, Cache | reproduzierbar, offline lauffähig, nachträgliche SMARD-Korrekturen verändern unsere Zahlen nicht | manueller CSV-Export von der Webseite (nicht nachvollziehbar) |
| 2 | Zusammenführen | alle Wochen untereinander, doppelte Zeitstempel prüfen | Wochendateien überlappen nicht, sollen es auch nicht; widersprüchliche Duplikate würden den Lauf stoppen | stillschweigend den ersten oder letzten Wert nehmen |
| 3 | Zeitzone | UTC → Europe/Berlin | Schichten richten sich nach der Ortszeit im Werk | in UTC rechnen (Block verschiebt sich halbjährlich um 1 h) |
| 4 | Zeitumstellung Oktober | doppelte Stunde 02:00 gemittelt | ein Wert je Uhrzeit für die Blockkosten | eine der beiden Stunden nehmen (willkürlich) |
| 5 | Zeitumstellung März | fehlende Stunde 02:00 nicht aufgefüllt (Tag mit 23 Zeilen) | keine erfundenen Werte | Interpolation (erfindet einen Preis) |
| 6 | Lücken | erwartetes Stundenraster, fehlende Werte bleiben leer und lösen einen Test aus | Lücken müssen sichtbar sein, nicht still gefüllt | Zeilen löschen oder interpolieren |
| 7 | Kalender | `werktag` = Mo–Fr ohne gesetzliche Feiertage in Bayern (Paket `holidays`), Mariä Himmelfahrt schaltbar | Auswertung Werktag/Wochenende; Feiertage beeinflussen Last und Preise | Feiertagsliste von Hand |
| 8 | Regime | `regime` = `stunde` bis 30.09.2025, `viertel` ab 01.10.2025 | Vergleich vor/nach Umstellung des Börsenhandels (H0c) | — |
| 9 | Ausreißer | markieren mit robustem z-Wert, nicht löschen | siehe Abschnitt 4 | löschen oder kappen |

**Wirkung der Zeitumstellung auf das Ergebnis:** keine. Sie betrifft 02:00–03:00 Uhr, produziert wird 06–22 Uhr (E-024, Test `test_zeitumstellung_liegt_ausserhalb_der_betriebszeit`).

## 4. Ausreißer: markieren, erklären, nicht löschen

**Methode.** Für jede Stunde wird ein *modifizierter z-Wert* berechnet (Iglewicz & Hoaglin 1993):

  z = 0,6745 · (Preis − Median) / MAD, mit MAD = Median der absoluten Abweichungen vom Median.

Verglichen wird jede Stunde nur mit vergleichbaren Stunden: **gleiches Jahr, gleicher Monat, gleiche Uhrzeit** (z. B. alle 12-Uhr-Stunden im Mai 2025). Auffällig ist |z| > 3,5, der von Iglewicz & Hoaglin empfohlene Grenzwert (Schalter `daten.ausreisser_schwelle`).

**Warum diese Methode:**
- *Median und MAD statt Mittelwert und Standardabweichung.* Mittelwert und Standardabweichung werden von genau den Extremwerten verschoben, die man sucht; große Ausreißer verdecken sich dann gegenseitig. Median und MAD sind robust (Leys et al. 2013; Hampel 1974).
- *Vergleich innerhalb Jahr × Monat × Stunde.* Strompreise haben starke Saison-, Tages- und Niveaumuster (Weron 2014). 50 €/MWh sind um 19 Uhr im Winter normal, mittags an einem sonnigen Maisonntag aber auffällig hoch. Ein Vergleich über alle Stunden hinweg würde vor allem das Krisenjahr 2022 markieren.
- *Klassische Boxplot-Regel (Tukey 1977) als Alternative:* ebenfalls robust und gut erklärbar; nicht gewählt, weil sie bei schiefen Verteilungen (Strompreise) einseitig viele Werte markiert. Kann im Bericht als Vergleich gezeigt werden.

**Ergebnis** (`results/tables/ausreisser.csv`):

| Jahr | auffällig | Anteil | davon ungewöhnlich niedrig | davon ungewöhnlich hoch | davon negativer Preis | davon in Betriebszeit 06–22 |
| --- | --- | --- | --- | --- | --- | --- |
| 2022 | 157 | 1,8 % | 127 | 30 | 4 | 84 |
| 2023 | 284 | 3,2 % | 252 | 32 | 73 | 163 |
| 2024 | 386 | 4,4 % | 287 | 99 | 56 | 194 |
| 2025 | 605 | 6,9 % | 334 | 271 | 77 | 415 |
| 2026 (bis Okt.) | 395 | 5,4 % | 277 | 118 | 47 | 244 |

**Interpretation (Ausreißer als Information, K3 Stufe 5):**
- **Rund 70 % sind ungewöhnlich niedrige Preise** (1 277 von 1 827). 58 % davon fallen aufs **Wochenende** (36 % auf Sonntage), 45 % in die **Nacht** (0–5 Uhr), gehäuft von Februar bis Oktober: wenig Nachfrage bei viel Wind- und Solarstrom. Das ist kein Messfehler, sondern das Marktverhalten, aus dem sich Flexibilität bezahlt macht.
- **Ungewöhnlich hohe Preise liegen vor allem mittags** (293 von 550, 10–16 Uhr) und abends (178). Mittags ist Strom meist billig; an Tagen mit wenig Sonne ist er dann umso teurer. **Für eine feste Regel „immer mittags“ (Strategie D) ist das genau das Risiko**, das eine Wochenprognose (Strategie B) vermeiden könnte (H0b). Beispiel: 476 €/MWh am 01.07.2025 um 20 Uhr.
- Der Anteil steigt von 1,8 % (2022) auf 6,9 % (2025): Die Preise werden mit mehr erneuerbarem Strom sprunghafter. Das stützt die Fragestellung.

**Warum nicht löschen:** Day-Ahead-Preise sind Auktionsergebnisse, keine Messwerte; extreme Preise sind echt und für Marktteilnehmer kostenwirksam (Janczura et al. 2013; Weron 2014). Löschte man sie, verschwänden gerade die billigsten Stunden, und der Flexibilitätswert würde systematisch **unterschätzt**. Die Ausreißer-Spalte dient deshalb der Erklärung und der Sensitivität, nicht der Bereinigung.

**Grenze der Methode:** In Monaten mit vielen Preisen nahe 0 € ist die MAD klein; dann gelten auch gewöhnliche Werktagspreise als „auffällig“ (z. B. 75 €/MWh im Mai 2025 um 11 Uhr). „Auffällig“ heißt deshalb nur „ungewöhnlich im Vergleich“, nicht „falsch“.

**Sensitivität (geplant 10.11.):** Ergebnis einmal mit allen Preisen (Basis) und einmal mit gekappten Ausreißern (auf den Grenzwert begrenzt, „winsorisiert“). Ändert sich die Ersparnis stark, hängt das Ergebnis an wenigen Extremstunden, und das muss im Bericht stehen.

## 5. Skalenniveaus (K2 Stufe 3)

| Merkmal | Skalenniveau | Bemerkung |
| --- | --- | --- |
| `preis_eur_mwh` | Verhältnisskala | natürlicher Nullpunkt (0 €), negative Werte möglich und echt |
| `mwh` | Verhältnisskala | synthetisch |
| `zeit`, `datum` | Intervallskala | Zeitpunkte |
| `stunde` | ordinal (zyklisch) | 0–23, 23 Uhr liegt neben 0 Uhr |
| `werktag`, `regime`, `auffaellig` | nominal | ja/nein bzw. zwei Kategorien |

## 6. Synthetische Daten (Verbrauch)

| Größe | Wert | Herkunft |
| --- | --- | --- |
| Produktionstage | täglich (7 Tage) | Praxiskontakt, 09.11.2026 (K-005) |
| Betriebszeit | 06–22 Uhr, 16 h | Praxiskontakt (K-003, K-005) |
| Verbrauch ganzes Werk | 50 MWh pro Tag | Praxiskontakt (K-005), nur zur Einordnung |
| verschiebbarer Anteil | 2 MWh pro Tag im 6-h-Block | **Platzhalter**, Prozess noch festzulegen (K-005) |

Synthetische Daten lassen sich nicht gegen die Wirklichkeit prüfen. Deshalb deterministisch (kein Zufall) und Sensitivität über Menge und Blocklänge (E-016).

## 7. Grenzen

- Nur Stundenpreise; ab 10/2025 bleibt Potenzial der Viertelstunden ungenutzt (E-021).
- Verschiebbare Menge ist eine Annahme, bis der Prozess feststeht.
- Keine unabhängige zweite Preisquelle (E-015).
- Ausreißer-Kennzeichnung hängt von der Vergleichsgruppe und der Schwelle ab; deshalb nur markieren.

## Literatur

- Hampel, F. R. (1974). The influence curve and its role in robust estimation. *Journal of the American Statistical Association*, 69(346), 383–393.
- Iglewicz, B., & Hoaglin, D. C. (1993). *How to Detect and Handle Outliers*. ASQC Quality Press.
- Janczura, J., Trück, S., Weron, R., & Wolff, R. C. (2013). Identifying spikes and seasonal components in electricity spot price data: A guide to robust modeling. *Energy Economics*, 38, 96–110.
- Leys, C., Ley, C., Klein, O., Bernard, P., & Licata, L. (2013). Detecting outliers: Do not use standard deviation around the mean, use absolute deviation around the median. *Journal of Experimental Social Psychology*, 49(4), 764–766.
- Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley.
- Wang, R. Y., & Strong, D. M. (1996). Beyond accuracy: What data quality means to data consumers. *Journal of Management Information Systems*, 12(4), 5–33.
- Weron, R. (2014). Electricity price forecasting: A review of the state-of-the-art with a look into the future. *International Journal of Forecasting*, 30(4), 1030–1081.
- Bundesnetzagentur | SMARD.de: Großhandelspreise Day-Ahead DE-LU, CC BY 4.0, abgerufen 07.11.2026.

*Literaturangaben vor der Abgabe im Original prüfen (Seitenzahlen, Zitierstil der HM).*
