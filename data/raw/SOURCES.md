# Datenherkunft

Rohdaten werden unverändert abgelegt und nie überschrieben.

| Quelle | Inhalt | URL | Abrufdatum | Lizenz / Namensnennung | Ordner | SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| SMARD (Bundesnetzagentur) | Day-Ahead-Großhandelspreis DE-LU, Filter 4169, stündlich bzw. viertelstündlich | https://www.smard.de/app/chart_data | | CC BY 4.0, „Bundesnetzagentur \| SMARD.de“ | `smard/4169/` | per Skript |
| synthetisch | Lastgang, Kosten | `src/02_synthetisch.py`, Seed in `params.yaml` | erzeugt | eigene Erzeugung | `data/interim/` | – |

Datenschutz: keine personenbezogenen Daten. Energy-Charts nur nach Lizenzprüfung.
