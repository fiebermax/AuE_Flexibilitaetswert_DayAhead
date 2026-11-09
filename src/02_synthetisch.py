# KI: Claude, Zweck: synthetischer Lastgang (deterministisch) aus params.yaml, geprüft von <Name R2> durch Review und pytest
"""Step 2b: synthetic load profile of the shiftable process -> data/processed/last_synth.csv.

Owner: R2. Output columns exactly as in docs/schnittstellen.md: `datum`, `mwh`.

What the file says: on which calendar day the shiftable process needs how much energy.
  * Production days (last.produktionstage):
      "taeglich"                    -> every day of the week (practice contact, diary K-005)
      "Mo-Fr ohne Feiertage Bayern" -> only working days (earlier assumption, kept as a variant)
  * On a production day: last.mwh_pro_tag (PLACEHOLDER 2.0 MWh until the shiftable process is fixed).
WHEN during the day the energy is used is NOT decided here: that is the strategies' job (R3). The block
of last.blocklaenge_h hours must lie inside the operating hours last.betrieb_start_h..betrieb_ende_h
(06-22 Uhr according to the practice contact). The whole plant uses about
last.gesamtverbrauch_mwh_pro_tag (50 MWh); that number is only for context.

Deterministic on purpose (no random numbers): a random day-to-day fluctuation would hit all strategies
equally (each week is compared under all strategies), so it would not change which strategy is cheaper,
but it would add a parameter nobody can check. Uncertainty about the amount is handled by the
sensitivity analysis over mwh_pro_tag and blocklaenge_h (docs/sensitivitaet_plan.md).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import lade_params, pfad, werktage  # noqa: E402

SPALTEN = ["datum", "mwh"]                          # exactly as in docs/schnittstellen.md
PRODUKTIONSTAGE = ("taeglich", "Mo-Fr ohne Feiertage Bayern")


class LastFehler(RuntimeError):
    """Own error type, printed as a readable message at the bottom of the file."""


def pruefe_parameter(last: dict) -> None:
    """Stop early with a clear message if a parameter makes no sense.

    Most important check: the block must fit into the operating hours. With 06-22 Uhr (16 h) and a
    6-hour block there are 11 possible start hours (06 ... 16); a 17-hour block would be impossible.
    """
    if last["produktionstage"] not in PRODUKTIONSTAGE:
        raise LastFehler(f"last.produktionstage = '{last['produktionstage']}' wird nicht unterstützt. "
                         f"Möglich: {', '.join(PRODUKTIONSTAGE)}.")
    if not last["mwh_pro_tag"] > 0:
        raise LastFehler("last.mwh_pro_tag muss größer als 0 sein.")
    if not 0 <= last["betrieb_start_h"] < last["betrieb_ende_h"] <= 24:
        raise LastFehler("Betriebszeit unplausibel: 0 <= betrieb_start_h < betrieb_ende_h <= 24.")
    fenster = last["betrieb_ende_h"] - last["betrieb_start_h"]
    if not 0 < last["blocklaenge_h"] <= fenster:
        raise LastFehler(f"last.blocklaenge_h muss zwischen 1 und {fenster} Stunden liegen (Betriebszeit).")
    if not last["betrieb_start_h"] <= last["status_quo_start_h"] <= last["betrieb_ende_h"] - last["blocklaenge_h"]:
        raise LastFehler("Der Status-quo-Block (status_quo_start_h) liegt nicht in der Betriebszeit.")


def erzeuge_last(von: str, bis: str, mwh_pro_tag: float, produktionstage: str = "taeglich") -> pd.DataFrame:
    """One row per calendar day from `von` to `bis` (both included).

    "taeglich": mwh_pro_tag on every day. "Mo-Fr ohne Feiertage Bayern": mwh_pro_tag on working days,
    0 otherwise (same rule as the column `werktag` of the prices, see gemeinsam.werktage).
    Kept free of file access so the tests can call it with small date ranges.
    """
    tage = pd.date_range(von, bis, freq="D")                       # plain calendar days, no time zone
    if produktionstage == "taeglich":
        produziert = [True] * len(tage)
    else:
        produziert = werktage(tage.tz_localize("Europe/Berlin"), mariae_himmelfahrt=False)
    df = pd.DataFrame({
        "datum": tage.strftime("%Y-%m-%d"),                         # pure date as text, e.g. 2025-01-06
        "mwh": [float(mwh_pro_tag) if x else 0.0 for x in produziert],
    })
    return df[SPALTEN]


def main() -> None:
    p = lade_params()
    last = p["last"]
    pruefe_parameter(last)

    # Same period as the prices, so every price day has a load value (and vice versa).
    df = erzeuge_last(p["daten"]["aufloesungen"]["hour"], p["zeitraeume"]["datenstand"],
                      last["mwh_pro_tag"], last["produktionstage"])

    ziel = pfad(p, "processed") / "last_synth.csv"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ziel, index=False)

    leistung = last["mwh_pro_tag"] / last["blocklaenge_h"]
    print(f"Lastgang (synthetisch): {len(df)} Tage, {int((df['mwh'] > 0).sum())} Produktionstage x "
          f"{last['mwh_pro_tag']} MWh = {df['mwh'].sum():.0f} MWh; Block {last['blocklaenge_h']} h mit "
          f"{leistung:.2f} MW in {last['betrieb_start_h']:02d}-{last['betrieb_ende_h']:02d} Uhr -> {ziel}")


if __name__ == "__main__":
    try:
        main()
    except LastFehler as e:
        sys.exit(f"FEHLER in 02_synthetisch: {e}")
