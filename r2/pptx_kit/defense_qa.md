# Verteidigung R2: wahrscheinliche Prüferfragen

Erzeugt von `src/build_presentation.py`; Zahlen aus `key_figures.json`.

## 1. Woher stammen die Daten, und dürft ihr sie nutzen?

Day-Ahead-Großhandelspreise DE-LU von Bundesnetzagentur | SMARD.de (Filter 4169), Lizenz CC BY 4.0: Nutzung und Weitergabe mit Namensnennung erlaubt. 253 Wochendateien, abgerufen am 07.11.2026.

**Beleg:** `data/raw/MANIFEST.md`, `src/01_download.py` (Commit 95ee403)

## 2. Woher weißt du, dass die Rohdaten nicht verändert wurden?

Jede Rohdatei hat eine SHA-256-Prüfsumme aus dem Abruf. Jeder Lauf und ein Test vergleichen sie; eine geänderte Zahl bricht den Lauf ab.

**Beleg:** `data/raw/smard/manifest.csv`, Test `test_rohdaten_unveraendert` (Commit 461a29d)

## 3. Wie behandelst du die Zeitumstellung?

Schlüssel ist UTC. Dort gibt es keine doppelten oder fehlenden Stunden; die doppelte Oktober-Stunde sind zwei verschiedene UTC-Stunden mit eigenem Preis, nichts wird gemittelt. Lokal gibt es 5 Tage mit 23 h und 5 mit 25 h; sie liegen nachts, außerhalb der Betriebszeit 06–22 Uhr.

**Beleg:** `reports/tables/zeitumstellung.csv`, Tagebuch E-026, `src/cleaning.py` (Commit b6bdf86)

## 4. Warum löschst du keine Ausreißer?

Day-Ahead-Preise sind Auktionsergebnisse, keine Messwerte. Extreme Preise sind echt, und gerade die billigen Stunden tragen den Flexibilitätswert. Deshalb werden 1.827 auffällige Preise (4,3 %) nur markiert, mit robustem z-Wert (Median/MAD) statt ±3 Standardabweichungen.

**Beleg:** `docs/datenaufbereitung.md` Abschnitt 4, Tagebuch E-025, `reports/tables/ausreisser.csv`

## 5. Wie hast du die Umstellung auf Viertelstunden behandelt?

Seit 01.10.2025 handelt die Börse in Viertelstunden. Wir nutzen einheitlich 60 min: den Stundenwert, den SMARD aus den vier Viertelstunden bildet. Bei Blöcken zur vollen Stunde ist das kostengleich.

**Beleg:** Tagebuch E-021, E-028; Quelle NEMO Committee (2025)

## 6. Warum keine zweite, unabhängige Preisquelle?

SMARD bezieht die Day-Ahead-Preise von ENTSO-E. Ein Abgleich wäre keine unabhängige Prüfung. Die Datenqualität prüfen wir stattdessen aktiv über die Sensitivitätsrechnung.

**Beleg:** Tagebuch E-015, `docs/sensitivitaet_plan.md`

## 7. Warum 2,0 MWh verschiebbar?

Ehrlich: Das ist ein Platzhalter. Der Praxiskontakt hat uns den Gesamtverbrauch (50 MWh/Tag), die Betriebszeit (06–22 Uhr) und die flexiblen Prozesse genannt, aber noch keine Menge für den verschiebbaren Teil. Bis Prozess und Menge feststehen, bleibt 2,0 MWh/Tag als Annahme stehen und ist überall so gekennzeichnet. Die Ersparnis in Euro skaliert damit linear; der Anteil am erreichbaren Optimum hängt nicht davon ab. Die Sensitivitätsrechnung zeigt die Wirkung anderer Mengen.

**Beleg:** `config/params.yaml` (`last.mwh_pro_tag`), Tagebuch K-005, E-024

## 8. Ist eure Mehrkosten-Kennzahl nicht ein Blick in die Zukunft?

Ja, bewusst: Sie ist ein Rückblick mit bekannten Preisen und zeigt nur, wie groß der Spielraum ist. Sie ist keine Strategie und steht so auf der Folie. Die Strategien im Backtest bekommen über `src/datenzugriff.py` nur Daten bis zum jeweiligen Freitag, und `flag_outlier` wird dort entfernt.

**Beleg:** `src/fensteranalyse.py`, `src/datenzugriff.py`, Test `test_kein_look_ahead_in_allen_planungswochen`

## 9. Warum sind die Prozentwerte so breit gestreut?

Mittags liegen die Preise im Frühling und Sommer oft nahe null. Prozent = Mehrkosten geteilt durch einen sehr kleinen Preis, das wird instabil; an 88 Sommertagen war das billigste Fenster sogar null oder negativ, dort gibt es keinen Prozentwert. Deshalb argumentieren wir in €/MWh (Sommer Median 22,3 €/MWh).

**Beleg:** `src/fensteranalyse.py`, `pptx_kit/key_figures.json`

## 10. Was hat die KI gemacht, und was hast du selbst entschieden?

Claude Code hat Code, Tests und Doku geschrieben. Ich habe vorher jeweils einen Plan freigegeben und die fachlichen Entscheidungen getroffen (UTC statt Mitteln, nur markieren statt löschen, CSV, Kennzahl Mehrkosten, Annahmen). Alles ist im Tagebuch und in `docs/ki-nutzung.md` gekennzeichnet; den Code erkläre ich selbst.

**Beleg:** `docs/ki-nutzung.md`, Tagebuch A-008, K-006, A-009

