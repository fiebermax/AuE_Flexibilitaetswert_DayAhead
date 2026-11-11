# KI: Claude, Zweck: Control-Grafik der Kennzahl mit Rücknahmeregel (Review Punkt H, E-057: Control bei R2), geprüft von Max (R2) durch Sichtung der Grafik und pytest
"""Control chart for the plant (Owner R2): net saving of "fixed 3 Uhr" vs 22-24 Uhr per week,
rolling over 13 weeks, target > 0, roll-back rule "below zero -> back to 22 Uhr, find the cause".

Input:  ergebnisse/kpi_rollierend.csv (look-back 2022-2026, from src/05_bewertung.py, R4)
        n8n/soll_ist_log.csv, if it exists (real weeks from the n8n workflow; columns woche, netto_ersparnis_eur)
Output: ergebnisse/control.png

No new calculation: the weekly net saving comes from R4 (look-back) or from src/soll_ist.py (real weeks);
here they are only put in time order, averaged over 13 weeks and drawn in R1's figure standard.
Run: python src/control.py [--wochen 52]
"""
import argparse
import importlib.util
import sys
from pathlib import Path

import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
from gemeinsam import ROOT, lade_params, pfad  # noqa: E402

_spec = importlib.util.spec_from_file_location("bericht", SRC / "07_bericht.py")
br = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(br)                     # figure standard of R1: colours, fonts, source line

KPI_WOCHEN = 13
GUT, KRITISCH = "#0ca30c", "#d03b3b"            # status colours, always with icon and text, never alone


def wochenreihe(kpi: pd.DataFrame, log: pd.DataFrame | None) -> pd.DataFrame:
    """One row per week (Monday): net saving in EUR, look-back first, real weeks from n8n after it."""
    w = kpi[["woche", "netto"]].assign(quelle="Rückblick")
    if log is not None and len(log):
        # n8n writes ISO weeks like 2026-W47; Monday of that week
        montag = pd.to_datetime(log["woche"].astype(str).str.replace("W", "") + "-1", format="%G-%V-%u")
        echt = pd.DataFrame({"woche": montag.dt.strftime("%Y-%m-%d"), "netto": log["netto_ersparnis_eur"], "quelle": "echt"})
        w = pd.concat([w[~w["woche"].isin(echt["woche"])], echt])
    w = w.drop_duplicates("woche", keep="last").sort_values("woche").reset_index(drop=True)
    w["rollierend_13w"] = w["netto"].rolling(KPI_WOCHEN).mean()
    return w


def status(w: pd.DataFrame) -> tuple[bool, float]:
    """Roll-back rule: True if the latest rolling 13-week mean is below zero."""
    letzter = w["rollierend_13w"].dropna().iloc[-1]
    return bool(letzter < 0), float(letzter)


def zeichne(w: pd.DataFrame, n_wochen: int, ziel: Path) -> Path:
    plt = br.plt
    br.stil()
    s = w.tail(n_wochen).copy()
    s["datum"] = pd.to_datetime(s["woche"])
    ruecknahme, wert = status(w)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(s["datum"], s["netto"], width=5, color=br.BLAU, alpha=0.35, label="Netto-Ersparnis je Woche")
    ax.plot(s["datum"], s["rollierend_13w"], color=br.BLAU, label="13-Wochen-Mittel (Kennzahl)")
    ax.axhline(0, color=br.GRAU, linewidth=1.2)
    ax.annotate("Rücknahmeregel: fällt die Kennzahl unter 0 → zurück auf 22 Uhr, Ursache klären",
                (s["datum"].iloc[0], 0), xytext=(0, -14), textcoords="offset points", fontsize=8, color=br.TEXT2)
    unten = min(0, s["netto"].min()) - 0.12 * s["netto"].max()
    ax.set_ylim(bottom=unten)
    zeichen, text, farbe = (("✕", "Rücknahme ausgelöst", KRITISCH) if ruecknahme else ("✓", "Ziel > 0 erfüllt", GUT))
    ax.text(0.99, 0.97, f"{zeichen} {text}\nKennzahl {br.de(wert)} € je Woche", transform=ax.transAxes, ha="right", va="top",
            fontsize=10, color=br.TEXT, bbox={"facecolor": "white", "edgecolor": farbe, "linewidth": 2, "boxstyle": "round,pad=0.4"})
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.set_ylabel("Netto-Ersparnis gegenüber 22–24 Uhr in € je Woche")
    echt = int((s["quelle"] == "echt").sum())
    herkunft = f"{echt} echte Wochen aus n8n" if echt else "Rückblick mit echten Preisen, noch keine echten Wochen"
    ax.set_xlabel(f"letzte {len(s)} Wochen; {herkunft}")
    # Title = key message, depends on the status (figure standard R1)
    ax.set_title("Kennzahl unter null: Reinigung zurück auf 22 Uhr, Ursache klären" if ruecknahme
                 else "Kennzahl über null: Reinigung bleibt fest um 3 Uhr (3–5 Uhr)")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    br.speichern(fig, ziel.parent, ziel.name)
    return ziel


def main() -> None:
    a = argparse.ArgumentParser(description="Control-Grafik der Kennzahl (13-Wochen-Mittel, Rücknahmeregel)")
    a.add_argument("--wochen", type=int, default=52, help="wie viele der letzten Wochen gezeigt werden")
    args = a.parse_args()
    p = lade_params()
    kpi = pd.read_csv(pfad(p, "tables") / "kpi_rollierend.csv")
    log_datei = ROOT / "n8n" / "soll_ist_log.csv"
    log = pd.read_csv(log_datei) if log_datei.exists() else None
    w = wochenreihe(kpi, log)
    ziel = zeichne(w, args.wochen, pfad(p, "tables") / "control.png")
    ruecknahme, wert = status(w)
    print(f"Control -> {ziel}; Kennzahl {wert:.0f} EUR/Woche; Rücknahme: {'ja' if ruecknahme else 'nein'}")


if __name__ == "__main__":
    main()
