# KI: Claude, Zweck: Hilfsfunktionen für Konfiguration, Pfade und Uhrzeitfenster, geprüft von <Name R2> durch Review und pytest
"""Shared helpers for all pipeline steps: load params.yaml, resolve folders, working-day rule.

Why a separate file: every step needs the same settings and folders. Defining this once avoids
copies that drift apart, and no step has to hard-code a path.
"""
from pathlib import Path

import holidays
import numpy as np
import pandas as pd
import yaml

# Repo root folder, derived from where THIS file lives (src/gemeinsam.py -> one level up).
# So the scripts work no matter from which folder they are started or on whose computer.
ROOT = Path(__file__).resolve().parent.parent
PARAMS_DATEI = ROOT / "params.yaml"


def lade_params(pfad: Path = PARAMS_DATEI) -> dict:
    """Read params.yaml into a nested dict, e.g. p["markt"]["zeitzone"] -> "Europe/Berlin".
    safe_load only reads plain data (no code execution from the YAML file)."""
    if not pfad.exists():
        raise FileNotFoundError(f"Konfiguration fehlt: {pfad}. Bitte aus dem Repo wiederherstellen.")
    with open(pfad, encoding="utf-8") as f:
        return yaml.safe_load(f)


def pfad(params: dict, name: str) -> Path:
    """Absolute path of a folder listed in params['daten']['pfade'], e.g. 'raw' -> <repo>/data/raw."""
    return ROOT / params["daten"]["pfade"][name]


def werktage(daten: pd.DatetimeIndex, mariae_himmelfahrt: bool) -> np.ndarray:
    """True = Monday to Friday and no public holiday in Bavaria.

    Holidays come from the package `holidays` (subdiv="BY" = Bavaria), not from a hand-written list.
    Mariä Himmelfahrt (15.08.) is a holiday only in mainly catholic municipalities; the package files
    it under the category "catholic", so we add that category only if the switch in params.yaml is on.
    The result is a True/False array with one entry per timestamp.
    Lives here because prices (cleaning) and load (02_synthetisch variant Mo-Fr) must use the SAME rule.
    """
    kategorien = ("public", "catholic") if mariae_himmelfahrt else ("public",)
    jahre = range(daten.min().year, daten.max().year + 1)
    feiertage = holidays.Germany(subdiv="BY", years=jahre, categories=kategorien)
    tage = daten.tz_localize(None).normalize()
    ist_feiertag = np.array([t.date() in feiertage for t in tage])
    return (tage.weekday < 5) & ~ist_feiertag      # weekday < 5 = Mon..Fri; "&" = and; "~" = not


def fensterstunden(start_h: int, ende_h: int) -> list[int]:
    """Local clock hours of a window in order; works across midnight: (22, 6) -> [22, 23, 0, 1, ..., 5].

    Lives here because the load check (02_synthetisch) and the board (build_board) must agree on
    which hours the cleaning window 22-06 Uhr contains (diary E-033)."""
    laenge = (ende_h - start_h) % 24 or 24
    return [(start_h + i) % 24 for i in range(laenge)]
