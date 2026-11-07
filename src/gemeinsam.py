# KI: Claude, Zweck: Hilfsfunktionen für Konfiguration und Pfade, geprüft von <Name R2> durch Review und pytest
"""Shared helpers for all pipeline steps: load params.yaml, resolve folders relative to the repo.

Why a separate file: every step needs the same settings and folders. Defining this once avoids
copies that drift apart, and no step has to hard-code a path.
"""
from pathlib import Path

import yaml

# Repo root folder, derived from where THIS file lives (src/gemeinsam.py -> one level up).
# So the scripts work no matter from which folder they are started or on whose computer.
ROOT = Path(__file__).resolve().parent.parent
PARAMS_DATEI = ROOT / "config" / "params.yaml"


def lade_params(pfad: Path = PARAMS_DATEI) -> dict:
    """Read config/params.yaml into a nested dict, e.g. p["markt"]["zeitzone"] -> "Europe/Berlin".
    safe_load only reads plain data (no code execution from the YAML file)."""
    if not pfad.exists():
        raise FileNotFoundError(f"Konfiguration fehlt: {pfad}. Bitte aus dem Repo wiederherstellen.")
    with open(pfad, encoding="utf-8") as f:
        return yaml.safe_load(f)


def pfad(params: dict, name: str) -> Path:
    """Absolute path of a folder listed in params['daten']['pfade'], e.g. 'raw' -> <repo>/data/raw."""
    return ROOT / params["daten"]["pfade"][name]
