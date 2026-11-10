# Abgabe und Bewertung: was wir brauchen, wie bewertet wird, wo wir stehen

<!-- KI: Claude, Zweck: Übersicht nach dem Original-Kriterienkatalog (Stand 28.09.2026), geprüft von Max (R2) -->

Quelle: Kriterienkatalog für die Projektarbeit, Analyse und Entscheidungsfindung, Stand 28.09.2026 (Abschnittsnummern in Klammern). Der Katalog selbst liegt nicht im Repo. Stand dieser Übersicht: 10.11.2026.

**Grundsatz (1.4, 7.3):** Bewertet wird, ob die Entscheidungen begründet, dokumentiert und kritisch geprüft sind, nicht der Umfang und nicht das Werkzeug. Laut Prof ist auch eine Excel-Lösung gleichwertig (Tagebuch A-013). Deshalb: **so wenig Dokumente wie nötig**, jede Zahl mit Beleg.

## 1. Was abgegeben wird (1.3)

| Abgabe | Umfang | Wer | Stand | Wo |
| --- | --- | --- | --- | --- |
| Analysebericht, ganze Kette von der Frage bis zur Empfehlung | 15–25 Seiten | Team | ⬜ nicht begonnen | später `bericht/` |
| Lauffähiges, reproduzierbares Analyseprojekt (Rohdaten, Aufbereitung, Modellcode, Ergebnisse) | — | Team | 🟨 Daten fertig, Backtest fehlt | dieses Repo, `python src/run_all.py` |
| Abschlusspräsentation | 20 min + Diskussion | Team | ⬜ | später |
| Projekttagebuch mit Entscheidungen, Annahmen, Begründung | — | Team | ✅ laufend | `docs/projekttagebuch.md` |
| Verantwortungsnachweis: eigenes Paket, Entscheidungen, begründete Alternativen, Schnittstellen | 2–3 Seiten | jede Person | ⬜ | je Person |
| Eigenanteil an Code und Dokumenten nachvollziehbar | — | jede Person | 🟨 Git-Verlauf; bisher fast nur R2 | Commits, Dateiköpfe |
| Verteidigung: Fragen zum eigenen Paket und zu den Nachbarpaketen | — | jede Person | ⬜ | mündlich |
| Peer-Einschätzung zu Kriterium 10, je 2–3 Sätze Begründung (6.3) | — | jede Person | ⬜ | vertraulich |

Mehr ist nicht verlangt. Codebook, Schnittstellen und Diagramme sind Belege für K2, K3 und K5, aber keine eigenen Abgaben; im Bericht reicht je ein Verweis.

## 2. Wie bewertet wird (2.1–2.4, 6)

- **Note je Person = 40 % Teamanteil + 60 % Individualanteil.** Team: K1–K9 auf das Gesamtwerk (auf 100 hochgerechnet). Individuell: K1–K10 auf das eigene Paket.
- **Punkte je Kriterium = Stufe (1–5) × Gewicht ÷ 5.** Eine Stufe gibt es nur, wenn alle Stufen darunter erfüllt sind. Stufe 3 ist „solide, vollständig“, Stufe 5 wird nicht regelmäßig vergeben.
- **Noten:** 95–100 Punkte = 1,0 · 90–94 = 1,3 · 85–89 = 1,7 · 80–84 = 2,0 · 75–79 = 2,3 · 70–74 = 2,7 · 65–69 = 3,0 · 60–64 = 3,3 · 55–59 = 3,7 · 50–54 = 4,0.
- **Evidenzprinzip (6.1):** Jede Stufe braucht einen Beleg (Seite im Bericht, Commit, Tagebucheintrag, Antwort in der Verteidigung). Was nicht dokumentiert ist, zählt nicht.
- **Verteidigung entscheidet (6.2):** Widersprechen sich Artefakt und Verteidigung, gilt die Verteidigung. Wer sein Paket nicht erklären kann, hat es nicht verantwortet.
- **KI (6.5):** erlaubt, im Projekttagebuch kennzeichnen (Werkzeug, wofür, wie geprüft). Unerklärlicher Code zählt als nicht erbracht.

**Sperrkriterien (2.4), führen unabhängig von den Punkten zu „nicht bestanden“:**

| Sperrkriterium | Wie wir es absichern | Stand |
| --- | --- | --- |
| Analyse nicht reproduzierbar, Grund nicht dokumentiert | ein Befehl `python src/run_all.py`, Prüfsummen, 51 Tests; Reproduktionstest durch eine Person außerhalb R2 | 🟨 Test durch Dritte offen |
| Datenherkunft oder Datenschutz ungeklärt | SMARD CC BY 4.0 (`data/raw/manifest.csv`), Praxisangaben anonymisiert, keine personenbezogenen Daten | ✅ |
| Fremde Beiträge, Quellen, Werkzeugausgaben nicht gekennzeichnet | Dateikopf `# KI: …`, Commit-Trailer, K-Einträge im Tagebuch | ✅ laufend |
| Person kann eigene Entscheidungen nicht erläutern | jeder erklärt seinen Code selbst; Probelauf mit Kreuzfragen | ⬜ |

## 3. Die zehn Kriterien: was Stufe 5 verlangt und wo wir stehen

Stufe 5 sinngemäß nach dem Katalog, jeweils **zusätzlich** zu allen Stufen darunter.

| K | Kriterium (Gewicht) | Stufe 5 verlangt | Unser Beleg bisher | Fehlt noch | Owner | Stand |
| --- | --- | --- | --- | --- | --- | --- |
| K1 | Fragestellung und fachlicher Rahmen (10) | Rückkopplung mit Praxispartner oder Branchenrecherche; Entscheidung samt Entscheidern und Zeitpunkt benannt; Nullhypothese formuliert | Frage und H0a–H0c (E-005, E-034); Praxisrückkopplung K-005, K-008; Entscheider: zentraler Einkauf und Werksleitung, Planung freitags (K-008) | Problem Statement, Prozessskizze im Bericht | R1 | 🟨 |
| K2 | Datenbeschaffung und Datenqualität (12) | Datenqualität **aktiv geprüft**, z. B. Sensitivitätsrechnung, wie stark das Ergebnis von Datenungenauigkeiten abhängt | Quelle, Lizenz, Prüfsummen, Skalenniveaus, Lücken, Qualitätsbericht (`r2/`) | Sensitivitätsrechnung (`r2/docs/sensitivitaet_plan.md`) | R2 | 🟨 |
| K3 | Datenaufbereitung und Merkmalsbildung (12) | mindestens eine eigene, fachlich begründete Merkmalskonstruktion, die das Ergebnis **messbar** verbessert (z. B. Kalendermerkmal, Aggregation über die Zeit); Ausreißer als Information über den Prozess | Bereinigung mit Log, Ausreißer nur markiert mit Begründung (E-025), Kalendermerkmale | Nachweis in Euro, dass ein Merkmal die Strategie verbessert | R3, R2 | 🟨 |
| K4 | Methodenwahl und statistische Fundierung (12) | Methodenklasse selbst hinterfragt (braucht es eine Prognose, reicht eine einfache Regel?), **mit Daten belegt** | Testdesign, Look-ahead-Schutz (E-020) | Backtest A, B, B′, C, D, T; Baseline-Vergleich; Konfidenzintervalle | R3 | ⬜ |
| K5 | Technische Umsetzung und Reproduzierbarkeit (10) | automatisierte Prüfungen der Datenannahmen, dokumentierte Schnittstellen, Dritte wenden die Analyse ohne Rückfragen auf neue Daten an | 51 Tests, `docs/schnittstellen.md`, fester Seed, ein Befehl | Reproduktionstest durch Dritte | R2 | 🟨 |
| K6 | Ergebnisinterpretation und kritische Prüfung (12) | aktiv Gegenbelege suchen: Scheinkorrelation, zurückgehaltener Zeitraum, Kipppunkte; negatives Ergebnis genauso klar | Testzeiträume und Stresstest 2022 festgelegt | Ergebnisse, Kipppunkte | R4 | ⬜ |
| K7 | Wirtschaftliche Verwertung und Empfehlung (10) | Empfehlung im Prozess: wer entscheidet, auf welcher Grundlage, was anders, welche Kennzahl, wann nachsteuern, wann zurücknehmen | Kostenannahmen in `params.yaml` (E-035) | Wirtschaftlichkeitsrechnung, Empfehlung | R4, R1 | ⬜ |
| K8 | Visualisierung (8) | für den Adressaten ohne Vorlesungswissen verständlich; interaktiv nur mit Erkenntnisgewinn | Grafiken und Board R2 (`r2/ergebnisse/`) | Abbildungen für Bericht und Folien | R1 | 🟨 |
| K9 | Kommunikation und Verteidigung (8) | Schnittstellen zu den Nachbarpaketen erklären, Team als Ganzes vertreten, Fehler und verworfene Wege offen darlegen | verworfene Alternativen in jedem E-Eintrag | Probelauf, Kapitel „Verworfene Wege“ | alle | ⬜ |
| K10 | Teamarbeit (6, nur individuell) | Verantwortung über das eigene Paket hinaus: roter Faden, Zielkonflikte moderieren, einspringen, andere befähigen | Tagebuch, M-001, Reviews durch Susan (A-012), Preisabfrage für Susan (A-011) | Peer-Einschätzung; Beiträge der anderen im Git-Verlauf | jede Person | 🟨 |

Status: ⬜ offen · 🟨 in Arbeit · ✅ belegt
