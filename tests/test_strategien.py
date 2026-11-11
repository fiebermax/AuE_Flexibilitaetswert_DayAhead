# KI: Claude, Zweck: Tests der Strategien im Backtest (R3, Phase 2), geprüft von Susan (R3) durch Review und Nachrechnen
"""Backtest rules (src/04_strategien.py): B's choice, no look-ahead, clock-change weeks, checks."""
import copy
import importlib.util
from pathlib import Path

import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PARAMS = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
CLEAN = ROOT / PARAMS["daten"]["pfade"]["processed"] / "preise_clean.csv"
L = PARAMS["last"]

spec = importlib.util.spec_from_file_location("strategien", ROOT / "src" / "04_strategien.py")
st = importlib.util.module_from_spec(spec)
spec.loader.exec_module(st)
dz, mk = st.dz, st.mk
braucht_daten = pytest.mark.skipif(not CLEAN.exists(), reason="preise_clean.csv fehlt; zuerst python src/run_all.py")


def _hist(naechte_preise):
    """Synthetic history matrix: {night: (weekday, {start: price})}."""
    zeilen = []
    for nacht, (wt, preise) in naechte_preise.items():
        for pos, (start, preis) in enumerate(preise.items()):
            zeilen.append({"nacht": nacht, "wochentag_nacht": wt, "saison": "Sommer", "pos": pos,
                           "start_lokal": start, "preis_eur_mwh": preis})
    return pd.DataFrame(zeilen)


def test_b_nimmt_median_der_letzten_vier_gleichen_wochentage():
    # Five Monday nights; the oldest one (cheap at 22 Uhr) must be ignored, the median of the last four wins.
    h = _hist({
        "2025-05-05": (0, {22: 1.0, 2: 90.0, 3: 90.0}),
        "2025-05-12": (0, {22: 99.0, 2: 50.0, 3: 60.0}),
        "2025-05-19": (0, {22: 99.0, 2: 70.0, 3: 40.0}),
        "2025-05-26": (0, {22: 99.0, 2: 55.0, 3: 65.0}),
        "2025-06-02": (0, {22: 99.0, 2: 52.0, 3: 61.0}),
        "2025-06-03": (1, {22: 1.0, 2: 99.0, 3: 99.0}),           # Tuesday: must not influence Monday
    })
    plan = st.regel_b(["2025-06-09"], {"2025-06-09": 0}, h, 22, 4)
    assert plan == {"2025-06-09": 2}                               # medians: 22 -> 99, 2 -> 53.5, 3 -> 60.5


def test_b_ohne_genug_historie_plant_nicht():
    h = _hist({"2022-01-03": (0, {22: 1.0, 3: 2.0})})
    assert st.regel_b(["2022-01-10"], {"2022-01-10": 0}, h, 22, 4) == {"2022-01-10": None}


@pytest.mark.parametrize("freitag, montag", [("2025-03-28", "2025-03-31"), ("2025-10-24", "2025-10-27"),
                                             ("2025-06-13", "2025-06-16")])
def test_woche_beginnt_auch_bei_zeitumstellung_am_montag(freitag, montag):
    n = st.naechte_der_woche(pd.Timestamp(freitag, tz="Europe/Berlin"))
    assert n[0] == montag and len(set(n)) == 7 and pd.Timestamp(n[0]).weekday() == 0


@braucht_daten
def test_b_sieht_die_zielwoche_nicht():
    """Change all prices from Saturday on: B's plan for the following week must not change."""
    p = PARAMS
    preise, last = dz.lade_preise(p), dz.lade_last(p)
    freitag = pd.Timestamp("2024-06-07", tz="Europe/Berlin")
    naechte = st.naechte_der_woche(freitag)

    def plan(pr):
        w = dz.planungswoche(pr, last, freitag, p, historie_wochen=st.B_HISTORIE_WOCHEN)
        hist = mk.blockkosten(w.historie, L["fenster_start_h"], L["fenster_ende_h"], L["blocklaenge_h"])
        wt = {n: pd.Timestamp(n).weekday() for n in naechte}
        return st.regel_b(naechte, wt, hist, L["fenster_start_h"], st.B_NAECHTE_JE_WOCHENTAG)

    verfaelscht = preise.copy()
    zukunft = verfaelscht["zeit"] >= dz.bekannt_bis(freitag, p)
    verfaelscht.loc[zukunft, "preis_eur_mwh"] = -verfaelscht.loc[zukunft, "preis_eur_mwh"] * 7
    assert plan(preise) == plan(verfaelscht)


@braucht_daten
def test_backtest_woche_mit_zeitumstellung_und_pruefungen():
    """Two training weeks around the October clock change 2024: 7 nights each, all checks pass."""
    p = copy.deepcopy(PARAMS)
    p["zeitraeume"]["mini"] = ["2024-10-21", "2024-11-03"]
    preise, last = dz.lade_preise(p), dz.lade_last(p)
    matrix = mk.blockkosten(preise, L["fenster_start_h"], L["fenster_ende_h"], L["blocklaenge_h"])
    n = st.backtest_periode("mini", preise, last, matrix, p)
    w = st.je_woche(n)
    st.pruefen(n, w, p)
    assert list(w["woche"]) == ["2024-10-21", "2024-10-28"]
    assert w[[f"kosten_{s}" for s in st.STRATEGIEN]].notna().all().all()
    assert (n.groupby(["woche", "strategie"]).size() == 7).all()
    a = n[n["strategie"] == "A"]
    assert (a["kosten_eur"] == a["mwh"] * a["preis_eur_mwh"]).all() and (a["mwh"] == L["mwh_pro_tag"]).all()

    # The checks must catch a broken oracle.
    kaputt = n.copy()
    kaputt.loc[kaputt["strategie"] == "C", "kosten_eur"] += 1000
    with pytest.raises(AssertionError):
        st.pruefen(kaputt, w, p)
