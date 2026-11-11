# KI: Claude, Zweck: Tests der Blockkosten-Matrix (R3, Phase 1), geprüft von Susan (R3) durch Review und Nachrechnen
"""Blockkosten-Matrix (src/03_merkmale.py): same nights as R2, clock changes, Sunday night, training only."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PARAMS = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
CLEAN = ROOT / PARAMS["daten"]["pfade"]["processed"] / "preise_clean.csv"
TZ = PARAMS["markt"]["zeitzone"]
L = PARAMS["last"]


def _modul(name, datei):
    spec = importlib.util.spec_from_file_location(name, ROOT / "src" / datei)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mk, fa, cl = _modul("merkmale", "03_merkmale.py"), _modul("fensteranalyse", "fensteranalyse.py"), _modul("cleaning", "cleaning.py")
braucht_daten = pytest.mark.skipif(not CLEAN.exists(), reason="preise_clean.csv fehlt; zuerst python src/run_all.py")


@pytest.fixture(scope="module")
def preise():
    return pd.read_csv(CLEAN)


@pytest.fixture(scope="module")
def matrix(preise):
    return mk.blockkosten(preise, L["fenster_start_h"], L["fenster_ende_h"], L["blocklaenge_h"])


def _nacht(utc_start, n_stunden, preise_je_stunde=None):
    """Synthetic hours from utc_start; prices 100 unless given."""
    zeiten = pd.date_range(utc_start, periods=n_stunden, freq="h", tz="UTC")
    p = preise_je_stunde or [100.0] * n_stunden
    df = pd.DataFrame({"ts_utc": zeiten, "preis_eur_mwh": p})
    return cl.zeitspalten(df, TZ, pd.Timestamp("2025-10-01", tz=TZ), False)


@braucht_daten
def test_gleiche_naechte_und_preise_wie_fensteranalyse_r2(preise, matrix):
    """Cross-check with R2's tested function: same nights, same status quo price, same cheapest block."""
    r2 = fa.fenster_je_tag(preise, L["fenster_start_h"], L["fenster_ende_h"], L["blocklaenge_h"], L["status_quo_start_h"])
    best = mk.billigster_block(matrix).set_index("nacht")
    sq = mk.block_fuer_start(matrix, L["status_quo_start_h"], L["fenster_start_h"]).set_index("nacht")
    r2 = r2.set_index("datum_lokal")
    assert list(best.index) == list(r2.index)
    assert (best["preis_eur_mwh"] - r2["preis_billigst"]).abs().max() < 1e-9
    assert (sq["preis_eur_mwh"] - r2["preis_status_quo"]).abs().max() < 1e-9
    assert (best["start_lokal"] == r2["start_billigst"]).all()


@braucht_daten
def test_blockanzahl_normal_und_zeitumstellung(matrix):
    n = matrix.groupby("nacht").size()
    assert n["2025-06-10"] == 7                       # 8 hours -> 7 blocks
    assert n["2025-03-29"] == 6                       # March: 02:00 missing, 7 hours
    assert n["2025-10-25"] == 8                       # October: 02:00 twice, 9 hours
    okt = matrix[matrix["nacht"] == "2025-10-25"]
    assert list(okt["start_lokal"]) == [22, 23, 0, 1, 2, 2, 3, 4]


@braucht_daten
def test_startregel_bei_zeitumstellung(matrix):
    """March: a 02:00 rule takes the 03:00 block; October: the first of the two 02:00 blocks."""
    zwei = mk.block_fuer_start(matrix, 2, L["fenster_start_h"]).set_index("nacht")
    assert zwei.loc["2025-03-29", "start_lokal"] == 3
    assert zwei.loc["2025-10-25", "pos"] == 4 and zwei.loc["2025-10-25", "start_lokal"] == 2
    assert (mk.block_fuer_start(matrix, 22, 22)["start_lokal"] == 22).all()   # status quo exists every night


@braucht_daten
def test_sonntagsnacht_reicht_bis_montag_6_uhr(matrix):
    """Sunday 15.06.2025: the 22:00 block is Sunday (2 h), the 04:00 block lies on Monday (0 h)."""
    so = matrix[matrix["nacht"] == "2025-06-15"].set_index("start_lokal")
    assert so.loc[22, "sonntag_h"] == 2 and so.loc[23, "sonntag_h"] == 1 and so.loc[4, "sonntag_h"] == 0
    sa = matrix[matrix["nacht"] == "2025-06-14"].set_index("start_lokal")      # Saturday night
    assert sa.loc[22, "sonntag_h"] == 0 and sa.loc[0, "sonntag_h"] == 2


def test_unvollstaendige_nacht_wird_verworfen():
    """A history that ends in the middle of a night must not create a (wrong) short night."""
    df = _nacht("2025-06-10 20:00", 5)                 # 22:00 to 02:00 local only
    leer = mk.blockkosten(df, 22, 6, 2)
    assert leer.empty and "wochentag_nacht" in leer.columns   # columns stay, so B can say "no plan" (E-044)


def test_blockpreis_ist_mittel_der_stunden_und_billigster_block():
    preise = [100, 90, 80, 10, 30, 70, 60, 50]         # 22, 23, 0, 1, 2, 3, 4, 5 local
    m = mk.blockkosten(_nacht("2025-06-10 20:00", 8, preise), 22, 6, 2)
    assert list(m["preis_eur_mwh"]) == [95, 85, 45, 20, 50, 65, 55]
    b = mk.billigster_block(m).iloc[0]
    assert b["start_lokal"] == 1 and b["preis_eur_mwh"] == 20


def test_bester_fester_start_mittel_und_gleichstand():
    m = pd.DataFrame({"nacht": ["a", "a", "b", "b"], "saison": "Sommer", "pos": [0, 1, 0, 1],
                      "start_lokal": [22, 23, 22, 23], "preis_eur_mwh": [10.0, 30.0, 50.0, 30.0]})
    r = mk.bester_fester_start(m, 22, nach_saison=False).iloc[0]
    assert r["start_lokal"] == 22                       # mean 30 vs 30 -> tie -> earlier in the night


@braucht_daten
def test_fester_block_nur_aus_dem_training(matrix):
    t = mk.training_naechte(matrix, PARAMS)
    jahre = pd.to_datetime(t["nacht"]).dt.year.unique()
    assert set(jahre) == {2023, 2024}
