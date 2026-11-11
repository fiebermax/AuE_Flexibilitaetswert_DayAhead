# KI: Claude, Zweck: Sensitivitätsrechnung K2 Stufe 5 nach r2/docs/sensitivitaet_plan.md (Phase 5, E-045), geprüft von Max (R2) durch Review, Kontrollvarianten und pytest
"""Step 6 (R2): how much does the result depend on data preparation and on the synthetic assumptions?

Owner: R2 (Max). Plan and threshold fixed BEFORE this run: r2/docs/sensitivitaet_plan.md, diary E-044 (5 %).
Output: r2/ergebnisse/sensitivitaet.csv, one row per variant x strategy x period.

Key figure: mean NET saving vs. A in EUR/week (electricity x contract factor minus extra staff cost, as
R4 computes it), per strategy and test period, plus the share of the oracle. A variant is "relevant" if
the mean changes by more than the threshold OR a test decision (H0a, H0b) flips. All variants are reported.

Why most variants work on the existing backtest instead of re-running everything:
the planning RULES never look at the amount (MWh), the staff cost or the holiday calendar. Those only
enter the evaluation, so they can be changed afterwards on the chosen blocks (backtest_naechte.csv).
Only V7 (block length) changes what a rule can choose, so V7 re-runs R3's backtest as a function.
"""
import copy
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
import datenzugriff as dz  # noqa: E402
from gemeinsam import ROOT, feiertage_bayern, lade_params, pfad  # noqa: E402


def _modul(name: str, datei: str):
    """Steps whose file names start with a digit cannot be imported with a normal import statement."""
    spec = importlib.util.spec_from_file_location(name, SRC / datei)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


syn, mk, st, bw = (_modul("synthetisch", "02_synthetisch.py"), _modul("merkmale", "03_merkmale.py"),
                   _modul("strategien", "04_strategien.py"), _modul("bewertung", "05_bewertung.py"))

STRATEGIEN = ["D", "B", "B_16", "C"]
PERIODEN = list(st.TEST)                           # the confirmatory periods; test_gesamt is added


# ---------------------------------------------------------------------------------------------
# Evaluation (same arithmetic as R4, plus optional scaling for V2)
# ---------------------------------------------------------------------------------------------
def je_woche(naechte: pd.DataFrame, faktor: float, hochrechnen: bool) -> pd.DataFrame:
    """Net saving vs A per week and strategy. Only nights that A and the strategy both have are compared.
    hochrechnen=True (V2 only): weeks with dropped nights are scaled to 7 nights, so EUR/week stays comparable."""
    w = naechte.groupby(["periode", "woche", "strategie"]).agg(strom=("kosten_eur", "sum"), personal=("personal_eur", "sum"),
                                                                n=("nacht", "count")).reset_index()
    a = w[w["strategie"] == "A"].set_index(["periode", "woche"])
    x = w[w["strategie"] != "A"].join(a[["strom", "personal", "n"]], on=["periode", "woche"], rsuffix="_a")
    x = x[(x["n"] == x["n_a"]) & (x["n"] > 0)]
    skala = 7 / x["n"] if hochrechnen else 1.0
    x["strom_ersparnis"] = (x["strom_a"] - x["strom"]) * faktor * skala
    x["personal_mehr"] = (x["personal"] - x["personal_a"]) * skala
    x["netto"] = x["strom_ersparnis"] - x["personal_mehr"]
    if not hochrechnen:
        x = x[x["n"] == 7]                                         # as in R4: only complete weeks
    return st.mit_testgesamt(x[["periode", "woche", "strategie", "strom_ersparnis", "personal_mehr", "netto"]])


def kennzahlen(naechte: pd.DataFrame, params: dict, faktor: float, hochrechnen: bool = False) -> pd.DataFrame:
    """One row per strategy x period: net EUR/week, share of the oracle, H0a and H0b decisions (test_gesamt)."""
    alpha = params["statistik"]["alpha_gesamt"] / params["statistik"]["anzahl_hypothesen"]
    w = je_woche(naechte, faktor, hochrechnen)
    zeilen = []
    for per, g in w.groupby("periode"):
        c = g[g["strategie"] == "C"].set_index("woche")["strom_ersparnis"]
        piv = g.pivot_table(index="woche", columns="strategie", values="strom_ersparnis")
        for s in STRATEGIEN:
            gs = g[g["strategie"] == s].set_index("woche")
            if gs.empty:
                continue
            zeile = {"strategie": s, "periode": per, "n_wochen": len(gs), "mittel_eur_woche": gs["netto"].mean(),
                     "anteil_oracle": gs["strom_ersparnis"].sum() / c.loc[gs.index].sum()}
            if per == "test_gesamt" and s == "D":                 # H0a: D vs A after staff cost
                zeile["h0a_verworfen"] = st.t_test_einseitig(gs["netto"].to_numpy(), alpha)["h0_verworfen"]
            if per == "test_gesamt" and s == "B":                 # H0b: B saves more than D (electricity)
                d = (piv["B"] - piv["D"]).dropna().to_numpy()
                zeile["h0b_verworfen"] = st.t_test_einseitig(d, alpha)["h0_verworfen"]
            zeilen.append(zeile)
    return pd.DataFrame(zeilen)


# ---------------------------------------------------------------------------------------------
# Variants
# ---------------------------------------------------------------------------------------------
def mit_personal(naechte: pd.DataFrame, preise: pd.DataFrame, params: dict) -> pd.DataFrame:
    n = naechte.copy()
    n["personal_eur"] = bw.personalkosten(n, preise, params)
    return n


def menge_skalieren(naechte: pd.DataFrame, mwh_neu: pd.Series | float) -> pd.DataFrame:
    """Electricity cost is linear in the MWh per night; the chosen block does not depend on it."""
    n = naechte.copy()
    neu = n["nacht"].map(mwh_neu) if isinstance(mwh_neu, pd.Series) else mwh_neu
    n["kosten_eur"] = n["preis_eur_mwh"] * neu
    n["mwh"] = neu
    return n


def auffaellige_naechte(preise_clean: pd.DataFrame, fenster_start: int, fenster_ende: int) -> set[str]:
    """Nights (named after their 22:00 day) with at least one flag_outlier hour in the window (V2)."""
    p = preise_clean[preise_clean["flag_outlier"].astype(bool)]
    h = p["stunde_lokal"]
    p = p[(h >= fenster_start) | (h < fenster_ende)]
    datum = pd.to_datetime(p["datum_lokal"])
    nacht = datum.where(p["stunde_lokal"] >= fenster_start, datum - pd.Timedelta(days=1))
    return set(nacht.dt.strftime("%Y-%m-%d"))


def varianten(basis_naechte: pd.DataFrame, preise_clean: pd.DataFrame, params: dict, mit_v7: bool = True):
    """Yields (id, switch, value, nights with staff cost, contract factor, scale-up flag).
    mit_v7=False skips the slow re-run of the backtest (tests only)."""
    L, f_band = params["last"], st.faktor(params, "band")
    basis = mit_personal(basis_naechte, preise_clean, params)
    yield "Basis", "—", "—", basis, f_band, False

    flag = auffaellige_naechte(preise_clean, L["fenster_start_h"], L["fenster_ende_h"])
    yield "V2", "Auswertung ohne Nächte mit flag_outlier", f"{len(flag)} Nächte raus", \
        basis[~basis["nacht"].isin(flag)], f_band, True

    p3 = copy.deepcopy(params)
    p3["last"]["feiertagsvariante_mariae_himmelfahrt"] = True
    pr3 = preise_clean.copy()
    pr3["feiertag"] = feiertage_bayern(pd.DatetimeIndex(pd.to_datetime(pr3["ts_lokal"], utc=True).dt.tz_convert(
        params["markt"]["zeitzone"])), True)
    yield "V3", "last.feiertagsvariante_mariae_himmelfahrt", True, mit_personal(basis_naechte, pr3, p3), f_band, False

    tage = syn.erzeuge_last("2022-01-01", params["zeitraeume"]["datenstand"], L["mwh_pro_tag"],
                            "Mo-Fr ohne Feiertage Bayern", L["gesamtverbrauch_mwh_pro_tag"])
    mwh = tage.set_index(tage["datum"].astype(str).str[:10])["mwh_flexibel"]
    v4 = menge_skalieren(basis, mwh)
    v4["personal_eur"] = np.where(v4["mwh"] > 0, v4["personal_eur"], 0.0)    # no production -> no cleaning
    yield "V4", "last.produktionstage", "Mo-Fr ohne Feiertage Bayern", v4, f_band, False

    for vid, m in (("V6a", 4.0), ("V6b", 12.0), ("V6c", 16.0)):                # V6c: team paper "8 MW for 2 h" (E-049)
        yield vid, "last.mwh_pro_tag", m, menge_skalieren(basis, m), f_band, False

    for vid, bh in ((("V7a", 1), ("V7b", 3), ("V7c", 4)) if mit_v7 else ()):
        p7 = copy.deepcopy(params)
        p7["last"]["blocklaenge_h"] = bh                                     # energy stays 8 MWh per night
        yield vid, "last.blocklaenge_h", bh, mit_personal(backtest_neu(p7), preise_clean, p7), f_band, False

    yield "V8", "vertrag.bewertung_verschiebung (falls der Festpreis nicht voll verbraucht wird)", "proportional", basis, st.faktor(params, "proportional"), False

    p9 = copy.deepcopy(params)
    p9["kosten"]["nachtstunden"] = [23, 0, 1, 2, 3, 4, 5]
    yield "V9", "kosten.nachtstunden", "23-06 Uhr", mit_personal(basis_naechte, preise_clean, p9), f_band, False

    p10 = copy.deepcopy(params)
    p10["kosten"]["zuschlag_regel"] = "addiert"
    yield "V10", "kosten.zuschlag_regel", "addiert", mit_personal(basis_naechte, preise_clean, p10), f_band, False


def backtest_neu(params: dict) -> pd.DataFrame:
    """Re-run R3's frozen rules with changed parameters (V7), test periods only."""
    L = params["last"]
    preise, last = dz.lade_preise(params), dz.lade_last(params)
    matrix = mk.blockkosten(preise, L["fenster_start_h"], L["fenster_ende_h"], L["blocklaenge_h"])
    return pd.concat([st.backtest_periode(per, preise, last, matrix, params) for per in PERIODEN], ignore_index=True)


def sensitivitaet(basis_naechte: pd.DataFrame, preise_clean: pd.DataFrame, params: dict) -> pd.DataFrame:
    schwelle = params["statistik"]["sensitivitaet_schwelle_pct"]
    alle = []
    for vid, schalter, wert, n, f, hoch in varianten(basis_naechte, preise_clean, params):
        k = kennzahlen(n, params, f, hoch)
        k.insert(0, "variante", vid)
        k.insert(1, "schalter", schalter)
        k.insert(2, "wert", str(wert))
        alle.append(k)
    t = pd.concat(alle, ignore_index=True)
    b = t[t["variante"] == "Basis"].set_index(["strategie", "periode"])
    t["delta_eur"] = t["mittel_eur_woche"] - b.loc[list(zip(t["strategie"], t["periode"])), "mittel_eur_woche"].to_numpy()
    t["delta_pct"] = 100 * t["delta_eur"] / b.loc[list(zip(t["strategie"], t["periode"])), "mittel_eur_woche"].to_numpy()
    h0 = t[t["periode"] == "test_gesamt"].groupby("variante")[["h0a_verworfen", "h0b_verworfen"]].first()
    gleich = (h0 == h0.loc["Basis"]).all(axis=1)
    t["h0_entscheidung_gleich"] = t["variante"].map(gleich)
    t["relevant"] = (t["delta_pct"].abs() > schwelle) | ~t["h0_entscheidung_gleich"]
    return t


def main() -> None:
    p = lade_params()
    datei = pfad(p, "tables") / "backtest_naechte.csv"
    if not datei.exists():
        raise FileNotFoundError(f"{datei} fehlt. Zuerst src/04_strategien.py (R3) ausführen.")
    naechte = pd.read_csv(datei)
    naechte = naechte[naechte["periode"].isin(PERIODEN)].reset_index(drop=True)
    preise_clean = pd.read_csv(pfad(p, "processed") / "preise_clean.csv")
    t = sensitivitaet(naechte, preise_clean, p)

    ziel = ROOT / p["cleaning"]["reports"]                      # next to the other R2 results
    t.round(4).to_csv(ziel / "sensitivitaet.csv", index=False)
    print(f"Sensitivität -> {ziel / 'sensitivitaet.csv'} (Schwelle {p['statistik']['sensitivitaet_schwelle_pct']} %)")
    sicht = t[(t["periode"] == "test_gesamt") & (t["strategie"] == "D")]
    print(sicht[["variante", "schalter", "wert", "mittel_eur_woche", "delta_pct", "anteil_oracle",
                 "h0a_verworfen", "h0_entscheidung_gleich", "relevant"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
