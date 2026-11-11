# Annahmenliste

<!-- KI: Claude, Zweck: Annahmen und Fakten nach dem Teamdokument „Analyse und Entscheidungsprojekt“ (Gruppe F) mit Quelle und Stand im Code, geprüft von Chiara (R1) -->

Owner: R1 (Chiara). Grundlage ist das Teamdokument „Analyse und Entscheidungsprojekt“ (Leitfrage, Rahmenbedingungen, Fragestellungen, Rollen), abgeglichen mit dem Praxisgespräch (K-005, K-008, K-012) und `params.yaml`. Jede Zahl im Code kommt aus `params.yaml`; diese Liste sagt, woher sie stammt.

**Art:** P = vom Praxispartner genannt · S = vom Partner geschätzt · T = Annahme des Teams · D = aus den Daten (SMARD) · N = Nichtziel

## Leitfrage (Teamdokument)

In welchem Maße kann ein bayerisches Molkereiwerk (anonym) seine Stromkosten am deutschen Day-Ahead-Markt senken, wenn es die nächtliche Maschinenreinigung in die günstigsten Stunden legt, deren Zeitpunkt jedoch eine Woche im Voraus im Schichtplan feststehen muss (2022–2026)?

## Fragestellungen und wo sie beantwortet werden

| Nr. | Fragestellung (Teamdokument) | Umsetzung | Ergebnis in |
| --- | --- | --- | --- |
| FS1 | Feste neue Uhrzeit aus den historischen Daten statt 22–24 Uhr: Lohnt sich das? | Strategie D: bester fester Start aus 2023–2024 (3 Uhr), gegen A | `ergebnisse/hypothesentests.csv` (FS1), R4 mit Personal |
| FS2 | Jede Woche am Freitag die Uhrzeiten je Tag neu berechnen, aus den Daten der letzten 16 Wochen | Strategie B_16: je Wochentag Mittel der letzten 16 gleichen Nächte (E-049) | `hypothesentests.csv` (FS2) |
| FS3 | Hätten wir vor einem Jahr so geplant: Hätten wir gespart? | B_16 gegen A im letzten Jahr = Test 2 (10/2025–09/2026) | `hypothesentests.csv` (FS3) |

Zusätzlich vorab festgelegt (`docs/hypothesen.md`): H0a (D nach Personalkosten), H0b (Prognose B gegen D), H0c (Kipppunkt Tagesplanung).

## Rahmenbedingungen

| Nr. | Annahme / Fakt | Wert | Art | Quelle | `params.yaml` | Stand |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Produktion läuft 16 h am Tag | 06–22 Uhr | P | K-005, K-008 P5 | `last.betrieb_start_h`, `betrieb_ende_h` | ✅ |
| 2 | Reinigung nur nachts | Fenster 22–06 Uhr | P | K-008 B5 | `last.fenster_start_h`, `fenster_ende_h` | ✅ |
| 3 | Reinigung heute | 22–24 Uhr (Status quo A) | P | K-012 (Interview 10.11.2026) | `last.status_quo_start_h` | ✅ Tatsache |
| 4 | Reinigung an jedem Tag | 7 Nächte pro Woche, auch Feiertage | P | K-005 | `last.produktionstage` | ✅ |
| 5 | Dauer der Reinigung | 2 h | P | K-008 P6 | `last.blocklaenge_h` | ✅ |
| 6 | **Energie der Reinigung** | **8 MWh pro Nacht (4 MW × 2 h)** | P | K-008 P6 | `last.mwh_pro_tag` | ⚠️ **offen:** Das Teamdokument nennt „8 MW für 2 h“ (= 16 MWh). Alle Euro-Beträge skalieren linear; Anteile, Tests und Kipppunkte in €/MWh bleiben gleich |
| 7 | Stromverbrauch Werk | 180 MWh pro Tag, 65 GWh pro Jahr | P | K-008 P1, P2 | `last.gesamtverbrauch_mwh_pro_tag` | ✅ |
| 8 | Anteil Day-Ahead | ca. 53 MWh pro Tag (30 %), Rest Festpreis 85 €/MWh | P | K-008 P3, P4 | `vertrag.spot_anteil`, `kosten.festpreis_eur_mwh` | ✅ |
| 9 | Bewertung der verschobenen MWh | Basis: 100 % am Spot (Band); Untergrenze 30 % | T | A3, K-008 | `vertrag.bewertung_verschiebung` | beide Fälle ausgewiesen |
| 10 | Planungsvorlauf | Schichtplan Freitag 08:00 für Mo–So der Folgewoche (7 Tage) | P | K-008 P11 | `planung` | ✅ |
| 11 | Nachtzuschlag | 25 % (25–30 %), gilt 22–06 Uhr | S / T | K-008 P13; Nachtstunden A-017 | `kosten.nachtzuschlag`, `nachtstunden` | Caro bestätigt beim Partner |
| 12 | Wochenendzuschlag | 50 % (30–50 %), **Samstag und Sonntag** | S | K-008 P14, Teamdokument | `kosten.wochenendzuschlag` | ✅ (vorher nur Sonntag, E-049) |
| 13 | Feiertagszuschlag | 100 % (gesetzliche Feiertage Bayern) | S | K-008 P15 | `kosten.feiertagszuschlag` | ✅ |
| 14 | Zusammentreffen von Zuschlägen | nur der höchste; Kalendertag der Stunde zählt | T | A-017 | `kosten.zuschlag_regel` | Sensitivität: addiert |
| 15 | Personal an der Reinigung | 3 Personen (2–4), Zeitarbeit 35 €/h (30–45) | T | A6, A7 | `kosten.mitarbeiter`, `stundenlohn_eur` | Quelle offen |
| 16 | Umstellungskosten | keine Quelle | T | E-044 | `kosten.umstellungskosten_eur_pro_jahr` | als Break-even-Kurve |
| 17 | Strompreise | Day-Ahead DE-LU, Stundenwerte 2022–10/2026 | D | Bundesnetzagentur \| SMARD.de, CC BY 4.0, Filter 4169 | `markt`, `daten` | ✅ |
| 18 | Historie für die Wochenplanung | 16 Wochen (FS2, B_16); zum Vergleich 4 Wochen (B) | T | Teamdokument; Kickoff | `strategien.historie_wochen` | ✅ |

## Nichtziele

| Nichtziel | Grund |
| --- | --- |
| Kälte, Produktion, Druckluft, Becher | nicht Gegenstand; C&E-Matrix (R4) begründet, warum nur die Reinigung (E-043) |
| Viertelstundenpreise | 2-h-Block zur vollen Stunde: Stundenmittel und Viertelstunden ergeben dieselben Kosten (E-021, E-043) |
| Intraday, Ausgleichsenergie | Plan wird eingehalten; Abweichungen kosten alle Strategien gleich |
| Netzentgelte, Steuern, Leistungspreis | für alle Strategien gleich bzw. nicht zeitvariabel |

## Rollen nach Teamdokument

| Rolle | Person | Aufgaben laut Teamdokument |
| --- | --- | --- |
| R1 Projektleitung und Controlling | Chiara | Define (Problem, Forschungsfrage); Empfehlung an die Werksleitung (Improve, Control); Rahmen (Process Map), Steuerung, Vertrag Festpreis gegen Börse |
| R2 Datenerhebung und IT | Max | Measure: Daten bestimmen, bereinigen, über Schnittstellen bereitstellen, Reproduzierbarkeit; kein Statistikteil |
| R3 Modellierung und Statistik | Susan | Ursachen und Zusammenhänge beim Strom; Mittelwerte und optimale Zeiten; Vergleich mit heute; gepaarter t-Test |
| R4 Produktion und Schichtplanung | Caro | Ursachen und Zusammenhänge bei den Zusatzkosten; Amortisation bzw. Break-even; dieselben Vergleiche mit Personalkosten |
