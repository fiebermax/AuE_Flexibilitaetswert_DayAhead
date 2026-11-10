# Datenaufbereitung und Datenqualität (R2)

Stand 09.11.2026 · Owner R2 (Max) · Grundlage für Bericht Kapitel 3 (K2) und 4 (K3). Code: `src/01_download.py`, `src/02_synthetisch.py`, `src/cleaning.py`. Zählungen je Schritt: `reports/cleaning_log.md`; Kennzahlen und Grafiken: `reports/data_quality.md`; Spalten: `docs/codebook.md`. Jede Entscheidung steht mit verworfener Alternative im Projekttagebuch (E-Nummer in Klammern).

> Begriffe aus dem Kursmaterial (Statistik-Grundlagenwerk, Rheinlack-Fallstudie) haben Vorrang. Vor dem Bericht prüfen, ob dort andere Bezeichnungen für Skalenniveaus, Ausreißer oder Datenqualität verwendet werden, und angleichen.

## 1. Vorgehen in einem Bild

```
SMARD (Rohdaten, JSON, 253 Wochen)
  │  Schritt 1: Erhebung       → unverändert speichern, Herkunft und Prüfsumme je Datei
  │  Schritt 2: Bereinigung    → zusammenführen, Dubletten, UTC-Raster, Lücken, Auflösung, Kalender
  │  Schritt 3: Prüfung        → Plausibilität, Ausreißer markieren (nicht löschen), Join Last, Kennzahlen
  ▼
preise_clean.csv (42 360 UTC-Stunden, Verbrauch angehängt)  →  Backtest (R3)
```

Grundsatz: **Rohdaten bleiben unverändert; jede Veränderung geschieht im Code, ist begründet und nachvollziehbar.** Nichts wird von Hand bearbeitet (K3 Stufe 3).

## 2. Datenqualität nach Qualitätsdimensionen

Datenqualität wird nicht nur beschrieben, sondern je Dimension geprüft. Die Dimensionen folgen der verbreiteten Einteilung von Wang & Strong (1996).

| Dimension | Frage | Prüfung | Ergebnis (Abruf 07.11.2026) | Beleg |
| --- | --- | --- | --- | --- |
| **Herkunft / Integrität** | Stammen die Daten unverändert aus der Quelle? | SHA256-Prüfsumme je Rohdatei, Abrufzeitpunkt, URL | 253 Dateien, alle unverändert | `data/raw/smard/manifest.csv`, Test `test_rohdaten_unveraendert` (E-008, E-009) |
| **Vollständigkeit** | Fehlen Stunden? | Abgleich gegen das erwartete UTC-Stundenraster, Lücken mit Beginn und Länge | 0 Lücken in 42 360 Stunden | `reports/tables/luecken.csv`, Test `test_lueckenloses_stundenraster_eindeutig` |
| **Eindeutigkeit** | Gibt es Stunden doppelt? | exakte und widersprüchliche Dubletten getrennt zählen; widersprüchliche → Abbruch | 0 / 0 | Tests `test_exakte_dublette_wird_einmal_behalten`, `test_lueckenloses_stundenraster_eindeutig` |
| **Konsistenz** | Passt die Struktur? | Abstand aufeinanderfolgender Stunden = 60 min; lokale Tage 24 h, je 5 Tage mit 23 und 25 h (Zeitumstellung) | erfüllt | Tests `test_lokale_tage_23_24_25_stunden`, `reports/tables/zeitumstellung.csv` |
| **Plausibilität** | Liegen die Werte im möglichen Bereich? | harmonisierte Preisgrenzen der Day-Ahead-Kopplung SDAC: Minimum −500 €/MWh, Maximum im Zeitraum zwischen +3 000 und +5 000 €/MWh → geprüft −500 bis +5 000 | erfüllt; Minimum −500 (2023), Maximum 936 €/MWh (2024) | Test `test_wertebereich` |
| **Genauigkeit** | Wie genau sind die Werte? | Quelle und Rundung prüfen | Auktionsergebnisse, kein Mess- oder Schätzwert; auf 0,01 €/MWh gerundet. Ab 10/2025 Stundenwert = Mittel aus 4 Viertelstunden (SMARD) | E-012, E-021 |
| **Aktualität** | Wie aktuell, und ändern sich Werte nachträglich? | Datenstand in `params.yaml`; Erstellzeitpunkt je Datei | Datenstand 31.10.2026; nachträgliche Korrekturen durch eingefrorene Rohdaten abgefangen | `manifest.csv` (Spalte `smard_created_utc`) |
| **Ausreißer** | Gibt es auffällige Werte, und was bedeuten sie? | robuster z-Wert je Jahr × Monat × Stunde (Abschnitt 4) | 1 827 Stunden (4,3 %) markiert, keine gelöscht | `reports/tables/ausreisser.csv`, Spalte `flag_outlier` (E-025) |

**Unabhängige zweite Quelle:** bewusst nicht. SMARD bezieht die Day-Ahead-Preise von ENTSO-E; ein Abgleich wäre keine unabhängige Prüfung (E-015). Die aktive Prüfung der Datenqualität für K2 Stufe 5 erfolgt über die Sensitivitätsrechnung (`docs/sensitivitaet_plan.md`).

## 3. Aufbereitungsschritte

| # | Schritt | Methode | Begründung | Verworfene Alternative |
| --- | --- | --- | --- | --- |
| 1 | Erhebung | automatischer Abruf der SMARD-Wochendateien, Ablage als Original-Bytes, Cache | reproduzierbar, offline lauffähig, nachträgliche SMARD-Korrekturen verändern unsere Zahlen nicht | manueller CSV-Export von der Webseite (nicht nachvollziehbar) |
| 2 | Zusammenführen | alle Wochen untereinander, doppelte Zeitstempel prüfen | Wochendateien überlappen nicht, sollen es auch nicht; widersprüchliche Duplikate würden den Lauf stoppen | stillschweigend den ersten oder letzten Wert nehmen |
| 3 | Zeit | **Schlüssel `ts_utc`**; lokale Zeit `ts_lokal` als Zusatzspalte | In UTC gibt es keine doppelten oder fehlenden Stunden. Die doppelte Oktober-Stunde sind zwei verschiedene UTC-Stunden mit zwei Preisen: beide bleiben, nichts wird gemittelt. Schichten werden über `stunde_lokal` geplant. | doppelte Stunde mitteln (bisherige Lösung E-010, verwirft eine echte Beobachtung); nur Ortszeit (mehrdeutig) |
| 4 | Auflösung | Abstand aufeinanderfolgender Zeitstempel geprüft: durchgehend 60 min | einheitliche Auflösung; ab 01.10.2025 (SDAC 15-min-Produkte, Lieferung ab 01.10.2025) SMARD-Stundenwert = Mittel der vier Viertelstunden | eigene Aggregation aus 15-min-Daten (aufwendiger, bei Blöcken zur vollen Stunde kostengleich, E-021, E-028) |
| 5 | Zeitumstellung | 23- und 25-Stunden-Tage gelistet | Transparenz; liegt 02–03 Uhr, außerhalb der Betriebszeit 06–22 Uhr | — |
| 6 | Lücken | erwartetes UTC-Stundenraster, fehlende Werte bleiben leer, Liste mit Beginn und Länge, Spalte `imputed` | Lücken müssen sichtbar sein, Imputation nur nach Rückfrage | Zeilen löschen oder interpolieren |
| 7 | Kalender | `werktag` = Mo–Fr ohne gesetzliche Feiertage in Bayern (Paket `holidays`), Mariä Himmelfahrt schaltbar | Auswertung Werktag/Wochenende; Feiertage beeinflussen Last und Preise | Feiertagsliste von Hand |
| 8 | Regime | `regime` = `stunde` bis 30.09.2025, `viertel` ab 01.10.2025 | Vergleich vor/nach Umstellung des Börsenhandels (H0c) | — |
| 9 | Ausreißer | markieren mit robustem z-Wert (`flag_outlier`), nicht löschen | siehe Abschnitt 4 | löschen oder kappen (±3 SD oder IQR als Löschregel) |
| 10 | Join Verbrauch | Tagesverbrauch über das lokale Datum an jede Stunde; Zeilen vor/nach gezählt | gemeinsame Datei für alle Rollen | Verbrauch in getrennter Datei lassen |

**Wirkung der Zeitumstellung auf das Ergebnis:** keine. Sie betrifft 02:00–03:00 Uhr, produziert wird 06–22 Uhr (E-024, Test `test_lokale_tage_23_24_25_stunden`).

## 4. Ausreißer: markieren, erklären, nicht löschen

**Methode.** Für jede Stunde wird ein *modifizierter z-Wert* berechnet (Iglewicz & Hoaglin 1993):

  z = 0,6745 · (Preis − Median) / MAD, mit MAD = Median der absoluten Abweichungen vom Median.

Verglichen wird jede Stunde nur mit vergleichbaren Stunden: **gleiches Jahr, gleicher Monat, gleiche Uhrzeit** (z. B. alle 12-Uhr-Stunden im Mai 2025). Auffällig ist ein Betrag von z über 3,5, der von Iglewicz & Hoaglin empfohlene Grenzwert (Schalter `cleaning.ausreisser_schwelle`). Ergebnis: Spalte `flag_outlier`.

**Warum diese Methode:**
- *Median und MAD statt Mittelwert und Standardabweichung.* Mittelwert und Standardabweichung werden von genau den Extremwerten verschoben, die man sucht; große Ausreißer verdecken sich dann gegenseitig. Median und MAD sind robust (Leys et al. 2013; Hampel 1974).
- *Vergleich innerhalb Jahr × Monat × Stunde.* Strompreise haben starke Saison-, Tages- und Niveaumuster (Weron 2014). 50 €/MWh sind um 19 Uhr im Winter normal, mittags an einem sonnigen Maisonntag aber auffällig hoch. Ein Vergleich über alle Stunden hinweg würde vor allem das Krisenjahr 2022 markieren.
- *Klassische Boxplot-Regel (Tukey 1977) als Alternative:* ebenfalls robust und gut erklärbar; nicht gewählt, weil sie bei schiefen Verteilungen (Strompreise) einseitig viele Werte markiert. Kann im Bericht als Vergleich gezeigt werden.

**Ergebnis** (`reports/tables/ausreisser.csv`):

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

**Look-ahead:** `flag_outlier` vergleicht mit dem ganzen Monat, also auch mit späteren Stunden. Die Spalte dient nur der Beschreibung; `src/datenzugriff.py` entfernt sie, damit keine Planungsstrategie sie nutzt (Test `test_datenzugriff_ohne_ausreisserflag`).

**Sensitivität (geplant 10.11.):** Ergebnis einmal mit allen Preisen (Basis) und einmal ohne die markierten Stunden in der Auswertung. Die Daten selbst bleiben unverändert. Ändert sich die Ersparnis stark, hängt das Ergebnis an wenigen Extremstunden, und das muss im Bericht stehen.

## 5. Skalenniveaus (K2 Stufe 3)

| Merkmal | Skalenniveau | Bemerkung |
| --- | --- | --- |
| `preis_eur_mwh` | Verhältnisskala | natürlicher Nullpunkt (0 €), negative Werte möglich und echt |
| `mwh` | Verhältnisskala | synthetisch |
| `zeit`, `datum` | Intervallskala | Zeitpunkte |
| `stunde` | ordinal (zyklisch) | 0–23, 23 Uhr liegt neben 0 Uhr |
| `werktag`, `in_betriebszeit`, `regime`, `saison`, `imputed`, `flag_outlier` | nominal | Kategorien bzw. ja/nein |
| `last_mwh_tag`, `last_mwh_flexibel_tag` | Verhältnisskala | MWh pro Tag |

## 6. Synthetische Daten (Verbrauch)

| Größe | Wert | Herkunft |
| --- | --- | --- |
| Produktionstage | an jedem Tag, auch an Feiertagen | Praxiskontakt, Interview 09.11.2026 (K-005) |
| Betriebszeit | 06–22 Uhr, 16 h | Praxiskontakt (K-003, K-005) |
| Verbrauch Werk | 180 MWh pro Tag (65 GWh/a) | Praxiskontakt, Termin 10.11.2026 (K-008, E-032) |
| verschiebbarer Anteil | Reinigung (CIP): 4 MW × 2 h = 8 MWh pro Tag, im Fenster 22–06 Uhr | Praxiskontakt (K-008, E-033) |
| Status quo A | Reinigung 22–24 Uhr, direkt nach Produktionsende | **Annahme** des Teams (E-031) |

Synthetische Daten lassen sich nicht gegen die Wirklichkeit prüfen. Deshalb deterministisch (kein Zufall) und Sensitivität über Menge und Blocklänge (E-016).

## 7. Grenzen

- Nur Stundenpreise; ab 10/2025 bleibt Potenzial der Viertelstunden ungenutzt (E-021).
- Status quo der Reinigung (22–24 Uhr) ist eine Annahme, nicht vom Praxiskontakt bestätigt (E-031).
- Die Zeitumstellung liegt jetzt im Reinigungsfenster: Nächte mit 7 bzw. 9 Stunden, Blöcke über echte Stunden (E-036).
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
- ACER (2026): Decision 02/2026, Annex I: harmonisierte Höchst- und Mindestclearingpreise für SDAC (Referenz +4 000 / −500 €/MWh). https://www.acer.europa.eu/sites/default/files/documents/Individual%20Decisions_annex/ACER-Decision-02-2026-AnnexI.pdf
- EPEX SPOT (2022): Harmonised maximum clearing price for SDAC to be set to +4,000 EUR/MWh from 10th May 2022. https://www.epexspot.com/en/news/harmonised-maximum-clearing-price-sdac-be-set-4000-eurmwh-10th-may-2022
- EXAA (2022): Harmonised maximum clearing price for SDAC to be set to +5,000 EUR/MWh from 20th September. https://www.exaa.at/uber-exaa/neuigkeiten/harmonised-maximum-clearing-price-for-sdac-to-be-set-to-5-000-eur-mwh/
- NEMO Committee (2025): 15-minute MTU in SDAC was implemented (Handelstag 30.09.2025, Lieferung ab 01.10.2025). https://nemo-committee.eu/assets/files/15-minute-mtu-in-sdac-was-implemented.pdf

*Literaturangaben vor der Abgabe im Original prüfen (Seitenzahlen, Zitierstil der HM).*
