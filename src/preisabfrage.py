# KI: Claude, Zweck: einfache Abfrage einzelner Tage und der letzten Monate (Preis, Datum, Uhrzeit, Wochentag) für das Team, geprüft von <Name R2> durch Review und pytest
"""Simple price lookup for exploring the data (request by Susan, diary A-011). NOT for strategies.

Use in Python (from the repo folder):

    import sys; sys.path.insert(0, "src")
    from preisabfrage import tag, tage, letzte_monate

    df = tag("2026-10-15")                      # one day, one row per hour
    df = tage("2026-08-01", "2026-08-31")       # several days (both included)
    df = letzte_monate(3)                       # the last 3 months up to the data cut-off
    df = letzte_monate(3, wochentag="Samstag")  # only Saturdays

    df["preis"]                                  # every column is a plain variable
    df[df["uhrzeit"] == "14:00"]                 # all 14:00 hours
    df.groupby("wochentag")["preis"].mean()      # mean price per weekday

Or in the terminal:  python src/preisabfrage.py 2026-10-15
                     python src/preisabfrage.py 2026-08-01 2026-08-31

Columns (all in German local time, Europe/Berlin):
  datum      calendar day (pandas date, prints as 2026-10-15)
  wochentag  Montag ... Sonntag
  uhrzeit    start of the hour as text, "00:00" ... "23:00"
  stunde     the same as a number 0 ... 23
  preis      day-ahead price DE-LU in EUR/MWh (Bundesnetzagentur | SMARD.de, CC BY 4.0)
  saison, werktag   as in docs/codebook.md
  zeit       full timestamp with UTC offset; unique even in the October night where 02:00 occurs twice

Why a separate file and not datenzugriff.py: datenzugriff.py guards the backtest against look-ahead
(a strategy only sees what was known on a Friday). Exploring the past is the opposite: here you may
look at any day. Results from this file must therefore never feed a planning strategy.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import lade_params, pfad  # noqa: E402

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
SPALTEN = ["datum", "wochentag", "uhrzeit", "stunde", "preis", "saison", "werktag", "zeit"]

_CACHE: dict[str, pd.DataFrame] = {}                 # read the 42 000-row file only once per session


def alle_preise() -> pd.DataFrame:
    """All hours of preise_clean.csv with the simple column names above."""
    if "preise" not in _CACHE:
        p = lade_params()
        datei = pfad(p, "processed") / "preise_clean.csv"
        if not datei.exists():
            raise FileNotFoundError(f"{datei} fehlt. Zuerst ausführen: python src/run_all.py")
        roh = pd.read_csv(datei)
        zeit = pd.to_datetime(roh["ts_utc"], utc=True).dt.tz_convert(p["markt"]["zeitzone"])
        df = pd.DataFrame({
            "datum": pd.to_datetime(roh["datum_lokal"]),
            "wochentag": [WOCHENTAGE[w] for w in roh["wochentag"]],
            "uhrzeit": [f"{h:02d}:00" for h in roh["stunde_lokal"]],
            "stunde": roh["stunde_lokal"],
            "preis": roh["preis_eur_mwh"],
            "saison": roh["saison"],
            "werktag": roh["werktag"],
            "zeit": zeit,
        })
        _CACHE["preise"] = df[SPALTEN]
    return _CACHE["preise"]


def tage(von: str, bis: str | None = None, wochentag: str | None = None) -> pd.DataFrame:
    """All hours from day `von` to day `bis` (both included; bis=None -> only `von`).

    Dates as text "JJJJ-MM-TT". Optional filter wochentag="Samstag" (German name, as in the column).
    Stops with a readable message if a date lies outside the data or the weekday is misspelled.
    """
    df = alle_preise()
    von_t = pd.Timestamp(von)
    bis_t = pd.Timestamp(bis) if bis else von_t
    erster, letzter = df["datum"].min(), df["datum"].max()
    if von_t > bis_t:
        raise ValueError(f"'von' ({von}) liegt nach 'bis' ({bis}).")
    if von_t < erster or bis_t > letzter:
        raise ValueError(f"Daten gibt es nur vom {erster:%d.%m.%Y} bis {letzter:%d.%m.%Y}.")
    if wochentag is not None and wochentag not in WOCHENTAGE:
        raise ValueError(f"Wochentag '{wochentag}' unbekannt. Möglich: {', '.join(WOCHENTAGE)}.")
    auswahl = df[(df["datum"] >= von_t) & (df["datum"] <= bis_t)]
    if wochentag is not None:
        auswahl = auswahl[auswahl["wochentag"] == wochentag]
    return auswahl.reset_index(drop=True)


def tag(datum: str) -> pd.DataFrame:
    """One day: normally 24 rows, 23 on the March clock-change Sunday, 25 in October."""
    return tage(datum)


def letzte_monate(anzahl: int = 1, wochentag: str | None = None) -> pd.DataFrame:
    """The last `anzahl` months up to the last day in the data (31.10.2026 -> 3 months = 01.08.-31.10.)."""
    if anzahl < 1:
        raise ValueError("anzahl muss mindestens 1 sein.")
    letzter = alle_preise()["datum"].max()
    von = letzter - pd.DateOffset(months=anzahl) + pd.Timedelta(days=1)
    return tage(f"{von:%Y-%m-%d}", f"{letzter:%Y-%m-%d}", wochentag)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("Aufruf: python src/preisabfrage.py JJJJ-MM-TT [JJJJ-MM-TT]")
    try:
        ergebnis = tage(*sys.argv[1:])
    except ValueError as e:
        sys.exit(f"FEHLER: {e}")
    with pd.option_context("display.max_rows", None, "display.width", 120):
        print(ergebnis.drop(columns=["zeit"]).to_string(index=False))
