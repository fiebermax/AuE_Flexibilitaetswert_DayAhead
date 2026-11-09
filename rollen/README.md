# Rollenbereiche

Ein Ordner je Rolle mit **Aufgabenliste (Status, Termin, Beleg, Link zur Datei)**, Schnittstellen, offenen Aufgaben, Notizen und dem Entwurf des Verantwortungsnachweises. Code, Daten und Ergebnisse bleiben nach Arbeitsschritten in `src/`, `data/`, `results/` (Pipeline `01_` bis `05_`, K5); die Zuordnung zu Rollen steht hier und in `.github/CODEOWNERS`.

| Rolle | Person | Ordner | Pipeline-Schritte | Review-Partner |
| --- | --- | --- | --- | --- |
| R1 Projektleitung & Controlling | offen | [`R1/`](R1/README.md) | `config/`, Bericht, Folien | R4 |
| R2 Datenanalyse & IT | Max | [`R2/`](R2/README.md) | `01_download`, `02_aufbereitung`, `02_synthetisch`, `tests/` | R3 |
| R3 Energieeinkauf | offen | [`R3/`](R3/README.md) | `03_merkmale`, `04_strategien` | R2 |
| R4 Produktion & Schichtplanung | offen | [`R4/`](R4/README.md) | `05_bewertung` | R1 |

Entscheidungen und Absprachen gehören immer zusätzlich ins `docs/projekttagebuch.md` (nur dort zählen sie als Beleg).
