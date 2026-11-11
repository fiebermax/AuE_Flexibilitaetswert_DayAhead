# KI: Claude, Zweck: Tests der Control-Grafik (Rücknahmeregel, echte Wochen aus n8n), geprüft von Max (R2)
"""src/control.py: roll-back rule on the 13-week mean, real n8n weeks replace look-back weeks."""
import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("control", ROOT / "src" / "control.py")
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)


def _kpi(werte):
    wochen = pd.date_range("2026-01-05", periods=len(werte), freq="7D").strftime("%Y-%m-%d")
    return pd.DataFrame({"woche": wochen, "netto": werte})


def test_ruecknahme_erst_wenn_13_wochen_mittel_unter_null():
    w = ct.wochenreihe(_kpi([100.0] * 12 + [-1000.0]), None)       # one bad week: mean (1200-1000)/13 > 0
    assert ct.status(w) == (False, (1200 - 1000) / 13)
    w = ct.wochenreihe(_kpi([100.0] * 12 + [-1300.0]), None)       # mean < 0 -> roll back
    assert ct.status(w)[0] is True


def test_echte_wochen_aus_n8n_ersetzen_den_rueckblick():
    kpi = _kpi([100.0] * 13)                                          # 2026-01-05 is ISO week 2026-W02
    log = pd.DataFrame({"woche": ["2026-W02", "2026-15"], "netto_ersparnis_eur": [-50.0, 70.0]})
    w = ct.wochenreihe(kpi, log)
    assert w.loc[w["woche"] == "2026-01-05", "netto"].item() == -50.0 and len(w) == 14
    assert w.loc[w["woche"] == "2026-04-06", "quelle"].item() == "echt"   # both formats 2026-W15 / 2026-15
