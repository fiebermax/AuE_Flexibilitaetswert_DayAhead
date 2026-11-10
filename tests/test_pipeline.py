# KI: Claude, Zweck: Tests für Download, synthetischen Lastgang und Datenzugriff, geprüft von <Name R2> durch Review und absichtlich eingebaute Fehler
"""Tests für src/01_download.py, src/02_synthetisch.py und src/datenzugriff.py (Bereinigung: tests/test_cleaning.py)."""
import csv
import hashlib
import importlib.util
from pathlib import Path

import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PARAMS = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
TZ = PARAMS["markt"]["zeitzone"]
PROCESSED = ROOT / PARAMS["daten"]["pfade"]["processed"]
CLEAN = PROCESSED / "preise_clean.csv"
LAST = PROCESSED / "last_synth.csv"
MANIFEST = ROOT / PARAMS["daten"]["pfade"]["raw"] / "manifest.csv"
WECHSEL = pd.Timestamp(PARAMS["markt"]["regimewechsel"]).tz_localize(TZ)


def _lade_modul(name):
    # R2's pipeline steps live in r2/src/, shared modules in src/ (diary E-038)
    ordner = ROOT / "src" if (ROOT / "src" / f"{name}.py").exists() else ROOT / "r2" / "src"
    spec = importlib.util.spec_from_file_location(name, ordner / f"{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


dl = _lade_modul("01_download")
syn = _lade_modul("02_synthetisch")
dz = _lade_modul("datenzugriff")


def test_wochenanfaenge_bleiben_montag_mitternacht():
    b, e = dl.benoetigter_zeitraum("2025-03-20", "2025-04-10", TZ)
    assert all(w.weekday() == 0 and w.hour == 0 for w in dl.wochenanfaenge(b, e, TZ))


def test_werktage_bayern_und_variante():
    gem = _lade_modul("gemeinsam")
    tage = pd.DatetimeIndex(pd.to_datetime(["2025-01-06", "2025-06-19", "2025-08-15", "2025-10-04", "2025-10-06"])).tz_localize(TZ)
    assert list(gem.werktage(tage, mariae_himmelfahrt=False)) == [False, False, True, False, True]
    assert list(gem.werktage(tage, mariae_himmelfahrt=True)) == [False, False, False, False, True]


def test_last_taeglich_inklusive_feiertage_und_variante():
    taeglich = syn.erzeuge_last("2025-06-16", "2025-06-22", 2.0, "taeglich", 50.0)     # Fronleichnam 19.06.
    assert list(taeglich.columns) == ["datum", "mwh_gesamt", "mwh_flexibel"]
    assert list(taeglich["mwh_gesamt"]) == [50.0] * 7 and list(taeglich["mwh_flexibel"]) == [2.0] * 7
    werktags = syn.erzeuge_last("2025-06-16", "2025-06-22", 2.0, "Mo-Fr ohne Feiertage Bayern", 50.0)
    assert list(werktags["mwh_gesamt"]) == [50.0, 50.0, 50.0, 0.0, 50.0, 0.0, 0.0]


def test_last_unsinnige_parameter_werden_abgelehnt():
    # 200 MWh > 180 MWh plant; 9 h > 8-h window; 12 Uhr is production time; 05-07 Uhr runs past 06 Uhr;
    # window 20-06 Uhr overlaps production until 22 Uhr
    for feld, wert in [("mwh_pro_tag", 0), ("mwh_pro_tag", 200), ("blocklaenge_h", 9), ("produktionstage", "Mo-Sa"),
                       ("status_quo_start_h", 12), ("status_quo_start_h", 5), ("fenster_start_h", 20),
                       ("fenster_ende_h", 24), ("betrieb_ende_h", 5)]:
        with pytest.raises(syn.LastFehler):
            syn.pruefe_parameter({**PARAMS["last"], feld: wert})


def test_basisfall_reinigung_ist_gueltig():
    syn.pruefe_parameter(PARAMS["last"])                                   # must not raise
    assert syn.fensterstunden(22, 6) == [22, 23, 0, 1, 2, 3, 4, 5]


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



braucht_daten = pytest.mark.skipif(not (CLEAN.exists() and LAST.exists()), reason="Pipeline noch nicht gelaufen")


@braucht_daten
def test_last_laut_params():
    last = dz.lade_last(PARAMS)
    assert len(last) == (last["datum"].max() - last["datum"].min()).days + 1
    if PARAMS["last"]["produktionstage"] == "taeglich":
        assert (last["mwh_gesamt"] == PARAMS["last"]["gesamtverbrauch_mwh_pro_tag"]).all()
        assert (last["mwh_flexibel"] == PARAMS["last"]["mwh_pro_tag"]).all()


@braucht_daten
def test_datenzugriff_ohne_ausreisserflag():
    # flag_outlier nutzt den ganzen Monat (auch Zukunft) und darf nicht in die Planung gelangen
    assert "flag_outlier" not in dz.lade_preise(PARAMS).columns


@braucht_daten
def test_kein_look_ahead_in_allen_planungswochen():
    preise, last = dz.lade_preise(PARAMS), dz.lade_last(PARAMS)
    for periode in ("training", "test_1_stunde", "test_2_viertel", "stresstest"):
        for w in dz.planungswochen(preise, last, periode, PARAMS, historie_wochen=4):
            assert w.historie.empty or w.historie["zeit"].max() < w.bekannt_bis
            assert w.zielwoche["zeit"].min() >= w.bekannt_bis
            assert len(w.zielwoche) in (167, 168, 169) and len(w.last) == 7


@pytest.mark.skipif(not MANIFEST.exists(), reason="Download noch nicht gelaufen")
def test_rohdaten_unveraendert():
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        zeilen = [z for z in csv.DictReader(f) if z["status"] == "aktiv"]
    assert zeilen
    for z in zeilen:
        assert hashlib.sha256((MANIFEST.parent / z["datei"]).read_bytes()).hexdigest() == z["sha256"]
