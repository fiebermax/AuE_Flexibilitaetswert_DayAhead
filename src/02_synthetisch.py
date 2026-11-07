# KI: Claude, Zweck: synthetischer Lastgang (deterministisch) aus params.yaml, geprüft von <Name R2> durch Review und pytest
"""Step 2b: synthetic load profile of the flexible process -> data/processed/last_synth.parquet.

Owner: R2. Output columns exactly as in docs/schnittstellen.md: `datum`, `mwh`.

What the file says: on which calendar day the shiftable process needs how much energy.
  * working day (Mon-Fri, no Bavarian public holiday): last.mwh_pro_werktag (placeholder 2.0 MWh)
  * other days: 0 MWh (the row is still there, so "no production" is explicit, not a missing row)
WHEN during the day the energy is used is NOT decided here: that is the strategies' job (R3).
The block length (last.blocklaenge_h) only sets the power: 2.0 MWh / 6 h = 0.33 MW constant.

Deterministic on purpose (no random numbers):
  A random day-to-day fluctuation of the amount would hit all strategies equally (each week is
  compared under all strategies), so it would not change which strategy is cheaper, but it would add a
  parameter (size of the fluctuation) that nobody can check against reality. The uncertainty about the
  amount is handled instead by the sensitivity analysis over mwh_pro_werktag and blocklaenge_h
  (docs/sensitivitaet_plan.md). `seed` stays in params.yaml for the bootstrap (R3) and for any later
  random component.

All numbers are placeholders until the talk with the practice contact ("vom Praxiskontakt zu plausibilisieren").
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import lade_params, pfad, werktage  # noqa: E402

SPALTEN = ["datum", "mwh"]                          # exactly as in docs/schnittstellen.md
UNTERSTUETZTE_WERKTAGSREGEL = "Mo-Fr ohne Feiertage Bayern"


class LastFehler(RuntimeError):
    """Own error type, printed as a readable message at the bottom of the file."""


def pruefe_parameter(last: dict) -> None:
    """Stop early with a clear message if a parameter makes no physical sense.

    `werktage` in params.yaml is a description for humans; the rule actually used is the function
    werktage() in gemeinsam.py. If somebody changes the text (e.g. to "Mo-Sa"), the code would silently
    keep using Mon-Fri, so we refuse instead and ask for the code to be adapted too.
    """
    if last["werktage"] != UNTERSTUETZTE_WERKTAGSREGEL:
        raise LastFehler(f"last.werktage = '{last['werktage']}' wird nicht unterstützt. "
                         f"Umgesetzt ist nur '{UNTERSTUETZTE_WERKTAGSREGEL}' (gemeinsam.werktage).")
    if not last["mwh_pro_werktag"] > 0:
        raise LastFehler("last.mwh_pro_werktag muss größer als 0 sein.")
    if not 0 < last["blocklaenge_h"] <= 24:
        raise LastFehler("last.blocklaenge_h muss zwischen 1 und 24 Stunden liegen.")


def erzeuge_last(von: str, bis: str, mwh_pro_werktag: float, mariae: bool) -> pd.DataFrame:
    """One row per calendar day from `von` to `bis` (both included): mwh on working days, else 0.

    Kept as a separate function without file access, so the tests can call it directly
    with small date ranges and check the result by hand.
    """
    tage = pd.date_range(von, bis, freq="D")                       # plain calendar days, no time zone
    ist_werktag = werktage(tage.tz_localize("Europe/Berlin"), mariae)
    df = pd.DataFrame({
        "datum": tage.date,                                         # stored as a pure date (no time)
        "mwh": [float(mwh_pro_werktag) if w else 0.0 for w in ist_werktag],
    })
    return df[SPALTEN]


def main() -> None:
    p = lade_params()
    last = p["last"]
    pruefe_parameter(last)

    # Same period as the prices, so every price day has a load value (and vice versa).
    von = p["daten"]["aufloesungen"]["hour"]
    bis = p["zeitraeume"]["datenstand"]
    df = erzeuge_last(von, bis, last["mwh_pro_werktag"], bool(last["feiertagsvariante_mariae_himmelfahrt"]))

    ziel = pfad(p, "processed") / "last_synth.parquet"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ziel, index=False)

    n_wt = int((df["mwh"] > 0).sum())
    leistung = last["mwh_pro_werktag"] / last["blocklaenge_h"]
    print(f"Lastgang (synthetisch): {len(df)} Tage, davon {n_wt} Werktage x {last['mwh_pro_werktag']} MWh "
          f"= {df['mwh'].sum():.0f} MWh; Leistung im Block {leistung:.2f} MW -> {ziel}")


if __name__ == "__main__":
    try:
        main()
    except LastFehler as e:
        sys.exit(f"FEHLER in 02_synthetisch: {e}")
