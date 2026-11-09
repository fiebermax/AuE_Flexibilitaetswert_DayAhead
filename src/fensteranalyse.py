# KI: Claude, Zweck: Rückblick-Kennzahl Mehrkosten Status quo 08-14 vs. billigstes 6-h-Fenster (Ortszeit), geprüft von <Name R2> durch Review, Nachrechnen eines Tages und pytest
"""Descriptive look-back figure for R2's slide c (diary E-030). NOT a strategy.

For every local day (Europe/Berlin): compare the status quo window A (08-14 Uhr, Kickoff definition)
with the cheapest 6-hour window that lies completely inside the operating hours (06-22 Uhr).
Uses the real prices of that day, i.e. hindsight ("Rückblick mit bekannten Preisen, keine Strategie").

Per day:
  preis_status_quo   mean price 08-14 Uhr                          EUR/MWh
  preis_billigst     mean price of the cheapest 6-h window          EUR/MWh
  start_billigst     local start hour of that window (06 ... 16)
  mehrkosten_eur_mwh preis_status_quo - preis_billigst (>= 0)      EUR/MWh
  mehrkosten_pct     mehrkosten / preis_billigst * 100, only if preis_billigst > 0 (otherwise empty:
                     a percentage of a price at or below zero has no meaning)

Why the mean price: with constant power over the block, cost per MWh = mean of the hourly prices.
All hours are LOCAL hours (stunde_lokal), never UTC: shifts follow the clock in the plant.
"""
import pandas as pd

SAISON_REIHENFOLGE = ["Winter", "Fruehling", "Sommer", "Herbst"]


def fenster_je_tag(df: pd.DataFrame, betrieb_start: int, betrieb_ende: int, block_h: int, status_quo_start: int) -> pd.DataFrame:
    """One row per local day. df needs: datum_lokal, stunde_lokal, saison, preis_eur_mwh.

    The two October hours "02:00" lie outside the operating hours, so each operating hour exists once.
    A day without a complete set of operating hours (gap) is skipped and counted by the caller.
    """
    starts = range(betrieb_start, betrieb_ende - block_h + 1)       # 06 ... 16 for 06-22 and 6 h
    zeilen = []
    for datum, g in df.groupby("datum_lokal"):
        stunden = g[(g["stunde_lokal"] >= betrieb_start) & (g["stunde_lokal"] < betrieb_ende)]
        preis = stunden.set_index("stunde_lokal")["preis_eur_mwh"].reindex(range(betrieb_start, betrieb_ende))
        if preis.isna().any() or stunden["stunde_lokal"].duplicated().any():
            continue
        mittel = {s: preis.loc[s:s + block_h - 1].mean() for s in starts}
        start_min = min(mittel, key=mittel.get)                       # earliest start if prices tie
        sq, best = mittel[status_quo_start], mittel[start_min]
        zeilen.append({
            "datum_lokal": datum, "saison": g["saison"].iloc[0],
            "preis_status_quo": sq, "preis_billigst": best, "start_billigst": start_min,
            "mehrkosten_eur_mwh": sq - best,
            "mehrkosten_pct": (sq - best) / best * 100 if best > 0 else float("nan"),
        })
    return pd.DataFrame(zeilen)


def kennzahlen_je_saison(tage: pd.DataFrame, status_quo_start: int) -> pd.DataFrame:
    """Median and IQR of the extra cost per season, plus start-hour mode and share 'exactly 08-14'."""
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
