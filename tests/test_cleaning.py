# KI: Claude, Zweck: Tests der Datenbereinigung (src/cleaning.py), geprüft von <Name R2> durch Review und absichtlich eingebaute Fehler
"""Tests für src/cleaning.py: Logik an kleinen Beispielen und Annahmen über data/preise_clean.csv.

Pflicht laut Auftrag: lückenloses Raster, eindeutiger Index, tz=UTC, Spalten und Typen, Wertebereich, Flags vorhanden.
Laufen mit `pytest tests/`.
"""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PARAMS = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
TZ = PARAMS["markt"]["zeitzone"]
CLEAN = ROOT / PARAMS["daten"]["pfade"]["processed"] / "preise_clean.csv"
SPALTEN = ["ts_utc", "ts_lokal", "datum_lokal", "stunde_lokal", "wochentag", "saison", "preis_eur_mwh", "regime",
           "werktag", "sonntag", "feiertag", "in_betriebszeit", "last_mwh_tag", "last_mwh_flexibel_tag", "imputed", "flag_outlier"]

spec = importlib.util.spec_from_file_location("cleaning", ROOT / "src" / "cleaning.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)


def _roh(zeiten_utc, preise):
    return pd.DataFrame({"ts_utc": pd.to_datetime(zeiten_utc, utc=True), "preis_eur_mwh": preise})


# ---------------------------------------------------------------------------------------------
# Logik an Beispielen
# ---------------------------------------------------------------------------------------------
def test_exakte_dublette_wird_einmal_behalten():
    df, n_exakt, n_wid = cl.dubletten(_roh(["2025-01-01 00:00", "2025-01-01 00:00", "2025-01-01 01:00"], [10.0, 10.0, 11.0]))
    assert len(df) == 2 and n_exakt == 1 and n_wid == 0


def test_widerspruechliche_dublette_bricht_ab():
    with pytest.raises(cl.CleaningFehler):
        cl.dubletten(_roh(["2025-01-01 00:00", "2025-01-01 00:00"], [10.0, 12.0]))


def test_luecke_bleibt_sichtbar_und_wird_gelistet():
    df = _roh(["2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 04:00"], [1.0, 2.0, 3.0])
    out, luecken = cl.raster_und_luecken(df, pd.Timestamp("2025-01-01 00:00", tz="UTC"), pd.Timestamp("2025-01-01 05:00", tz="UTC"))
    assert len(out) == 5 and out["preis_eur_mwh"].isna().sum() == 2          # nichts aufgefüllt
    assert len(luecken) == 1 and luecken["laenge_h"].iloc[0] == 2
    assert not out["imputed"].any()


def test_oktober_hat_25_lokale_stunden_ohne_mitteln():
    # 26.10.2025: 25 UTC-Stunden; beide 02:00-Stunden bleiben mit eigenem Preis erhalten
    zeiten = pd.date_range("2025-10-25 22:00", periods=25, freq="h", tz="UTC")
    df = pd.DataFrame({"ts_utc": zeiten, "preis_eur_mwh": np.arange(25.0)})
    out = cl.zeitspalten(df, TZ, pd.Timestamp("2025-10-01", tz=TZ), False)
    assert len(out) == 25 and (out["stunde_lokal"] == 2).sum() == 2
    assert out.loc[out["stunde_lokal"] == 2, "preis_eur_mwh"].tolist() == [2.0, 3.0]
    assert cl.zeitumstellungstage(out)["stunden_lokal"].tolist() == [25]


def test_maerz_hat_23_lokale_stunden():
    zeiten = pd.date_range("2026-03-28 23:00", periods=23, freq="h", tz="UTC")
    out = cl.zeitspalten(pd.DataFrame({"ts_utc": zeiten, "preis_eur_mwh": 1.0}), TZ, pd.Timestamp("2025-10-01", tz=TZ), False)
    assert 2 not in set(out["stunde_lokal"]) and cl.zeitumstellungstage(out)["stunden_lokal"].tolist() == [23]


def test_preisgrenzen():
    df = _roh(["2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 02:00"], [-500.0, 5000.0, 5000.01])
    assert len(cl.ausserhalb_preisgrenzen(df, -500, 5000)) == 1               # Grenzwerte selbst sind gültig


def test_ausreisser_nur_markiert_nichts_veraendert():
    werte = [50.0 + (i % 5) for i in range(27)] + [500.0]
    zeiten = pd.date_range("2025-05-01 10:00", periods=28, freq="D", tz="UTC")   # 12:00 deutscher Zeit, alle im Mai
    df = cl.zeitspalten(pd.DataFrame({"ts_utc": zeiten, "preis_eur_mwh": werte}), TZ, pd.Timestamp("2025-10-01", tz=TZ), False)
    out, _ = cl.flagge_ausreisser(df, 3.5)
    assert len(out) == len(df) and out["preis_eur_mwh"].equals(df["preis_eur_mwh"])
    assert out["flag_outlier"].sum() == 1 and out["flag_outlier"].iloc[-1]


def test_join_zaehlt_nicht_gematchte():
    zeiten = pd.date_range("2025-01-01 00:00", periods=48, freq="h", tz="UTC")
    df = cl.zeitspalten(pd.DataFrame({"ts_utc": zeiten, "preis_eur_mwh": 1.0}), TZ, pd.Timestamp("2025-10-01", tz=TZ), False)
    last = pd.DataFrame({"datum": ["2025-01-01", "2025-01-05"], "mwh_gesamt": [50.0, 50.0], "mwh_flexibel": [2.0, 2.0]})
    out, ohne_last, ohne_preis = cl.join_last(df, last, 6, 22)
    assert len(out) == len(df)                                     # Join verändert die Zeilenzahl nicht
    assert ohne_last == 25 and ohne_preis == 1                     # 02.01. (24 h) + 03.01. 00:00 ohne Last; 05.01. ohne Preis
    assert out.loc[out["stunde_lokal"].between(6, 21), "in_betriebszeit"].all()


# ---------------------------------------------------------------------------------------------
# Annahmen über die bereinigte Datei
# ---------------------------------------------------------------------------------------------
braucht_daten = pytest.mark.skipif(not CLEAN.exists(), reason="src/cleaning.py noch nicht gelaufen")


@pytest.fixture(scope="module")
def clean():
    df = pd.read_csv(CLEAN)
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
    return df


@braucht_daten
def test_spalten_und_typen(clean):
    assert list(clean.columns) == SPALTEN
    assert str(clean["ts_utc"].dt.tz) == "UTC"
    for spalte in ("werktag", "sonntag", "feiertag", "in_betriebszeit", "imputed", "flag_outlier"):
        assert clean[spalte].dtype == bool, spalte
    assert clean["preis_eur_mwh"].dtype == float and clean["stunde_lokal"].between(0, 23).all()


@braucht_daten
def test_lueckenloses_stundenraster_eindeutig(clean):
    assert clean["ts_utc"].is_unique and clean["ts_utc"].is_monotonic_increasing
    assert (clean["ts_utc"].diff().dropna() == pd.Timedelta(hours=1)).all()
    beginn = pd.Timestamp(PARAMS["daten"]["aufloesungen"]["hour"]).tz_localize(TZ).tz_convert("UTC")
    ende = (pd.Timestamp(PARAMS["zeitraeume"]["datenstand"]) + pd.Timedelta(days=1)).tz_localize(TZ).tz_convert("UTC")
    assert clean["ts_utc"].min() == beginn and clean["ts_utc"].max() == ende - pd.Timedelta(hours=1)
    assert clean["preis_eur_mwh"].notna().all()


@braucht_daten
def test_wertebereich(clean):
    c = PARAMS["cleaning"]
    assert clean["preis_eur_mwh"].between(c["preis_min_eur_mwh"], c["preis_max_eur_mwh"]).all()
    assert (clean["preis_eur_mwh"] < 0).any()                      # negative Preise wurden nicht entfernt
    assert (clean["last_mwh_tag"] == PARAMS["last"]["gesamtverbrauch_mwh_pro_tag"]).all()


@braucht_daten
def test_flags_vorhanden_und_plausibel(clean):
    assert not clean["imputed"].any()
    assert 0 < clean["flag_outlier"].mean() < 0.10
    assert set(clean["regime"]) == {"stunde", "viertel"}


@braucht_daten
def test_lokale_tage_23_24_25_stunden(clean):
    n = clean.groupby("datum_lokal").size()
    assert set(n.unique()) <= {23, 24, 25}
    assert (n == 23).sum() == 5 and (n == 25).sum() == 5            # je eine März- und Oktober-Umstellung 2022-2026
    # Umstellungstage sind Sonntage; 02-03 Uhr liegt außerhalb der Betriebszeit
    tage = pd.to_datetime(pd.Series(n[n != 24].index))
    assert (tage.dt.weekday == 6).all() and PARAMS["last"]["betrieb_start_h"] >= 3
