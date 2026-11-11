# KI: Claude, Zweck: Datenbereinigung SMARD-Preise + Join synthetische Last, mit Log und Berichten, geprüft von <Name R2> durch Review, Nachrechnen einzelner Tage und pytest
"""Step 02 (cleaning): SMARD raw week files -> one cleaned hourly table in UTC, plus log and reports.

Owner: R2. Run: python src/cleaning.py   (after src/01_download.py and src/02_synthetisch.py)
Input (read-only):  data/raw/... (JSON as delivered by SMARD), data/last_synth.csv
Output:
  data/preise_clean.csv      one row per UTC hour, columns see docs/codebook.md
  r2/ergebnisse/cleaning_log.md              step | rule | N before | N after | affected rows | reason
  r2/ergebnisse/data_quality.md              key figures and figures (generated)
  r2/ergebnisse/*.csv                 monthly / seasonal figures, daily profile, clock changes, gaps, outliers
  r2/ergebnisse/*.png                time series, boxplot per month, daily profile per season

Principles (diary E-024 to E-029):
  * data/raw/ is never written. Every change happens here, in code, is counted and justified.
  * Key is the UTC timestamp. In UTC there are no doubled or missing hours; the October "02:00 twice"
    are two different UTC hours and both are kept. Local time is an extra column for planning.
  * Only hourly values. From 01.10.2025 (15-minute day-ahead products) we use the hourly value SMARD
    publishes (mean of the four quarter hours, rounded to 0.01 EUR/MWh); see diary E-028.
  * Nothing is deleted, imputed or capped without asking. Negative prices and spikes are valid.
    Conspicuous values are only flagged (flag_outlier), and that flag is for DESCRIPTION ONLY: it compares
    with the whole month, i.e. also with later hours, so a planning rule must never use it (look-ahead).
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                    # draw to files, no screen needed
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402
import pandas as pd                      # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))     # make the other files in src/ importable
from gemeinsam import ROOT, feiertage_bayern, lade_params, pfad, werktage  # noqa: E402

SPALTEN = ["ts_utc", "ts_lokal", "datum_lokal", "stunde_lokal", "wochentag", "saison",
           "preis_eur_mwh", "regime", "werktag", "sonntag", "feiertag", "in_betriebszeit", "last_mwh_tag", "last_mwh_flexibel_tag",
           "imputed", "flag_outlier"]
SAISON = {12: "Winter", 1: "Winter", 2: "Winter", 3: "Fruehling", 4: "Fruehling", 5: "Fruehling",
          6: "Sommer", 7: "Sommer", 8: "Sommer", 9: "Herbst", 10: "Herbst", 11: "Herbst"}


class CleaningFehler(RuntimeError):
    """Stops the run with a readable message (e.g. contradicting duplicates, prices outside the limits)."""


class Log:
    """Collects one row per cleaning step for r2/ergebnisse/cleaning_log.md.

    Why: every step must be traceable for K2/K5 ("how many rows before and after, and why?").
    The log is the evidence that nothing was removed or changed silently.
    """

    def __init__(self):
        self.zeilen = []

    def schritt(self, schritt, regel, vorher, nachher, betroffen, begruendung):
        self.zeilen.append((schritt, regel, vorher, nachher, betroffen, begruendung))
        print(f"  {schritt}: {vorher} -> {nachher} (betroffen: {betroffen})")

    def markdown(self) -> str:
        kopf = "| Schritt | Regel | N vorher | N nachher | betroffene Zeilen | Begründung |\n| --- | --- | --- | --- | --- | --- |\n"
        return kopf + "".join(f"| {' | '.join(str(x) for x in z)} |\n" for z in self.zeilen)


# ---------------------------------------------------------------------------------------------
# Single steps (each one also tested on small examples in tests/test_cleaning.py)
# ---------------------------------------------------------------------------------------------
def pruefe_rohdaten(raw: Path) -> list[dict]:
    """Integrity check: every active raw file must still have the SHA-256 from the time of download."""
    with open(raw / "manifest.csv", newline="", encoding="utf-8") as f:
        zeilen = [z for z in csv.DictReader(f) if z["status"] == "aktiv" and z["aufloesung"] == "hour"]
    for z in zeilen:
        datei = raw / z["datei"]
        if not datei.exists() or hashlib.sha256(datei.read_bytes()).hexdigest() != z["sha256"]:
            raise CleaningFehler(f"Rohdatei fehlt oder wurde verändert: {datei}. Aus Git wiederherstellen.")
    return zeilen


def lies_roh(raw: Path, dateien: list[dict]) -> pd.DataFrame:
    """Stack all weekly files. Each holds "series": [[unix_ms, price], ...]; null becomes NaN."""
    # One small table per weekly file, then all stacked below each other (concat).
    teile = [pd.DataFrame(json.loads((raw / z["datei"]).read_bytes())["series"], columns=["ms", "preis_eur_mwh"])
             for z in dateien]
    df = pd.concat(teile, ignore_index=True)
    # SMARD counts time in milliseconds since 1970 (UTC). Converting to a UTC timestamp gives every hour
    # exactly one unique name, even on clock-change days (see principle "key is UTC" above).
    df["ts_utc"] = pd.to_datetime(df["ms"], unit="ms", utc=True)
    df["preis_eur_mwh"] = df["preis_eur_mwh"].astype(float)
    return df[["ts_utc", "preis_eur_mwh"]]


def dubletten(df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    """Split duplicates into exact (same time, same price: keep one) and contradicting (same time,
    different price: stop and ask, because we cannot know which value is right)."""
    # keep=False marks ALL copies of a doubled timestamp, not just the second one.
    mehrfach = df[df["ts_utc"].duplicated(keep=False)]
    # Per doubled timestamp: how many DIFFERENT prices? 1 = harmless copy, >1 = contradiction.
    widerspruch = mehrfach.groupby("ts_utc")["preis_eur_mwh"].nunique(dropna=False)
    n_widerspruch = int((widerspruch > 1).sum())
    if n_widerspruch:
        raise CleaningFehler(f"{n_widerspruch} Zeitpunkte mit widersprüchlichen Preisen, z. B.:\n"
                             f"{mehrfach[mehrfach['ts_utc'].isin(widerspruch[widerspruch > 1].index)].head()}")
    n_exakt = int(df["ts_utc"].duplicated().sum())
    return df.drop_duplicates("ts_utc").sort_values("ts_utc").reset_index(drop=True), n_exakt, n_widerspruch


def intervall_laengen(df: pd.DataFrame) -> pd.Series:
    """How often each distance between consecutive timestamps occurs (in minutes). Expected: only 60."""
    return (df["ts_utc"].diff().dropna().dt.total_seconds() / 60).value_counts().sort_index()


def raster_und_luecken(df: pd.DataFrame, beginn_utc: pd.Timestamp, ende_utc: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lay the data onto the complete expected UTC hour grid. Missing hours become rows with an empty
    price (visible, not filled). Returns the gridded table and a list of gaps (start, length in hours)."""
    # The "should" list: every UTC hour of the period. A left join keeps every hour of this list;
    # an hour without a price in SMARD's data shows up as an empty price instead of disappearing.
    raster = pd.date_range(beginn_utc, ende_utc, freq="h", inclusive="left", tz="UTC")
    out = pd.DataFrame({"ts_utc": raster}).merge(df, on="ts_utc", how="left")
    fehlt = out["preis_eur_mwh"].isna()
    # Group consecutive missing hours into one gap: the counter goes up whenever "missing" switches
    # on or off, so all hours of one gap share the same number (classic run-length trick).
    block = (fehlt != fehlt.shift()).cumsum()
    luecken = (out[fehlt].groupby(block[fehlt])["ts_utc"].agg(["min", "count"])
               .rename(columns={"min": "beginn_utc", "count": "laenge_h"}).reset_index(drop=True))
    out["imputed"] = False            # no imputation without asking (none needed so far)
    return out, luecken


def zeitspalten(df: pd.DataFrame, tz: str, wechsel: pd.Timestamp, mariae: bool) -> pd.DataFrame:
    """Local time and calendar columns. Clock changes need no special handling here: local time is
    derived from UTC, so the October Sunday simply has 25 local hours and the March Sunday 23."""
    out = df.copy()
    lokal = out["ts_utc"].dt.tz_convert(tz)
    out["ts_lokal"] = lokal
    out["datum_lokal"] = lokal.dt.strftime("%Y-%m-%d")
    out["stunde_lokal"] = lokal.dt.hour
    out["wochentag"] = lokal.dt.dayofweek            # 0 = Monday ... 6 = Sunday
    out["saison"] = lokal.dt.month.map(SAISON)
    # Market regime: hourly auction until 30.09.2025, quarter-hour auction from 01.10.2025 (needed for H0c).
    out["regime"] = np.where(out["ts_utc"] >= wechsel.tz_convert("UTC"), "viertel", "stunde")
    out["werktag"] = werktage(pd.DatetimeIndex(lokal), mariae)
    # Sunday and holiday separately: R4 applies different surcharges (diary A-016). Both refer to the
    # calendar day of the HOUR itself, so Sat 22:00 is Saturday and the following 02:00 is Sunday (A-017).
    out["sonntag"] = out["wochentag"] == 6
    out["feiertag"] = feiertage_bayern(pd.DatetimeIndex(lokal), mariae)
    return out


def zeitumstellungstage(df: pd.DataFrame) -> pd.DataFrame:
    """Local days with 23 or 25 hours (clock changes)."""
    n = df.groupby("datum_lokal").size()
    n = n[n != 24]
    return pd.DataFrame({"datum_lokal": n.index, "stunden_lokal": n.to_numpy(),
                         "art": np.where(n.to_numpy() < 24, "Maerz: 02:00 Uhr entfaellt", "Oktober: 02:00 Uhr doppelt")})


def ausserhalb_preisgrenzen(df: pd.DataFrame, minimum: float, maximum: float) -> pd.DataFrame:
    """Prices outside the exchange's technical limits (-500 / +5 000 EUR/MWh). Such a price cannot come
    out of the auction, so it would be a data error. We do not fix it ourselves: main() stops and asks."""
    p = df["preis_eur_mwh"]
    return df[p.notna() & ((p < minimum) | (p > maximum))]


def robuster_z(werte: pd.Series) -> pd.Series:
    """Modified z-score (Iglewicz & Hoaglin 1993): 0.6745 * (x - median) / MAD.
    Median and MAD are not pulled by the extreme values we look for, unlike mean and SD (Leys et al. 2013)."""
    median = werte.median()
    mad = (werte - median).abs().median()
    if not mad or np.isnan(mad):
        # MAD = 0 means more than half of the values are identical: no scale to compare with,
        # so no hour of this group is flagged (instead of dividing by zero).
        return pd.Series(np.nan, index=werte.index)
    # 0.6745 rescales the MAD so that the value is comparable with an ordinary z-score for normal data.
    return 0.6745 * (werte - median) / mad


def flagge_ausreisser(df: pd.DataFrame, schwelle: float) -> tuple[pd.DataFrame, pd.Series]:
    """flag_outlier = |modified z| > schwelle, compared within the same local year, month and hour.
    Only a flag: no value is changed or removed. Uses the whole month -> description only (look-ahead)."""
    lokal = df["ts_lokal"]
    # Compare like with like: a 13:00 price in July 2025 only with the other 13:00 prices of July 2025.
    # Otherwise every sunny noon hour would look "conspicuous" against the night hours.
    # transform() returns one z-value per row, in the original order.
    z = df.groupby([lokal.dt.year, lokal.dt.month, df["stunde_lokal"]])["preis_eur_mwh"].transform(robuster_z)
    out = df.copy()
    out["flag_outlier"] = (z.abs() > schwelle).fillna(False).astype(bool)
    return out, z


def join_last(df: pd.DataFrame, last: pd.DataFrame, start_h: int, ende_h: int) -> tuple[pd.DataFrame, int, int]:
    """Attach the daily load (synthetic, last_synth.csv) to every hour of the same local date.
    Key: local date derived from the UTC timestamp. Returns the table, unmatched price rows and unmatched
    load days. in_betriebszeit marks the production hours (06-22 Uhr local); the other 8 hours are the
    cleaning window of case S1 (diary E-033). The load value of date d belongs to the cleaning in the
    night starting at d 22:00, see src/02_synthetisch.py."""
    l = last.rename(columns={"datum": "datum_lokal", "mwh_gesamt": "last_mwh_tag",
                             "mwh_flexibel": "last_mwh_flexibel_tag"})[["datum_lokal", "last_mwh_tag", "last_mwh_flexibel_tag"]]
    # validate="many_to_one": many hours per date, but at most one load row per date. If the load file
    # ever had a date twice, pandas stops here instead of silently doubling hours.
    out = df.merge(l, on="datum_lokal", how="left", validate="many_to_one")
    ohne_last = int(out["last_mwh_tag"].isna().sum())
    ohne_preis = int((~l["datum_lokal"].isin(df["datum_lokal"])).sum())
    out["in_betriebszeit"] = (out["stunde_lokal"] >= start_h) & (out["stunde_lokal"] < ende_h)
    return out, ohne_last, ohne_preis


# ---------------------------------------------------------------------------------------------
# Description (tables and figures)
# ---------------------------------------------------------------------------------------------
def kennzahlen(df: pd.DataFrame, nach: list[str]) -> pd.DataFrame:
    """Mean and robust figures (median, IQR) plus share of negative hours, per group."""
    g = df.groupby(nach)["preis_eur_mwh"]
    out = pd.DataFrame({
        "stunden": g.size(),
        "mittel": g.mean().round(2),
        "median": g.median().round(2),
        "q25": g.quantile(0.25).round(2),
        "q75": g.quantile(0.75).round(2),
        "min": g.min(), "max": g.max(),
        "anteil_negativ_pct": g.apply(lambda s: round(100 * (s < 0).mean(), 2)),
    })
    out["iqr"] = (out["q75"] - out["q25"]).round(2)
    return out.reset_index()


def grafiken(df: pd.DataFrame, ordner: Path) -> list[str]:
    """Three figures, raw values only (no smoothing). Returns the file names."""
    ordner.mkdir(parents=True, exist_ok=True)
    namen = []

    fig, ax = plt.subplots(figsize=(11, 3.6))
    ax.plot(df["ts_lokal"], df["preis_eur_mwh"], linewidth=0.3, color="#2f6db5")
    ax.axhline(0, color="#555", linewidth=0.6)
    ax.set_title("Day-Ahead-Preis DE-LU je Stunde, 2022 bis 10/2026 (Rohwerte, ungeglättet)")
    ax.set_ylabel("EUR/MWh"); ax.set_xlabel("Zeit (deutsche Zeit)")
    fig.text(0.01, 0.01, "Quelle: Bundesnetzagentur | SMARD.de, CC BY 4.0", fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(ordner / "zeitreihe.png", dpi=150); plt.close(fig); namen.append("zeitreihe.png")

    fig, ax = plt.subplots(figsize=(11, 4))
    monate = [df.loc[df["ts_lokal"].dt.month == m, "preis_eur_mwh"].dropna() for m in range(1, 13)]
    ax.boxplot(monate, tick_labels=["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
               showfliers=True, flierprops={"markersize": 1.5, "alpha": 0.4})
    ax.axhline(0, color="#555", linewidth=0.6)
    ax.set_title("Preisverteilung je Monat, alle Jahre (Punkte = Einzelwerte außerhalb 1,5 x IQR, nicht entfernt)")
    ax.set_ylabel("EUR/MWh")
    fig.text(0.01, 0.01, "Quelle: Bundesnetzagentur | SMARD.de, CC BY 4.0", fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(ordner / "boxplot_monat.png", dpi=150); plt.close(fig); namen.append("boxplot_monat.png")

    fig, ax = plt.subplots(figsize=(9, 4.2))
    for saison, farbe in [("Winter", "#2f6db5"), ("Fruehling", "#3b8a5a"), ("Sommer", "#c47a00"), ("Herbst", "#b5483a")]:
        prof = df[df["saison"] == saison].groupby("stunde_lokal")["preis_eur_mwh"].median()
        ax.plot(prof.index, prof.to_numpy(), marker="o", markersize=3, label=saison, color=farbe)
    ax.axvspan(6, 22, color="#999", alpha=0.08, label="Produktion 06-22 Uhr (Rest: Reinigungsfenster)")
    ax.set_xticks(range(0, 24, 2)); ax.set_xlabel("Stunde (deutsche Zeit)"); ax.set_ylabel("Median EUR/MWh")
    ax.set_title("Tagesprofil je Saison: Median des Preises je Uhrzeit, 2022 bis 10/2026")
    ax.legend(frameon=False, fontsize=8)
    fig.text(0.01, 0.01, "Quelle: Bundesnetzagentur | SMARD.de, CC BY 4.0", fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(ordner / "tagesprofil_saison.png", dpi=150); plt.close(fig); namen.append("tagesprofil_saison.png")
    return namen


# ---------------------------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------------------------
def main() -> pd.DataFrame:
    p = lade_params()
    tz, c = p["markt"]["zeitzone"], p["cleaning"]
    raw, processed = pfad(p, "raw"), pfad(p, "processed")
    reports = ROOT / c["reports"]
    reports.mkdir(parents=True, exist_ok=True)               # one flat folder for all R2 results
    log = Log()

    # Period as half-open interval [beginn, ende) in German time: ende = 00:00 on the day after the
    # data cut-off, so the last day is complete and nothing needs "23:59" tricks.
    beginn = pd.Timestamp(p["daten"]["aufloesungen"]["hour"]).tz_localize(tz)
    ende = (pd.Timestamp(p["zeitraeume"]["datenstand"]) + pd.Timedelta(days=1)).tz_localize(tz)
    wechsel = pd.Timestamp(p["markt"]["regimewechsel"]).tz_localize(tz)

    # 0 Integrity of the raw data
    dateien = pruefe_rohdaten(raw)
    log.schritt("0 Rohdaten prüfen", "SHA-256 jeder Rohdatei = Wert im Manifest", len(dateien), len(dateien), 0,
                "Rohdaten unverändert, Herkunft belegt (data/raw/manifest.csv)")

    # 1 Read
    df = lies_roh(raw, dateien)
    n_roh = len(df)
    log.schritt("1 Einlesen", "alle Wochendateien untereinander, Zeitstempel UTC", n_roh, n_roh, 0,
                "Wochendateien von SMARD (Mo 00:00 bis So 24:00 deutscher Zeit)")

    # 2 Duplicates
    df, n_exakt, n_widerspruch = dubletten(df)
    log.schritt("2 Dubletten", "exakt: einer bleibt; widersprüchlich: Abbruch", n_roh, len(df), n_exakt + n_widerspruch,
                f"{n_exakt} exakte, {n_widerspruch} widersprüchliche Dubletten")

    # 3 Period
    vorher = len(df)
    df = df[(df["ts_utc"] >= beginn.tz_convert("UTC")) & (df["ts_utc"] < ende.tz_convert("UTC"))].reset_index(drop=True)
    log.schritt("3 Zeitraum", f"{beginn:%d.%m.%Y} 00:00 bis {ende - pd.Timedelta(days=1):%d.%m.%Y} 24:00 deutscher Zeit",
                vorher, len(df), vorher - len(df),
                "Randtage der ersten und letzten Wochendatei liegen außerhalb des Untersuchungszeitraums")

    # 4 Resolution
    laengen = intervall_laengen(df)
    nicht_60 = int(laengen.drop(60.0, errors="ignore").sum())
    log.schritt("4 Auflösung", "Abstand aufeinanderfolgender Zeitstempel = 60 min", len(df), len(df), nicht_60,
                "SMARD-Stundenwerte; ab 01.10.2025 Mittel der 4 Viertelstunden (SDAC 15-min-MTU, Lieferung ab 01.10.2025)")
    if nicht_60:
        raise CleaningFehler(f"Unerwartete Intervalllängen (Minuten):\n{laengen}")

    # 5 Completeness
    vorher = len(df)
    df, luecken = raster_und_luecken(df, beginn.tz_convert("UTC"), ende.tz_convert("UTC"))
    log.schritt("5 Vollständigkeit", "erwartetes UTC-Stundenraster; fehlende Stunden als leere Zeile, Flag imputed",
                vorher, len(df), int(df["preis_eur_mwh"].isna().sum()),
                f"{len(luecken)} Lücken; keine Imputation ohne Rückfrage")
    luecken.to_csv(reports / "luecken.csv", index=False)

    # 6 Time columns and clock changes
    df = zeitspalten(df, tz, wechsel, bool(p["last"]["feiertagsvariante_mariae_himmelfahrt"]))
    zu = zeitumstellungstage(df)
    zu.to_csv(reports / "zeitumstellung.csv", index=False)
    log.schritt("6 Zeitumstellung", "lokale Zeit aus UTC; 23-/25-Stunden-Tage auflisten, nichts mitteln", len(df), len(df),
                int(len(zu)), "die doppelte Oktober-Stunde sind zwei verschiedene UTC-Stunden, keine Dubletten")

    # 7 Plausibility
    grenzen = ausserhalb_preisgrenzen(df, c["preis_min_eur_mwh"], c["preis_max_eur_mwh"])
    log.schritt("7 Plausibilität", f"{c['preis_min_eur_mwh']} <= Preis <= {c['preis_max_eur_mwh']} EUR/MWh (SDAC-Preisgrenzen)",
                len(df), len(df), len(grenzen), "negative Preise und Spitzen sind gültig und bleiben")
    if len(grenzen):
        raise CleaningFehler(f"{len(grenzen)} Preise außerhalb der Börsengrenzen, Rückfrage nötig:\n{grenzen.head()}")

    # 8 Conspicuous values (flag only)
    df, z = flagge_ausreisser(df, float(c["ausreisser_schwelle"]))
    log.schritt("8 Auffällige Werte", f"Betrag modifizierter z-Wert > {c['ausreisser_schwelle']} je Jahr x Monat x Stunde",
                len(df), len(df), int(df["flag_outlier"].sum()),
                "nur markiert (flag_outlier), nichts gelöscht; nur zur Beschreibung, nicht für die Planung")
    au = df[df["flag_outlier"]].assign(z=z[df["flag_outlier"]].round(2))
    au[["ts_utc", "ts_lokal", "preis_eur_mwh", "z"]].to_csv(reports / "ausreisser.csv", index=False)

    # 9 Join synthetic load
    last = pd.read_csv(processed / "last_synth.csv")
    vorher = len(df)
    df, ohne_last, ohne_preis = join_last(df, last, p["last"]["betrieb_start_h"], p["last"]["betrieb_ende_h"])
    log.schritt("9 Join Last", "Schlüssel: lokales Datum aus UTC-Zeitstempel; last_synth.csv (synthetisch)", vorher, len(df),
                ohne_last + ohne_preis, f"{ohne_last} Preisstunden ohne Last, {ohne_preis} Lasttage ohne Preis")

    # Write the result. Timestamps become text with an explicit time zone ("Z" = UTC, "+01:00" local),
    # so Excel and pandas read the same moment and the October double hour stays distinguishable.
    df = df[SPALTEN]
    out = df.copy()
    out["ts_utc"] = out["ts_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out["ts_lokal"] = out["ts_lokal"].dt.strftime("%Y-%m-%d %H:%M:%S%z").str.replace(r"(\d{2})(\d{2})$", r"\1:\2", regex=True)
    out.to_csv(processed / "preise_clean.csv", index=False)

    # Description
    monat = kennzahlen(df.assign(jahr=df["ts_lokal"].dt.year, monat=df["ts_lokal"].dt.month), ["jahr", "monat"])
    saison = kennzahlen(df.assign(jahr=df["ts_lokal"].dt.year), ["jahr", "saison"])
    profil = kennzahlen(df, ["saison", "stunde_lokal"])
    monat.to_csv(reports / "kennzahlen_monat.csv", index=False)
    saison.to_csv(reports / "kennzahlen_saison.csv", index=False)
    profil.to_csv(reports / "tagesprofil_saison.csv", index=False)
    figuren = grafiken(df, reports)

    (reports / "cleaning_log.md").write_text(
        "# Cleaning-Log\n\nErzeugt von `src/cleaning.py`. Eingabe: `data/raw/` (unverändert), "
        "`data/last_synth.csv`. Ausgabe: `data/preise_clean.csv`.\n\n" + log.markdown(), encoding="utf-8")
    schreibe_qualitaetsbericht(reports, df, zu, luecken, figuren, jahr=kennzahlen(df.assign(jahr=df["ts_lokal"].dt.year), ["jahr"]))
    print(f"Cleaning: {len(df)} Stunden -> {processed / 'preise_clean.csv'}; Berichte in {reports}")
    return df


def schreibe_qualitaetsbericht(reports: Path, df: pd.DataFrame, zu: pd.DataFrame, luecken: pd.DataFrame,
                               figuren: list[str], jahr: pd.DataFrame) -> None:
    """Short generated report; the method and its justification are in r2/docs/datenaufbereitung.md."""
    def tabelle(t: pd.DataFrame) -> str:
        return "| " + " | ".join(t.columns) + " |\n| " + " | ".join("---" for _ in t.columns) + " |\n" + \
               "".join("| " + " | ".join(str(v) for v in r) + " |\n" for r in t.itertuples(index=False))
    text = f"""# Datenqualität (erzeugt)

Erzeugt von `src/cleaning.py`. Methode und Begründung: `r2/docs/datenaufbereitung.md`. Schritte und Zählungen: `cleaning_log.md`.

## Überblick

- Stunden (UTC): {len(df)} von {df['ts_utc'].min():%d.%m.%Y %H:%M} bis {df['ts_utc'].max():%d.%m.%Y %H:%M} UTC
- Lücken: {len(luecken)} · imputiert: {int(df['imputed'].sum())} · auffällig markiert: {int(df['flag_outlier'].sum())} ({100 * df['flag_outlier'].mean():.1f} %)
- Stunden mit negativem Preis: {int((df['preis_eur_mwh'] < 0).sum())} ({100 * (df['preis_eur_mwh'] < 0).mean():.1f} %)
- Zeitumstellungstage: {len(zu)} (je Jahr ein Tag mit 23 und einer mit 25 Stunden, immer sonntags; 02:00 bis 03:00 Uhr liegt außerhalb der Produktion, aber im Reinigungsfenster 22–06 Uhr: diese Nächte haben 7 bzw. 9 Stunden, Tagebuch E-036)

## Kennzahlen je Jahr (EUR/MWh)

{tabelle(jahr)}
Je Monat und Saison: `kennzahlen_monat.csv`, `kennzahlen_saison.csv`; Tagesprofil: `tagesprofil_saison.csv`.

## Grafiken

""" + "".join(f"![{f}]({f})\n\n" for f in figuren) + \
        "Quelle der Preise: Bundesnetzagentur | SMARD.de, CC BY 4.0. Grafiken zeigen Rohwerte, nichts geglättet.\n"
    (reports / "data_quality.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except CleaningFehler as e:
        sys.exit(f"FEHLER in cleaning: {e}")
