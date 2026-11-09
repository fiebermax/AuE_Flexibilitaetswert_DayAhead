# R1 · Projektleitung & Controlling

Arbeitsbereich der Rolle: alle Aufgaben mit Status und Beleg. **Code, Daten und Ergebnisse liegen in `src/`, `data/`, `results/`** (Pipeline mit einem Befehl, K5); die Links unten führen direkt zu den Dateien.

Status: ✅ erledigt · 🟨 in Arbeit · ⬜ offen. Stand 09.11.2026.

| | |
| --- | --- |
| Person | offen |
| Kernfrage | Was wollen wir wissen, und wie überzeugen wir? |
| Führt | Fachlicher Rahmen (Frage, Hypothesen, Problem Statement); Aufbereitung & Übergabe (Bericht, Präsentation, Grafikstandard); Spot gegen Festpreis |
| Wirkt mit | Ergebnis & Verwertung (R4) |
| Kriterien | K1, K8, K9, K10 |
| Vertretung | R4 |
| Review-Partner | R4 (kein Merge nach `main` ohne dessen Review) |

## Aufgaben (0 von 14 erledigt)

| # | Aufgabe | Ergebnis / Datei | Termin | Status | Beleg / Hinweis |
| --- | --- | --- | --- | --- | --- |
| 1 | Rollen verteilen, Personen eintragen (alle) | Kickoff, Tagebuch E-001 | Sa 07.11. | 🟨 | R2 = Max; R1, R3, R4 offen |
| 2 | Steckbrief festzurren; Problem Statement mit H0a, H0b (mit R4) | Folien 1 und 2 | So 08.11. | ⬜ |  |
| 3 | Eigene Rolle im Format a) bis d) | Folie 5 | Mo 09.11. | ⬜ |  |
| 4 | Probelauf Pitch moderieren; Meilensteinprotokoll | Tagebuch M-xxx | vor/am Pitch | ⬜ |  |
| 5 | Review neuer Block `daten` in `params.yaml` | [`config/params.yaml`](../../config/params.yaml) | vor 13.11. | ⬜ | Tagebuch A-002 |
| 6 | Prozessskizze der Freitagsplanung (wer, womit, wann) | Bericht Kap. 2 | vor 13.11. | ⬜ | K1 S3 |
| 7 | 3–5 Literaturquellen zu Lastflexibilität (mit R4) | Quellenliste | vor 13.11. | ⬜ | K1 S5 |
| 8 | Vorlage und Folienmaster, Grafikstandard | Vorlage | ab 12.11. | ⬜ | K8 |
| 9 | Zwischenreview moderieren; Belegmatrix aktualisieren | [`docs/belegmatrix.md`](../../docs/belegmatrix.md) | Fr 13.11. | ⬜ |  |
| 10 | Spot gegen Festpreis (mit R4) | Wirtschaftlichkeitsrechnung | So 15.11. | ⬜ | K7 |
| 11 | Folien Endpräsentation | Folien | So 15.11. | ⬜ |  |
| 12 | `results/kennzahlen.json`, Zahlen-Freeze Git-Tag `v1.0` | results/kennzahlen.json | vor dem Bericht | ⬜ | K5, Evidenzprinzip |
| 13 | Bericht: Redaktion, Kap. 1 und 2 | Bericht | bis Abgabe | ⬜ |  |
| 14 | Verantwortungsnachweis | diese Datei, Abschnitt unten | bis Abgabe | ⬜ |  |

## Schnittstellen (Details in `docs/schnittstellen.md`)

**Erhält:**
- Von allen: Ergebnisse, Grafiken, Tabellen in `results/`
- Von R4: `results/tables/wirtschaftlichkeit.csv`

**Übergibt:**
- An alle: `config/params.yaml` (Annahmen, Zeiträume, Kosten)
- An die Prüfer: Bericht, Präsentation, Belegmatrix

## Verantwortungsnachweis (2–3 Seiten, Gliederung laut Kickoff)

1. a) Aufgabenstellung des eigenen Pakets
2. b) Problematik im Paket
3. c) Methode: getroffene Entscheidungen und begründete Alternativen (Verweise auf Tagebuch-E-Einträge)
4. d) Beitrag zum Gesamterfolg, Schnittstellen (erhält von, übergibt an)
5. Eigene Fehler und verworfene Wege (K9 Stufe 5)
6. Belegliste: Commits, Tagebucheinträge, Berichtsseiten

## Notizen

*(Arbeitsnotizen, Ideen, offene Fragen. Entscheidungen und Absprachen gehören zusätzlich ins `docs/projekttagebuch.md`.)*
