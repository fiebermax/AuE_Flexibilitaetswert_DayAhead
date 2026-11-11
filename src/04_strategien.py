# KI: Claude, Zweck: Strategien A, D, D_saison, B, B_ohne_wochentag, C im Backtest (Phase 2, E-045), geprüft von Susan (R3) durch Erklärzettel, Nachrechnen einer Woche und pytest
"""Step 4 (R3): backtest of the planning rules for the cleaning (CIP), 8 MWh per night, window 22-06 Uhr.

Owner: R3 (Susan). Rules (docs/hypothesen.md, E-042, E-046, E-047):
  A                 status quo: always 22-24 Uhr (fact, K-012)
  D                 fixed start hour, the one with the lowest mean block price in the TRAINING nights
  D_saison          same, but one start hour per season (feature "season", K3)
  B                 every Friday: per weekday the median block price of the last 4 nights with the
                    same weekday that are known on that Friday; per night the start with the lowest median
  B_ohne_wochentag  like B, but median over the last 28 known nights, one start for the whole week
                    (only to measure what the feature "same weekday" is worth, E-046)
  B_16              the team's rule from its project paper (question FS2): per weekday the MEAN block price
                    of the last 16 known nights with the same weekday; added after the freeze (diary E-049)
  C                 oracle: cheapest block with the real prices = flexibility value (upper bound);
                    equals daily planning, because a night's prices are known the day before at 12:45

Costs here are ELECTRICITY ONLY (A-017): mwh_flexibel x mean block price. R4 adds staff and surcharges
from backtest_naechte.csv (chosen block, its Sunday/holiday hours).

Look-ahead protection: B only ever sees `w.historie` from datenzugriff (R2), which raises
LookAheadFehler if future hours slip in. D and D_saison only see training nights. The real prices of the
planned nights come from the full block-cost matrix (step 03) and are used for EVALUATION only.

Rules frozen in commit 1d59427 (diary M-002). Phase 3 only added the test periods and the statistics
below; the rule functions are unchanged (check: git diff 1d59427 -- src/04_strategien.py).
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
import datenzugriff as dz  # noqa: E402
from gemeinsam import lade_params, pfad  # noqa: E402

# 03_merkmale starts with a digit, so it cannot be imported with a normal import statement.
_spec = importlib.util.spec_from_file_location("merkmale", SRC / "03_merkmale.py")
mk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mk)

STRATEGIEN = ["A", "D", "D_saison", "B", "B_ohne_wochentag", "B_16", "C"]
PERIODEN = ["training", "test_1_stunde", "test_2_viertel", "stresstest"]
TEST = ("test_1_stunde", "test_2_viertel")   # pooled = the one confirmatory sample (docs/hypothesen.md)
B_NAECHTE_JE_WOCHENTAG = 4               # params strategien.historie_wochen
B16_NAECHTE_JE_WOCHENTAG = 16           # team paper FS2: "Daten der letzten 16 Wochen" (E-049)
# one extra week: the last Friday night ends on Saturday (unknown on Friday morning). 17 weeks serve B_16;
# B and B_ohne_wochentag only take their last 4 / 28 nights from it, so they are unchanged.
B_HISTORIE_WOCHEN = B16_NAECHTE_JE_WOCHENTAG + 1


# ---------------------------------------------------------------------------------------------
# Rules: each returns the planned start hour (local clock) for every night of the week
# ---------------------------------------------------------------------------------------------
def regel_fest(naechte: list[str], start_h: int) -> dict[str, int]:
    """A and D: the same clock time every night."""
    return {n: start_h for n in naechte}


def regel_saison(naechte: list[str], saison_je_nacht: dict[str, str], start_je_saison: dict[str, int]) -> dict[str, int]:
    """D_saison: start hour of the season of that night (learned on training)."""
    return {n: start_je_saison[saison_je_nacht[n]] for n in naechte}


def _median_je_start(hist: pd.DataFrame, fenster_start: int, mass: str = "median") -> pd.Series:
    """Median (B) or mean (B_16) block price per clock start hour over the given history nights.
    Uses block_fuer_start, so the clock-change rule is the same as when the plan is executed."""
    starts = sorted(hist["start_lokal"].unique(), key=lambda h: (h - fenster_start) % 24)
    return pd.Series({h: mk.block_fuer_start(hist, h, fenster_start)["preis_eur_mwh"].agg(mass) for h in starts})


def _bester(median: pd.Series, fenster_start: int) -> int:
    """Lowest median; ties -> earlier in the night (same tie rule as everywhere else)."""
    return int(min(median.index, key=lambda h: (median[h], (h - fenster_start) % 24)))


def regel_b(naechte: list[str], wochentag_je_nacht: dict[str, int], hist_matrix: pd.DataFrame,
            fenster_start: int, n_je_wochentag: int, mass: str = "median") -> dict[str, int | None]:
    """B: per weekday the last n known nights with the same weekday; None if there are fewer than n
    (start of the data in 2022, E-044) -> that week is not counted for B."""
    plan = {}
    for n in naechte:
        wt = wochentag_je_nacht[n]
        gleiche = sorted(hist_matrix.loc[hist_matrix["wochentag_nacht"] == wt, "nacht"].unique())[-n_je_wochentag:]
        if len(gleiche) < n_je_wochentag:
            plan[n] = None
            continue
        plan[n] = _bester(_median_je_start(hist_matrix[hist_matrix["nacht"].isin(gleiche)], fenster_start, mass), fenster_start)
    return plan


def regel_b_ohne_wochentag(naechte: list[str], hist_matrix: pd.DataFrame, fenster_start: int,
                           n_naechte: int) -> dict[str, int | None]:
    """B without the weekday feature: one start for the week from the last n_naechte known nights."""
    letzte = sorted(hist_matrix["nacht"].unique())[-n_naechte:]
    if len(letzte) < n_naechte:
        return {n: None for n in naechte}
    start = _bester(_median_je_start(hist_matrix[hist_matrix["nacht"].isin(letzte)], fenster_start), fenster_start)
    return {n: start for n in naechte}


def naechte_der_woche(freitag: pd.Timestamp) -> list[str]:
    """The 7 nights Mon..Sun of the week planned on `freitag` (named after the day they start).

    Calendar dates, not "Friday + 72 hours": across a clock change that lands on Sunday 23:00 and
    shifts the whole week by one night (same pitfall as in datenzugriff._kalendertag)."""
    montag = pd.Timestamp(freitag).tz_localize(None).normalize() + pd.Timedelta(days=3)
    return [(montag + pd.Timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


# ---------------------------------------------------------------------------------------------
# Execute a plan with real prices
# ---------------------------------------------------------------------------------------------
def ausfuehren(matrix_woche: pd.DataFrame, plan: dict[str, int | None], fenster_start: int) -> pd.DataFrame:
    """Chosen block per night (real prices). Nights without a plan (B in early 2022) are left out."""
    zeilen = []
    for nacht, start in plan.items():
        if start is None:
            continue
        b = mk.block_fuer_start(matrix_woche[matrix_woche["nacht"] == nacht], start, fenster_start)
        zeilen.append(b)
    return pd.concat(zeilen, ignore_index=True) if zeilen else matrix_woche.iloc[0:0]


def backtest_periode(periode: str, preise: pd.DataFrame, last: pd.DataFrame, matrix: pd.DataFrame,
                     params: dict) -> pd.DataFrame:
    """One row per night x strategy for all planning weeks of the period (rolling origin)."""
    L = params["last"]
    fs, fe, bh = L["fenster_start_h"], L["fenster_ende_h"], L["blocklaenge_h"]
    train = mk.training_naechte(matrix, params)
    d_start = int(mk.bester_fester_start(train, fs, nach_saison=False)["start_lokal"].iloc[0])
    saison = mk.bester_fester_start(train, fs, nach_saison=True)
    d_saison = dict(zip(saison["saison"], saison["start_lokal"].astype(int)))
    mwh = last.set_index(last["datum"].dt.strftime("%Y-%m-%d"))["mwh_flexibel"]

    zeilen = []
    for w in dz.planungswochen(preise, last, periode, params, historie_wochen=B_HISTORIE_WOCHEN):
        naechte = naechte_der_woche(w.freitag)
        montag = naechte[0]
        mw = matrix[matrix["nacht"].isin(naechte)]               # real prices, incl. Sunday night to Mon 06:00
        if mw["nacht"].nunique() != 7:
            raise ValueError(f"Woche ab {montag}: nur {mw['nacht'].nunique()} vollständige Nächte")
        info = mw.drop_duplicates("nacht").set_index("nacht")
        hist = mk.blockkosten(w.historie, fs, fe, bh)             # ONLY what was known on that Friday

        plaene = {
            "A": regel_fest(naechte, L["status_quo_start_h"]),
            "D": regel_fest(naechte, d_start),
            "D_saison": regel_saison(naechte, info["saison"].to_dict(), d_saison),
            "B": regel_b(naechte, info["wochentag_nacht"].to_dict(), hist, fs, B_NAECHTE_JE_WOCHENTAG),
            "B_ohne_wochentag": regel_b_ohne_wochentag(naechte, hist, fs, 7 * B_NAECHTE_JE_WOCHENTAG),
            "B_16": regel_b(naechte, info["wochentag_nacht"].to_dict(), hist, fs, B16_NAECHTE_JE_WOCHENTAG, "mean"),
        }
        gewaehlt = {s: ausfuehren(mw, p, fs) for s, p in plaene.items()}
        gewaehlt["C"] = mk.billigster_block(mw)
        for s, g in gewaehlt.items():
            for _, r in g.iterrows():
                zeilen.append({"periode": periode, "woche": montag, "nacht": r["nacht"], "strategie": s,
                               "start_lokal": int(r["start_lokal"]), "start_utc": r["start_utc"],
                               "preis_eur_mwh": r["preis_eur_mwh"], "mwh": mwh[r["nacht"]],
                               "kosten_eur": mwh[r["nacht"]] * r["preis_eur_mwh"],
                               "sonntag_h": int(r["sonntag_h"]), "feiertag_h": int(r["feiertag_h"])})
    return pd.DataFrame(zeilen)


def je_woche(naechte: pd.DataFrame) -> pd.DataFrame:
    """Weekly electricity cost per strategy (EUR). A week counts for a strategy only with all 7 nights."""
    n = naechte.pivot_table(index=["periode", "woche"], columns="strategie", values="kosten_eur", aggfunc=["sum", "count"])
    kosten = n["sum"].where(n["count"] == 7)                     # e.g. B in the first weeks of 2022 -> empty
    kosten.columns = [f"kosten_{c}" for c in kosten.columns]
    return kosten[[f"kosten_{s}" for s in STRATEGIEN]].reset_index()


def pruefen(naechte: pd.DataFrame, wochen: pd.DataFrame, params: dict) -> None:
    """Checks that must hold for every run; stop instead of writing wrong results."""
    sq = naechte[naechte["strategie"] == "A"]
    assert (sq["start_lokal"] == params["last"]["status_quo_start_h"]).all(), "A ist nicht immer 22 Uhr"
    c = naechte[naechte["strategie"] == "C"].set_index("nacht")["kosten_eur"]
    andere = naechte[naechte["strategie"] != "C"]
    assert (andere["kosten_eur"].to_numpy() >= c.loc[andere["nacht"]].to_numpy() - 1e-9).all(), "Oracle teurer als eine Strategie"
    summe = naechte.groupby(["periode", "woche", "strategie"])["kosten_eur"].sum().unstack()
    for s in STRATEGIEN:
        ok = wochen.set_index(["periode", "woche"])[f"kosten_{s}"].dropna()
        assert (abs(ok - summe.loc[ok.index, s]) < 1e-6).all(), f"Wochensumme {s} stimmt nicht"


# ---------------------------------------------------------------------------------------------
# Statistics (Phase 3, docs/hypothesen.md, E-047)
# ---------------------------------------------------------------------------------------------
def mit_testgesamt(wochen: pd.DataFrame) -> pd.DataFrame:
    """Add the pooled confirmatory sample 'test_gesamt' = test 1 + test 2 (hourly prices in both)."""
    t = wochen[wochen["periode"].isin(TEST)].assign(periode="test_gesamt")
    return pd.concat([wochen, t], ignore_index=True)


def block_bootstrap_ki(d: np.ndarray, block: int, n_boot: int, seed: int, niveau: float = 0.95) -> tuple[float, float]:
    """Moving-block bootstrap interval of the mean. Blocks of consecutive weeks keep the dependence
    between neighbouring weeks (same season), which the t-test ignores. Used only as a check (E-047)."""
    rng = np.random.default_rng(seed)
    n = len(d)
    k = int(np.ceil(n / block))
    starts = rng.integers(0, n - block + 1, size=(n_boot, k))
    idx = (starts[:, :, None] + np.arange(block)).reshape(n_boot, -1)[:, :n]
    mittel = d[idx].mean(axis=1)
    a = (1 - niveau) / 2
    return float(np.quantile(mittel, a)), float(np.quantile(mittel, 1 - a))


def beschreibe(d: np.ndarray, p: dict) -> dict:
    """Mean with two-sided 95 % t-interval and block-bootstrap interval."""
    n, m, sd = len(d), float(d.mean()), float(d.std(ddof=1))
    h = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
    s = p["statistik"]
    bu, bo = block_bootstrap_ki(d, s["bootstrap_block_wochen"], s["bootstrap_n"], p["seed"])
    return {"n_wochen": n, "mittel_eur_woche": m, "sd": sd, "ki_unten": m - h, "ki_oben": m + h,
            "boot_unten": bu, "boot_oben": bo}


def t_test_einseitig(d: np.ndarray, alpha: float) -> dict:
    """H0: mean(d) <= 0 against H1: mean(d) > 0. t-test decides; Shapiro-Wilk and Wilcoxon are reported."""
    n, m, se = len(d), float(d.mean()), float(d.std(ddof=1) / np.sqrt(len(d)))
    t = stats.ttest_1samp(d, 0.0, alternative="greater")
    w = stats.wilcoxon(d, alternative="greater") if np.any(d != 0) else None
    p_w = float(w.pvalue) if w is not None else 1.0
    verworfen = bool(t.pvalue < alpha)
    return {"shapiro_p": float(stats.shapiro(d).pvalue), "t": float(t.statistic), "p_t": float(t.pvalue),
            "p_wilcoxon": p_w, "schwelle": alpha, "h0_verworfen": verworfen,
            "robust": verworfen == bool(p_w < alpha),
            # one-sided lower (1 - alpha) bound of the mean: for H0c this is the tipping point m*
            "untere_schranke": m - stats.t.ppf(1 - alpha, n - 1) * se}


def faktor(p: dict, art: str) -> float:
    """Contract: 'band' -> every shifted MWh at the spot price (1.0); 'proportional' -> spot share (0.3)."""
    return 1.0 if art == "band" else float(p["vertrag"]["spot_anteil"])


def ersparnis_tabelle(wochen: pd.DataFrame, p: dict) -> pd.DataFrame:
    """Interface R3 -> R4 (ki_strategien.csv): saving of every strategy against A, per period and contract case."""
    zeilen = []
    for per, g in wochen.groupby("periode", sort=False):
        for s in STRATEGIEN[1:]:
            ok = g[f"kosten_{s}"].notna()                  # same weeks for strategy and oracle (B in 2022)
            d = (g.loc[ok, "kosten_A"] - g.loc[ok, f"kosten_{s}"]).to_numpy()
            oracle = (g.loc[ok, "kosten_A"] - g.loc[ok, "kosten_C"]).mean()
            b = beschreibe(d, p)
            for art in ("band", "proportional"):
                f = faktor(p, art)
                zeilen.append({"strategie": s, "periode": per, "vertrag": art, "faktor": f, "n_wochen": b["n_wochen"],
                               **{k: b[k] * f for k in ("mittel_eur_woche", "ki_unten", "ki_oben", "boot_unten", "boot_oben")},
                               "eur_jahr": b["mittel_eur_woche"] * f * 52,
                               "anteil_oracle": b["mittel_eur_woche"] / oracle})
    return pd.DataFrame(zeilen)


def hypothesentests(wochen: pd.DataFrame, p: dict) -> pd.DataFrame:
    """H0b and H0c (electricity, R3) plus the two K3 comparisons. H0a needs staff costs -> R4 (Phase 4).
    Test decision only in test_gesamt; the other periods get the same numbers as a cross-check."""
    alpha = p["statistik"]["alpha_gesamt"] / p["statistik"]["anzahl_hypothesen"]
    vergleiche = [  # (name, column whose cost is subtracted FROM, column subtracted) -> d > 0 = H1
        ("H0b", "B spart mehr als D", "kosten_D", "kosten_B"),
        ("H0c", "Kipppunkt m*: C spart mehr als B", "kosten_B", "kosten_C"),
        ("K3 explorativ", "D_saison spart mehr als D", "kosten_D", "kosten_D_saison"),
        ("K3 explorativ", "B spart mehr als B_ohne_wochentag", "kosten_B_ohne_wochentag", "kosten_B"),
        ("explorativ", "B_16 spart mehr als D", "kosten_D", "kosten_B_16"),
    ]
    # Questions of the team paper (E-049), each against the status quo A; FS3 = "a year ago" = test 2.
    # Reported with the same t-test; NOT part of the pre-registered H0a-H0c (added after the freeze).
    team = [("FS1", "D spart gegenüber A", "kosten_A", "kosten_D", None),
            ("FS2", "B_16 spart gegenüber A", "kosten_A", "kosten_B_16", None),
            ("FS3", "B_16 spart gegenüber A im letzten Jahr", "kosten_A", "kosten_B_16", "test_2_viertel")]
    zeilen = []
    for per, g in wochen.groupby("periode", sort=False):
        for name, text, x, y, nur in team:
            if nur and per != nur:
                continue
            d = (g[x] - g[y]).dropna().to_numpy()
            zeilen.append({"hypothese": name, "vergleich": text, "periode": per, "konfirmatorisch": False,
                           **beschreibe(d, p), **t_test_einseitig(d, alpha)})
        for name, text, x, y in vergleiche:
            d = (g[x] - g[y]).dropna().to_numpy()
            zeile = {"hypothese": name, "vergleich": text, "periode": per,
                     "konfirmatorisch": per == "test_gesamt" and name.startswith("H0"), **beschreibe(d, p)}
            if np.any(d != 0):
                zeile.update(t_test_einseitig(d, alpha))
            zeilen.append(zeile)
    return pd.DataFrame(zeilen)


def fehleranalyse_b(naechte: pd.DataFrame) -> pd.DataFrame:
    """When does B miss? Regret = cost B - cost C per night, by period, season and weekday of the night."""
    b = naechte[naechte["strategie"] == "B"].set_index(["periode", "nacht"])
    c = naechte[naechte["strategie"] == "C"].set_index(["periode", "nacht"])
    d = naechte[naechte["strategie"] == "D"].set_index(["periode", "nacht"])
    x = b[["kosten_eur", "start_lokal"]].join(c[["kosten_eur", "start_lokal"]], rsuffix="_c").join(
        d[["kosten_eur"]], rsuffix="_d").reset_index()
    x["regret_b"] = x["kosten_eur"] - x["kosten_eur_c"]
    x["b_minus_d"] = x["kosten_eur"] - x["kosten_eur_d"]
    x["wochentag_nacht"] = pd.to_datetime(x["nacht"]).dt.dayofweek
    monat = pd.to_datetime(x["nacht"]).dt.month
    x["saison"] = monat.map({12: "Winter", 1: "Winter", 2: "Winter", 3: "Fruehling", 4: "Fruehling", 5: "Fruehling",
                             6: "Sommer", 7: "Sommer", 8: "Sommer", 9: "Herbst", 10: "Herbst", 11: "Herbst"})
    x["b_trifft_oracle"] = x["start_lokal"] == x["start_lokal_c"]
    zeilen = []
    for gruppe in ("saison", "wochentag_nacht"):
        for (per, wert), g in x.groupby(["periode", gruppe]):
            zeilen.append({"periode": per, "gruppe": gruppe, "wert": str(wert), "naechte": len(g),
                           "regret_b_eur_nacht": g["regret_b"].mean(), "b_minus_d_eur_nacht": g["b_minus_d"].mean(),
                           "anteil_b_trifft_oracle_pct": 100 * g["b_trifft_oracle"].mean()})
    return pd.DataFrame(zeilen)


def main(perioden: list[str] = PERIODEN) -> None:
    p = lade_params()
    L = p["last"]
    preise, last = dz.lade_preise(p), dz.lade_last(p)
    matrix = mk.blockkosten(preise, L["fenster_start_h"], L["fenster_ende_h"], L["blocklaenge_h"])
    naechte = pd.concat([backtest_periode(per, preise, last, matrix, p) for per in perioden], ignore_index=True)
    wochen = je_woche(naechte)
    pruefen(naechte, wochen, p)

    ziel = pfad(p, "tables")
    ziel.mkdir(parents=True, exist_ok=True)
    naechte.round(4).to_csv(ziel / "backtest_naechte.csv", index=False)
    wochen.round(2).to_csv(ziel / "backtest_wochen.csv", index=False)
    if not set(TEST) <= set(perioden):
        print("Nur Training gerechnet; Statistik erst mit den Testzeiträumen.")
        return
    w = mit_testgesamt(wochen)
    ki, ht, fa = ersparnis_tabelle(w, p), hypothesentests(w, p), fehleranalyse_b(naechte)
    ki.round(4).to_csv(ziel / "ki_strategien.csv", index=False)
    ht.round(4).to_csv(ziel / "hypothesentests.csv", index=False)
    fa.round(2).to_csv(ziel / "fehleranalyse_b.csv", index=False)

    print(f"Backtest: {len(wochen)} Wochen in {', '.join(perioden)} -> {ziel}")
    band = ki[ki["vertrag"] == "band"]
    for per in ["training", *TEST, "test_gesamt", "stresstest"]:
        print(f"\n{per}: Ersparnis gegenüber A in €/Woche (nur Strom, Faktor 1,0), 95-%-KI, Anteil am Oracle")
        for _, r in band[band["periode"] == per].iterrows():
            print(f"  {r['strategie']:17s} {r['mittel_eur_woche']:7.0f}  [{r['ki_unten']:6.0f}; {r['ki_oben']:6.0f}]"
                  f"  {100 * r['anteil_oracle']:5.1f} %  (n={r['n_wochen']})")
    print("\nHypothesen (test_gesamt, einseitig, Schwelle α/3):")
    k = ht[ht["periode"] == "test_gesamt"]
    print(k[["hypothese", "vergleich", "n_wochen", "mittel_eur_woche", "shapiro_p", "p_t", "p_wilcoxon",
             "h0_verworfen", "robust", "untere_schranke"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
