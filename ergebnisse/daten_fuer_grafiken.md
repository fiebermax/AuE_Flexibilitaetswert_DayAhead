# Alle Daten für Grafiken, Folien und Bericht

<!-- KI: Claude, Zweck: alle Kennzahlen in einer Datei für Grafiken in Claude (E-052), erzeugt von src/07_bericht.py, geprüft von Chiara (R1) -->

Erzeugt von `src/07_bericht.py` bei jedem `python src/run_all.py` aus den Ergebnisdateien; nichts von Hand eingetragen. Zahlen mit Dezimalpunkt. € = Euro. Strategien: **A** Status quo 22–24 Uhr · **D** fest 3 Uhr (FS1, Empfehlung) · **B** jede Woche neu aus 4 Wochen (Median) · **B_16** jede Woche neu aus 16 Wochen (FS2) · **C** Oracle = Tagesplanung (Obergrenze) · D_saison = D je Saison (identisch mit D) · B_ohne_wochentag = Kontrolle für K3. Zeiträume: training 2023–2024 · test_1_stunde 01–09/2025 · test_2_viertel 10/2025–09/2026 · test_gesamt = beide Tests (89 Wochen, Testentscheidung nur hier) · stresstest 2022. Vertrag: band = alle verschobenen MWh am Spot (Basis), proportional = nur 30 %. Annahmen: `docs/annahmen.md`.

## Kernaussagen

- Fest 3 Uhr spart netto 62 351 € pro Jahr (30 %-Fall 18 770 €), 93 % des Möglichen; H0a verworfen (p < 0.001).
- Eine wöchentliche Prognose (B, B_16) ist nicht signifikant besser als fest 3 Uhr (H0b nicht verworfen).
- Tagesplanung lohnt nur, wenn kurzfristiges Personal weniger als rund 2 € pro Stunde Aufpreis kostet (H0c, Kipppunkt).
- Kipppunkt der Empfehlung: mehr als 1.3 h (30 %-Fall 0.4 h) bezahlte Wartezeit je Person und Nacht.
- In keiner Woche 2022–2026 war 3 Uhr teurer als 22 Uhr; keine Sensitivitätsvariante kippt eine Entscheidung.

## 1 Preistal der Nacht: mittlerer Preis des 2-h-Blocks je Startuhrzeit (€/MWh)
Quelle: `ergebnisse/blockkosten_nacht.csv`. Grafikidee: Linien je Zeitraum über die Startuhrzeit.

| start_uhr | 2022 Krise | 2023-2024 Training | 2025-2026 Test |
| --- | --- | --- | --- |
| 22 | 242.9 | 91.4 | 116.9 |
| 23 | 222.7 | 83.3 | 107.7 |
| 0 | 209.5 | 78.2 | 102.5 |
| 1 | 198.6 | 73.9 | 98.0 |
| 2 | 192.0 | 71.5 | 95.5 |
| 3 | 190.7 | 70.8 | 95.4 |
| 4 | 199.2 | 74.0 | 98.9 |

Je Jahr:

| start_uhr | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | --- | --- | --- | --- |
| 22 | 242.9 | 99.7 | 83.2 | 98.8 | 138.8 |
| 23 | 222.7 | 90.9 | 75.8 | 91.0 | 127.9 |
| 0 | 209.5 | 85.1 | 71.4 | 86.4 | 121.9 |
| 1 | 198.6 | 80.6 | 67.3 | 82.3 | 117.0 |
| 2 | 192.0 | 77.8 | 65.2 | 80.2 | 113.9 |
| 3 | 190.7 | 76.9 | 64.7 | 80.3 | 113.7 |
| 4 | 199.2 | 80.3 | 67.7 | 84.1 | 116.8 |

## 2 Ersparnis je Strategie gegenüber A, nur Strom (€/Woche, 95-%-Intervall)
Quelle: `ergebnisse/ki_strategien.csv`.

| strategie | periode | n_wochen | mittel_eur_woche | ki_unten | ki_oben | boot_unten | boot_oben | eur_jahr | anteil_oracle |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D | stresstest | 51 | 2943.348 | 2449.119 | 3437.576 | 2154.387 | 3953.786 | 153054.068 | 0.934 |
| D_saison | stresstest | 51 | 2943.348 | 2449.119 | 3437.576 | 2154.387 | 3953.786 | 153054.068 | 0.934 |
| B | stresstest | 46 | 2989.187 | 2443.896 | 3534.478 | 2151.833 | 4062.96 | 155437.722 | 0.908 |
| B_ohne_wochentag | stresstest | 46 | 3001.173 | 2470.652 | 3531.694 | 2191.704 | 4044.38 | 156060.998 | 0.911 |
| B_16 | stresstest | 34 | 3677.307 | 3094.594 | 4260.02 | 2812.493 | 4784.405 | 191219.967 | 0.956 |
| C | stresstest | 51 | 3152.271 | 2665.795 | 3638.748 | 2385.017 | 4155.065 | 163918.111 | 1.0 |
| D | test_1_stunde | 38 | 1093.077 | 958.846 | 1227.308 | 928.202 | 1326.513 | 56839.996 | 0.92 |
| D_saison | test_1_stunde | 38 | 1093.077 | 958.846 | 1227.308 | 928.202 | 1326.513 | 56839.996 | 0.92 |
| B | test_1_stunde | 38 | 1082.04 | 947.295 | 1216.785 | 916.597 | 1319.193 | 56266.08 | 0.911 |
| B_ohne_wochentag | test_1_stunde | 38 | 1094.607 | 966.042 | 1223.172 | 931.476 | 1326.755 | 56919.583 | 0.921 |
| B_16 | test_1_stunde | 38 | 1108.857 | 975.574 | 1242.14 | 943.802 | 1342.936 | 57660.556 | 0.933 |
| C | test_1_stunde | 38 | 1188.167 | 1053.357 | 1322.978 | 1025.23 | 1424.947 | 61784.703 | 1.0 |
| D | test_2_viertel | 51 | 1274.922 | 1053.145 | 1496.698 | 939.608 | 1615.356 | 66295.922 | 0.936 |
| D_saison | test_2_viertel | 51 | 1274.922 | 1053.145 | 1496.698 | 939.608 | 1615.356 | 66295.922 | 0.936 |
| B | test_2_viertel | 51 | 1251.054 | 1027.872 | 1474.237 | 902.668 | 1602.935 | 65054.814 | 0.919 |
| B_ohne_wochentag | test_2_viertel | 51 | 1265.325 | 1043.966 | 1486.684 | 927.596 | 1607.552 | 65796.885 | 0.929 |
| B_16 | test_2_viertel | 51 | 1280.542 | 1061.948 | 1499.136 | 946.286 | 1616.737 | 66588.182 | 0.94 |
| C | test_2_viertel | 51 | 1361.671 | 1143.08 | 1580.262 | 1026.723 | 1704.594 | 70806.871 | 1.0 |
| D | training | 104 | 1162.368 | 1064.792 | 1259.943 | 1018.086 | 1294.785 | 60443.12 | 0.934 |
| D_saison | training | 104 | 1162.368 | 1064.792 | 1259.943 | 1018.086 | 1294.785 | 60443.12 | 0.934 |
| B | training | 104 | 1131.567 | 1035.589 | 1227.545 | 986.409 | 1266.571 | 58841.48 | 0.91 |
| B_ohne_wochentag | training | 104 | 1139.208 | 1041.832 | 1236.584 | 996.86 | 1270.146 | 59238.82 | 0.916 |
| B_16 | training | 104 | 1148.815 | 1052.856 | 1244.774 | 1007.507 | 1281.36 | 59738.4 | 0.924 |
| C | training | 104 | 1243.867 | 1145.386 | 1342.347 | 1097.738 | 1378.806 | 64681.08 | 1.0 |
| D | test_gesamt | 89 | 1197.28 | 1058.892 | 1335.668 | 983.731 | 1404.714 | 62258.56 | 0.93 |
| D_saison | test_gesamt | 89 | 1197.28 | 1058.892 | 1335.668 | 983.731 | 1404.714 | 62258.56 | 0.93 |
| B | test_gesamt | 89 | 1178.891 | 1039.876 | 1317.906 | 957.73 | 1398.395 | 61302.321 | 0.916 |
| B_ohne_wochentag | test_gesamt | 89 | 1192.434 | 1055.35 | 1329.518 | 976.16 | 1401.712 | 62006.576 | 0.926 |
| B_16 | test_gesamt | 89 | 1207.238 | 1070.778 | 1343.698 | 994.767 | 1413.76 | 62776.386 | 0.938 |
| C | test_gesamt | 89 | 1287.591 | 1150.848 | 1424.333 | 1075.295 | 1497.074 | 66954.709 | 1.0 |

## 3 Netto nach Personalkosten (€/Woche) und H0a
Quelle: `ergebnisse/netto_tests.csv`. Grafikidee: Balken je Strategie mit Intervall (test_gesamt).

| strategie | periode | vertrag | strom_ersparnis_eur_woche | personal_mehr_eur_woche | netto_eur_woche | ki_unten | ki_oben | netto_eur_jahr | p_t | p_wilcoxon | h0_verworfen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C | stresstest | band | 3152.27 | -0.51 | 3152.79 | 2668.08 | 3637.49 | 163944.88 | 0.0 | 0.0 | True |
| D | stresstest | band | 2943.35 | 3.09 | 2940.26 | 2447.11 | 3433.41 | 152893.48 | 0.0 | 0.0 | True |
| B | stresstest | band | 2989.19 | 1.71 | 2987.48 | 2444.42 | 3530.53 | 155348.7 | 0.0 | 0.0 | True |
| B_16 | stresstest | band | 3677.31 | 4.63 | 3672.67 | 3090.47 | 4254.88 | 190979.08 | 0.0 | 0.0 | True |
| B | test_1_stunde | band | 1082.04 | -4.14 | 1086.18 | 951.78 | 1220.59 | 56481.61 | 0.0 | 0.0 | True |
| B_16 | test_1_stunde | band | 1108.86 | -4.14 | 1113.0 | 979.52 | 1246.49 | 57876.08 | 0.0 | 0.0 | True |
| C | test_1_stunde | band | 1188.17 | -4.14 | 1192.31 | 1058.06 | 1326.57 | 62000.23 | 0.0 | 0.0 | True |
| D | test_1_stunde | band | 1093.08 | -4.14 | 1097.22 | 962.78 | 1231.66 | 57055.52 | 0.0 | 0.0 | True |
| B | test_2_viertel | band | 1251.05 | 1.03 | 1250.02 | 1027.33 | 1472.72 | 65001.28 | 0.0 | 0.0 | True |
| B_16 | test_2_viertel | band | 1280.54 | 0.0 | 1280.54 | 1062.58 | 1498.5 | 66588.18 | 0.0 | 0.0 | True |
| C | test_2_viertel | band | 1361.67 | 0.0 | 1361.67 | 1143.62 | 1579.72 | 70806.87 | 0.0 | 0.0 | True |
| D | test_2_viertel | band | 1274.92 | 0.0 | 1274.92 | 1053.8 | 1496.04 | 66295.92 | 0.0 | 0.0 | True |
| B | training | band | 1131.57 | -1.01 | 1132.58 | 1035.95 | 1229.2 | 58893.98 | 0.0 | 0.0 | True |
| B_16 | training | band | 1148.82 | 0.0 | 1148.82 | 1052.17 | 1245.46 | 59738.4 | 0.0 | 0.0 | True |
| C | training | band | 1243.87 | 0.0 | 1243.87 | 1145.35 | 1342.38 | 64681.08 | 0.0 | 0.0 | True |
| D | training | band | 1162.37 | 0.0 | 1162.37 | 1064.16 | 1260.58 | 60443.12 | 0.0 | 0.0 | True |
| B | test_gesamt | band | 1178.89 | -1.18 | 1180.07 | 1041.43 | 1318.71 | 61363.67 | 0.0 | 0.0 | True |
| B_16 | test_gesamt | band | 1207.24 | -1.77 | 1209.01 | 1072.89 | 1345.12 | 62868.41 | 0.0 | 0.0 | True |
| C | test_gesamt | band | 1287.59 | -1.77 | 1289.36 | 1153.04 | 1425.68 | 67046.73 | 0.0 | 0.0 | True |
| D | test_gesamt | band | 1197.28 | -1.77 | 1199.05 | 1061.02 | 1337.08 | 62350.58 | 0.0 | 0.0 | True |
| C | stresstest | proportional | 945.68 | -0.51 | 946.2 | 801.28 | 1091.11 | 49202.2 | 0.0 | 0.0 | True |
| D | stresstest | proportional | 883.0 | 3.09 | 879.92 | 732.08 | 1027.75 | 45755.63 | 0.0 | 0.0 | True |
| B | stresstest | proportional | 896.76 | 1.71 | 895.04 | 733.01 | 1057.08 | 46542.29 | 0.0 | 0.0 | True |
| B_16 | stresstest | proportional | 1103.19 | 4.63 | 1098.56 | 923.34 | 1273.78 | 57125.11 | 0.0 | 0.0 | True |
| B | test_1_stunde | proportional | 324.61 | -4.14 | 328.76 | 285.64 | 371.87 | 17095.35 | 0.0 | 0.0 | True |
| B_16 | test_1_stunde | proportional | 332.66 | -4.14 | 336.8 | 293.59 | 380.01 | 17513.69 | 0.0 | 0.0 | True |
| C | test_1_stunde | proportional | 356.45 | -4.14 | 360.59 | 317.53 | 403.66 | 18750.94 | 0.0 | 0.0 | True |
| D | test_1_stunde | proportional | 327.92 | -4.14 | 332.07 | 288.58 | 375.55 | 17267.53 | 0.0 | 0.0 | True |
| B | test_2_viertel | proportional | 375.32 | 1.03 | 374.29 | 306.99 | 441.58 | 19462.91 | 0.0 | 0.0 | True |
| B_16 | test_2_viertel | proportional | 384.16 | 0.0 | 384.16 | 318.38 | 449.94 | 19976.45 | 0.0 | 0.0 | True |
| C | test_2_viertel | proportional | 408.5 | 0.0 | 408.5 | 342.57 | 474.43 | 21242.06 | 0.0 | 0.0 | True |
| D | test_2_viertel | proportional | 382.48 | 0.0 | 382.48 | 315.77 | 449.18 | 19888.78 | 0.0 | 0.0 | True |
| B | training | proportional | 339.47 | -1.01 | 340.48 | 309.75 | 371.21 | 17704.94 | 0.0 | 0.0 | True |
| B_16 | training | proportional | 344.64 | 0.0 | 344.64 | 313.9 | 375.39 | 17921.52 | 0.0 | 0.0 | True |
| C | training | proportional | 373.16 | 0.0 | 373.16 | 342.35 | 403.97 | 19404.32 | 0.0 | 0.0 | True |
| D | training | proportional | 348.71 | 0.0 | 348.71 | 317.55 | 379.87 | 18132.94 | 0.0 | 0.0 | True |
| B | test_gesamt | proportional | 353.67 | -1.18 | 354.85 | 312.57 | 397.12 | 18452.04 | 0.0 | 0.0 | True |
| B_16 | test_gesamt | proportional | 362.17 | -1.77 | 363.94 | 322.39 | 405.49 | 18924.94 | 0.0 | 0.0 | True |
| C | test_gesamt | proportional | 386.28 | -1.77 | 388.05 | 346.44 | 429.65 | 20178.44 | 0.0 | 0.0 | True |
| D | test_gesamt | proportional | 359.18 | -1.77 | 360.95 | 318.85 | 403.06 | 18769.59 | 0.0 | 0.0 | True |

## 4 Hypothesentests (einseitig, Schwelle 0.05/3 = 0.0167)
Quelle: `ergebnisse/hypothesentests.csv`; H0a in Abschnitt 3. konfirmatorisch = vorab festgelegt und nur test_gesamt.

| hypothese | vergleich | periode | konfirmatorisch | n_wochen | mittel_eur_woche | ki_unten | ki_oben | shapiro_p | p_t | p_wilcoxon | h0_verworfen | robust | untere_schranke |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FS1 | D spart gegenüber A | stresstest | False | 51 | 2943.348 | 2449.119 | 3437.576 | 0.005 | 0.0 | 0.0 | True | True | 2404.847 |
| FS2 | B_16 spart gegenüber A | stresstest | False | 34 | 3677.307 | 3094.594 | 4260.02 | 0.21 | 0.0 | 0.0 | True | True | 3041.207 |
| H0b | B spart mehr als D | stresstest | False | 46 | -87.864 | -145.274 | -30.454 | 0.242 | 0.998 | 0.997 | False | True | -150.442 |
| H0c | Kipppunkt m*: C spart mehr als B | stresstest | False | 46 | 304.456 | 234.386 | 374.527 | 0.0 | 0.0 | 0.0 | True | True | 228.079 |
| K3 explorativ | D_saison spart mehr als D | stresstest | False | 51 | 0.0 | 0.0 | 0.0 |  |  |  |  |  |  |
| K3 explorativ | B spart mehr als B_ohne_wochentag | stresstest | False | 46 | -11.986 | -79.492 | 55.52 | 0.103 | 0.639 | 0.746 | False | True | -85.568 |
| explorativ | B_16 spart mehr als D | stresstest | False | 34 | -0.069 | -35.489 | 35.35 | 0.25 | 0.502 | 0.426 | False | True | -38.734 |
| FS1 | D spart gegenüber A | test_1_stunde | False | 38 | 1093.077 | 958.846 | 1227.308 | 0.041 | 0.0 | 0.0 | True | True | 946.636 |
| FS2 | B_16 spart gegenüber A | test_1_stunde | False | 38 | 1108.857 | 975.574 | 1242.14 | 0.048 | 0.0 | 0.0 | True | True | 963.45 |
| H0b | B spart mehr als D | test_1_stunde | False | 38 | -11.037 | -24.145 | 2.071 | 0.006 | 0.952 | 0.895 | False | True | -25.337 |
| H0c | Kipppunkt m*: C spart mehr als B | test_1_stunde | False | 38 | 106.127 | 86.742 | 125.513 | 0.029 | 0.0 | 0.0 | True | True | 84.979 |
| K3 explorativ | D_saison spart mehr als D | test_1_stunde | False | 38 | 0.0 | 0.0 | 0.0 |  |  |  |  |  |  |
| K3 explorativ | B spart mehr als B_ohne_wochentag | test_1_stunde | False | 38 | -12.567 | -36.149 | 11.015 | 0.001 | 0.856 | 0.972 | False | True | -38.294 |
| explorativ | B_16 spart mehr als D | test_1_stunde | False | 38 | 15.78 | 1.942 | 29.618 | 0.0 | 0.013 | 0.011 | True | True | 0.683 |
| FS1 | D spart gegenüber A | test_2_viertel | False | 51 | 1274.922 | 1053.145 | 1496.698 | 0.0 | 0.0 | 0.0 | True | True | 1033.279 |
| FS2 | B_16 spart gegenüber A | test_2_viertel | False | 51 | 1280.542 | 1061.948 | 1499.136 | 0.0 | 0.0 | 0.0 | True | True | 1042.367 |
| FS3 | B_16 spart gegenüber A im letzten Jahr | test_2_viertel | False | 51 | 1280.542 | 1061.948 | 1499.136 | 0.0 | 0.0 | 0.0 | True | True | 1042.367 |
| H0b | B spart mehr als D | test_2_viertel | False | 51 | -23.868 | -48.858 | 1.123 | 0.0 | 0.97 | 0.937 | False | True | -51.097 |
| H0c | Kipppunkt m*: C spart mehr als B | test_2_viertel | False | 51 | 110.616 | 84.73 | 136.502 | 0.0 | 0.0 | 0.0 | True | True | 82.412 |
| K3 explorativ | D_saison spart mehr als D | test_2_viertel | False | 51 | 0.0 | 0.0 | 0.0 |  |  |  |  |  |  |
| K3 explorativ | B spart mehr als B_ohne_wochentag | test_2_viertel | False | 51 | -14.271 | -38.147 | 9.606 | 0.0 | 0.882 | 0.582 | False | True | -40.286 |
| explorativ | B_16 spart mehr als D | test_2_viertel | False | 51 | 5.62 | -7.385 | 18.626 | 0.221 | 0.195 | 0.274 | False | True | -8.55 |
| FS1 | D spart gegenüber A | training | False | 104 | 1162.368 | 1064.792 | 1259.943 | 0.002 | 0.0 | 0.0 | True | True | 1056.246 |
| FS2 | B_16 spart gegenüber A | training | False | 104 | 1148.815 | 1052.856 | 1244.774 | 0.003 | 0.0 | 0.0 | True | True | 1044.451 |
| H0b | B spart mehr als D | training | False | 104 | -30.801 | -44.547 | -17.055 | 0.0 | 1.0 | 1.0 | False | True | -45.751 |
| H0c | Kipppunkt m*: C spart mehr als B | training | False | 104 | 112.3 | 93.914 | 130.686 | 0.0 | 0.0 | 0.0 | True | True | 92.304 |
| K3 explorativ | D_saison spart mehr als D | training | False | 104 | 0.0 | 0.0 | 0.0 |  |  |  |  |  |  |
| K3 explorativ | B spart mehr als B_ohne_wochentag | training | False | 104 | -7.641 | -24.634 | 9.352 | 0.001 | 0.813 | 0.758 | False | True | -26.122 |
| explorativ | B_16 spart mehr als D | training | False | 104 | -13.552 | -22.018 | -5.087 | 0.0 | 0.999 | 0.999 | False | True | -22.759 |
| FS1 | D spart gegenüber A | test_gesamt | False | 89 | 1197.28 | 1058.892 | 1335.668 | 0.0 | 0.0 | 0.0 | True | True | 1046.727 |
| FS2 | B_16 spart gegenüber A | test_gesamt | False | 89 | 1207.238 | 1070.778 | 1343.698 | 0.0 | 0.0 | 0.0 | True | True | 1058.783 |
| H0b | B spart mehr als D | test_gesamt | True | 89 | -18.389 | -33.573 | -3.206 | 0.0 | 0.991 | 0.976 | False | True | -34.907 |
| H0c | Kipppunkt m*: C spart mehr als B | test_gesamt | True | 89 | 108.7 | 92.006 | 125.394 | 0.0 | 0.0 | 0.0 | True | True | 90.538 |
| K3 explorativ | D_saison spart mehr als D | test_gesamt | False | 89 | 0.0 | 0.0 | 0.0 |  |  |  |  |  |  |
| K3 explorativ | B spart mehr als B_ohne_wochentag | test_gesamt | False | 89 | -13.543 | -30.21 | 3.123 | 0.0 | 0.945 | 0.908 | False | True | -31.675 |
| explorativ | B_16 spart mehr als D | test_gesamt | False | 89 | 9.958 | 0.572 | 19.345 | 0.006 | 0.019 | 0.043 | False | True | -0.254 |

## 5 Kennzahl im Zeitverlauf: Netto-Ersparnis D je Monat (Mittel der Wochen)
Quelle: `ergebnisse/kpi_rollierend.csv` (je Woche, mit 13-Wochen-Mittel und Rücknahme-Flag). Rücknahmeregel (13-Wochen-Mittel < 0) hätte in 0 von 196 Wochen ausgelöst; kleinstes 13-Wochen-Mittel 626 €/Woche.

| monat | wochen | netto_eur_woche | spreizung_eur_mwh |
| --- | --- | --- | --- |
| 2022-01 | 5 | 1713.3 | 30.6 |
| 2022-02 | 4 | 837.6 | 15.0 |
| 2022-03 | 4 | 1357.4 | 24.2 |
| 2022-04 | 4 | 1933.3 | 34.5 |
| 2022-05 | 5 | 2789.4 | 50.4 |
| 2022-06 | 4 | 4051.2 | 71.6 |
| 2022-07 | 4 | 5882.4 | 105.0 |
| 2022-08 | 5 | 5675.4 | 101.3 |
| 2022-09 | 4 | 4367.6 | 78.7 |
| 2022-10 | 5 | 1928.7 | 33.9 |
| 2022-11 | 4 | 2093.7 | 37.4 |
| 2022-12 | 3 | 2442.2 | 44.5 |
| 2023-01 | 5 | 1410.8 | 25.2 |
| 2023-02 | 4 | 856.7 | 15.3 |
| 2023-03 | 4 | 1404.0 | 25.1 |
| 2023-04 | 4 | 1077.6 | 19.9 |
| 2023-05 | 5 | 1075.8 | 18.6 |
| 2023-06 | 4 | 1651.3 | 29.5 |
| 2023-07 | 5 | 1894.8 | 33.8 |
| 2023-08 | 4 | 1061.8 | 19.0 |
| 2023-09 | 4 | 1054.6 | 18.8 |
| 2023-10 | 5 | 1551.6 | 27.7 |
| 2023-11 | 4 | 1090.8 | 19.5 |
| 2023-12 | 4 | 1012.4 | 18.8 |
| 2024-01 | 5 | 982.7 | 17.0 |
| 2024-02 | 4 | 579.2 | 10.3 |
| 2024-03 | 4 | 532.0 | 10.2 |
| 2024-04 | 5 | 937.4 | 16.2 |
| 2024-05 | 4 | 1103.8 | 19.7 |
| 2024-06 | 4 | 1710.8 | 30.6 |
| 2024-07 | 5 | 1439.9 | 25.7 |
| 2024-08 | 4 | 1148.7 | 20.5 |
| 2024-09 | 5 | 974.2 | 17.4 |
| 2024-10 | 4 | 892.7 | 15.9 |
| 2024-11 | 4 | 879.8 | 15.7 |
| 2024-12 | 4 | 1331.2 | 23.8 |
| 2025-01 | 4 | 901.5 | 15.4 |
| 2025-02 | 4 | 868.6 | 15.5 |
| 2025-03 | 5 | 789.8 | 14.1 |
| 2025-04 | 4 | 1082.9 | 19.3 |
| 2025-05 | 4 | 1177.2 | 21.0 |
| 2025-06 | 5 | 1812.6 | 32.4 |
| 2025-07 | 4 | 1193.7 | 21.3 |
| 2025-08 | 4 | 988.7 | 17.7 |
| 2025-09 | 4 | 958.0 | 17.1 |
| 2025-10 | 4 | 1100.8 | 19.7 |
| 2025-11 | 4 | 732.7 | 13.1 |
| 2025-12 | 5 | 887.1 | 15.8 |
| 2026-01 | 4 | 641.6 | 11.5 |
| 2026-02 | 4 | 531.7 | 9.5 |
| 2026-03 | 5 | 1097.1 | 20.2 |
| 2026-04 | 4 | 763.3 | 12.9 |
| 2026-05 | 4 | 1214.1 | 21.7 |
| 2026-06 | 5 | 2655.4 | 47.4 |
| 2026-07 | 4 | 1625.4 | 29.0 |
| 2026-08 | 5 | 1812.9 | 32.4 |
| 2026-09 | 3 | 2106.4 | 37.6 |

## 6 Sensitivität (D, test_gesamt, Schwelle 5 %)
Quelle: `r2/ergebnisse/sensitivitaet.csv`. Grafikidee: liegende Balken der Änderung in %.

| variante | schalter | wert | mittel_eur_woche | delta_pct | anteil_oracle | h0_entscheidung_gleich | relevant |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Basis | — | — | 1199.05 | 0.0 | 0.93 | True | False |
| V2 | Auswertung ohne Nächte mit flag_outlier | 174 Nächte raus | 1070.19 | -10.75 | 0.93 | True | True |
| V3 | last.feiertagsvariante_mariae_himmelfahrt | True | 1199.05 | 0.0 | 0.93 | True | False |
| V4 | last.produktionstage | Mo-Fr ohne Feiertage Bayern | 770.98 | -35.7 | 0.94 | True | True |
| V6a | last.mwh_pro_tag | 4.0 | 600.41 | -49.93 | 0.93 | True | True |
| V6b | last.mwh_pro_tag | 12.0 | 1797.69 | 49.93 | 0.93 | True | True |
| V6c | last.mwh_pro_tag | 16.0 | 2396.33 | 99.85 | 0.93 | True | True |
| V7a | last.blocklaenge_h | 1 | 1608.72 | 34.17 | 0.94 | True | True |
| V7b | last.blocklaenge_h | 3 | 964.76 | -19.54 | 0.94 | True | True |
| V7c | last.blocklaenge_h | 4 | 724.02 | -39.62 | 0.92 | True | True |
| V8 | vertrag.bewertung_verschiebung | proportional | 360.95 | -69.9 | 0.93 | True | True |
| V9 | kosten.nachtstunden | 23-06 Uhr | 1072.81 | -10.53 | 0.93 | True | True |
| V10 | kosten.zuschlag_regel | addiert | 1199.64 | 0.05 | 0.93 | True | False |

## 7 Break-even: Monate bis zur Amortisation einmaliger Umstellungskosten (D, test_gesamt)
Quelle: `ergebnisse/wirtschaftlichkeit.csv`.

| vertrag | umstellungskosten_eur | ersparnis_eur_jahr | break_even | break_even_vorsichtig_monate |
| --- | --- | --- | --- | --- |
| band | 0 | 62350.58 | 0.0 | 0.0 |
| band | 5000 | 62350.58 | 0.96 | 1.09 |
| band | 10000 | 62350.58 | 1.92 | 2.17 |
| band | 25000 | 62350.58 | 4.81 | 5.44 |
| band | 50000 | 62350.58 | 9.62 | 10.87 |
| band | 100000 | 62350.58 | 19.25 | 21.75 |
| proportional | 0 | 18769.59 | 0.0 | 0.0 |
| proportional | 5000 | 18769.59 | 3.2 | 3.62 |
| proportional | 10000 | 18769.59 | 6.39 | 7.24 |
| proportional | 25000 | 18769.59 | 15.98 | 18.09 |
| proportional | 50000 | 18769.59 | 31.97 | 36.19 |
| proportional | 100000 | 18769.59 | 63.93 | 72.38 |

## 8 Kipppunkte (D, test_gesamt)
Quelle: `ergebnisse/kipppunkte.csv`.

| vertrag | annahme | basis | kipppunkt | einheit | lesart |
| --- | --- | --- | --- | --- | --- |
| band | Vertragsfaktor (Anteil der verschobenen MWh am Spot) | 1.0 | -0.001 | Faktor | darunter frisst der Personal-Mehraufwand die Stromersparnis; <= 0 heißt: kein Kipppunkt |
| band | Aufpreis je Personalstunde für die Verschiebung (zusätzlich zu Lohn und Zuschlägen) | 0.0 | 28.549 | EUR je Personalstunde | so viel mehr pro Stunde dürfte das Personal für 3 statt 22 Uhr kosten |
| band | Zusätzlich bezahlte Stunden je Nacht (Warten oder zweite Anfahrt), mit Nachtzuschlag | 0.0 | 1.305 | Stunden je Person und Nacht | muss jede Person länger bezahlt werden als das, kippt die Verschiebung |
| band | Preisunterschied 22-24 Uhr gegen gewählten Block | 21.38 | -0.032 | EUR/MWh | fällt die mittlere Spreizung darunter, lohnt die Verschiebung nicht mehr |
| band | Tagesplanung statt Wochenplanung (H0c): Mehrkosten kurzfristiges Personal |  | 2.156 | EUR je Personalstunde | nur wenn kurzfristiges Personal weniger Aufpreis kostet, lohnt die Tagesplanung gegenüber B |
| proportional | Vertragsfaktor (Anteil der verschobenen MWh am Spot) | 0.3 | -0.001 | Faktor | darunter frisst der Personal-Mehraufwand die Stromersparnis; <= 0 heißt: kein Kipppunkt |
| proportional | Aufpreis je Personalstunde für die Verschiebung (zusätzlich zu Lohn und Zuschlägen) | 0.0 | 8.594 | EUR je Personalstunde | so viel mehr pro Stunde dürfte das Personal für 3 statt 22 Uhr kosten |
| proportional | Zusätzlich bezahlte Stunden je Nacht (Warten oder zweite Anfahrt), mit Nachtzuschlag | 0.0 | 0.393 | Stunden je Person und Nacht | muss jede Person länger bezahlt werden als das, kippt die Verschiebung |
| proportional | Preisunterschied 22-24 Uhr gegen gewählten Block | 21.38 | -0.105 | EUR/MWh | fällt die mittlere Spreizung darunter, lohnt die Verschiebung nicht mehr |
| proportional | Tagesplanung statt Wochenplanung (H0c): Mehrkosten kurzfristiges Personal |  | 0.647 | EUR je Personalstunde | nur wenn kurzfristiges Personal weniger Aufpreis kostet, lohnt die Tagesplanung gegenüber B |

## 9 Spot gegen Festpreis (85 €/MWh)
Quelle: `ergebnisse/spot_festpreis.csv`. Lastprofil (Annahme): 180 MWh/Tag, Reinigung 22–24 Uhr, Rest gleichmäßig 06–22 Uhr. vorteil_festpreis > 0 heißt: Der Festpreis war günstiger als die Börse.

| jahr | tage | vollstaendig | spot_grundlast_eur_mwh | spot_profil_eur_mwh | festpreis_eur_mwh | vorteil_festpreis_eur_mwh | vorteil_festpreis_spotanteil_eur | vorteil_festpreis_ganzes_werk_eur |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 365 | True | 235.4 | 247.4 | 85.0 | 162.4 | 3201516.1 | 10671720.2 |
| 2023 | 365 | True | 95.2 | 99.9 | 85.0 | 14.9 | 293369.7 | 977899.1 |
| 2024 | 366 | True | 78.5 | 81.9 | 85.0 | -3.1 | -61252.9 | -204176.2 |
| 2025 | 365 | True | 89.3 | 90.7 | 85.0 | 5.7 | 112558.0 | 375193.2 |
| 2026 | 304 | False | 114.0 | 110.9 | 85.0 | 25.9 | 425926.9 | 1419756.4 |

## 10 C&E-Matrix (Skala 0/1/3/9, Gewichte Teamannahme)
Quelle: `ergebnisse/ce_matrix.csv`. Grafikidee: Pareto-Balken mit kumulierter Linie.

| prozess | Steuerbarkeit im Wochenplan | Kein Produktrisiko | Personalgebunden (Schichtplan relevant) | Verschiebbare Leistung (MW) | Datenlage | begruendung | summe_gewichtet | anteil_pct | kumuliert_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GEWICHT | 5 | 5 | 4 | 3 | 2 | Steuerbarkeit im Wochenplan: Kern der Leitfrage: Zeitpunkt muss eine Woche vorher feststehen | Kein Produktrisiko: Hygiene, Rohmilch 36-48 h (K-008 P9): ein Risiko für das Produkt schließt einen Prozess aus | Personalgebunden (Schichtplan relevant): nur dann ist es eine Frage des Schichtplans und nicht der Automatik | Verschiebbare Leistung (MW): Hebel in EUR, aber wertlos ohne die drei Kriterien davor | Datenlage: belastbare Zahlen vom Partner statt Teamannahmen |  |  |  |
| Reinigung (CIP) | 9 | 9 | 9 | 3 | 9 | 8-h-Fenster 22-06 Uhr, Pflicht nach 24 h (P10), Zeitarbeit; 4 MW; Zahlen vom Partner (P6, K-012) | 153.0 | 61.9 | 61.9 |
| Produktion | 1 | 1 | 3 | 9 | 1 | Rohmilch muss sofort verarbeitet werden (P9), 06-22 Uhr fest; ca. 7 MW; keine Daten zur Verschiebung | 51.0 | 20.6 | 82.6 |
| Kälte | 3 | 3 | 1 | 1 | 3 | läuft automatisch, Vorkühlung 2 h nur angenommen (A1); 1 MW; Produkttemperatur als Risiko | 43.0 | 17.4 | 100.0 |

## 11 Fehleranalyse B: wann liegt die Prognose daneben (€ je Nacht)
Quelle: `ergebnisse/fehleranalyse_b.csv`. regret_b = B − C, b_minus_d = B − D.

| periode | gruppe | wert | naechte | regret_b_eur_nacht | b_minus_d_eur_nacht | anteil_b_trifft_oracle_pct |
| --- | --- | --- | --- | --- | --- | --- |
| stresstest | saison | Fruehling | 92 | 55.83 | 22.76 | 23.91 |
| stresstest | saison | Herbst | 91 | 47.6 | 16.31 | 31.87 |
| stresstest | saison | Sommer | 92 | 22.95 | 0.44 | 59.78 |
| stresstest | saison | Winter | 53 | 47.87 | 8.06 | 18.87 |
| test_1_stunde | saison | Fruehling | 92 | 14.02 | 0.22 | 25.0 |
| test_1_stunde | saison | Herbst | 28 | 16.87 | -1.9 | 32.14 |
| test_1_stunde | saison | Sommer | 92 | 13.45 | 0.94 | 38.04 |
| test_1_stunde | saison | Winter | 54 | 19.13 | 6.78 | 37.04 |
| test_2_viertel | saison | Fruehling | 92 | 25.13 | 8.05 | 23.91 |
| test_2_viertel | saison | Herbst | 83 | 20.47 | 7.19 | 37.35 |
| test_2_viertel | saison | Sommer | 92 | 6.96 | -3.91 | 50.0 |
| test_2_viertel | saison | Winter | 90 | 10.99 | 2.66 | 28.89 |
| training | saison | Fruehling | 184 | 13.8 | 2.01 | 33.15 |
| training | saison | Herbst | 182 | 16.81 | 7.89 | 28.57 |
| training | saison | Sommer | 184 | 12.98 | 1.13 | 38.04 |
| training | saison | Winter | 178 | 20.74 | 6.69 | 37.64 |
| stresstest | wochentag_nacht | 0 | 47 | 65.32 | 22.2 | 23.4 |
| stresstest | wochentag_nacht | 1 | 47 | 29.54 | 2.52 | 46.81 |
| stresstest | wochentag_nacht | 2 | 47 | 36.13 | 17.82 | 38.3 |
| stresstest | wochentag_nacht | 3 | 47 | 47.06 | 18.64 | 17.02 |
| stresstest | wochentag_nacht | 4 | 46 | 59.78 | 19.95 | 36.96 |
| stresstest | wochentag_nacht | 5 | 47 | 29.3 | -4.34 | 42.55 |
| stresstest | wochentag_nacht | 6 | 47 | 34.51 | 9.69 | 42.55 |
| test_1_stunde | wochentag_nacht | 0 | 38 | 24.31 | 8.86 | 26.32 |
| test_1_stunde | wochentag_nacht | 1 | 38 | 8.69 | -0.27 | 31.58 |
| test_1_stunde | wochentag_nacht | 2 | 38 | 15.87 | 2.29 | 36.84 |
| test_1_stunde | wochentag_nacht | 3 | 38 | 12.49 | -0.22 | 31.58 |
| test_1_stunde | wochentag_nacht | 4 | 38 | 11.03 | 1.02 | 36.84 |
| test_1_stunde | wochentag_nacht | 5 | 38 | 21.15 | 2.71 | 31.58 |
| test_1_stunde | wochentag_nacht | 6 | 38 | 12.59 | -3.35 | 34.21 |
| test_2_viertel | wochentag_nacht | 0 | 51 | 18.23 | 11.05 | 31.37 |
| test_2_viertel | wochentag_nacht | 1 | 51 | 12.43 | -0.48 | 31.37 |
| test_2_viertel | wochentag_nacht | 2 | 51 | 19.17 | 9.6 | 25.49 |
| test_2_viertel | wochentag_nacht | 3 | 51 | 9.02 | 0.23 | 41.18 |
| test_2_viertel | wochentag_nacht | 4 | 51 | 10.1 | -1.0 | 45.1 |
| test_2_viertel | wochentag_nacht | 5 | 51 | 26.01 | -0.27 | 35.29 |
| test_2_viertel | wochentag_nacht | 6 | 51 | 15.66 | 4.76 | 35.29 |
| training | wochentag_nacht | 0 | 104 | 17.47 | 6.36 | 31.73 |
| training | wochentag_nacht | 1 | 104 | 15.47 | 2.67 | 30.77 |
| training | wochentag_nacht | 2 | 104 | 11.8 | 2.79 | 42.31 |
| training | wochentag_nacht | 3 | 104 | 10.79 | 4.25 | 43.27 |
| training | wochentag_nacht | 4 | 104 | 22.95 | 4.15 | 25.96 |
| training | wochentag_nacht | 5 | 104 | 18.56 | 5.41 | 31.73 |
| training | wochentag_nacht | 6 | 104 | 15.25 | 5.16 | 34.62 |

## 12 R2: Rückblick-Kennzahl je Jahr (Mehrkosten 22–24 Uhr gegen billigstes Fenster)
Quelle: `r2/ergebnisse/reinigungsfenster_jahr.csv`, `reinigungsfenster_saison.csv`. Obergrenze mit bekannten Preisen, keine Strategie.

| jahr | fenster | vollstaendig | mittel_eur_mwh | median_eur_mwh | eur_summe | eur_pro_jahr |
| --- | --- | --- | --- | --- | --- | --- |
| 2022 | 365 | True | 55.83 | 46.2 | 163032.28 | 163032.28 |
| 2023 | 365 | True | 24.33 | 20.69 | 71033.56 | 71033.56 |
| 2024 | 366 | True | 19.96 | 16.9 | 58434.28 | 58274.62 |
| 2025 | 365 | True | 20.13 | 17.46 | 58768.44 | 58768.44 |
| 2026 | 303 | False | 26.71 | 23.19 | 64743.48 | 77991.32 |

| saison | tage | median_eur_mwh | q25_eur_mwh | q75_eur_mwh | median_pct | q25_pct | q75_pct | tage_ohne_pct | haeufigster_start | anteil_genau_status_quo_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Winter | 420 | 16.18 | 9.66 | 27.09 | 17.78 | 11.07 | 35.36 | 18 | 3 | 2.86 |
| Fruehling | 460 | 19.64 | 11.87 | 29.88 | 20.39 | 12.42 | 29.87 | 3 | 3 | 2.61 |
| Sommer | 460 | 29.64 | 21.11 | 50.83 | 28.1 | 19.97 | 40.71 | 5 | 3 | 0.22 |
| Herbst | 424 | 20.68 | 10.91 | 37.82 | 21.27 | 11.79 | 43.29 | 15 | 3 | 1.89 |

## 13 R2: Preis je Monat (€/MWh) und Tagesprofil je Saison (Median je Stunde)
Quelle: `r2/ergebnisse/kennzahlen_monat.csv`, `tagesprofil_saison.csv`.

| jahr | monat | stunden | mittel | median | q25 | q75 | min | max | anteil_negativ_pct | iqr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 1 | 744 | 167.73 | 172.32 | 110.17 | 217.07 | -1.05 | 399.85 | 0.54 | 106.9 |
| 2022 | 2 | 672 | 128.8 | 120.09 | 94.96 | 173.23 | -0.52 | 322.9 | 0.6 | 78.27 |
| 2022 | 3 | 743 | 252.01 | 245.03 | 192.12 | 316.54 | -19.04 | 700.0 | 0.81 | 124.42 |
| 2022 | 4 | 720 | 165.73 | 185.59 | 108.93 | 213.64 | -2.49 | 309.93 | 0.69 | 104.71 |
| 2022 | 5 | 744 | 177.48 | 192.68 | 155.65 | 220.94 | -13.85 | 298.21 | 2.15 | 65.29 |
| 2022 | 6 | 720 | 218.03 | 210.12 | 164.86 | 265.4 | -0.59 | 500.0 | 0.42 | 100.54 |
| 2022 | 7 | 744 | 315.0 | 332.45 | 239.35 | 400.14 | -0.1 | 679.54 | 0.27 | 160.79 |
| 2022 | 8 | 744 | 465.18 | 463.96 | 360.98 | 569.24 | 13.29 | 871.0 | 0.0 | 208.26 |
| 2022 | 9 | 720 | 346.12 | 356.38 | 274.47 | 435.38 | 2.0 | 729.9 | 0.0 | 160.91 |
| 2022 | 10 | 745 | 152.6 | 139.91 | 98.34 | 189.41 | 0.1 | 497.39 | 0.0 | 91.07 |
| 2022 | 11 | 720 | 173.63 | 152.01 | 112.16 | 217.91 | 0.09 | 503.55 | 0.0 | 105.75 |
| 2022 | 12 | 744 | 251.62 | 254.4 | 127.26 | 355.02 | -3.78 | 665.01 | 3.9 | 227.76 |
| 2023 | 1 | 744 | 117.83 | 127.74 | 84.98 | 158.97 | -5.4 | 270.22 | 1.88 | 73.99 |
| 2023 | 2 | 672 | 128.31 | 129.64 | 106.36 | 153.82 | 22.01 | 245.6 | 0.0 | 47.46 |
| 2023 | 3 | 743 | 102.52 | 105.23 | 83.68 | 129.55 | -6.02 | 217.09 | 1.21 | 45.87 |
| 2023 | 4 | 720 | 100.74 | 103.68 | 88.67 | 122.44 | -8.82 | 207.92 | 1.53 | 33.77 |
| 2023 | 5 | 744 | 81.72 | 89.5 | 71.43 | 105.18 | -129.96 | 182.68 | 4.44 | 33.75 |
| 2023 | 6 | 720 | 94.76 | 97.16 | 79.39 | 116.0 | -36.35 | 197.77 | 2.78 | 36.61 |
| 2023 | 7 | 744 | 77.61 | 88.1 | 66.63 | 104.45 | -500.0 | 188.0 | 7.53 | 37.82 |
| 2023 | 8 | 744 | 94.32 | 96.88 | 79.07 | 115.02 | -21.77 | 291.93 | 3.09 | 35.95 |
| 2023 | 9 | 720 | 100.72 | 98.05 | 87.32 | 114.9 | -5.74 | 524.27 | 3.06 | 27.58 |
| 2023 | 10 | 745 | 87.38 | 95.68 | 60.51 | 120.0 | -11.07 | 250.28 | 5.1 | 59.49 |
| 2023 | 11 | 720 | 91.12 | 91.27 | 71.85 | 117.16 | -0.08 | 261.0 | 0.42 | 45.31 |
| 2023 | 12 | 744 | 68.52 | 75.74 | 26.04 | 101.15 | -13.37 | 230.69 | 9.68 | 75.11 |
| 2024 | 1 | 744 | 76.57 | 77.76 | 60.04 | 94.19 | -4.84 | 150.09 | 2.15 | 34.15 |
| 2024 | 2 | 696 | 61.34 | 63.1 | 53.1 | 73.26 | -0.13 | 136.22 | 0.57 | 20.16 |
| 2024 | 3 | 743 | 64.7 | 66.52 | 53.77 | 77.83 | -9.98 | 174.7 | 1.62 | 24.06 |
| 2024 | 4 | 720 | 62.36 | 69.38 | 41.84 | 85.04 | -65.06 | 204.57 | 6.94 | 43.2 |
| 2024 | 5 | 744 | 67.21 | 78.08 | 45.22 | 93.28 | -135.45 | 221.46 | 10.48 | 48.06 |
| 2024 | 6 | 720 | 72.89 | 80.46 | 44.56 | 101.77 | -80.01 | 235.52 | 8.89 | 57.21 |
| 2024 | 7 | 744 | 67.7 | 77.41 | 36.8 | 96.49 | -73.96 | 257.35 | 10.89 | 59.69 |
| 2024 | 8 | 744 | 82.05 | 89.22 | 57.64 | 109.89 | -59.96 | 289.27 | 9.14 | 52.25 |
| 2024 | 9 | 720 | 78.31 | 83.9 | 51.02 | 100.08 | -24.0 | 656.37 | 5.56 | 49.06 |
| 2024 | 10 | 745 | 86.1 | 85.34 | 64.4 | 107.79 | -15.69 | 285.8 | 3.36 | 43.39 |
| 2024 | 11 | 720 | 113.91 | 108.4 | 91.28 | 130.95 | -1.86 | 820.11 | 1.53 | 39.67 |
| 2024 | 12 | 744 | 108.32 | 98.5 | 68.0 | 120.96 | -2.06 | 936.28 | 1.08 | 52.96 |
| 2025 | 1 | 744 | 114.14 | 114.92 | 85.06 | 136.66 | -1.01 | 583.4 | 1.88 | 51.6 |
| 2025 | 2 | 672 | 128.52 | 127.02 | 106.89 | 149.43 | 37.1 | 298.91 | 0.0 | 42.54 |
| 2025 | 3 | 743 | 94.73 | 101.91 | 72.93 | 125.18 | -26.07 | 280.07 | 4.04 | 52.25 |
| 2025 | 4 | 720 | 77.94 | 88.4 | 62.57 | 106.4 | -129.81 | 263.2 | 10.42 | 43.83 |
| 2025 | 5 | 744 | 67.34 | 85.32 | 10.09 | 102.24 | -250.32 | 229.11 | 17.34 | 92.15 |
| 2025 | 6 | 720 | 63.99 | 76.72 | 4.08 | 101.54 | -99.01 | 288.97 | 19.58 | 97.46 |
| 2025 | 7 | 744 | 87.8 | 92.49 | 77.64 | 107.76 | -2.26 | 476.19 | 1.61 | 30.12 |
| 2025 | 8 | 744 | 76.99 | 88.66 | 56.31 | 103.27 | -61.08 | 283.89 | 8.6 | 46.96 |
| 2025 | 9 | 720 | 83.51 | 86.1 | 59.25 | 108.96 | -53.4 | 413.66 | 8.33 | 49.71 |
| 2025 | 10 | 745 | 84.4 | 88.15 | 63.39 | 107.68 | -4.98 | 407.21 | 6.44 | 44.29 |
| 2025 | 11 | 720 | 101.88 | 93.04 | 81.02 | 112.4 | 4.93 | 373.31 | 0.0 | 31.38 |
| 2025 | 12 | 744 | 93.47 | 89.97 | 80.03 | 103.3 | 3.51 | 308.35 | 0.0 | 23.27 |
| 2026 | 1 | 744 | 110.09 | 104.9 | 92.74 | 126.76 | -0.01 | 276.74 | 0.27 | 34.02 |
| 2026 | 2 | 672 | 96.58 | 98.0 | 84.81 | 111.24 | -0.25 | 227.21 | 1.04 | 26.43 |
| 2026 | 3 | 743 | 99.29 | 107.03 | 65.81 | 135.2 | -11.76 | 310.86 | 4.44 | 69.39 |
| 2026 | 4 | 720 | 78.52 | 101.2 | 27.06 | 121.56 | -413.77 | 245.12 | 17.08 | 94.5 |
| 2026 | 5 | 744 | 97.54 | 116.49 | 74.33 | 135.12 | -499.0 | 393.94 | 10.35 | 60.79 |
| 2026 | 6 | 720 | 109.52 | 113.14 | 72.06 | 137.25 | -45.87 | 665.82 | 6.81 | 65.19 |
| 2026 | 7 | 744 | 105.45 | 121.9 | 63.16 | 149.29 | -12.28 | 311.69 | 10.62 | 86.13 |
| 2026 | 8 | 744 | 126.89 | 145.67 | 97.57 | 169.03 | -12.15 | 338.86 | 7.26 | 71.46 |
| 2026 | 9 | 720 | 144.82 | 159.23 | 93.49 | 195.82 | -19.0 | 697.31 | 5.0 | 102.33 |
| 2026 | 10 | 745 | 169.27 | 174.05 | 125.0 | 224.6 | -0.01 | 559.63 | 0.27 | 99.6 |

| stunde_lokal | Fruehling | Herbst | Sommer | Winter |
| --- | --- | --- | --- | --- |
| 0 | 100.2 | 94.0 | 107.1 | 90.6 |
| 1 | 95.1 | 90.4 | 100.4 | 87.5 |
| 2 | 92.9 | 88.5 | 95.7 | 85.7 |
| 3 | 93.0 | 87.2 | 94.3 | 84.1 |
| 4 | 94.2 | 88.3 | 94.4 | 84.6 |
| 5 | 99.4 | 93.3 | 100.6 | 88.7 |
| 6 | 114.7 | 110.8 | 117.9 | 97.4 |
| 7 | 122.5 | 132.8 | 125.0 | 111.3 |
| 8 | 110.7 | 133.1 | 114.6 | 122.2 |
| 9 | 91.5 | 116.2 | 95.2 | 118.4 |
| 10 | 75.5 | 99.4 | 81.8 | 111.5 |
| 11 | 64.7 | 89.9 | 67.9 | 106.4 |
| 12 | 53.2 | 83.5 | 50.9 | 100.6 |
| 13 | 40.2 | 81.4 | 39.3 | 100.4 |
| 14 | 45.2 | 84.4 | 37.9 | 104.8 |
| 15 | 63.1 | 94.6 | 51.2 | 112.5 |
| 16 | 76.7 | 109.8 | 72.4 | 120.2 |
| 17 | 97.6 | 131.5 | 89.5 | 131.2 |
| 18 | 120.7 | 149.4 | 110.5 | 134.8 |
| 19 | 141.1 | 155.4 | 139.5 | 124.7 |
| 20 | 142.7 | 131.3 | 161.7 | 111.8 |
| 21 | 128.1 | 115.0 | 144.5 | 102.9 |
| 22 | 115.9 | 107.0 | 126.3 | 101.9 |
| 23 | 103.8 | 96.7 | 110.3 | 92.6 |

