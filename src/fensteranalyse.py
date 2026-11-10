# KI: Claude, Zweck: Rückblick-Kennzahl Mehrkosten Status quo vs. billigstes Fenster (Ortszeit, auch über Mitternacht), geprüft von <Name R2> durch Review, Nachrechnen einer Nacht und pytest
"""Descriptive look-back figure for R2's slide c (diary E-030, revised by E-037). NOT a strategy.

Case S1 (diary E-033): the cleaning (CIP, 4 MW for 2 h = 8 MWh) may run anywhere in the night window
22-06 Uhr. Status quo A is 22-24 Uhr, right after production ends (assumption, E-031).

For every window (here: every night, named after the day it starts, e.g. 2025-03-07 = Fri 22:00 to
Sat 06:00): compare the status quo block with the cheapest block of the same length inside the window,
using the real prices of that night, i.e. hindsight ("Rückblick mit bekannten Preisen, keine Strategie").

Per window:
  preis_status_quo   mean price of the status quo block             EUR/MWh
  preis_billigst     mean price of the cheapest block                EUR/MWh
  start_billigst     local start hour of that block (22, 23, 0, ... 4)
  mehrkosten_eur_mwh preis_status_quo - preis_billigst (>= 0)      EUR/MWh
  mehrkosten_pct     mehrkosten / preis_billigst * 100, only if preis_billigst > 0 (otherwise empty:
                     a percentage of a price at or below zero has no meaning)
  n_stunden          real hours in the window: 8, or 7 / 9 in the nights of the clock change

Why the mean price: with constant power over the block, cost per MWh = mean of the hourly prices.
Why real hours: blocks are consecutive UTC hours (E-026, E-036). In the October night the clock shows
02:00 twice; a 2-hour cleaning is still 2 hours of work and 8 MWh, so a block may cover both "02:00".
Window boundaries are LOCAL hours (stunde_lokal), never UTC: shifts follow the clock in the plant.

Run directly (`python src/fensteranalyse.py`) to write the tables in reports/tables/ (diary E-037).
"""
import sys
from pathlib import Path

import pandas as pd

SAISON_REIHENFOLGE = ["Winter", "Fruehling", "Sommer", "Herbst"]


def fenster_je_tag(df: pd.DataFrame, fenster_start: int, fenster_ende: int, block_h: int, status_quo_start: int) -> pd.DataFrame:
    """One row per window. df needs: ts_utc, datum_lokal, stunde_lokal, saison, preis_eur_mwh.

    fenster_start > fenster_ende means the window crosses midnight (22, 6 -> 22:00 to 06:00 next day);
    then the hours after midnight belong to the window of the PREVIOUS calendar day.
    A window that is not complete (data edge or gap) is skipped; the caller sees it in the row count.
    """
    d = df[["ts_utc", "datum_lokal", "stunde_lokal", "saison", "preis_eur_mwh"]].copy()
    d["ts_utc"] = pd.to_datetime(d["ts_utc"], utc=True)
    h = d["stunde_lokal"]
    ueber_mitternacht = fenster_start > fenster_ende
    if ueber_mitternacht:
        im_fenster = (h >= fenster_start) | (h < fenster_ende)
    else:
        im_fenster = (h >= fenster_start) & (h < fenster_ende)
    d = d[im_fenster].sort_values("ts_utc")

    # Name each window after the day it starts: hours after midnight move back one calendar day.
    datum = pd.to_datetime(d["datum_lokal"])
    if ueber_mitternacht:
        datum = datum.where(d["stunde_lokal"] >= fenster_start, datum - pd.Timedelta(days=1))
    d["fenster_datum"] = datum.dt.strftime("%Y-%m-%d")

    letzte_stunde = (fenster_ende - 1) % 24
    zeilen = []
    for fdatum, g in d.groupby("fenster_datum", sort=True):
        stunden = g["stunde_lokal"].to_numpy()
        lueckenlos = (g["ts_utc"].diff().dropna() == pd.Timedelta(hours=1)).all()
        if not lueckenlos or stunden[0] != fenster_start or stunden[-1] != letzte_stunde:
            continue                                                  # incomplete window at the data edge
        preis = g["preis_eur_mwh"].to_numpy()
        mittel = [preis[i:i + block_h].mean() for i in range(len(preis) - block_h + 1)]
        i_min = min(range(len(mittel)), key=mittel.__getitem__)       # earliest start if prices tie
        i_sq = list(stunden).index(status_quo_start)                  # first hour with the status quo clock time
        sq, best = mittel[i_sq], mittel[i_min]
        zeilen.append({
            "datum_lokal": fdatum, "saison": g["saison"].iloc[0], "n_stunden": len(preis),
            "preis_status_quo": sq, "preis_billigst": best, "start_billigst": int(stunden[i_min]),
            "mehrkosten_eur_mwh": sq - best,
            "mehrkosten_pct": (sq - best) / best * 100 if best > 0 else float("nan"),
        })
    return pd.DataFrame(zeilen)


def kennzahlen_je_saison(tage: pd.DataFrame, status_quo_start: int) -> pd.DataFrame:
    """Median and IQR of the extra cost per season, plus start-hour mode and share 'exactly status quo'."""
    zeilen = []
    for saison in SAISON_REIHENFOLGE:
        t = tage[tage["saison"] == saison]
        eur, pct = t["mehrkosten_eur_mwh"], t["mehrkosten_pct"].dropna()
        zeilen.append({
            "saison": saison, "tage": len(t),
            "median_eur_mwh": eur.median(), "q25_eur_mwh": eur.quantile(0.25), "q75_eur_mwh": eur.quantile(0.75),
            "median_pct": pct.median(), "q25_pct": pct.quantile(0.25), "q75_pct": pct.quantile(0.75),
            "tage_ohne_pct": int(t["mehrkosten_pct"].isna().sum()),
            "haeufigster_start": int(t["start_billigst"].mode().iloc[0]),
            "anteil_genau_status_quo_pct": 100 * (t["start_billigst"] == status_quo_start).mean(),
        })
    return pd.DataFrame(zeilen)


def kennzahlen_je_jahr(tage: pd.DataFrame, mwh_pro_tag: float) -> pd.DataFrame:
    """Per calendar year: extra cost in EUR/MWh and the EUR amount at mwh_pro_tag per window.

    eur_summe: sum over the windows of that year (a partial year gives a partial sum).
    eur_pro_jahr: mean per window x 365, so partial years (2026 ends on 31.10.) stay comparable.
    Upper bound in hindsight: no staff cost, no surcharges, and every shifted MWh valued at the spot
    price (contract assumption A3 "band"; with "proportional" multiply by vertrag.spot_anteil).
    """
    t = tage.assign(jahr=pd.to_datetime(tage["datum_lokal"]).dt.year)
    zeilen = []
    for jahr, g in t.groupby("jahr"):
        tage_im_jahr = 366 if pd.Timestamp(year=int(jahr), month=12, day=31).dayofyear == 366 else 365
        zeilen.append({
            "jahr": int(jahr), "fenster": len(g), "vollstaendig": len(g) == tage_im_jahr,
            "mittel_eur_mwh": g["mehrkosten_eur_mwh"].mean(), "median_eur_mwh": g["mehrkosten_eur_mwh"].median(),
            "eur_summe": g["mehrkosten_eur_mwh"].sum() * mwh_pro_tag,
            "eur_pro_jahr": g["mehrkosten_eur_mwh"].mean() * mwh_pro_tag * 365,
        })
    return pd.DataFrame(zeilen)


def main() -> None:
    """Write the look-back tables for the cleaning window (reproduces the first estimate of 10.11.2026)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from gemeinsam import ROOT, lade_params, pfad
    p = lade_params()
    last = p["last"]
    d = pd.read_csv(pfad(p, "processed") / "preise_clean.csv")
    tage = fenster_je_tag(d, last["fenster_start_h"], last["fenster_ende_h"], last["blocklaenge_h"], last["status_quo_start_h"])
    ziel = ROOT / p["cleaning"]["reports"] / "tables"             # next to the other R2 report tables
    ziel.mkdir(parents=True, exist_ok=True)
    js = kennzahlen_je_saison(tage, last["status_quo_start_h"])
    jj = kennzahlen_je_jahr(tage, last["mwh_pro_tag"])
    js.round(2).to_csv(ziel / "reinigungsfenster_saison.csv", index=False)
    jj.round(2).to_csv(ziel / "reinigungsfenster_jahr.csv", index=False)
    print(f"Fensteranalyse: {len(tage)} Nächte ({last['prozess']}, {last['blocklaenge_h']} h ab {last['status_quo_start_h']:02d} Uhr "
          f"vs. billigstes Fenster {last['fenster_start_h']:02d}-{last['fenster_ende_h']:02d} Uhr) -> {ziel}")
    print(jj.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
