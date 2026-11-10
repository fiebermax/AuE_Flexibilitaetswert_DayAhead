# Arbeitsregeln für Claude in diesem Repo

AuE-Projekt (HM, WS 26/27). Maßstab: Stufe 5 in K1–K10, siehe `docs/belegmatrix.md` (Kriterienkatalog) und `docs/kickoff.md` (Plan, Testdesign, Arbeitsanweisung an die KI am Ende).

## Kommunikation immer dokumentieren (wichtigste Regel)
- Jede Absprache, Nachricht, Frage oder Antwort zwischen Rollen (auch per WhatsApp vorbereitete Nachrichten) kommt **sofort** mit Datum ins `docs/projekttagebuch.md`: Absprache/Schnittstelle als **A-xxx**, Problem/Konflikt als **P-xxx**, KI-Einsatz und Praxisrückkopplung als **K-xxx**, Meilensteine als **M-xxx**, Entscheidungen als **E-xxx** (mit verworfener Alternative).
- Antworten anderer Rollen werden im bestehenden Eintrag nachgetragen (Datum, Inhalt, was geändert wurde, Commit).
- Was nur im Chat steht, ist kein Beleg (Kickoff). Ohne Beleg keine Stufe.

## Weitere Regeln
- Tagebucheinträge trägt Claude im Auftrag von Max (R2) ein; das ist in K-002 offengelegt.
- Belege immer mit Commit-Hash, Datei oder Test angeben.
- Firmenname des Praxispartners nie ins (öffentliche) Repo; „Praxispartner“ bzw. „Großmolkerei in Bayern“.
- Einfach halten: so wenig Dateien und Ordner wie nötig; Umfang und Werkzeug werden nicht bewertet (Katalog 7.3, A-013).
- KI-Kennzeichnung: Dateikopf `# KI: Claude, Zweck …, geprüft von …`, Commit-Trailer `AI-Assisted: Claude`, K-Eintrag im Projekttagebuch (Katalog 6.5; eigene KI-Liste entfällt, E-039).
- Kein Merge nach `main` ohne Review des Paarpartners (P-003), außer Max verlangt es ausdrücklich; dann im Tagebuch festhalten.
- Code-Kommentare auf Englisch, pro Abschnitt, mit dem Warum; Max muss den Code in der Verteidigung erklären können.
- Vor jedem Commit `pytest tests/`; Prototyp-Zahlen sind Hypothesen, keine Ergebnisse.
