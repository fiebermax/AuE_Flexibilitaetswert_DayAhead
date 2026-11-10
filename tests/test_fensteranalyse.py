# KI: Claude, Zweck: Tests Ortszeit und Fenster-Kennzahl (Tag und Nacht über Mitternacht, E-036), geprüft von <Name R2> durch Review und Nachrechnen
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


def _stunden(utc_von, utc_bis, preis_lokal):
    """Hourly frame between two UTC times; preis_lokal(local timestamp) -> price."""
    zeiten = pd.date_range(utc_von, utc_bis, freq="h", tz="UTC", inclusive="left")
    df = cl.zeitspalten(pd.DataFrame({"ts_utc": zeiten, "preis_eur_mwh": 0.0}), TZ, pd.Timestamp("2025-10-01", tz=TZ), False)
    df["preis_eur_mwh"] = [preis_lokal(t) for t in pd.to_datetime(df["ts_utc"], utc=True).dt.tz_convert(TZ)]
    return df


def test_nacht_ueber_mitternacht_gehoert_zum_vortag():
    # Fri 07.03.2025 12:00 to Sat 08.03. 12:00 local (winter, UTC+1); cheap 02-04 Uhr on Saturday morning
    df = _stunden("2025-03-07 11:00", "2025-03-08 11:00", lambda t: 20.0 if t.hour in (2, 3) else 80.0)
    nacht = fa.fenster_je_tag(df, 22, 6, 2, 22)
    assert len(nacht) == 1                                    # one complete night, named after Friday
    n = nacht.iloc[0]
    assert n["datum_lokal"] == "2025-03-07" and n["n_stunden"] == 8
    assert n["start_billigst"] == 2 and n["preis_billigst"] == 20.0
    assert n["preis_status_quo"] == 80.0 and n["mehrkosten_eur_mwh"] == pytest.approx(60.0)


@pytest.mark.parametrize("utc_von, n_stunden", [("2025-03-29 12:00", 7), ("2025-10-25 12:00", 9)])
def test_umstellungsnaechte_mit_echten_stunden(utc_von, n_stunden):
    # March night 29./30.03.2025 has no 02:00 -> 7 h; October night 25./26.10.2025 has 02:00 twice -> 9 h
    df = _stunden(utc_von, pd.Timestamp(utc_von) + pd.Timedelta(hours=24), lambda t: 50.0)
    nacht = fa.fenster_je_tag(df, 22, 6, 2, 22).iloc[0]
    assert nacht["n_stunden"] == n_stunden and nacht["mehrkosten_eur_mwh"] == 0.0


def test_block_darf_beide_oktober_zwei_uhr_stunden_nutzen():
    # both "02:00" hours of 26.10.2025 are cheap: a 2-hour block covers both real hours, start label 2
    df = _stunden("2025-10-25 12:00", "2025-10-26 12:00", lambda t: 10.0 if t.hour == 2 else 60.0)
    nacht = fa.fenster_je_tag(df, 22, 6, 2, 22).iloc[0]
    assert nacht["start_billigst"] == 2 and nacht["preis_billigst"] == 10.0


def test_unvollstaendige_nacht_am_datenrand_wird_uebersprungen():
    df = _stunden("2025-03-07 23:00", "2025-03-08 11:00", lambda t: 50.0)   # starts at 00:00 local, 22-24 missing
    assert fa.fenster_je_tag(df, 22, 6, 2, 22).empty


def test_jahreswerte_hochgerechnet():
    tage = pd.DataFrame({"datum_lokal": ["2025-01-01", "2025-01-02"], "mehrkosten_eur_mwh": [10.0, 30.0]})
    j = fa.kennzahlen_je_jahr(tage, 8.0).iloc[0]
    assert j["eur_summe"] == 320.0 and j["eur_pro_jahr"] == 20.0 * 8 * 365 and not j["vollstaendig"]
