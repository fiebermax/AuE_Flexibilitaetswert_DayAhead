# KI: Claude, Zweck: Tests Ortszeit und Fenster-Kennzahl, geprüft von <Name R2> durch Review und Nachrechnen
"""Ortszeit-Umrechnung (Sommer- und Winterzeit) und Fenster-Kennzahl (src/fensteranalyse.py)."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
TZ = "Europe/Berlin"


def _modul(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "src" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


cl, fa = _modul("cleaning"), _modul("fensteranalyse")


@pytest.mark.parametrize("utc, lokal_stunde, in_betrieb", [
    ("2025-07-15 03:00", 5, False), ("2025-07-15 04:00", 6, True),      # Sommerzeit: UTC+2
    ("2025-07-15 19:00", 21, True), ("2025-07-15 20:00", 22, False),
    ("2025-01-15 04:00", 5, False), ("2025-01-15 05:00", 6, True),      # Winterzeit: UTC+1
    ("2025-01-15 20:00", 21, True), ("2025-01-15 21:00", 22, False),
])
def test_betriebszeit_in_ortszeit_sommer_und_winter(utc, lokal_stunde, in_betrieb):
    df = pd.DataFrame({"ts_utc": [pd.Timestamp(utc, tz="UTC")], "preis_eur_mwh": [1.0]})
    df = cl.zeitspalten(df, TZ, pd.Timestamp("2025-10-01", tz=TZ), False)
    last = pd.DataFrame({"datum": [df["datum_lokal"].iloc[0]], "mwh_gesamt": [50.0], "mwh_flexibel": [2.0]})
    out, _, _ = cl.join_last(df, last, 6, 22)
    assert out["stunde_lokal"].iloc[0] == lokal_stunde and bool(out["in_betriebszeit"].iloc[0]) is in_betrieb


def _tag(datum_utc_start, preise_lokal):
    """24 hours of one local day; preise_lokal maps local hour -> price, others 100."""
    zeiten = pd.date_range(datum_utc_start, periods=24, freq="h", tz="UTC")
    df = cl.zeitspalten(pd.DataFrame({"ts_utc": zeiten, "preis_eur_mwh": 100.0}), TZ, pd.Timestamp("2025-10-01", tz=TZ), False)
    df["preis_eur_mwh"] = [preise_lokal.get(h, 100.0) for h in df["stunde_lokal"]]
    return df


@pytest.mark.parametrize("utc_start", ["2025-07-14 22:00", "2025-01-14 23:00"])   # 15.07. (Sommer) / 15.01. (Winter) 00:00 lokal
def test_billigstes_fenster_in_ortszeit(utc_start):
    # billig 10-16 Uhr deutscher Zeit; in UTC wäre das 08-14 (Sommer) bzw. 09-15 (Winter)
    df = _tag(utc_start, {h: 40.0 for h in range(10, 16)})
    tag = fa.fenster_je_tag(df, 6, 22, 6, 8).iloc[0]
    assert tag["start_billigst"] == 10
    assert tag["preis_billigst"] == 40.0
    assert tag["preis_status_quo"] == pytest.approx((100 * 2 + 40 * 4) / 6)       # 08-14: 8,9 teuer, 10-13 billig
    assert tag["mehrkosten_eur_mwh"] == pytest.approx(tag["preis_status_quo"] - 40.0)


def test_prozent_nur_bei_positivem_billigsten_preis():
    df = _tag("2025-05-10 22:00", {h: -5.0 for h in range(11, 17)})
    tag = fa.fenster_je_tag(df, 6, 22, 6, 8).iloc[0]
    assert tag["preis_billigst"] < 0 and pd.isna(tag["mehrkosten_pct"]) and tag["mehrkosten_eur_mwh"] > 0
