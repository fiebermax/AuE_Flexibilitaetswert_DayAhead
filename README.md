# AuE-Projekt: Flexibilitätswert am Day-Ahead-Strommarkt

Modul Analyse und Entscheidungsfindung, Hochschule München, WS 26/27. Team aus 4 Personen.

## Fragestellung

Inwiefern lässt sich der Flexibilitätswert verschiebbarer Produktionslast eines bayerischen Werks einer international tätigen Großmolkerei am Day-Ahead-Strommarkt DE-LU durch eine wöchentliche Schichtplanung realisieren, und wie verändert die Umstellung auf den Viertelstundenhandel im Oktober 2025 diesen Wert?

*Backtest-Analyse auf Basis der SMARD-Marktdaten 2022 bis 2026 (Datenstand Oktober 2026).*

Nullhypothesen (vor der Auswertung festgelegt, siehe `docs/projekttagebuch.md`):

- **H0a:** Nach Zuschlägen und Umstellungskosten ist die Netto-Ersparnis gegenüber dem Status quo nicht größer als null.
- **H0b:** Eine wöchentliche Preisprognose realisiert nicht mehr vom Wert als eine feste Zeitregel.
- **H0c:** Der realisierbare Anteil unterscheidet sich nicht zwischen Stunden- und Viertelstundenregime.

Signifikanzniveau nach Bonferroni: α = 0,05 / 3 ≈ 0,017 je Test.

## Ausführung

```bash
pip install -r requirements.txt
python src/run_all.py      # Rohdaten -> Ergebnisse, ein Befehl
pytest tests/              # Prüfung der Datenannahmen
```

Alle Annahmen (Last, Zeiträume, Kosten, Seed) stehen in `config/params.yaml`. Für neue Daten nur dort den Zeitraum ändern.

## Struktur

| Ordner | Inhalt |
| --- | --- |
| `config/` | Alle Parameter und Annahmen |
| `data/raw/` | Rohdaten, unverändert, mit Herkunft in `SOURCES.md` |
| `data/interim/`, `data/processed/` | Zwischenstände und aufbereitete Daten (werden erzeugt) |
| `src/` | Pipeline in getrennten Schritten `01_` bis `05_` |
| `tests/` | Automatisierte Prüfungen der Datenannahmen |
| `notebooks/` | Nur Exploration, nichts Ergebnisrelevantes |
| `results/` | Grafiken und Tabellen (werden erzeugt) |
| `rollen/` | Ein Bereich je Rolle R1–R4: eigene Dateien, Schnittstellen, offene Aufgaben, Verantwortungsnachweis |
| `docs/` | Kickoff, Projektanweisung (KI-Coach), Projekttagebuch, Belegmatrix, KI-Nutzung, Datenkatalog, Schnittstellen |

## Daten und Lizenzen

- Day-Ahead-Großhandelspreise DE-LU: Bundesnetzagentur | SMARD.de, Lizenz CC BY 4.0.
- Lastgang, Kosten und Betriebsdaten: **synthetisch**, per Skript mit festem Seed erzeugt und mit einem Praxisvertreter plausibilisiert. Das Szenario ist an eine Großmolkerei angelehnt; es werden keine internen Unternehmensdaten verwendet.
- Keine personenbezogenen Daten.

## KI-Nutzung

KI-Werkzeuge werden eingesetzt und gekennzeichnet: Dateikopf, Commit-Trailer `AI-Assisted: Claude` und `docs/ki-nutzung.md`.
