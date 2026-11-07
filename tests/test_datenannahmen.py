# KI: Claude, Zweck: Tests der Datenannahmen und der Aufbereitungslogik erweitert, geprüft von <Name R2> durch Review und absichtlich eingebaute Fehler
"""Automatisierte Prüfungen der Datenannahmen (K5 Stufe 5). Laufen mit `pytest tests/`.

Teil 1 (immer): Logik der Aufbereitung an kleinen, von Hand nachrechenbaren Beispielen.
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
PREISE = ROOT / PARAMS["daten"]["pfade"]["processed"] / "preise_h.parquet"
PREISE_15 = ROOT / PARAMS["daten"]["pfade"]["processed"] / "preise_15min.parquet"
MANIFEST = ROOT / PARAMS["daten"]["pfade"]["raw"] / "smard" / "manifest.csv"
WECHSEL = pd.Timestamp(PARAMS["markt"]["regimewechsel"]).tz_localize(TZ)


def _lade_modul(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "src" / f"{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


auf = _lade_modul("02_aufbereitung")
syn = _lade_modul("02_synthetisch")
LAST = ROOT / PARAMS["daten"]["pfade"]["processed"] / "last_synth.parquet"
dl = _lade_modul("01_download")


# ---------------------------------------------------------------------------------------------
# Teil 1: Logik an Beispielen
# ---------------------------------------------------------------------------------------------
def _utc_reihe(start_utc, n, freq="h"):
    idx = pd.date_range(start_utc, periods=n, freq=freq, tz="UTC")
    return pd.Series(np.arange(n, dtype=float), index=idx)


def test_oktober_doppelte_stunde_wird_gemittelt():
    # 26.10.2025: 00:00 Uhr deutscher Zeit = 22:00 UTC am Vortag; 25 UTC-Stunden
    s = _utc_reihe("2025-10-25 22:00", 25)
    ort, n_doppelt = auf.zu_ortszeit(s, TZ)
    assert len(ort) == 24 and n_doppelt == 1
    zwei_uhr = ort[ort.index.hour == 2]
    assert len(zwei_uhr) == 1
    assert zwei_uhr.iloc[0] == pytest.approx((2 + 3) / 2)  # UTC-Stunden 00:00 und 01:00 -> 02:00 Uhr doppelt
    assert ort.index.is_unique and ort.index.is_monotonic_increasing


def test_oktober_mittel_bleibt_leer_wenn_ein_wert_fehlt():
    s = _utc_reihe("2025-10-25 22:00", 25)
    s.iloc[3] = np.nan
    ort, _ = auf.zu_ortszeit(s, TZ)
    assert np.isnan(ort[ort.index.hour == 2].iloc[0]), "fehlender Wert darf nicht still durch den anderen ersetzt werden"


def test_maerz_fehlende_stunde_wird_nicht_aufgefuellt():
    # 29.03.2026: 23 Stunden, 02:00 Uhr existiert nicht
    s = _utc_reihe("2026-03-28 23:00", 23)
    ort, _ = auf.zu_ortszeit(s, TZ)
    assert len(ort) == 23
    assert 2 not in set(ort.index.hour)
    raster = auf.erwartetes_raster(pd.Timestamp("2026-03-29", tz=TZ), pd.Timestamp("2026-03-30", tz=TZ), "h", TZ)
    assert len(raster) == 23


def test_viertelstunden_zu_stundenmittel():
    s = _utc_reihe("2025-10-01 00:00", 8, "15min")              # Werte 0..7
    h, n_unv = auf.viertel_zu_stunde(s)
    assert list(h) == [1.5, 5.5] and n_unv == 0


def test_unvollstaendige_stunde_bleibt_leer():
    s = _utc_reihe("2025-10-01 00:00", 8, "15min")
    s = s.drop(s.index[5])                                      # eine Viertelstunde fehlt
    h, n_unv = auf.viertel_zu_stunde(s)
    assert h.iloc[0] == 1.5 and np.isnan(h.iloc[1]) and n_unv == 1


def test_werktage_bayern_und_variante():
    tage = pd.DatetimeIndex(pd.to_datetime(["2025-01-06", "2025-06-19", "2025-08-15", "2025-10-04", "2025-10-06"])
                            ).tz_localize(TZ)
    ohne = auf.werktage(tage, mariae_himmelfahrt=False)
    mit = auf.werktage(tage, mariae_himmelfahrt=True)
    # Hl. Drei Könige, Fronleichnam: Feiertag; Samstag: kein Werktag; Montag: Werktag
    assert list(ohne) == [False, False, True, False, True]
    assert list(mit) == [False, False, False, False, True]


def test_last_beispielwoche():
    # Mo 02.06. bis So 08.06.2025; Pfingstmontag 09.06. liegt außerhalb, Do 05.06. normaler Werktag
    df = syn.erzeuge_last("2025-06-02", "2025-06-08", 2.0, mariae=False)
    assert list(df.columns) == ["datum", "mwh"]
    assert list(df["mwh"]) == [2.0, 2.0, 2.0, 2.0, 2.0, 0.0, 0.0]


def test_last_feiertag_und_variante():
    # Fr 15.08.2025 (Mariä Himmelfahrt) zählt nur in der Variante als Feiertag
    assert syn.erzeuge_last("2025-08-15", "2025-08-15", 2.0, mariae=False)["mwh"].iloc[0] == 2.0
    assert syn.erzeuge_last("2025-08-15", "2025-08-15", 2.0, mariae=True)["mwh"].iloc[0] == 0.0


def test_last_deterministisch():
    a = syn.erzeuge_last("2024-01-01", "2024-12-31", 2.0, mariae=False)
    b = syn.erzeuge_last("2024-01-01", "2024-12-31", 2.0, mariae=False)
    assert a.equals(b)


def test_last_unsinnige_parameter_werden_abgelehnt():
    gut = dict(PARAMS["last"])
    for feld, wert in [("mwh_pro_werktag", 0), ("blocklaenge_h", 25), ("werktage", "Mo-Sa")]:
        with pytest.raises(syn.LastFehler):
            syn.pruefe_parameter({**gut, feld: wert})


def test_wochenanfaenge_bleiben_montag_mitternacht():
    b, e = dl.benoetigter_zeitraum("2025-03-20", "2025-04-10", TZ)  # über die Zeitumstellung im März
    wochen = dl.wochenanfaenge(b, e, TZ)
    assert all(w.weekday() == 0 and w.hour == 0 and w.minute == 0 for w in wochen)
    assert wochen[0] <= b and wochen[-1] < e


# ---------------------------------------------------------------------------------------------
# Teil 2: Annahmen über die echten Daten (erst nach `python src/run_all.py`)
# ---------------------------------------------------------------------------------------------
braucht_daten = pytest.mark.skipif(not PREISE.exists(), reason="Pipeline noch nicht gelaufen")


@pytest.fixture(scope="module")
def preise():
    return pd.read_parquet(PREISE)


@pytest.fixture(scope="module")
def preise_15():
    return pd.read_parquet(PREISE_15)


@braucht_daten
def test_spalten_laut_schnittstelle(preise, preise_15):
    for df in (preise, preise_15):
        assert list(df.columns) == ["zeit", "preis_eur_mwh", "regime", "werktag"]
        assert str(df["zeit"].dt.tz) == TZ
        assert df["werktag"].dtype == bool


@braucht_daten
def test_keine_luecken(preise):
    assert preise["preis_eur_mwh"].notna().all(), f"Fehlende Preise:\n{preise[preise['preis_eur_mwh'].isna()].head()}"


@braucht_daten
def test_stunden_pro_tag(preise):
    # 24 Stunden; nur am letzten Sonntag im März 23 (02:00 Uhr existiert nicht).
    # Oktober: doppelte Stunde gemittelt, also ebenfalls 24.
    n = preise.groupby(preise["zeit"].dt.date).size()
    tage = pd.to_datetime(pd.Series(n.index))
    maerz_umstellung = ((tage.dt.month == 3) & (tage.dt.weekday == 6) & (tage.dt.day >= 25)).to_numpy()
    assert (n[maerz_umstellung] == 23).all()
    assert (n[~maerz_umstellung] == 24).all(), f"Unplausible Stundenzahl: {n[~maerz_umstellung][n[~maerz_umstellung] != 24]}"


@braucht_daten
def test_zeitraum_vollstaendig(preise):
    erster = pd.Timestamp(PARAMS["daten"]["aufloesungen"]["hour"]).tz_localize(TZ)
    letzter = pd.Timestamp(PARAMS["zeitraeume"]["datenstand"]).tz_localize(TZ) + pd.Timedelta(hours=23)
    assert preise["zeit"].min() == erster and preise["zeit"].max() == letzter


@braucht_daten
def test_zeit_sortiert_und_volle_stunden(preise):
    assert preise["zeit"].is_monotonic_increasing
    assert (preise["zeit"].dt.minute == 0).all()


@braucht_daten
def test_preisbereich(preise):
    # Harmonisierte Preisgrenzen der Day-Ahead-Auktion (SDAC); negative Preise sind erlaubt und bleiben drin
    assert preise["preis_eur_mwh"].between(-500, 4000).all()
    assert (preise["preis_eur_mwh"] < 0).any(), "negative Preise wurden offenbar entfernt"


@braucht_daten
def test_keine_duplikate(preise):
    assert not preise["zeit"].duplicated().any()


@braucht_daten
def test_regime_am_wechsel(preise):
    assert set(preise["regime"]) == {"stunde", "viertel"}
    assert (preise.loc[preise["zeit"] < WECHSEL, "regime"] == "stunde").all()
    assert (preise.loc[preise["zeit"] >= WECHSEL, "regime"] == "viertel").all()


@braucht_daten
def test_werktag_nie_am_wochenende(preise):
    assert not preise.loc[preise["zeit"].dt.weekday >= 5, "werktag"].any()


@braucht_daten
def test_stundenmittel_passt_zu_viertelstunden(preise, preise_15):
    # 15-min-Datei ist die Grundlage der Stundenwerte ab dem Regimewechsel: beide müssen zusammenpassen
    stunde = preise_15.assign(h=preise_15["zeit"].dt.floor("h", ambiguous=True)).groupby("h")["preis_eur_mwh"].mean()
    neu = preise[preise["zeit"] >= WECHSEL].set_index("zeit")["preis_eur_mwh"]
    assert np.allclose(neu.to_numpy(), stunde.reindex(neu.index).to_numpy())


@pytest.mark.skipif(not MANIFEST.exists(), reason="Download noch nicht gelaufen")
def test_rohdaten_unveraendert():
    # Jede aktive Rohdatei hat noch denselben SHA256 wie beim Abruf (Rohdaten werden nie überschrieben)
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        zeilen = [z for z in csv.DictReader(f) if z["status"] == "aktiv"]
    assert zeilen
    for z in zeilen:
        datei = MANIFEST.parent.parent / z["datei"]
        assert hashlib.sha256(datei.read_bytes()).hexdigest() == z["sha256"], f"verändert: {datei}"


@pytest.mark.skipif(not LAST.exists(), reason="02_synthetisch noch nicht gelaufen")
def test_last_synth_laut_schnittstelle_und_params():
    last = pd.read_parquet(LAST)
    assert list(last.columns) == ["datum", "mwh"]
    tage = pd.to_datetime(last["datum"])
    # lückenlos ein Eintrag je Kalendertag, gleicher Zeitraum wie die Preise
    assert tage.is_monotonic_increasing and not tage.duplicated().any()
    assert len(tage) == (tage.max() - tage.min()).days + 1
    assert tage.min() == pd.Timestamp(PARAMS["daten"]["aufloesungen"]["hour"])
    assert tage.max() == pd.Timestamp(PARAMS["zeitraeume"]["datenstand"])
    # nur zwei Werte: mwh_pro_werktag oder 0
    assert set(last["mwh"]) <= {PARAMS["last"]["mwh_pro_werktag"], 0.0}


@pytest.mark.skipif(not (LAST.exists() and PREISE.exists()), reason="Pipeline noch nicht gelaufen")
def test_last_und_preise_gleiche_werktage(preise):
    # Last und Preise müssen dieselbe Werktagsregel benutzen, sonst verbraucht R3 an Feiertagen Strom
    last = pd.read_parquet(LAST).set_index(pd.to_datetime(pd.read_parquet(LAST)["datum"]).dt.date)
    wt_preise = preise.groupby(preise["zeit"].dt.date)["werktag"].first()
    assert ((last["mwh"] > 0) == wt_preise.reindex(last.index)).all()


@pytest.mark.skipif(not (LAST.exists() and PREISE.exists()), reason="Pipeline noch nicht gelaufen")
def test_zeitumstellung_nur_an_lastfreien_tagen(preise):
    # Tagebuch E-018: Zeitumstellungstage (23 Stunden bzw. gemittelte 02:00) sind Sonntage ohne Last.
    # Solange das gilt, beeinflusst die Behandlung der Zeitumstellung die Kosten nicht.
    zu = pd.read_csv(ROOT / PARAMS["daten"]["pfade"]["processed"] / "zeitumstellung.csv")
    tage = pd.to_datetime(zu["datum"].unique())
    assert len(tage) > 0 and (tage.weekday == 6).all()
    last = pd.read_parquet(LAST)
    last_an_tagen = last[pd.to_datetime(last["datum"]).isin(tage)]["mwh"]
    assert (last_an_tagen == 0).all(), "Last an einem Zeitumstellungstag: Varianten V1/V2 der Sensitivität aktivieren"
