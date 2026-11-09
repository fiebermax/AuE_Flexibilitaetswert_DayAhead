# AuE-Projekt: Flexibilitätswert am Day-Ahead-Strommarkt

Modul Analyse und Entscheidungsfindung, Hochschule München, WS 26/27. Team aus 4 Personen.

**Worum es geht:** Eine Großmolkerei in Bayern kauft Strom zum Day-Ahead-Preis, der jede Stunde anders ist und erst am Vortag feststeht. Die Schichten werden aber schon freitags für die ganze Woche geplant. Wir spielen mit echten Preisen von 2022 bis 2026 nach, wie viel Geld sie gespart hätte, wenn sie ihre stromintensive Produktion jeden Freitag in die voraussichtlich billigsten Stunden gelegt hätte.

## Daten ansehen (ohne das Repo zu kennen)

Alle fertigen Daten liegen als **CSV** in `data/processed/`. Öffnen mit Excel oder pandas:

| Datei | Inhalt |
| --- | --- |
| [`data/processed/preise_h.csv`](data/processed/preise_h.csv) | Strompreis für jede Stunde, 01.01.2022 bis 31.10.2026: `zeit`, `datum`, `stunde`, `preis_eur_mwh`, `regime`, `werktag` |
| [`data/processed/last_synth.csv`](data/processed/last_synth.csv) | Stromverbrauch der Molkerei pro Tag (angenommen): `datum`, `mwh` |
| [`results/tables/datenqualitaet.csv`](results/tables/datenqualitaet.csv) | Kennzahlen je Jahr: Stunden, Lücken, negative Preise, Durchschnittspreis |

```python
import pandas as pd
preise = pd.read_csv("data/processed/preise_h.csv")
preise.groupby("stunde")["preis_eur_mwh"].mean()   # Durchschnittspreis je Uhrzeit
```

Spalten und Einheiten im Detail: [`docs/schnittstellen.md`](docs/schnittstellen.md).

## Wo was liegt

| Ordner | Inhalt |
| --- | --- |
| `data/processed/` | **fertige Daten als CSV** (siehe oben) |
| `docs/` | [Projekttagebuch](docs/projekttagebuch.md), [Kickoff](docs/kickoff.md), Schnittstellen, Datenkatalog |
| `config/params.yaml` | alle Annahmen (Zeiträume, Verbrauch, Kosten) |
| `src/` | die Programme (`01_download`, `02_aufbereitung`, …) |
| `data/raw/` | Original-Rohdaten von SMARD, nicht anfassen |
| `tests/`, `results/`, `notebooks/` | automatische Prüfungen, Ergebnisse, Ausprobieren |

## Fragestellung und Hypothesen

Inwiefern lässt sich der Flexibilitätswert verschiebbarer Produktionslast eines bayerischen Werks einer international tätigen Großmolkerei am Day-Ahead-Strommarkt DE-LU durch eine wöchentliche Schichtplanung realisieren, und wie verändert die Umstellung auf den Viertelstundenhandel im Oktober 2025 diesen Wert?

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

Für neue Daten nur `zeitraeume.datenstand` in `config/params.yaml` ändern.

## Daten, Lizenzen, KI

- Day-Ahead-Großhandelspreise DE-LU: **Bundesnetzagentur | SMARD.de**, Lizenz CC BY 4.0.
- Verbrauch, Kosten und Betriebsdaten: **synthetisch**, per Skript erzeugt und mit einem Praxisvertreter plausibilisiert. Keine internen Unternehmensdaten, keine personenbezogenen Daten.
- KI-Einsatz ist gekennzeichnet: Dateikopf, Commit-Trailer `AI-Assisted: Claude`, [`docs/ki-nutzung.md`](docs/ki-nutzung.md).
