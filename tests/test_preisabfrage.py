# KI: Claude, Zweck: Tests der einfachen Preisabfrage (src/preisabfrage.py), geprüft von <Name R2> durch Review und Nachsehen in preise_clean.csv
"""Einzelne Tage, letzte Monate, Wochentage, Umstellungstage und verständliche Fehlermeldungen."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "processed" / "preise_clean.csv"
pytestmark = pytest.mark.skipif(not CLEAN.exists(), reason="Pipeline noch nicht gelaufen")

spec = importlib.util.spec_from_file_location("preisabfrage", ROOT / "src" / "preisabfrage.py")
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)


def test_ein_tag_mit_einfachen_spalten():
    df = pa.tag("2025-01-06")                       # Montag, Heilige Drei Könige
    assert list(df.columns) == pa.SPALTEN and len(df) == 24
    assert (df["wochentag"] == "Montag").all() and not df["werktag"].any()
    assert list(df["uhrzeit"].head(3)) == ["00:00", "01:00", "02:00"] and list(df["stunde"]) == list(range(24))


def test_preis_stimmt_mit_der_bereinigten_datei():
    roh = pd.read_csv(CLEAN)
    erwartet = roh[(roh["datum_lokal"] == "2025-07-15") & (roh["stunde_lokal"] == 14)]["preis_eur_mwh"].iloc[0]
    df = pa.tag("2025-07-15")
    assert df[df["uhrzeit"] == "14:00"]["preis"].iloc[0] == erwartet


@pytest.mark.parametrize("datum, stunden", [("2025-03-30", 23), ("2025-10-26", 25)])
def test_umstellungstage(datum, stunden):
    df = pa.tag(datum)
    assert len(df) == stunden and df["zeit"].is_unique


def test_letzte_monate_und_wochentag():
    df = pa.letzte_monate(3)
    letzter = pa.alle_preise()["datum"].max()
    assert df["datum"].max() == letzter
    assert df["datum"].min() == letzter - pd.DateOffset(months=3) + pd.Timedelta(days=1)
    samstage = pa.letzte_monate(3, wochentag="Samstag")
    assert (samstage["wochentag"] == "Samstag").all() and (samstage["datum"].dt.weekday == 5).all()


@pytest.mark.parametrize("aufruf", [lambda: pa.tag("2030-01-01"), lambda: pa.tage("2025-02-01", "2025-01-01"),
                                    lambda: pa.letzte_monate(1, wochentag="samstag"), lambda: pa.letzte_monate(0)])
def test_verstaendliche_fehler(aufruf):
    with pytest.raises(ValueError):
        aufruf()
