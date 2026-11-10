# KI: Claude, Zweck: synthetischer Lastgang (deterministisch) aus params.yaml, Reinigungsfenster über Mitternacht (E-033), geprüft von <Name R2> durch Review und pytest
"""Step 2b: synthetic load profile of the shiftable process -> data/processed/last_synth.csv.

Owner: R2. Output columns exactly as in docs/schnittstellen.md: `datum`, `mwh`.

What the file says: on which calendar day the shiftable process needs how much energy.
  * Production days (last.produktionstage):
      "taeglich"                    -> every day of the week (practice contact, diary K-005)
      "Mo-Fr ohne Feiertage Bayern" -> only working days (earlier assumption, kept as a variant)
  * On a production day: last.mwh_pro_tag = 8 MWh for the cleaning (CIP, 4 MW for 2 h; diary K-008, E-033).
    The value on date d belongs to the cleaning AFTER production on d, i.e. in the night d 22:00 to d+1 06:00.
WHEN during that night the cleaning runs is NOT decided here: that is the strategies' job (R3). The block
of last.blocklaenge_h hours must lie inside the cleaning window last.fenster_start_h..fenster_ende_h
(22-06 Uhr, the hours without production). The window crosses midnight, so all hour arithmetic is
modulo 24. The whole plant uses last.gesamtverbrauch_mwh_pro_tag (180 MWh); that number is only for context.

Deterministic on purpose (no random numbers): a random day-to-day fluctuation would hit all strategies
equally (each week is compared under all strategies), so it would not change which strategy is cheaper,
but it would add a parameter nobody can check. Uncertainty about the amount is handled by the
sensitivity analysis over mwh_pro_tag and blocklaenge_h (docs/sensitivitaet_plan.md).

The night of the clock change has 7 (March) or 9 (October) real hours; the strategies count real hours
(UTC), so a 2-hour block is always 2 hours of work and 8 MWh (diary E-036).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import fensterstunden, lade_params, pfad, werktage  # noqa: E402

SPALTEN = ["datum", "mwh_gesamt", "mwh_flexibel"]   # exactly as in docs/schnittstellen.md / docs/codebook.md
PRODUKTIONSTAGE = ("taeglich", "Mo-Fr ohne Feiertage Bayern")


class LastFehler(RuntimeError):
    """Own error type, printed as a readable message at the bottom of the file."""


def pruefe_parameter(last: dict) -> None:
    """Stop early with a clear message if a parameter makes no sense.

    Most important checks: the cleaning block must fit into the cleaning window 22-06 Uhr, and that window
    must not overlap the production hours 06-22 Uhr (cleaning needs the lines to stand still, K-008 B5).
    With an 8-hour window and a 2-hour block there are 7 possible start hours (22, 23, 0, ..., 4).
    """
    if last["produktionstage"] not in PRODUKTIONSTAGE:
        raise LastFehler(f"last.produktionstage = '{last['produktionstage']}' wird nicht unterstützt. "
                         f"Möglich: {', '.join(PRODUKTIONSTAGE)}.")
    if not 0 < last["mwh_pro_tag"] <= last["gesamtverbrauch_mwh_pro_tag"]:
        raise LastFehler("last.mwh_pro_tag muss größer als 0 und höchstens gesamtverbrauch_mwh_pro_tag sein.")
    if not 0 <= last["betrieb_start_h"] < last["betrieb_ende_h"] <= 24:
        raise LastFehler("Betriebszeit unplausibel: 0 <= betrieb_start_h < betrieb_ende_h <= 24.")
    if not (0 <= last["fenster_start_h"] <= 23 and 0 <= last["fenster_ende_h"] <= 23):
        raise LastFehler("Reinigungsfenster: fenster_start_h und fenster_ende_h müssen zwischen 0 und 23 liegen.")
    fenster = fensterstunden(last["fenster_start_h"], last["fenster_ende_h"])
    if any(last["betrieb_start_h"] <= h < last["betrieb_ende_h"] for h in fenster):
        raise LastFehler("Das Reinigungsfenster überschneidet sich mit der Betriebszeit (Produktion).")
    if not 0 < last["blocklaenge_h"] <= len(fenster):
        raise LastFehler(f"last.blocklaenge_h muss zwischen 1 und {len(fenster)} Stunden liegen (Reinigungsfenster).")
    if last["status_quo_start_h"] not in fenster[:len(fenster) - last["blocklaenge_h"] + 1]:
        raise LastFehler("Der Status-quo-Block (status_quo_start_h) liegt nicht vollständig im Reinigungsfenster.")


def erzeuge_last(von: str, bis: str, mwh_pro_tag: float, produktionstage: str = "taeglich",
                 mwh_gesamt: float = 180.0) -> pd.DataFrame:
    """One row per calendar day from `von` to `bis` (both included).

    mwh_gesamt:   consumption of the whole plant on a production day (practice contact: 180 MWh, K-008).
    mwh_flexibel: the shiftable part of it: the cleaning after that day's production (8 MWh, K-008).
    "taeglich": every day incl. public holidays. "Mo-Fr ohne Feiertage Bayern": working days only, 0 otherwise.
    Kept free of file access so the tests can call it with small date ranges.
    """
    tage = pd.date_range(von, bis, freq="D")                       # plain calendar days, no time zone
    if produktionstage == "taeglich":
        produziert = [True] * len(tage)
    else:
        produziert = werktage(tage.tz_localize("Europe/Berlin"), mariae_himmelfahrt=False)
    df = pd.DataFrame({
        "datum": tage.strftime("%Y-%m-%d"),                         # pure date as text, e.g. 2025-01-06
        "mwh_gesamt": [float(mwh_gesamt) if x else 0.0 for x in produziert],
        "mwh_flexibel": [float(mwh_pro_tag) if x else 0.0 for x in produziert],
    })
    return df[SPALTEN]


def main() -> None:
    p = lade_params()
    last = p["last"]
    pruefe_parameter(last)

    # Same period as the prices, so every price day has a load value (and vice versa).
    df = erzeuge_last(p["daten"]["aufloesungen"]["hour"], p["zeitraeume"]["datenstand"],
                      last["mwh_pro_tag"], last["produktionstage"], last["gesamtverbrauch_mwh_pro_tag"])

    ziel = pfad(p, "processed") / "last_synth.csv"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ziel, index=False)

    leistung = last["mwh_pro_tag"] / last["blocklaenge_h"]
    fenster = fensterstunden(last["fenster_start_h"], last["fenster_ende_h"])
    print(f"Lastgang: {len(df)} Tage, {int((df['mwh_gesamt'] > 0).sum())} Produktionstage x "
          f"{last['gesamtverbrauch_mwh_pro_tag']} MWh gesamt, davon {last['mwh_pro_tag']} MWh verschiebbar ({last['prozess']}); "
          f"Block {last['blocklaenge_h']} h mit {leistung:.2f} MW im Fenster {fenster[0]:02d}-{last['fenster_ende_h']:02d} Uhr "
          f"({len(fenster)} h), Status quo ab {last['status_quo_start_h']:02d} Uhr -> {ziel}")

if __name__ == "__main__":
    try:
        main()
    except LastFehler as e:
        sys.exit(f"FEHLER in 02_synthetisch: {e}")
