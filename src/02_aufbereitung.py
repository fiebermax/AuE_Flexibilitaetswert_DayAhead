# KI: Claude, Zweck: Aufbereitung der SMARD-Stundenpreise (Zeitzone, Zeitumstellung, Werktage, Datenqualität), geprüft von <Name R2> durch Review, Nachrechnen einzelner Tage und pytest
"""Step 2: SMARD raw week files -> one clean hourly price table as CSV.

Owner: R2. Input: data/raw/smard/ (from step 1). Output (columns see docs/schnittstellen.md):
  data/processed/preise_h.csv          zeit, datum, stunde, preis_eur_mwh, regime, werktag   (hand-over to R3)
  data/processed/zeitumstellung.csv    days with a clock change and how they were treated
  results/tables/datenqualitaet.csv    gaps, duplicates, negative prices per year

Open the result with:  pd.read_csv("data/processed/preise_h.csv")   (or in Excel)

Rules (reasons in the project diary):
  * Only hourly prices (diary E-021). From 01.10.2025 the exchange trades quarter hours; SMARD
    publishes the hourly mean of them, and that is what we use.
  * Time: SMARD delivers UTC. We convert to German time; `zeit` = start of the hour.
  * October clock change: 02:00-03:00 happens twice; both prices are averaged (one row per clock time).
  * March clock change: 02:00 does not exist; that day has 23 rows. Nothing is filled in.
    Clock changes are always on a Sunday, when the plant has no load, so they do not affect costs (E-018).
  * Real gaps (SMARD delivers null) stay as a row with an empty price and are counted.
  * Negative prices are real market results and stay in.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import lade_params, pfad, werktage  # noqa: E402

# Column order of the hand-over file (must match docs/schnittstellen.md; a test checks it)
SPALTEN = ["zeit", "datum", "stunde", "preis_eur_mwh", "regime", "werktag"]


class AufbereitungsFehler(RuntimeError):
    """Own error type, printed as a readable message at the bottom of the file."""


# ---------------------------------------------------------------------------------------------
# 1) Read all weekly raw files into one long series (index = UTC time)
# ---------------------------------------------------------------------------------------------
def lies_roh(raw: Path) -> tuple[pd.Series, int]:
    """Stack all active hourly SMARD files. Each file holds "series": [[ms, price], ...].

    Returns the series and the number of timestamps that were delivered twice. Same price twice:
    keep one copy. Different prices: stop, because we cannot know which one is right.
    """
    manifest = raw / "smard" / "manifest.csv"
    if not manifest.exists():
        raise AufbereitungsFehler(f"{manifest} fehlt. Zuerst Schritt 1 ausführen: python src/01_download.py")
    with open(manifest, newline="", encoding="utf-8") as f:
        dateien = [raw / z["datei"] for z in csv.DictReader(f) if z["aufloesung"] == "hour" and z["status"] == "aktiv"]
    if not dateien:
        raise AufbereitungsFehler("Keine Rohdateien im Manifest.")

    teile = []
    for d in dateien:
        if not d.exists():
            raise AufbereitungsFehler(f"Rohdatei fehlt: {d}. Schritt 1 erneut ausführen.")
        teile.append(pd.DataFrame(json.loads(d.read_bytes())["series"], columns=["ms", "preis"]))
    df = pd.concat(teile, ignore_index=True)
    df["zeit_utc"] = pd.to_datetime(df["ms"], unit="ms", utc=True)     # Unix milliseconds -> timestamp

    dup = df["zeit_utc"].duplicated(keep="first")
    if dup.any():
        widerspruch = df[df["zeit_utc"].duplicated(keep=False)].groupby("zeit_utc")["preis"].nunique(dropna=False)
        if (widerspruch > 1).any():
            raise AufbereitungsFehler(f"Doppelte Zeitstempel mit unterschiedlichen Preisen:\n{widerspruch[widerspruch > 1].head()}")
        df = df[~dup]
    # astype(float) turns JSON null into NaN ("no value"), so gaps stay visible
    return df.set_index("zeit_utc")["preis"].astype(float).sort_index(), int(dup.sum())


# ---------------------------------------------------------------------------------------------
# 2) UTC -> German clock time, with the clock changes handled explicitly
# ---------------------------------------------------------------------------------------------
def zu_ortszeit(s_utc: pd.Series, tz: str) -> tuple[pd.Series, int]:
    """One value per clock time in German time (Europe/Berlin).

    Idea: convert to German time and drop the time zone, keeping only what the wall clock shows.
    On the October day the wall clock shows 02:00 twice, so grouping by wall time averages the two
    prices. In March 02:00 never appears, so there is simply no row for it.
    groupby().mean() would silently ignore a missing value; hat_luecke sets such hours back to NaN.
    ambiguous=True files the doubled 02:00 under the first (summer time) version.
    """
    wanduhr = s_utc.index.tz_convert(tz).tz_localize(None)
    gruppe = s_utc.groupby(wanduhr)
    mittel = gruppe.mean()
    mittel[s_utc.isna().groupby(wanduhr).any()] = np.nan
    n_doppelt = int((gruppe.size() > 1).sum())
    zeit = mittel.index.tz_localize(tz, ambiguous=np.ones(len(mittel), dtype=bool), nonexistent="raise")
    return pd.Series(mittel.to_numpy(), index=zeit), n_doppelt


def erwartetes_raster(beginn: pd.Timestamp, ende: pd.Timestamp, tz: str) -> pd.DatetimeIndex:
    """Every clock hour that SHOULD exist in [start, end), built with the same rule as zu_ortszeit.
    Laying the data onto this grid later turns real gaps into visible empty rows."""
    utc = pd.date_range(beginn.tz_convert("UTC"), ende.tz_convert("UTC"), freq="h", inclusive="left")
    wanduhr = utc.tz_convert(tz).tz_localize(None).unique()
    return wanduhr.tz_localize(tz, ambiguous=np.ones(len(wanduhr), dtype=bool), nonexistent="raise")


# ---------------------------------------------------------------------------------------------
# 3) Final table
# ---------------------------------------------------------------------------------------------
def baue_tabelle(s_ort: pd.Series, raster: pd.DatetimeIndex, wechsel: pd.Timestamp, mariae: bool) -> pd.DataFrame:
    """Final table with the hand-over columns.

    datum and stunde are extra helper columns so that a simple groupby("stunde") works in pandas
    or Excel without any date handling. regime marks hour trading (before 01.10.2025) vs.
    quarter-hour trading (from then on); needed for the comparison test 1 vs. test 2 (H0c).
    """
    df = pd.DataFrame({"zeit": raster, "preis_eur_mwh": s_ort.reindex(raster).to_numpy()})
    df["datum"] = df["zeit"].dt.strftime("%Y-%m-%d")
    df["stunde"] = df["zeit"].dt.hour
    df["regime"] = np.where(df["zeit"] >= wechsel, "viertel", "stunde")
    df["werktag"] = werktage(pd.DatetimeIndex(df["zeit"]), mariae)
    return df[SPALTEN]


# ---------------------------------------------------------------------------------------------
# 4) Data quality
# ---------------------------------------------------------------------------------------------
def zeitumstellungstage(s_utc: pd.Series, df: pd.DataFrame, tz: str) -> pd.DataFrame:
    """Days on which SMARD delivers 23 or 25 hours instead of 24, and how many rows remain."""
    roh = pd.Series(s_utc.index.tz_convert(tz).date).value_counts()
    roh = roh[roh != 24].sort_index()
    nachher = df.groupby("datum").size()
    return pd.DataFrame({
        "datum": [str(d) for d in roh.index],
        "stunden_roh": roh.to_numpy(),
        "stunden_aufbereitet": [int(nachher.get(str(d), 0)) for d in roh.index],
        "art": np.where(roh.to_numpy() < 24, "Maerz: 02-03 Uhr existiert nicht, nicht aufgefuellt",
                        "Oktober: doppelte 02-03 Uhr gemittelt"),
    })


def qualitaet(df: pd.DataFrame, n_doppelt_roh: int) -> pd.DataFrame:
    """One row per year: number of hours, gaps, negative prices, min/mean/max."""
    zeilen = []
    for jahr, g in df.groupby(df["zeit"].dt.year):
        p = g["preis_eur_mwh"]
        stunden_je_tag = g.groupby("datum").size()
        zeilen.append({
            "jahr": jahr,
            "stunden": len(g),
            "mit_preis": int(p.notna().sum()),
            "luecken": int(p.isna().sum()),
            "zeitumstellung_23h_tage": int((stunden_je_tag == 23).sum()),
            "negative_preise": int((p < 0).sum()),
            "anteil_negativ_pct": round(100 * float((p < 0).mean()), 2),
            "preis_min": p.min(), "preis_mittel": round(p.mean(), 2), "preis_max": p.max(),
        })
    out = pd.DataFrame(zeilen)
    out["doppelte_zeitstempel_roh"] = n_doppelt_roh if len(out) else 0
    return out


# ---------------------------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------------------------
def main() -> None:
    p = lade_params()
    tz = p["markt"]["zeitzone"]
    raw, processed, tables = (pfad(p, k) for k in ("raw", "processed", "tables"))
    processed.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)

    beginn = pd.Timestamp(p["daten"]["aufloesungen"]["hour"]).tz_localize(tz)
    ende = (pd.Timestamp(p["zeitraeume"]["datenstand"]) + pd.Timedelta(days=1)).tz_localize(tz)
    wechsel = pd.Timestamp(p["markt"]["regimewechsel"]).tz_localize(tz)

    s_roh, n_doppelt = lies_roh(raw)
    s_utc = s_roh[(s_roh.index >= beginn) & (s_roh.index < ende)]
    s_ort, _ = zu_ortszeit(s_utc, tz)
    preise = baue_tabelle(s_ort, erwartetes_raster(beginn, ende, tz), wechsel,
                          bool(p["last"]["feiertagsvariante_mariae_himmelfahrt"]))

    # CSV with the time as text incl. UTC offset (e.g. 2025-10-26 02:00:00+02:00), readable everywhere
    preise.to_csv(processed / "preise_h.csv", index=False)
    zeitumstellungstage(s_utc, preise, tz).to_csv(processed / "zeitumstellung.csv", index=False)
    qualitaet(preise, n_doppelt).to_csv(tables / "datenqualitaet.csv", index=False)

    print(f"Aufbereitung: {len(preise)} Stunden, {preise['preis_eur_mwh'].isna().sum()} Lücken "
          f"-> {processed / 'preise_h.csv'}")


if __name__ == "__main__":
    try:
        main()
    except AufbereitungsFehler as e:
        sys.exit(f"FEHLER in 02_aufbereitung: {e}")
