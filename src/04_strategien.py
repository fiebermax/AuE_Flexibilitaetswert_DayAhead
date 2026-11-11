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
  C                 oracle: cheapest block with the real prices = flexibility value (upper bound);
                    equals daily planning, because a night's prices are known the day before at 12:45

Costs here are ELECTRICITY ONLY (A-017): mwh_flexibel x mean block price. R4 adds staff and surcharges
from backtest_naechte.csv (chosen block, its Sunday/holiday hours).

Look-ahead protection: B only ever sees `w.historie` from datenzugriff (R2), which raises
LookAheadFehler if future hours slip in. D and D_saison only see training nights. The real prices of the
planned nights come from the full block-cost matrix (step 03) and are used for EVALUATION only.

Phase 2 (this commit) runs the training period only. Test periods and statistics follow in Phase 3,
after the rules are frozen (commit "Strategien eingefroren").
"""
import importlib.util
import sys
from pathlib import Path

import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
import datenzugriff as dz  # noqa: E402
from gemeinsam import lade_params, pfad  # noqa: E402

# 03_merkmale starts with a digit, so it cannot be imported with a normal import statement.
_spec = importlib.util.spec_from_file_location("merkmale", SRC / "03_merkmale.py")
mk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mk)

STRATEGIEN = ["A", "D", "D_saison", "B", "B_ohne_wochentag", "C"]
PERIODEN_PHASE_2 = ["training"]          # Phase 3 adds test_1_stunde, test_2_viertel, stresstest
B_NAECHTE_JE_WOCHENTAG = 4               # params strategien.historie_wochen
B_HISTORIE_WOCHEN = 5                    # one extra week: the last Friday night ends on Saturday (unknown)


# ---------------------------------------------------------------------------------------------
# Rules: each returns the planned start hour (local clock) for every night of the week
# ---------------------------------------------------------------------------------------------
def regel_fest(naechte: list[str], start_h: int) -> dict[str, int]:
    """A and D: the same clock time every night."""
    return {n: start_h for n in naechte}


def regel_saison(naechte: list[str], saison_je_nacht: dict[str, str], start_je_saison: dict[str, int]) -> dict[str, int]:
    """D_saison: start hour of the season of that night (learned on training)."""
    return {n: start_je_saison[saison_je_nacht[n]] for n in naechte}


def _median_je_start(hist: pd.DataFrame, fenster_start: int) -> pd.Series:
    """Median block price per clock start hour over the given history nights.
    Uses block_fuer_start, so the clock-change rule is the same as when the plan is executed."""
    starts = sorted(hist["start_lokal"].unique(), key=lambda h: (h - fenster_start) % 24)
    return pd.Series({h: mk.block_fuer_start(hist, h, fenster_start)["preis_eur_mwh"].median() for h in starts})


def _bester(median: pd.Series, fenster_start: int) -> int:
    """Lowest median; ties -> earlier in the night (same tie rule as everywhere else)."""
    return int(min(median.index, key=lambda h: (median[h], (h - fenster_start) % 24)))


def regel_b(naechte: list[str], wochentag_je_nacht: dict[str, int], hist_matrix: pd.DataFrame,
            fenster_start: int, n_je_wochentag: int) -> dict[str, int | None]:
    """B: per weekday the last n known nights with the same weekday; None if there are fewer than n
    (start of the data in 2022, E-044) -> that week is not counted for B."""
    plan = {}
    for n in naechte:
        wt = wochentag_je_nacht[n]
        gleiche = sorted(hist_matrix.loc[hist_matrix["wochentag_nacht"] == wt, "nacht"].unique())[-n_je_wochentag:]
        if len(gleiche) < n_je_wochentag:
            plan[n] = None
            continue
        plan[n] = _bester(_median_je_start(hist_matrix[hist_matrix["nacht"].isin(gleiche)], fenster_start), fenster_start)
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


def main(perioden: list[str] = PERIODEN_PHASE_2) -> None:
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

    print(f"Backtest {', '.join(perioden)}: {wochen['woche'].nunique()} Wochen -> {ziel / 'backtest_wochen.csv'}")
    for per, g in wochen.groupby("periode"):
        ers = {s: g["kosten_A"] - g[f"kosten_{s}"] for s in STRATEGIEN if s != "A"}
        oracle = ers["C"].mean()
        print(f"\n{per}: mittlere Ersparnis gegenüber A, nur Strom, Faktor 1,0")
        for s, e in ers.items():
            print(f"  {s:17s} {e.mean():8.0f} €/Woche   Anteil am Oracle {100 * e.mean() / oracle:5.1f} %")


if __name__ == "__main__":
    main()
