# Datenherkunft

Rohdaten werden unverändert abgelegt und nie überschrieben.

| Quelle | Inhalt | URL | Abrufdatum | Lizenz / Namensnennung | Ordner | SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| SMARD (Bundesnetzagentur) | Day-Ahead-Großhandelspreis DE-LU, Filter 4169, stündlich bzw. viertelstündlich | https://www.smard.de/app/chart_data | je Datei in `smard/manifest.csv` | CC BY 4.0, „Bundesnetzagentur \| SMARD.de“ | `smard/4169/<auflösung>/` | je Datei in `smard/manifest.csv` |
| synthetisch | Lastgang (Kosten folgen, R4) | `src/02_synthetisch.py`, deterministisch, Parameter `last.*` in `params.yaml` | bei jedem Lauf erzeugt | eigene Erzeugung | `data/processed/last_synth.parquet` | – |

Datenschutz: keine personenbezogenen Daten. Energy-Charts nur nach Lizenzprüfung.

<!-- manifest:start (automatisch von src/01_download.py erzeugt, nicht von Hand ändern) -->

### SMARD-Abrufe (Stand dieses Laufs)

Je Datei URL, Abrufzeitpunkt und SHA256 in `smard/manifest.csv` (SHA256 des Manifests: `5ffb0ca1ed2cc884c5d8f01df0ff292fc608aa1bacabddea3469442be79bc041`).

| Filter | Region | Auflösung | Dateien (Wochen) | erste Woche ab | letzte Woche ab | Abruf von | Abruf bis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4169 | DE-LU | hour | 253 | 2021-12-27 | 2026-10-26 | 2026-11-07T10:50:42Z | 2026-11-07T10:51:15Z |
| 4169 | DE-LU | quarterhour | 57 | 2025-09-29 | 2026-10-26 | 2026-11-07T10:51:15Z | 2026-11-07T10:51:22Z |

<!-- manifest:ende -->
