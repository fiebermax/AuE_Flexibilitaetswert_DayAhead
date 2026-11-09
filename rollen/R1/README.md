# R1 · Projektleitung & Controlling

Arbeitsbereich der Rolle. **Code, Daten und Ergebnisse bleiben in `src/`, `data/`, `results/`**, damit die Pipeline mit einem Befehl läuft (K5). Hier steht, was davon zu dieser Rolle gehört, plus Notizen und der Entwurf des Verantwortungsnachweises.

| | |
| --- | --- |
| Person | offen |
| Kernfrage | Was wollen wir wissen, und wie überzeugen wir? |
| Führt | Fachlicher Rahmen (Frage, Hypothesen, Problem Statement); Aufbereitung & Übergabe (Bericht, Präsentation, Grafikstandard); Spot gegen Festpreis |
| Wirkt mit | Ergebnis & Verwertung (R4) |
| Kriterien | K1, K8, K9, K10 |
| Vertretung | R4 |

## Meine Dateien im Repo

- `config/params.yaml` (Owner aller Annahmen; Review jeder Änderung)
- `docs/belegmatrix.md`
- `docs/kickoff.md`, `docs/projektanweisung.md`
- Bericht (Redaktion), Folien, Grafikstandard; `results/kennzahlen.json` (geplant, Zahlen-Freeze `v1.0`)

## Schnittstellen (Details in `docs/schnittstellen.md`)

**Erhält:**
- Von allen: Ergebnisse, Grafiken, Tabellen in `results/` (Kennzahlen nur aus `results/kennzahlen.json`)
- Von R4: `results/tables/wirtschaftlichkeit.csv` (`szenario`, `ersparnis_eur_jahr`, `umstellungskosten_eur`, `break_even`)

**Übergibt:**
- An alle: `config/params.yaml` (Annahmen, Zeiträume, Kosten)
- An die Prüfer: Bericht, Präsentation, Belegmatrix

## Offene Aufgaben (Stand 09.11.2026)

- [ ] Review des neuen Blocks `daten` in `params.yaml` (Tagebuch A-002)
- [ ] Problem Statement mit H0a–H0c, Prozessskizze der Freitagsplanung
- [ ] 3–5 Literaturquellen zu Lastflexibilität (mit R4)
- [ ] Vorlage und Folienmaster festlegen (K8)
- [ ] Meilensteinprotokolle moderieren (Pitch, Zwischenreview Fr 13.11.)

**Review-Regel:** Kein Merge ohne Review durch R4 (Review-Paar R1 ↔ R4).

## Verantwortungsnachweis (2–3 Seiten, Gliederung laut Kickoff)

1. a) Aufgabenstellung des eigenen Pakets
2. b) Problematik im Paket
3. c) Methode: getroffene Entscheidungen und begründete Alternativen (Verweise auf Tagebuch-E-Einträge)
4. d) Beitrag zum Gesamterfolg, Schnittstellen (erhält von, übergibt an)
5. Eigene Fehler und verworfene Wege (K9 Stufe 5)
6. Belegliste: Commits, Tagebucheinträge, Berichtsseiten

## Notizen

*(Arbeitsnotizen, Ideen, offene Fragen. Entscheidungen und Absprachen gehören zusätzlich ins `docs/projekttagebuch.md`.)*
