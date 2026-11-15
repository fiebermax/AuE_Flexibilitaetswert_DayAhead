# AuE-Projekt: Flexibilitätswert am Day-Ahead-Strommarkt

Modul Analyse und Entscheidungsfindung, Hochschule München, WS 26/27. Team aus 4 Personen (Rollen R1–R4).

**Worum es geht:** Eine Großmolkerei in Bayern kauft Strom zum Day-Ahead-Preis, der jede Stunde anders ist und erst am Vortag feststeht. Die Schichten werden aber schon freitags für die ganze Woche geplant. Wir spielen mit echten Preisen von 2022 bis 2026 nach, wie viel Geld sie gespart hätte, wenn sie die stromintensive Reinigung der Anlagen (4 MW für 2 Stunden pro Nacht) jeden Freitag in die voraussichtlich billigsten Nachtstunden zwischen 22 und 6 Uhr gelegt hätte, statt sie direkt nach Produktionsende um 22 Uhr zu starten.

**Ergebnis auf einer Seite:** [`ergebnisse/analyse.html`](ergebnisse/analyse.html), von den Parametern bis zur Entscheidung für die Betriebsleitung.

## Leitfrage, Teilfragen und Hypothesen

**Leitfrage:** In welchem Maße kann ein bayerisches Molkereiwerk seine Stromkosten am deutschen Day-Ahead-Markt senken, wenn es die nächtliche Maschinenreinigung in die günstigsten Stunden legt, deren Zeitpunkt jedoch eine Woche im Voraus im Schichtplan feststehen muss (2022–2026)?

| Teilfrage | Nullhypothese | Prüfung | im Code |
| --- | --- | --- | --- |
| **1 · Ersparnis:** Ist eine feste, aus historischen Daten berechnete Reinigungszeit günstiger als heute (22–24 Uhr)? | **H0a Statische Optimierung:** Die feste Reinigungszeit führt gegenüber 22–24 Uhr zu keiner durchschnittlichen Kostenersparnis (μa ≤ 0). | einseitiger gepaarter t-Test, 95-%-Konfidenzintervall | `FS1`: Strategie D gegen A |
| **2 · Planbarkeit:** Sparen wir Geld, wenn wir jeden Freitag für jede Nacht der nächsten Woche eine neue Uhrzeit berechnen, auf Basis der letzten 16 Wochen? | **H0b Dynamische Optimierung:** Die wöchentliche Neuplanung führt gegenüber 22–24 Uhr zu keiner durchschnittlichen Kostenersparnis (μb ≤ 0). | einseitiger gepaarter t-Test, 95-%-Konfidenzintervall | `FS2`: Strategie B_16 gegen A |
| **3 · Bestfall:** Hätten wir im letzten Jahr gespart, wenn wir so geplant hätten wie in Teilfrage 2? | **H0c Rücktest:** Die dynamische Planung führt im Rücktestjahr gegenüber 22–24 Uhr zu keiner durchschnittlichen Kostenersparnis (μc ≤ 0). | Block-Bootstrap der jährlichen Ersparnis, 95-%-Konfidenzintervall | `FS3`: B_16 gegen A im Testjahr 10/2025–09/2026 |

Signifikanzniveau nach Bonferroni: α = 0,05 / 3 ≈ 0,017 je Test. Ergebnisse: `ergebnisse/hypothesentests.csv` (Zeilen FS1–FS3) und Abschnitt 3 der Analyseseite.

## Wo was liegt

```
params.yaml   alle Annahmen und Zahlen an einer Stelle (Zeiträume, Verbrauch, Kosten), mit Quelle je Wert
data/         preise_clean.csv, last_synth.csv; raw/ = Originaldateien von SMARD, nur lesen
src/          aller Code, Schritte 01-08, ausgeführt über run_all.py
analyse.ipynb die Analyseseite; wird als ergebnisse/analyse.html exportiert
ergebnisse/   Tabellen (CSV), grafiken/, datenqualitaet/ (Bereinigungsprotokoll, Datenqualität, Kennzahlen)
tests/        automatische Prüfungen: pytest tests/
```

| Schritt | Datei | Rolle |
| --- | --- | --- |
| Daten laden, Lastgang, Bereinigung, Rückblick Reinigungsfenster | `src/01_download.py`, `src/02_synthetisch.py`, `src/cleaning.py`, `src/fensteranalyse.py` | R2 |
| Datenzugriff je Planungsfreitag ohne Blick in die Zukunft | `src/datenzugriff.py` | R2 |
| Merkmale und Backtest der Strategien, Statistik | `src/03_merkmale.py`, `src/04_strategien.py` | R3 |
| Personalkosten, Break-even, Kipppunkte, Empfehlung | `src/05_bewertung.py` | R4 |
| Sensitivität | `src/06_sensitivitaet.py` | R2 |
| Grafiken, Spot gegen Festpreis | `src/07_bericht.py` | R1 |
| Analyseseite als HTML | `src/08_board.py` | alle |

## Daten ansehen

Alle fertigen Daten liegen als CSV in `data/` und `ergebnisse/`. Öffnen mit Excel oder pandas:

| Datei | Inhalt |
| --- | --- |
| `data/preise_clean.csv` | bereinigter Strompreis für jede Stunde, 01.01.2022 bis 31.10.2026, mit Uhrzeit, Saison, Werktag, Betriebszeit, Verbrauch |
| `data/last_synth.csv` | Stromverbrauch des Werks pro Tag (180 MWh) und verschiebbarer Anteil (Reinigung, 8 MWh) |
| [`ergebnisse/datenqualitaet/data_quality.md`](ergebnisse/datenqualitaet/data_quality.md) | Kennzahlen und Grafiken zur Datenqualität |
| [`ergebnisse/datenqualitaet/cleaning_log.md`](ergebnisse/datenqualitaet/cleaning_log.md) | jeder Bereinigungsschritt mit Zeilenzahl vorher/nachher |

Einzelne Tage oder die letzten Monate abfragen (`src/preisabfrage.py`, nur zum Anschauen):

```python
import sys; sys.path.insert(0, "src")
from preisabfrage import tag, letzte_monate

df = tag("2026-10-15")                       # ein Tag, eine Zeile je Stunde
df = letzte_monate(3, wochentag="Samstag")   # nur Samstage der letzten 3 Monate
df.groupby("wochentag")["preis"].mean()      # mittlerer Preis je Wochentag
```

## Alles neu berechnen

```bash
pip install -r requirements.txt
python src/run_all.py      # Rohdaten -> Ergebnisse, ein Befehl
pytest tests/              # Prüfung der Datenannahmen
```

Für neue Daten nur `zeitraeume.datenstand` in `params.yaml` ändern.

## Daten, Lizenzen, KI

- Day-Ahead-Großhandelspreise DE-LU: **Bundesnetzagentur | SMARD.de**, Lizenz CC BY 4.0.
- Verbrauch, Betriebszeit, Reinigung, Vertrag und Zuschläge: Angaben des Praxispartners (Zuschläge geschätzt); Personal, Stundensatz und Umstellungskosten: Annahmen des Teams (alle in `params.yaml`). Keine internen Unternehmensdaten, keine personenbezogenen Daten.
- KI-Einsatz (Claude) ist im Kopf jeder Datei gekennzeichnet (`# KI: Claude, Zweck …, geprüft von …`).
