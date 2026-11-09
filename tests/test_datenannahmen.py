# KI: Claude, Zweck: Tests der Datenannahmen und der Aufbereitungslogik, geprüft von <Name R2> durch Review und absichtlich eingebaute Fehler
"""Automatisierte Prüfungen der Datenannahmen (K5 Stufe 5). Laufen mit `pytest tests/`.

Teil 1 (immer): Logik an kleinen, von Hand nachrechenbaren Beispielen.
Teil 2 (nach Pipeline-Lauf): Annahmen über die echten Dateien in data/ und die Schnittstelle zu R3.
"""
import csv
import hashlib
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PARAMS = yaml.safe_load((ROOT / "config" / "params.yaml").read_text(encoding="utf-8"))
TZ = PARAMS["markt"]["zeitzone"]
PROCESSED = ROOT / PARAMS["daten"]["pfade"]["processed"]
PREISE = PROCESSED / "preise_h.csv"
LAST = PROCESSED / "last_synth.csv"
MANIFEST = ROOT / PARAMS["daten"]["pfade"]["raw"] / "smard" / "manifest.csv"
WECHSEL = pd.Timestamp(PARAMS["markt"]["regimewechsel"]).tz_localize(TZ)


def _lade_modul(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "src" / f"{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


dl = _lade_modul("01_download")
auf = _lade_modul("02_aufbereitung")
syn = _lade_modul("02_synthetisch")
dz = _lade_modul("datenzugriff")


# ---------------------------------------------------------------------------------------------
# Teil 1: Logik an Beispielen
# ---------------------------------------------------------------------------------------------
def _utc_reihe(start_utc, n):
    idx = pd.date_range(start_utc, periods=n, freq="h", tz="UTC")
    return pd.Series(np.arange(n, dtype=float), index=idx)


def test_oktober_doppelte_stunde_wird_gemittelt():
    s = _utc_reihe("2025-10-25 22:00", 25)          # 26.10.2025: 25 Stunden
    ort, n_doppelt = auf.zu_ortszeit(s, TZ)
    assert len(ort) == 24 and n_doppelt == 1
    assert ort[ort.index.hour == 2].iloc[0] == pytest.approx((2 + 3) / 2)


def test_oktober_mittel_bleibt_leer_wenn_ein_wert_fehlt():
    s = _utc_reihe("2025-10-25 22:00", 25)
    s.iloc[3] = np.nan
    ort, _ = auf.zu_ortszeit(s, TZ)
    assert np.isnan(ort[ort.index.hour == 2].iloc[0])


def test_maerz_fehlende_stunde_wird_nicht_aufgefuellt():
    s = _utc_reihe("2026-03-28 23:00", 23)          # 29.03.2026: 23 Stunden
    ort, _ = auf.zu_ortszeit(s, TZ)
    assert len(ort) == 23 and 2 not in set(ort.index.hour)
    raster = auf.erwartetes_raster(pd.Timestamp("2026-03-29", tz=TZ), pd.Timestamp("2026-03-30", tz=TZ), TZ)
    assert len(raster) == 23


def test_werktage_bayern_und_variante():
    tage = pd.DatetimeIndex(pd.to_datetime(["2025-01-06", "2025-06-19", "2025-08-15", "2025-10-04", "2025-10-06"])).tz_localize(TZ)
    assert list(auf.werktage(tage, mariae_himmelfahrt=False)) == [False, False, True, False, True]
    assert list(auf.werktage(tage, mariae_himmelfahrt=True)) == [False, False, False, False, True]


def test_wochenanfaenge_bleiben_montag_mitternacht():
    b, e = dl.benoetigter_zeitraum("2025-03-20", "2025-04-10", TZ)
    wochen = dl.wochenanfaenge(b, e, TZ)
    assert all(w.weekday() == 0 and w.hour == 0 for w in wochen)


def test_last_beispielwoche():
    df = syn.erzeuge_last("2025-06-02", "2025-06-08", 2.0, mariae=False)
    assert list(df.columns) == ["datum", "mwh"]
    assert list(df["mwh"]) == [2.0, 2.0, 2.0, 2.0, 2.0, 0.0, 0.0]


def test_last_feiertag_und_variante():
    assert syn.erzeuge_last("2025-08-15", "2025-08-15", 2.0, mariae=False)["mwh"].iloc[0] == 2.0
    assert syn.erzeuge_last("2025-08-15", "2025-08-15", 2.0, mariae=True)["mwh"].iloc[0] == 0.0


def test_last_unsinnige_parameter_werden_abgelehnt():
    for feld, wert in [("mwh_pro_werktag", 0), ("blocklaenge_h", 25), ("werktage", "Mo-Sa")]:
        with pytest.raises(syn.LastFehler):
            syn.pruefe_parameter({**PARAMS["last"], feld: wert})


def test_bekannt_bis_haengt_an_der_planungsuhrzeit():
    fr = pd.Timestamp("2025-03-07", tz=TZ)
    vorher = {**PARAMS, "planung": {**PARAMS["planung"], "planungsuhrzeit": "12:00"}}
    nachher = {**PARAMS, "planung": {**PARAMS["planung"], "planungsuhrzeit": "14:00"}}
    assert dz.bekannt_bis(fr, vorher) == pd.Timestamp("2025-03-08", tz=TZ)
    assert dz.bekannt_bis(fr, nachher) == pd.Timestamp("2025-03-09", tz=TZ)


def test_freitage_nur_volle_wochen_je_periode():
    f1, f2 = dz.freitage("test_1_stunde", PARAMS), dz.freitage("test_2_viertel", PARAMS)
    assert all(f.weekday() == 4 for f in f1 + f2) and set(f1).isdisjoint(f2)
    assert f1[-1] + pd.Timedelta(days=10) < WECHSEL <= f2[0] + pd.Timedelta(days=3)


def test_look_ahead_wird_erkannt():
    fr = pd.Timestamp("2025-03-07", tz=TZ)
    preise = pd.DataFrame({"zeit": pd.date_range("2025-03-01", "2025-03-17", freq="h", tz=TZ), "preis_eur_mwh": 1.0})
    last = pd.DataFrame({"datum": pd.date_range("2025-03-01", "2025-03-17"), "mwh": 2.0})
    original = dz.bekannt_bis
    try:
        dz.bekannt_bis = lambda f, p=None: pd.Timestamp("2025-03-12", tz=TZ)   # absichtlich falsche Grenze
        with pytest.raises(dz.LookAheadFehler):
            dz.planungswoche(preise, last, fr, PARAMS)
    finally:
        dz.bekannt_bis = original


# ---------------------------------------------------------------------------------------------
# Teil 2: Annahmen über die echten Daten (erst nach `python src/run_all.py`)
# ---------------------------------------------------------------------------------------------
braucht_daten = pytest.mark.skipif(not (PREISE.exists() and LAST.exists()), reason="Pipeline noch nicht gelaufen")


@pytest.fixture(scope="module")
def preise():
    return dz.lade_preise(PARAMS)


@pytest.fixture(scope="module")
def last():
    return dz.lade_last(PARAMS)


@braucht_daten
def test_spalten_laut_schnittstelle():
    assert list(pd.read_csv(PREISE, nrows=1).columns) == ["zeit", "datum", "stunde", "preis_eur_mwh", "regime", "werktag"]
    assert list(pd.read_csv(LAST, nrows=1).columns) == ["datum", "mwh"]


@braucht_daten
def test_keine_luecken(preise):
    assert preise["preis_eur_mwh"].notna().all(), f"Fehlende Preise:\n{preise[preise['preis_eur_mwh'].isna()].head()}"


@braucht_daten
def test_stunden_pro_tag(preise):
    # 24 Stunden; nur am letzten Sonntag im März 23 (02:00 Uhr existiert nicht)
    n = preise.groupby("datum").size()
    tage = pd.to_datetime(pd.Series(n.index))
    maerz = ((tage.dt.month == 3) & (tage.dt.weekday == 6) & (tage.dt.day >= 25)).to_numpy()
    assert (n[maerz] == 23).all() and (n[~maerz] == 24).all()


@braucht_daten
def test_zeitraum_vollstaendig(preise):
    assert preise["zeit"].min() == pd.Timestamp(PARAMS["daten"]["aufloesungen"]["hour"]).tz_localize(TZ)
    assert preise["zeit"].max() == pd.Timestamp(PARAMS["zeitraeume"]["datenstand"]).tz_localize(TZ) + pd.Timedelta(hours=23)


@braucht_daten
def test_zeit_sortiert_eindeutig_volle_stunden(preise):
    assert preise["zeit"].is_monotonic_increasing and not preise["zeit"].duplicated().any()
    assert (preise["zeit"].dt.minute == 0).all()
    assert (preise["stunde"] == preise["zeit"].dt.hour).all()


@braucht_daten
def test_preisbereich(preise):
    # Preisgrenzen der Day-Ahead-Auktion; negative Preise sind erlaubt und bleiben drin
    assert preise["preis_eur_mwh"].between(-500, 4000).all()
    assert (preise["preis_eur_mwh"] < 0).any()


@braucht_daten
def test_regime_am_wechsel(preise):
    assert (preise.loc[preise["zeit"] < WECHSEL, "regime"] == "stunde").all()
    assert (preise.loc[preise["zeit"] >= WECHSEL, "regime"] == "viertel").all()


@braucht_daten
def test_werktag_nie_am_wochenende(preise):
    assert not preise.loc[preise["zeit"].dt.weekday >= 5, "werktag"].any()


@braucht_daten
def test_last_laut_params(last):
    assert last["datum"].is_monotonic_increasing and not last["datum"].duplicated().any()
    assert len(last) == (last["datum"].max() - last["datum"].min()).days + 1
    assert set(last["mwh"]) <= {PARAMS["last"]["mwh_pro_werktag"], 0.0}


@braucht_daten
def test_last_und_preise_gleiche_werktage(preise, last):
    wt = preise.groupby("datum")["werktag"].first()
    assert ((last["mwh"] > 0).to_numpy() == wt.reindex(last["datum"].dt.strftime("%Y-%m-%d")).to_numpy()).all()


@braucht_daten
def test_zeitumstellung_nur_an_lastfreien_tagen(last):
    # Tagebuch E-018: Umstellungstage sind Sonntage ohne Last, die Behandlung ändert keine Kosten
    tage = pd.to_datetime(pd.read_csv(PROCESSED / "zeitumstellung.csv")["datum"])
    assert len(tage) > 0 and (tage.dt.weekday == 6).all()
    assert (last[last["datum"].isin(tage)]["mwh"] == 0).all()


@braucht_daten
def test_kein_look_ahead_in_allen_planungswochen(preise, last):
    for periode in ("training", "test_1_stunde", "test_2_viertel", "stresstest"):
        for w in dz.planungswochen(preise, last, periode, PARAMS, historie_wochen=4):
            assert w.historie.empty or w.historie["zeit"].max() < w.bekannt_bis
            assert w.zielwoche["zeit"].min() >= w.bekannt_bis
            assert len(w.zielwoche) in (167, 168) and len(w.last) == 7


@pytest.mark.skipif(not MANIFEST.exists(), reason="Download noch nicht gelaufen")
def test_rohdaten_unveraendert():
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        zeilen = [z for z in csv.DictReader(f) if z["status"] == "aktiv"]
    assert zeilen
    for z in zeilen:
        datei = MANIFEST.parent.parent / z["datei"]
        assert hashlib.sha256(datei.read_bytes()).hexdigest() == z["sha256"], f"verändert: {datei}"
