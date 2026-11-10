# AuE-Projekt: Flexibilitätswert am Day-Ahead-Strommarkt

Modul Analyse und Entscheidungsfindung, Hochschule München, WS 26/27. Team aus 4 Personen.

**Worum es geht:** Eine Großmolkerei in Bayern kauft Strom zum Day-Ahead-Preis, der jede Stunde anders ist und erst am Vortag feststeht. Die Schichten werden aber schon freitags für die ganze Woche geplant. Wir spielen mit echten Preisen von 2022 bis 2026 nach, wie viel Geld sie gespart hätte, wenn sie die stromintensive Reinigung der Anlagen (4 MW für 2 Stunden pro Nacht) jeden Freitag in die voraussichtlich billigsten Nachtstunden zwischen 22 und 6 Uhr gelegt hätte, statt sie direkt nach Produktionsende um 22 Uhr zu starten.

## Daten ansehen (ohne das Repo zu kennen)

Alle fertigen Daten liegen als **CSV** in `data/`. Öffnen mit Excel oder pandas:

| Datei | Inhalt |
| --- | --- |
| [`data/preise_clean.csv`](data/preise_clean.csv) | bereinigter Strompreis für jede Stunde, 01.01.2022 bis 31.10.2026, mit Uhrzeit, Saison, Werktag, Betriebszeit, Verbrauch |
| [`data/last_synth.csv`](data/last_synth.csv) | Stromverbrauch des Werks pro Tag (180 MWh) und verschiebbarer Anteil (Reinigung, 8 MWh) |
| [`r2/ergebnisse/data_quality.md`](r2/ergebnisse/data_quality.md) | Kennzahlen und Grafiken zur Datenqualität |
| [`r2/ergebnisse/cleaning_log.md`](r2/ergebnisse/cleaning_log.md) | jeder Bereinigungsschritt mit Zeilenzahl vorher/nachher |

```python
import pandas as pd
preise = pd.read_csv("data/preise_clean.csv")
preise.groupby("stunde_lokal")["preis_eur_mwh"].median()   # typischer Preis je Uhrzeit
```

Jede Spalte erklärt: [`docs/codebook.md`](docs/codebook.md).

**Einzelne Tage oder die letzten Monate abfragen** (`src/preisabfrage.py`, nur zum Anschauen, nicht für Strategien):

```python
import sys; sys.path.insert(0, "src")
from preisabfrage import tag, tage, letzte_monate

df = tag("2026-10-15")                       # ein Tag, eine Zeile je Stunde
df = letzte_monate(3)                        # die letzten 3 Monate
df = letzte_monate(3, wochentag="Samstag")   # nur Samstage
df[["datum", "wochentag", "uhrzeit", "preis"]]
df.groupby("wochentag")["preis"].mean()      # mittlerer Preis je Wochentag
```

Im Terminal: `python src/preisabfrage.py 2026-10-15` (oder zwei Daten für einen Zeitraum).

## Wo was liegt

Eine Einstellungsdatei und fünf Ordner. **Aller Code liegt in `src/`.** In **`r2/`** liegen nur Dokumente und Ergebnisse von Max (R2), das Team kann es ignorieren.

```
params.yaml   alle Annahmen und Zahlen an einer Stelle (Zeiträume, Verbrauch, Kosten)
data/         die Daten: preise_clean.csv, last_synth.csv; raw/ = Originaldateien von SMARD, nur lesen
src/          aller Code: Download, Bereinigung, Lastgang, Fensteranalyse, Board (R2), preisabfrage,
              datenzugriff (R3), Gerüste R3/R4, run_all
docs/         Projekttagebuch, Belegmatrix (Abgaben und Bewertung), Schnittstellen, Codebook, Kickoff
tests/        automatische Prüfungen, vor jedem Commit: pytest tests/
r2/           nur R2, kein Code: ergebnisse/ (Bereinigungsprotokoll, Datenqualität, Tabellen, Grafiken,
              board.html), docs/ (Diagramme, Aufbereitung, Datenkatalog, Sensitivitätsplan)
```

| Datei | Was steht drin | Wer braucht es |
| --- | --- | --- |
| `data/preise_clean.csv` | Strompreis je Stunde 2022–10/2026, bereinigt | alle |
| `data/last_synth.csv` | Verbrauch je Tag: 180 MWh Werk, davon 8 MWh Reinigung | R3, R4 |
| `params.yaml` | alle Annahmen | alle |
| `src/preisabfrage.py` | Tage und Monate ansehen (siehe oben) | alle |
| `src/datenzugriff.py` | Daten je Planungsfreitag für den Backtest, ohne Blick in die Zukunft | R3 |
| `src/03_merkmale.py`, `src/04_strategien.py` | Backtest (noch leer) | R3 |
| `src/05_bewertung.py` | Kosten, Break-even, Empfehlung (noch leer) | R4 |
| `src/run_all.py` | rechnet alles mit einem Befehl neu | alle |
| `src/01_download.py`, `src/02_synthetisch.py`, `src/cleaning.py`, `src/fensteranalyse.py`, `src/build_board.py` | Daten laden, Lastgang, Bereinigung, Rückblick Reinigungsfenster, Board (R2); laufen über `run_all.py` | R2, indirekt alle |
| `docs/projekttagebuch.md` | jede Entscheidung, Absprache, jedes Problem und jeder KI-Einsatz mit Datum | alle |
| `docs/belegmatrix.md` | was wir abgeben müssen, wie bewertet wird, wo wir stehen | alle |
| `docs/schnittstellen.md` | wer liefert welche Datei an wen | alle |
| `docs/codebook.md` | jede Spalte der CSV-Dateien erklärt | alle |
| `docs/kickoff.md` | Fragestellung, Rollen, Testdesign, Plan | alle |

**Endergebnis:** eine einzige Analyseseite wie der Notebook-Prototyp, von den Parametern bis zur Entscheidung für die Betriebsleitung. Folien macht das Team am Ende mit Claude.

## Fragestellung und Hypothesen

Inwiefern lässt sich der Flexibilitätswert verschiebbarer Last eines bayerischen Werks einer international tätigen Großmolkerei am Day-Ahead-Strommarkt DE-LU durch eine wöchentliche Schichtplanung realisieren, und wie verändert die Umstellung auf den Viertelstundenhandel im Oktober 2025 diesen Wert?

- **H0a:** Nach Zuschlägen und Umstellungskosten ist die Netto-Ersparnis gegenüber dem Status quo nicht größer als null.
- **H0b:** Eine wöchentliche Preisprognose realisiert nicht mehr vom Wert als eine feste Zeitregel.
- **H0c:** Der realisierbare Anteil unterscheidet sich nicht zwischen Stunden- und Viertelstundenregime.

Signifikanzniveau nach Bonferroni: α = 0,05 / 3 ≈ 0,017 je Test. Vor der Auswertung festgelegt (Tagebuch E-005, E-006).

## Alles neu berechnen

```bash
pip install -r requirements.txt
python src/run_all.py      # Rohdaten -> Ergebnisse, ein Befehl
pytest tests/              # Prüfung der Datenannahmen
```

Für neue Daten nur `zeitraeume.datenstand` in `params.yaml` ändern.

## Daten, Lizenzen, KI

- Day-Ahead-Großhandelspreise DE-LU: **Bundesnetzagentur | SMARD.de**, Lizenz CC BY 4.0.
- Verbrauch, Betriebszeit, Reinigung, Vertrag und Zuschläge: Angaben des Praxiskontakts (Interview 09.11.2026, Termin 10.11.2026; Zuschläge geschätzt); Status quo, Personal, Stundensatz und Umstellungskosten: **Annahmen des Teams** (alle in `params.yaml`). Keine internen Unternehmensdaten, keine personenbezogenen Daten.
- KI-Einsatz ist gekennzeichnet: Dateikopf, Commit-Trailer `AI-Assisted: Claude`, K-Einträge im [Projekttagebuch](docs/projekttagebuch.md).
