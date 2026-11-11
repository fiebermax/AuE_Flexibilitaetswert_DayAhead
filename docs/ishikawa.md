# Ishikawa: Warum bleibt Ersparnis gegenüber dem Oracle liegen?

<!-- KI: Claude, Zweck: Ursache-Wirkungs-Diagramm nach Operational Intelligence Teil E (Phase 4), geprüft von Caro (R4) -->

Owner: R4 (Caro). **Wirkung:** Die feste Regel D (3 Uhr) holt im Test 93 % des Oracle-Werts, B_16 94 %, die Prognose B 92 % (`ergebnisse/ki_strategien.csv`). Die Lücke beträgt rund 80–110 € pro Woche. Woher kommt sie? Belegte Ursachen sind mit Datei markiert, die übrigen sind Hypothesen.

```mermaid
flowchart LR
    W["Lücke zum Oracle<br/>D 7 %, B 8 %, rund 90 €/Woche"]

    subgraph Mensch
      M1["Schichtplan steht Freitag 08:00 für 7 Tage fest (P11)"]
      M2["kurzfristiges Personal kostet Aufpreis<br/>Kipppunkt 2,16 €/h (kipppunkte.csv)"]
    end
    subgraph Methode
      ME1["feste Uhrzeit ignoriert, wo das Preistal in der einzelnen Nacht liegt<br/>(Oracle-Start 3 Uhr nur in 39 % der Nächte)"]
      ME2["Prognose aus 4 bzw. 16 Wochen reagiert auf Zufall<br/>B trifft den billigsten Block nur in 24–50 % (fehleranalyse_b.csv)"]
    end
    subgraph Markt
      MA1["Preistal wandert mit Wind und Last (2–4 Uhr)"]
      MA2["Wochenend- und Feiertagsnächte anders geformt"]
      MA3["Krise 2022: größere Spreizung, gleicher Anteil (93 %)"]
    end
    subgraph Daten
      D1["Preise der Folgewoche am Freitag unbekannt<br/>(Auktion erst am Vortag 12:45)"]
      D2["nur Stundenwerte, Blöcke zur vollen Stunde (E-021)"]
    end
    subgraph Messung
      ME3["nur Stromkosten und Personal bewertet;<br/>Umstellungskosten ohne Quelle (Break-even)"]
      ME4["Vertragsfaktor 1,0 oder 0,3 (A3)"]
    end
    subgraph Maschine
      MS1["CIP-Block fest 2 h, 4 MW konstant"]
      MS2["Reinigung nur 22–06 Uhr, Pflicht nach 24 h (P10)"]
    end

    M1 --> W
    M2 --> W
    ME1 --> W
    ME2 --> W
    MA1 --> W
    MA2 --> W
    MA3 --> W
    D1 --> W
    D2 --> W
    ME3 --> W
    ME4 --> W
    MS1 --> W
    MS2 --> W
```

**Lesart:** Die Hauptursache ist **Daten × Mensch**: Am Freitag sind die Preise der Folgewoche unbekannt, und der Schichtplan legt sich trotzdem für 7 Tage fest. Eine bessere Prognose hebt die Lücke nicht: B und B_16 liegen nicht signifikant über D (H0b, E-049). Schließen ließe sich die Lücke nur durch Tagesplanung (C), und die lohnt nur, wenn kurzfristiges Personal weniger als rund 2 € pro Stunde Aufpreis kostet (H0c).
