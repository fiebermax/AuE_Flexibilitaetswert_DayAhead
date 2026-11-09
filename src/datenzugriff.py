# KI: Claude, Zweck: Datenzugriff für den Backtest (rollierender Ursprung, Look-ahead-Schutz), geprüft von <Name R2> durch Review und pytest
"""Data access for the backtest: what was known on a given Friday, and which week is being planned.

Owner: R2. Used by: R3 (src/03_merkmale.py, src/04_strategien.py), later src/06_sensitivitaet.py.

The backtest replays every Friday of a period ("rolling origin"). On each Friday a strategy may only
use prices that were already published at planning time; afterwards the plan is evaluated with the
real prices of the following week. This module does the date logic once, in one place, so that no
strategy can accidentally look into the future.

Typical use (R3):

    import datenzugriff as dz
    preise = dz.lade_preise()
    last = dz.lade_last()
    for w in dz.planungswochen(preise, last, "test_1_stunde"):
        plan = meine_strategie(w.historie)          # only data known on w.freitag
        kosten = bewerte(plan, w.zielwoche, w.last)  # real prices of the planned week

Rules (all switches in config/params.yaml, block `planung`):
  * Planning happens on Friday at `planungsuhrzeit` (assumption: 12:00).
  * Known at that moment: all prices up to and including Friday 23:00. Saturday's prices come out of the
    day-ahead auction only around `day_ahead_veroeffentlichung` (12:45). If someone moves the planning
    time after that, Saturday becomes known as well; the code handles both cases.
  * The planned week is Monday 00:00 to next Monday 00:00 (German time).
  * A week counts for a period only if it lies completely inside it (`nur_volle_wochen`), so no week
    mixes test 1 and test 2 (hour regime / quarter-hour regime).
"""
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import lade_params, pfad  # noqa: E402


class LookAheadFehler(RuntimeError):
    """Raised if data from after the planning moment would end up in the history."""


@dataclass
class Planungswoche:
    """Everything a strategy needs for one Friday."""
    freitag: pd.Timestamp        # planning day (00:00, German time)
    bekannt_bis: pd.Timestamp    # exclusive: everything before this moment was published
    historie: pd.DataFrame       # prices known on that Friday (zeit < bekannt_bis)
    zielwoche: pd.DataFrame      # real prices of the planned week (Mon 00:00 to next Mon 00:00)
    last: pd.DataFrame           # load of the planned week (datum, mwh)


# ---------------------------------------------------------------------------------------------
# Loading (thin wrappers, so R3 never has to know paths)
# ---------------------------------------------------------------------------------------------
def lade_preise(params: dict | None = None) -> pd.DataFrame:
    """Load preise_h.csv (step 02) and turn the text column `zeit` back into German time.

    The CSV stores times with their UTC offset (+01:00 winter, +02:00 summer). Reading them via UTC and
    converting back to Europe/Berlin gives one clean time column, also across the clock changes.
    """
    p = params or lade_params()
    datei = pfad(p, "processed") / "preise_h.csv"
    if not datei.exists():
        raise FileNotFoundError(f"{datei} fehlt. Zuerst ausführen: python src/run_all.py")
    df = pd.read_csv(datei)
    df["zeit"] = pd.to_datetime(df["zeit"], utc=True).dt.tz_convert(p["markt"]["zeitzone"])
    return df


def lade_last(params: dict | None = None) -> pd.DataFrame:
    """Load last_synth.csv (datum, mwh) as produced by step 02b; `datum` as pandas Timestamp."""
    p = params or lade_params()
    datei = pfad(p, "processed") / "last_synth.csv"
    if not datei.exists():
        raise FileNotFoundError(f"{datei} fehlt. Zuerst ausführen: python src/run_all.py")
    df = pd.read_csv(datei)
    df["datum"] = pd.to_datetime(df["datum"])
    return df


# ---------------------------------------------------------------------------------------------
# Date logic
# ---------------------------------------------------------------------------------------------
def _kalendertag(ts: pd.Timestamp) -> pd.Timestamp:
    """Plain calendar date (no time zone, 00:00). All day arithmetic is done on these.

    Same pitfall as in 01_download: adding days to a time-zone-aware timestamp adds fixed 24-hour
    blocks, so across a clock change "Monday 00:00" would become 01:00 or Sunday 23:00.
    """
    ts = pd.Timestamp(ts)
    return (ts.tz_localize(None) if ts.tzinfo else ts).normalize()


def bekannt_bis(freitag: pd.Timestamp, params: dict | None = None) -> pd.Timestamp:
    """First moment that is NOT yet known when planning on `freitag` (exclusive bound).

    Day-ahead logic: the auction on day X fixes the prices of day X+1. So on Friday morning Friday's
    prices are known (auction on Thursday), Saturday's are not. Only if planning happens after the
    publication time is Saturday known too.
    Works with plain clock times as strings ("12:00") so the rule stays readable in params.yaml.
    """
    params = params or lade_params()
    p, tz = params["planung"], params["markt"]["zeitzone"]
    tag = _kalendertag(freitag)
    nach_veroeffentlichung = pd.Timestamp(p["planungsuhrzeit"]) >= pd.Timestamp(p["day_ahead_veroeffentlichung"])
    tage = 2 if nach_veroeffentlichung else 1
    return (tag + pd.Timedelta(days=tage)).tz_localize(tz)


def freitage(periode: str, params: dict | None = None) -> list[pd.Timestamp]:
    """All planning Fridays whose planned week (following Mon-Sun) belongs to the period.

    `periode` is a key of `zeitraeume` in params.yaml, e.g. "test_1_stunde", "test_2_viertel",
    "training", "stresstest". With nur_volle_wochen the whole Mon-Sun week must lie inside the period;
    a week that crosses the boundary (e.g. 29.09.-05.10.2025, hour -> quarter-hour regime) is left out.
    """
    p = params or lade_params()
    start, ende = (pd.Timestamp(x) for x in p["zeitraeume"][periode])
    tz = p["markt"]["zeitzone"]
    # every Monday from the week containing `start` to the week containing `ende`
    montage = pd.date_range(start - pd.Timedelta(days=start.weekday()), ende, freq="7D")
    if p["planung"]["nur_volle_wochen"]:
        montage = [m for m in montage if m >= start and m + pd.Timedelta(days=6) <= ende]
    else:
        montage = [m for m in montage if m + pd.Timedelta(days=6) >= start]
    return [(m - pd.Timedelta(days=3)).tz_localize(tz) for m in montage]   # Friday before each Monday


def planungswoche(preise: pd.DataFrame, last: pd.DataFrame, freitag: pd.Timestamp,
                  params: dict | None = None, historie_wochen: int | None = None) -> Planungswoche:
    """Cut out what a strategy may see on `freitag` and what it is evaluated on.

    historie_wochen: optional window length (e.g. 4 for strategy B). None = everything since the start
    of the data (expanding window). The look-ahead check at the end is deliberately redundant: if anyone
    changes the slicing above, the run stops instead of producing too-good results.
    """
    p = params or lade_params()
    tz = p["markt"]["zeitzone"]
    grenze = bekannt_bis(freitag, p)
    montag_tag = _kalendertag(freitag) + pd.Timedelta(days=3)            # calendar dates first ...
    folge_montag_tag = montag_tag + pd.Timedelta(days=7)
    montag, naechster_montag = montag_tag.tz_localize(tz), folge_montag_tag.tz_localize(tz)   # ... then 00:00 local

    hist = preise[preise["zeit"] < grenze]
    if historie_wochen is not None:
        fenster_start = (_kalendertag(grenze) - pd.Timedelta(weeks=historie_wochen)).tz_localize(tz)
        hist = hist[hist["zeit"] >= fenster_start]
    ziel = preise[(preise["zeit"] >= montag) & (preise["zeit"] < naechster_montag)]
    tage = last[(last["datum"] >= montag_tag) & (last["datum"] < folge_montag_tag)]

    if len(hist) and hist["zeit"].max() >= grenze:
        raise LookAheadFehler(f"Historie für {freitag:%d.%m.%Y} enthält Daten ab {grenze}.")
    if len(hist) and len(ziel) and hist["zeit"].max() >= ziel["zeit"].min():
        raise LookAheadFehler(f"Historie und Zielwoche überschneiden sich am {freitag:%d.%m.%Y}.")
    return Planungswoche(freitag=freitag, bekannt_bis=grenze, historie=hist.reset_index(drop=True),
                         zielwoche=ziel.reset_index(drop=True), last=tage.reset_index(drop=True))


def planungswochen(preise: pd.DataFrame, last: pd.DataFrame, periode: str,
                   params: dict | None = None, historie_wochen: int | None = None):
    """Loop helper: yields one Planungswoche per Friday of the period, in time order."""
    p = params or lade_params()
    for f in freitage(periode, p):
        yield planungswoche(preise, last, f, p, historie_wochen)
