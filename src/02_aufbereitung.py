# KI: Claude, Zweck: Aufbereitung SMARD-Preise (Zeitzone, Zeitumstellung, 15->60 min, Werktage, Datenqualität), geprüft von <Name R2> durch Review, Nachrechnen einzelner Tage und pytest
"""Step 2: SMARD raw data -> cleaned price series and data quality table.

Owner: R2. Input: data/raw/smard/ (from step 1). Output (columns see docs/schnittstellen.md):
  data/interim/preise_utc.parquet        hourly series in UTC, before conversion to German time
  data/processed/preise_h.parquet        zeit, preis_eur_mwh, regime, werktag   (hand-over to R3)
  data/processed/preise_15min.parquet    same columns, 15-min values from the regime switch (sensitivity)
  data/processed/zeitumstellung.csv      days with a clock change and how they were treated
  results/tables/datenqualitaet.csv      gaps, duplicates, negative prices, aggregation check

Rules (reasons in the project diary):
  * Time: SMARD delivers UTC. Output in Europe/Berlin, `zeit` = start of the hour / quarter hour.
  * Clock change in October: the hour 02:00-03:00 happens twice; both prices are averaged.
  * Clock change in March: 02:00 does not exist; that day has 23 rows. Nothing is filled in;
    the days are listed in zeitumstellung.csv and in the quality table.
  * Real gaps (SMARD delivers null) stay as a row with an empty price and are counted.
  * From the regime switch: hourly price = mean of the four quarter hours, only if all four exist.
  * Negative prices are real market results and stay in.

Two pandas basics used throughout:
  * Series = one column of values with an index (here: the timestamp). DataFrame = table of columns.
  * NaN = "no value". Most pandas functions skip NaN silently (e.g. mean of [1, NaN] = 1).
    That is exactly the "silent filling" we want to avoid, so the code checks for NaN explicitly.
"""
import csv
import json
import sys
from pathlib import Path

import holidays
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import lade_params, pfad  # noqa: E402

# Column names and order of the hand-over file. Must match docs/schnittstellen.md exactly,
# otherwise R3's code breaks. A test checks this.
SPALTEN = ["zeit", "preis_eur_mwh", "regime", "werktag"]


class AufbereitungsFehler(RuntimeError):
    """Own error type, printed as a readable message at the bottom of the file."""


# ---------------------------------------------------------------------------------------------
# Reading the raw files
# ---------------------------------------------------------------------------------------------
def lies_roh(raw: Path, aufl: str) -> tuple[pd.Series, pd.DatetimeIndex]:
    """Combine all active SMARD week files of one resolution into one long series (index = UTC time).

    Also returns timestamps that occurred twice (same moment delivered in two files).
    Same price twice: keep one copy. Different prices: stop, because we cannot know which is right.
    """
    # Use only files the manifest lists as "aktiv" (outdated versions are ignored).
    manifest = raw / "smard" / "manifest.csv"
    if not manifest.exists():
        raise AufbereitungsFehler(f"{manifest} fehlt. Zuerst Schritt 1 ausführen: python src/01_download.py")
    with open(manifest, newline="", encoding="utf-8") as f:
        dateien = [raw / z["datei"] for z in csv.DictReader(f) if z["aufloesung"] == aufl and z["status"] == "aktiv"]
    if not dateien:
        raise AufbereitungsFehler(f"Keine Rohdateien für Auflösung '{aufl}' im Manifest.")

    # Each file contains "series": [[ms, price], ...] -> small table per week, then stack all weeks.
    teile = []
    for d in dateien:
        if not d.exists():
            raise AufbereitungsFehler(f"Rohdatei fehlt: {d}. Schritt 1 erneut ausführen.")
        serie = json.loads(d.read_bytes())["series"]
        teile.append(pd.DataFrame(serie, columns=["ms", "preis"]))
    df = pd.concat(teile, ignore_index=True)
    df["zeit_utc"] = pd.to_datetime(df["ms"], unit="ms", utc=True)   # Unix ms -> real timestamp

    # Duplicate check. duplicated(keep="first") marks every repeat after the first occurrence.
    dup = df["zeit_utc"].duplicated(keep="first")
    doppelte = pd.DatetimeIndex(df.loc[dup, "zeit_utc"])
    if len(doppelte):
        # nunique = number of different prices per duplicated timestamp; >1 means contradiction
        widerspruch = df[df["zeit_utc"].duplicated(keep=False)].groupby("zeit_utc")["preis"].nunique(dropna=False)
        if (widerspruch > 1).any():
            raise AufbereitungsFehler(f"Doppelte Zeitstempel mit unterschiedlichen Preisen in '{aufl}':\n"
                                      f"{widerspruch[widerspruch > 1].head()}")
        df = df[~dup]   # "~" means "not": keep all rows that are not repeats
    # astype(float) turns JSON null (None) into NaN, so gaps stay visible as "no value"
    s = df.set_index("zeit_utc")["preis"].astype(float).sort_index()
    return s, doppelte


# ---------------------------------------------------------------------------------------------
# Core logic (also tested directly with small hand-made examples in tests/)
# ---------------------------------------------------------------------------------------------
def viertel_zu_stunde(s15: pd.Series) -> tuple[pd.Series, int]:
    """Hourly mean from quarter hours (index UTC). If one of the four quarters is missing, the hour stays empty.

    Why the mean: with constant power within the hour, cost = mean price x energy, exactly.
    Why in UTC: in UTC every hour has exactly four quarters, even on clock-change days.
    floor("h") cuts each time down to the full hour (10:45 -> 10:00), so the four quarters of an hour
    share the same key and groupby can average them.
    count() counts only real values (not NaN); if it is below 4, where() replaces the mean by NaN.
    Returns the hourly series and the number of incomplete hours.
    """
    stunde = s15.index.floor("h")
    gruppe = s15.groupby(stunde)
    mittel = gruppe.mean()
    vollstaendig = gruppe.count() == 4
    return mittel.where(vollstaendig), int((~vollstaendig).sum())


def zu_ortszeit(s_utc: pd.Series, tz: str) -> tuple[pd.Series, int]:
    """UTC series -> one value per clock time in German time (Europe/Berlin).

    Idea: convert UTC to German time and then drop the time zone, keeping only what the clock on the
    wall shows ("wanduhr"). On the October day the wall clock shows 02:00 twice, so grouping by wall
    time puts both values into one group and averages them. In March 02:00 never appears on the wall
    clock, so there is simply no row for it.

    The NaN check: groupby().mean() would ignore a missing value and return the other one as "mean".
    hat_luecke marks every group with at least one NaN, and those means are set back to NaN.

    At the end the time zone is attached again. For the doubled 02:00 we have to tell pandas which of
    the two it is: ambiguous=True for all = "summer time version" (02:00+02:00, the first one).
    nonexistent="raise" would stop if a non-existent time (March 02:00) showed up: a built-in safety check.
    Returns the series with Berlin index and the number of averaged (doubled) clock times.
    """
    wanduhr = s_utc.index.tz_convert(tz).tz_localize(None)
    gruppe = s_utc.groupby(wanduhr)
    mittel = gruppe.mean()
    hat_luecke = s_utc.isna().groupby(wanduhr).any()
    mittel[hat_luecke] = np.nan
    n_doppelt = int((gruppe.size() > 1).sum())
    zeit = mittel.index.tz_localize(tz, ambiguous=np.ones(len(mittel), dtype=bool), nonexistent="raise")
    return pd.Series(mittel.to_numpy(), index=zeit), n_doppelt


def erwartetes_raster(beginn: pd.Timestamp, ende: pd.Timestamp, freq: str, tz: str) -> pd.DatetimeIndex:
    """Every clock time (German time) that SHOULD exist in [start, end), built with the same rule as
    zu_ortszeit. Comparing data against this grid later reveals real gaps.

    Built in UTC (where hours are evenly spaced), converted to wall time, duplicates (October 02:00)
    removed with unique(), time zone attached again.
    """
    utc = pd.date_range(beginn.tz_convert("UTC"), ende.tz_convert("UTC"), freq=freq, inclusive="left")
    wanduhr = utc.tz_convert(tz).tz_localize(None).unique()
    return wanduhr.tz_localize(tz, ambiguous=np.ones(len(wanduhr), dtype=bool), nonexistent="raise")


def werktage(daten: pd.DatetimeIndex, mariae_himmelfahrt: bool) -> np.ndarray:
    """True = Monday to Friday and no public holiday in Bavaria.

    Holidays come from the package `holidays` (subdiv="BY" = Bavaria), not from a hand-written list.
    Mariä Himmelfahrt (15.08.) is a holiday only in mainly catholic municipalities; the package files
    it under the category "catholic", so we add that category only if the switch in params.yaml is on.
    The result is a True/False array with one entry per timestamp.
    """
    kategorien = ("public", "catholic") if mariae_himmelfahrt else ("public",)
    jahre = range(daten.min().year, daten.max().year + 1)
    feiertage = holidays.Germany(subdiv="BY", years=jahre, categories=kategorien)
    tage = daten.tz_localize(None).normalize()
    ist_feiertag = np.array([t.date() in feiertage for t in tage])
    return (tage.weekday < 5) & ~ist_feiertag      # weekday < 5 = Mon..Fri; "&" = and; "~" = not


def baue_tabelle(s_ort: pd.Series, raster: pd.DatetimeIndex, wechsel: pd.Timestamp, mariae: bool) -> pd.DataFrame:
    """Build the final table with exactly the columns from the interface.

    reindex(raster) lays the data onto the expected grid: wherever a clock time has no price,
    a row with NaN appears. That is how a real gap becomes visible instead of silently missing.
    regime: "stunde" before the switch date, "viertel" from it (np.where = if/else for a whole column).
    """
    s = s_ort.reindex(raster)
    df = pd.DataFrame({"zeit": raster, "preis_eur_mwh": s.to_numpy()})
    df["regime"] = np.where(df["zeit"] >= wechsel, "viertel", "stunde")
    df["werktag"] = werktage(pd.DatetimeIndex(df["zeit"]), mariae)
    return df[SPALTEN]


# ---------------------------------------------------------------------------------------------
# Data quality
# ---------------------------------------------------------------------------------------------
def zeitumstellungstage(s_utc: pd.Series, df: pd.DataFrame, pro_tag: int, aufl: str, tz: str) -> pd.DataFrame:
    """List of days on which SMARD delivers more or fewer than pro_tag points (24 hours or 96 quarter
    hours), i.e. the clock-change days, with the number of rows before and after cleaning."""
    roh = pd.Series(s_utc.index.tz_convert(tz).date).value_counts()   # points per German calendar day
    roh = roh[roh != pro_tag].sort_index()
    nachher = df.groupby(df["zeit"].dt.date).size()
    return pd.DataFrame({
        "aufloesung": aufl,
        "datum": [str(d) for d in roh.index],
        "zeitpunkte_roh": roh.to_numpy(),
        "zeitpunkte_aufbereitet": [int(nachher.get(d, 0)) for d in roh.index],
        "art": np.where(roh.to_numpy() < pro_tag, "Maerz: 02-03 Uhr existiert nicht, nicht aufgefuellt",
                        "Oktober: doppelte 02-03 Uhr gemittelt"),
    })


def qualitaet(df: pd.DataFrame, aufl: str, doppelte_roh: pd.DatetimeIndex, zu: pd.DataFrame, tz: str,
              extra: dict | None = None) -> pd.DataFrame:
    """One row per year and regime: completeness, duplicates, clock changes, negative prices, min/mean/max.

    `extra` holds additional columns per regime (here: the aggregation check, only for "viertel").
    """
    zeilen = []
    df = df.assign(jahr=df["zeit"].dt.year)
    dup_jahr = pd.Series(doppelte_roh.tz_convert(tz).year).value_counts() if len(doppelte_roh) else pd.Series(dtype=int)
    zu_jahr = zu.assign(jahr=pd.to_datetime(zu["datum"]).dt.year)
    for (jahr, regime), g in df.groupby(["jahr", "regime"]):
        p = g["preis_eur_mwh"]
        tage = set(g["zeit"].dt.date.astype(str))
        zj = zu_jahr[zu_jahr["datum"].isin(tage)]      # clock-change days that fall into this group
        z = {
            "aufloesung": aufl, "jahr": jahr, "regime": regime,
            "zeitpunkte": len(g),
            "mit_preis": int(p.notna().sum()),
            "luecken": int(p.isna().sum()),
            "doppelte_zeitstempel_roh": int(dup_jahr.get(jahr, 0)),
            "zeitumstellung_maerz_tage": int(zj["art"].str.startswith("Maerz").sum()),
            "zeitumstellung_oktober_tage": int(zj["art"].str.startswith("Oktober").sum()),
            "negative_preise": int((p < 0).sum()),
            "anteil_negativ_pct": round(100 * float((p < 0).mean()), 2),   # mean of True/False = share
            "preis_null": int((p == 0).sum()),
            "preis_min": p.min(), "preis_mittel": round(p.mean(), 2), "preis_max": p.max(),
        }
        z.update((extra or {}).get(regime, {}))
        zeilen.append(z)
    return pd.DataFrame(zeilen)


# ---------------------------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------------------------
def main() -> None:
    # --- Settings and folders ----------------------------------------------------------------
    p = lade_params()
    tz = p["markt"]["zeitzone"]
    mariae = bool(p["last"]["feiertagsvariante_mariae_himmelfahrt"])
    raw, interim, processed, tables = (pfad(p, k) for k in ("raw", "interim", "processed", "tables"))
    for o in (interim, processed, tables):
        o.mkdir(parents=True, exist_ok=True)

    # Period [start, end) in German time and the date of the regime switch (01.10.2025)
    beginn = pd.Timestamp(p["daten"]["aufloesungen"]["hour"]).tz_localize(tz)
    ende = (pd.Timestamp(p["zeitraeume"]["datenstand"]) + pd.Timedelta(days=1)).tz_localize(tz)
    wechsel = pd.Timestamp(p["markt"]["regimewechsel"]).tz_localize(tz)
    if pd.Timestamp(p["daten"]["aufloesungen"]["quarterhour"]).tz_localize(tz) > wechsel:
        raise AufbereitungsFehler("Viertelstunden müssen spätestens ab markt.regimewechsel geladen sein.")

    # --- 1) Read raw data ----------------------------------------------------------------------
    s_h_roh, dup_h = lies_roh(raw, "hour")
    s_q_roh, dup_q = lies_roh(raw, "quarterhour")

    # --- 2) Build one hourly series in UTC ---------------------------------------------------------
    # Before the switch: SMARD's hourly prices (the auction really traded hours).
    # From the switch: our own hourly mean of the quarter hours (the auction traded quarter hours).
    s_h_alt = s_h_roh[(s_h_roh.index >= beginn) & (s_h_roh.index < wechsel)]
    s_q = s_q_roh[(s_q_roh.index >= wechsel) & (s_q_roh.index < ende)]
    s_h_neu, n_unvollst = viertel_zu_stunde(s_q)

    # Aggregation check: our hourly mean vs. the hourly values SMARD itself publishes after 10/2025.
    # Same source, so this is NOT an independent check, only a check for calculation/transfer errors.
    # concat(..., join="inner") puts both series side by side, only for hours present in both.
    vergleich = pd.concat([s_h_neu.rename("eigen"), s_h_roh.rename("smard")], axis=1, join="inner").dropna()
    abw = (vergleich["eigen"] - vergleich["smard"]).abs()
    pruefung = {"viertel": {"unvollstaendige_stunden_aus_15min": n_unvollst,
                            "abw_smard_stunde_max_eur": round(abw.max(), 4) if len(abw) else np.nan,
                            "abw_smard_stunde_mittel_eur": round(abw.mean(), 4) if len(abw) else np.nan,
                            "abw_smard_stunde_n": len(abw)}}

    # Stick both parts together and save this intermediate state (data/interim), with a column
    # telling where each value came from.
    s_utc = pd.concat([s_h_alt, s_h_neu]).sort_index()
    pd.DataFrame({"zeit_utc": s_utc.index, "preis_eur_mwh": s_utc.to_numpy(),
                  "quelle": np.where(s_utc.index < wechsel, "smard_hour", "mittel_aus_quarterhour")}
                 ).to_parquet(interim / "preise_utc.parquet", index=False)

    # --- 3) German time, clock changes, expected grid, working days ----------------------------
    # Same procedure for hours (whole period) and quarter hours (from the switch only).
    s_ort, _ = zu_ortszeit(s_utc, tz)
    preise_h = baue_tabelle(s_ort, erwartetes_raster(beginn, ende, "h", tz), wechsel, mariae)

    s_q_ort, _ = zu_ortszeit(s_q, tz)
    preise_15 = baue_tabelle(s_q_ort, erwartetes_raster(wechsel, ende, "15min", tz), wechsel, mariae)

    # --- 4) Save results -------------------------------------------------------------------------
    # Parquet keeps data types (time zone, True/False) intact; CSV would turn everything into text.
    preise_h.to_parquet(processed / "preise_h.parquet", index=False)
    preise_15.to_parquet(processed / "preise_15min.parquet", index=False)

    zu_h = zeitumstellungstage(s_utc, preise_h, 24, "hour", tz)
    zu_q = zeitumstellungstage(s_q, preise_15, 96, "quarterhour", tz)
    pd.concat([zu_h, zu_q]).to_csv(processed / "zeitumstellung.csv", index=False)

    # Quality table: hourly rows (incl. the aggregation check) + quarter-hour rows
    dq = pd.concat([
        qualitaet(preise_h, "hour", dup_h.append(dup_q[dup_q >= wechsel]), zu_h, tz, pruefung),
        qualitaet(preise_15, "quarterhour", dup_q[dup_q >= wechsel], zu_q, tz),
    ], ignore_index=True)
    dq.to_csv(tables / "datenqualitaet.csv", index=False)

    print(f"Aufbereitung: {len(preise_h)} Stunden ({preise_h['preis_eur_mwh'].isna().sum()} Lücken), "
          f"{len(preise_15)} Viertelstunden; Datenqualität -> {tables / 'datenqualitaet.csv'}")


if __name__ == "__main__":
    try:
        main()
    except AufbereitungsFehler as e:
        sys.exit(f"FEHLER in 02_aufbereitung: {e}")
