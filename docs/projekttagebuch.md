# Projekttagebuch

Ein Eintrag pro Entscheidung, Problem, Meilenstein, Absprache oder KI-Einsatz. Neueste Einträge oben. Jeder Eintrag wird von der Person committet, die ihn verfasst. Entscheidungen aus dem WhatsApp-Chat werden innerhalb von 24 Stunden hier eingetragen.

Eintragsarten: **E** Entscheidung · **P** Problem/Konflikt · **M** Meilensteinprotokoll · **A** Absprache/Schnittstelle · **K** KI-Einsatz und Rückkopplung

---

## 07.11.2026

### E-007 · Abgrenzung auf Day-Ahead, kein Intraday
- **Person:** Max
- **Entscheidung:** Analyse nur mit Day-Ahead-Preisen DE-LU.
- **Verworfen:** Intraday-Preise einbeziehen.
- **Begründung:** Schichtplan steht eine Woche vorher fest, Intraday-Preise sind erst Stunden vorher bekannt; Spotverträge orientieren sich üblicherweise am Day-Ahead-Preis (Annahme, belegen); Intraday braucht aktives Trading. Intraday als Ausblick.
- **Beleg:** `config/params.yaml` (markt.produkt)

### E-006 · Mehrfachtest-Korrektur
- **Person:** Max
- **Entscheidung:** Bonferroni, α = 0,05 / 3 ≈ 0,017 je Hypothese.
- **Verworfen:** α = 0,05 je Test (Risiko eines Zufallstreffers über drei Tests fast 15 %).
- **Beleg:** `config/params.yaml` (statistik)

### E-005 · Fragestellung und Nullhypothesen festgelegt (vor jeder Auswertung)
- **Person:** Max (Vorschlag), Team (Bestätigung offen)
- **Entscheidung:** Fragestellung und H0a, H0b, H0c wie im README.
- **Verworfen:** Ja/Nein-Frage „Senkt ein Betrieb … seine Energiekosten?“ (nicht offen, kein Rahmen, keine Methode erkennbar); Fokus auf Kälteerzeugung (täglich automatisch steuerbar, Wochenplanung wäre unbegründet; bleibt Kontrastfall T).
- **Begründung:** Analysefrage mit räumlichem, zeitlichem und thematischem Rahmen; Begriffe operationalisiert (siehe Kickoff-Dokument).

### E-004 · Praxisfall Großmolkerei
- **Person:** Max
- **Entscheidung:** Szenario angelehnt an ein bayerisches Werk eines realen Praxispartners; im Bericht „Großmolkerei in Bayern“, Name nur mit schriftlicher Freigabe.
- **Verworfen:** fiktive Galvanik (keine Rückkopplung möglich); Siemens Energy (kaum flexible Last, Vertraulichkeit).
- **Begründung:** Max hat einen Kontakt im Werk (Elektriker) für die Rückkopplung (K1 Stufe 5).

### E-003 · Daten: echt, wo möglich, synthetisch, wo nötig
- **Person:** Max
- **Entscheidung:** Preise echt von SMARD; Lastgang, Kosten und Betriebsdaten synthetisch mit festem Seed.
- **Verworfen:** Preise generieren (Prüfungen fänden nur, was wir hineinstecken; entwertet K2 und K6).
- **Grundlage:** Der Prof hat die Nutzung generierter Daten in der Vorlesung am **[Datum eintragen]** erlaubt; Max war anwesend. **[Folie oder Moodle-Link eintragen, falls vorhanden]**

### P-001 · Unklar, ob generierte Daten erlaubt sind
- **Problem:** Erlaubnis zunächst nur aus dem Gruppenchat bekannt, Quelle unklar; Sperrkriterium Datenherkunft.
- **Angesprochen von:** Max, 07.11.2026
- **Lösungsvorschlag:** Prof direkt fragen.
- **Ergebnis:** Gelöst. Max bestätigt, dass der Prof es in der Vorlesung erlaubt hat (siehe E-003).

### E-002 · Prototyp nur als Machbarkeitsnachweis
- **Person:** Max
- **Entscheidung:** Der vorhandene Notebook-Prototyp gilt als Machbarkeitsnachweis. Seine Zahlen sind Hypothesen, keine Ergebnisse. Jedes Paket wird vom Owner neu aufgebaut.
- **Verworfen:** Prototyp direkt übernehmen (Eigenanteil je Person nicht nachweisbar).

### K-001 · KI-Einsatz bei Themenfindung und Planung
- **Werkzeug:** Claude
- **Zweck:** Prototyp-Notebook (SMARD-Download, Backtest), Kickoff-Dokument, Abgleich mit dem Kriterienkatalog, Formulierung der Fragestellung.
- **Prüfung:** Abgleich mit Kriterienkatalog und Kursmaterial durch das Team; Prototyp-Zahlen ausdrücklich nicht als Ergebnis übernommen.

### E-001 · Rollen und Teilpakete
- **Person:** Team
- **Entscheidung:** Vier Rollen R1 bis R4 mit zusammengelegten Teilpaketen (Katalog 1.2), Vertretungen R1↔R4, R2↔R3. Personen: **[eintragen]**.

### A-001 · Termine
- Case- und Rollen-Pitch: **[Datum eintragen]**
- Analyse fertig: So 15.11.2026
- Endpräsentation: ab 16.11.2026, Termin **[eintragen]**
- Abgabe Bericht: **[eintragen]**
- Praxisgespräch: Sonntag 08.11. oder Montag 09.11.2026

---

## Vorlagen

### E-xxx · Titel
- **Person:**
- **Entscheidung:**
- **Verworfen:**
- **Begründung:**
- **Beleg:** (Commit, Datei, Berichtsseite)

### P-xxx · Titel
- **Problem:**
- **Angesprochen von:** (Person, Datum)
- **Lösungsvorschlag:**
- **Entscheidung:**
- **Ergebnis:**

### M-xxx · Meilenstein: Titel, Datum
| Paket | Stand | Rückstand | Maßnahme | Owner | bis |
| --- | --- | --- | --- | --- | --- |
| R1 | | | | | |
| R2 | | | | | |
| R3 | | | | | |
| R4 | | | | | |

### A-xxx · Absprache/Schnittstelle
- **Von → an:**
- **Was (Datei, Spalten, Einheit):**
- **Bis:**
- **Änderung, nachgezogen von:**

### K-xxx · KI-Einsatz oder Rückkopplung
- **Werkzeug bzw. Gesprächspartner:**
- **Zweck bzw. Aussage:**
- **Wie geprüft bzw. was wir geändert haben:**
