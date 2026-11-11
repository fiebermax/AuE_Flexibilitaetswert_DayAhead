# KI: Claude, Zweck: Tests der Sensitivitätsrechnung (R2, Phase 5), geprüft von Max (R2) durch Review
"""Sensitivity (src/06_sensitivitaet.py): base = R4, variants really change their switch, V6 is linear."""
import copy
import importlib.util
from pathlib import Path

import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PARAMS = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
CLEAN = ROOT / PARAMS["daten"]["pfade"]["processed"] / "preise_clean.csv"
NAECHTE = ROOT / PARAMS["daten"]["pfade"]["tables"] / "backtest_naechte.csv"

spec = importlib.util.spec_from_file_location("sensitivitaet", ROOT / "src" / "06_sensitivitaet.py")
s6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s6)
braucht_daten = pytest.mark.skipif(not (CLEAN.exists() and NAECHTE.exists()), reason="zuerst python src/run_all.py")


@pytest.fixture(scope="module")
def daten():
    n = pd.read_csv(NAECHTE)
    return n[n["periode"].isin(s6.PERIODEN)].reset_index(drop=True), pd.read_csv(CLEAN)


@braucht_daten
def test_basis_reproduziert_r4(daten):
    n, pr = daten
    basis = s6.kennzahlen(s6.mit_personal(n, pr, PARAMS), PARAMS, 1.0).set_index(["strategie", "periode"])
    r4 = s6.bw.netto_tests(s6.mit_personal(n, pr, PARAMS), PARAMS)
    r4 = r4[r4["vertrag"] == "band"].set_index(["strategie", "periode"])
    for s in s6.STRATEGIEN:
        assert basis.loc[(s, "test_gesamt"), "mittel_eur_woche"] == pytest.approx(r4.loc[(s, "test_gesamt"), "netto_eur_woche"])


@braucht_daten
def test_menge_skaliert_strom_linear_anteil_bleibt(daten):
    n, pr = daten
    b = s6.mit_personal(n, pr, PARAMS)
    k1 = s6.kennzahlen(b, PARAMS, 1.0).set_index(["strategie", "periode"])
    k2 = s6.kennzahlen(s6.menge_skalieren(b, 2 * PARAMS["last"]["mwh_pro_tag"]), PARAMS, 1.0).set_index(["strategie", "periode"])
    assert (k1["anteil_oracle"] - k2["anteil_oracle"]).abs().max() < 1e-12
    w1, w2 = s6.je_woche(b, 1.0, False), s6.je_woche(s6.menge_skalieren(b, 2 * PARAMS["last"]["mwh_pro_tag"]), 1.0, False)
    assert (w2["strom_ersparnis"] - 2 * w1["strom_ersparnis"]).abs().max() < 1e-6


@braucht_daten
def test_jede_variante_aendert_ihren_schalter(daten):
    """No silent null variant: personal cost, amount, nights or factor differ from the base."""
    n, pr = daten
    gesehen = {}
    for vid, _, _, nn, f, hoch in s6.varianten(n.head(2000), pr, PARAMS, mit_v7=False):   # V7: slow, checked in the run
        gesehen[vid] = (round(nn["personal_eur"].sum(), 2), round(nn["kosten_eur"].sum(), 2), len(nn), f, hoch)
    basis = gesehen.pop("Basis")
    for vid, wert in gesehen.items():
        assert wert != basis, vid


def test_v4_ohne_produktion_keine_reinigung_und_kein_personal():
    n = pd.DataFrame({"nacht": ["2025-06-14", "2025-06-16"], "preis_eur_mwh": [50.0, 60.0], "personal_eur": [300.0, 300.0]})
    mwh = pd.Series({"2025-06-14": 0.0, "2025-06-16": 8.0})
    v = s6.menge_skalieren(n, mwh)
    assert list(v["kosten_eur"]) == [0.0, 480.0]


def test_auffaellige_naechte_gehoeren_zur_nacht_davor():
    pr = pd.DataFrame({"flag_outlier": [True, True, True], "stunde_lokal": [23, 3, 12],
                       "datum_lokal": ["2025-06-10", "2025-06-12", "2025-06-12"]})
    assert s6.auffaellige_naechte(pr, 22, 6) == {"2025-06-10", "2025-06-11"}
