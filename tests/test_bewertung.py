# KI: Claude, Zweck: Tests der Personalkosten und Bewertung (R4, Phase 4), geprüft von Caro (R4) durch Review und Nachrechnen
"""Staff cost with surcharges, net saving and C&E matrix (src/05_bewertung.py)."""
import copy
import importlib.util
from pathlib import Path

import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PARAMS = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
CLEAN = ROOT / PARAMS["daten"]["pfade"]["processed"] / "preise_clean.csv"
K = PARAMS["kosten"]

spec = importlib.util.spec_from_file_location("bewertung", ROOT / "src" / "05_bewertung.py")
bw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bw)
braucht_daten = pytest.mark.skipif(not CLEAN.exists(), reason="preise_clean.csv fehlt; zuerst python src/run_all.py")


def test_zuschlag_hoechster_und_addiert():
    h = pd.DataFrame({"stunde_lokal": [12, 23, 3, 3, 3], "wochentag": [2, 2, 5, 6, 2],
                      "feiertag": [False, False, False, True, True]})
    assert list(bw.zuschlag_je_stunde(h, K)) == [0.0, 0.25, 0.5, 1.0, 1.0]
    k = {**K, "zuschlag_regel": "addiert"}
    assert list(bw.zuschlag_je_stunde(h, k)) == [0.0, 0.25, 0.75, 1.75, 1.25]


@braucht_daten
def test_personalkosten_von_hand_freitagnacht():
    """Fri 13.06.2025: A 22-24 Uhr (Friday, night 25 %) = 3 x 35 x 2 x 1.25 = 262.50 EUR;
    D 03-05 Uhr is already Saturday (weekend 50 %) = 3 x 35 x 2 x 1.5 = 315.00 EUR."""
    preise = pd.read_csv(CLEAN)
    n = pd.DataFrame({"start_utc": ["2025-06-13T20:00:00Z", "2025-06-14T01:00:00Z"]})
    kosten = bw.personalkosten(n, preise, PARAMS)
    lohn = K["mitarbeiter"] * K["stundenlohn_eur"] * PARAMS["last"]["blocklaenge_h"]
    assert list(kosten.round(2)) == [round(lohn * (1 + K["nachtzuschlag"]), 2), round(lohn * (1 + K["wochenendzuschlag"]), 2)]


def test_netto_ist_stromersparnis_mal_faktor_minus_personal():
    zeilen = []
    for s, strom, pers in [("A", 100.0, 10.0), ("D", 80.0, 12.0)]:
        for i in range(7):
            zeilen.append({"periode": "x", "woche": "w1", "nacht": f"n{i}", "strategie": s,
                           "kosten_eur": strom, "personal_eur": pers})
    w = bw.netto_je_woche(pd.DataFrame(zeilen), PARAMS, 0.3).iloc[0]
    assert w["strom_ersparnis"] == pytest.approx(7 * 20 * 0.3)
    assert w["personal_mehr"] == pytest.approx(7 * 2)
    assert w["netto"] == pytest.approx(7 * 20 * 0.3 - 14)


def test_unvollstaendige_woche_zaehlt_nicht():
    zeilen = [{"periode": "x", "woche": "w1", "nacht": f"n{i}", "strategie": s, "kosten_eur": 1.0, "personal_eur": 1.0}
              for s in ("A", "D") for i in range(6)]
    assert bw.netto_je_woche(pd.DataFrame(zeilen), PARAMS, 1.0).empty


def test_ce_matrix_reinigung_vorn_und_gewichte_begruendet():
    m = bw.ce_matrix()
    assert m.iloc[0]["prozess"] == "GEWICHT" and m.iloc[1]["prozess"] == "Reinigung (CIP)"
    assert m["kumuliert_pct"].dropna().iloc[-1] == pytest.approx(100)
    assert all(w for _, w in bw.CE_KRITERIEN.values())                   # every weight has a reason
    assert all(v in (0, 1, 3, 9) for werte, _ in bw.CE_BEWERTUNG.values() for v in werte)
