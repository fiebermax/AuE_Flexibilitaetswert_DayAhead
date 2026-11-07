# KI: Claude, Zweck: Hilfsfunktionen für Konfiguration und Pfade, geprüft von <Name R2> durch Review und pytest
"""Gemeinsame Hilfen für alle Pipeline-Schritte: params.yaml laden, Pfade relativ zum Repo auflösen."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PARAMS_DATEI = ROOT / "config" / "params.yaml"


def lade_params(pfad: Path = PARAMS_DATEI) -> dict:
    """Liest config/params.yaml. Bricht mit klarer Meldung ab, wenn die Datei fehlt."""
    if not pfad.exists():
        raise FileNotFoundError(f"Konfiguration fehlt: {pfad}. Bitte aus dem Repo wiederherstellen.")
    with open(pfad, encoding="utf-8") as f:
        return yaml.safe_load(f)


def pfad(params: dict, name: str) -> Path:
    """Absoluter Pfad zu einem Ordner aus params['daten']['pfade'] (z. B. 'raw', 'processed')."""
    return ROOT / params["daten"]["pfade"][name]
