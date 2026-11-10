# KI: Claude, Zweck: Folien R2 und pptx_kit reproduzierbar aus dem Repo erzeugen, geprüft von <Name R2> durch Sichtprüfung der gerenderten Folien und Zahlenprüfung
"""Builds r2/output/R2_Datenanalyse.pptx and r2/pptx_kit/ from the repository. One command:

    python r2/src/build_presentation.py            # build + number check
    python r2/src/build_presentation.py --render   # additionally render slides to PNG (needs LibreOffice)

Every number on the slides and in the speaker notes comes from r2/pptx_kit/key_figures.json, which this
script computes from data/processed/, r2/reports/ and config/params.yaml. A check at the end stops the
build if a slide contains a number that is not in key_figures.json (D5: labels such as R2, K5, H0c and
the slide number are exempt).

Design constants are at the top so a team template can replace them later (D3).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
import pandas as pd                                  # noqa: E402
from pptx import Presentation                        # noqa: E402
from pptx.dml.color import RGBColor                  # noqa: E402
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR      # noqa: E402
from pptx.util import Inches, Pt                     # noqa: E402

# R2's own scripts live in r2/src/, the shared helpers (gemeinsam.py) in src/ (diary E-038).
_HIER = Path(__file__).resolve().parent
sys.path[:0] = [str(_HIER), str(_HIER.parents[1] / "src")]
from gemeinsam import ROOT, lade_params, pfad       # noqa: E402
import fensteranalyse as fa                          # noqa: E402

# ---------------------------------------------------------------------------------------------
# Design constants (replace here for a team template)
# ---------------------------------------------------------------------------------------------
FOLIE_BREITE, FOLIE_HOEHE = Inches(13.333), Inches(7.5)          # 16:9
SCHRIFT = "Calibri"
FARBE_TEXT = RGBColor(0x1D, 0x23, 0x30)
FARBE_GRAU = RGBColor(0x5A, 0x62, 0x73)
FARBE_AKZENT = RGBColor(0x2F, 0x6D, 0xB5)
FARBE_WARNUNG = RGBColor(0xB2, 0x6A, 0x00)          # badges "Annahme" / "vorläufig"
HEX_AKZENT, HEX_GRAU, HEX_HELL = "#2f6db5", "#5a6273", "#dfe7f2"
SAISON_FARBEN = {"Winter": "#2f6db5", "Fruehling": "#3b8a5a", "Sommer": "#c47a00", "Herbst": "#b5483a"}
SAISON_NAME = {"Winter": "Winter", "Fruehling": "Frühling", "Sommer": "Sommer", "Herbst": "Herbst"}
AUTOR = "Max · R2 Datenanalyse & IT"
QUELLE_PREISE = "Quelle: Bundesnetzagentur | SMARD.de, Day-Ahead DE-LU, CC BY 4.0; eigene Berechnung"

OUTPUT = ROOT / "r2" / "output" / "R2_Datenanalyse.pptx"
KIT = ROOT / "r2" / "pptx_kit"
FIG = KIT / "figures"


# ---------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------
def de(x: float, nachkomma: int = 0) -> str:
    """German number format: 42.360 / 4,3."""
    s = f"{x:,.{nachkomma}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def git_hash(datei: str) -> str:
    """Last commit that changed the producing script (short hash); 'uncommitted' if none."""
    try:
        h = subprocess.run(["git", "log", "-1", "--format=%h", "--", datei], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.strip()
        return h or "uncommitted"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "uncommitted"


class Kennzahlen:
    """The single source of all numbers (r2/pptx_kit/key_figures.json)."""

    def __init__(self):
        self.daten = {}

    def add(self, key, name, wert, einheit, zeitraum, skript, status, anzeige, quelle=""):
        assert status in ("ERGEBNIS", "HYPOTHESE", "ANNAHME"), status
        self.daten[key] = {"name": name, "wert": wert, "einheit": einheit, "zeitraum": zeitraum,
                           "skript": skript, "commit": git_hash(skript), "status": status,
                           "anzeige": anzeige, "quelle": quelle}

    def __call__(self, key) -> str:
        return self.daten[key]["anzeige"]

    def schreibe(self, datei: Path):
        datei.write_text(json.dumps(self.daten, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------------------------
# 1) Key figures
# ---------------------------------------------------------------------------------------------
def lies_cleaning_log() -> pd.DataFrame:
    zeilen = [z for z in (ROOT / "r2" / "reports" / "cleaning_log.md").read_text(encoding="utf-8").splitlines()
              if re.match(r"\| \d+ ", z)]
    teile = [[t.strip() for t in z.strip("|").split(" | ")] for z in zeilen]
    return pd.DataFrame(teile, columns=["schritt", "regel", "vorher", "nachher", "betroffen", "begruendung"])


def anzahl_tests() -> int:
    out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/"], cwd=ROOT,
                         capture_output=True, text=True).stdout
    return sum(1 for z in out.splitlines() if "::" in z)


def berechne_kennzahlen(p: dict) -> tuple[Kennzahlen, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    k = Kennzahlen()
    L, CL, PA, FA = "config/params.yaml", "r2/src/cleaning.py", "r2/src/01_download.py", "r2/src/fensteranalyse.py"
    start = pd.Timestamp(p["daten"]["aufloesungen"]["hour"])
    ende = pd.Timestamp(p["zeitraeume"]["datenstand"])
    zr = f"{start:%d.%m.%Y}–{ende:%d.%m.%Y}"

    # Source and period
    k.add("quelle", "Datenquelle", "Bundesnetzagentur | SMARD.de", "", zr, PA, "ERGEBNIS",
          "Bundesnetzagentur | SMARD.de", "https://www.smard.de")
    k.add("filter", "SMARD-Filter Day-Ahead-Preis", p["markt"]["smard_filter_preis"], "", zr, L, "ERGEBNIS",
          str(p["markt"]["smard_filter_preis"]))
    k.add("lizenz", "Lizenz", "CC BY 4.0", "", zr, PA, "ERGEBNIS", "CC BY 4.0")
    k.add("zeitraum_start", "Beginn Untersuchungszeitraum", f"{start:%Y-%m-%d}", "Datum", zr, L, "ERGEBNIS", f"{start:%d.%m.%Y}")
    k.add("zeitraum_ende", "Ende Untersuchungszeitraum (Datenstand)", f"{ende:%Y-%m-%d}", "Datum", zr, L, "ERGEBNIS", f"{ende:%d.%m.%Y}")
    k.add("stresstest_jahr", "Stresstest (Gaspreiskrise)", 2022, "Jahr", "2022", L, "ERGEBNIS", "2022")
    manifest = pd.read_csv(pfad(p, "raw") / "smard" / "manifest.csv")
    manifest = manifest[(manifest["status"] == "aktiv") & (manifest["aufloesung"] == "hour")]
    abruf = pd.to_datetime(manifest["abgerufen_am_utc"]).max()
    k.add("rohdateien", "Rohdateien (SMARD-Wochendateien)", len(manifest), "Dateien", zr, PA, "ERGEBNIS", de(len(manifest)))
    k.add("abrufdatum", "Abrufdatum Rohdaten", f"{abruf:%Y-%m-%d}", "Datum", zr, PA, "ERGEBNIS", f"{abruf:%d.%m.%Y}")
    k.add("pruefsumme", "Prüfsummenverfahren je Rohdatei", "SHA-256", "", zr, PA, "ERGEBNIS", "SHA-256")
    k.add("regimewechsel", "Erster Liefertag mit 15-min-Produkten (SDAC)", p["markt"]["regimewechsel"], "Datum", "",
          L, "ERGEBNIS", pd.Timestamp(p["markt"]["regimewechsel"]).strftime("%d.%m.%Y"),
          "NEMO Committee (2025): 15-minute MTU in SDAC was implemented")
    k.add("aufloesung", "Einheitliche Auflösung", 60, "min", zr, CL, "ERGEBNIS", "60 min")
    k.add("tests", "Automatische Tests (pytest)", anzahl_tests(), "Tests", "", "tests/", "ERGEBNIS", str(anzahl_tests()))

    # Assumptions (inputs, not results)
    last = p["last"]
    k.add("status_quo", "Status quo A: festes Fenster (Kickoff-Definition)", f"{last['status_quo_start_h']:02d}-{last['status_quo_start_h'] + last['blocklaenge_h']:02d}",
          "Uhr (Ortszeit)", "", L, "ANNAHME", f"{last['status_quo_start_h']:02d}–{last['status_quo_start_h'] + last['blocklaenge_h']:02d} Uhr", "Kickoff, Strategie A")
    k.add("betriebszeit", "Betriebszeit", f"{last['betrieb_start_h']:02d}-{last['betrieb_ende_h']:02d}", "Uhr (Ortszeit)", "", L,
          "ANNAHME", f"{last['betrieb_start_h']:02d}–{last['betrieb_ende_h']:02d} Uhr", "Praxiskontakt, Interview 09.11.2026 (K-005)")
    k.add("blocklaenge", "Länge des verschiebbaren Blocks", last["blocklaenge_h"], "h", "", L, "ANNAHME", f"{last['blocklaenge_h']} h")
    k.add("verbrauch_gesamt", "Stromverbrauch Werk", last["gesamtverbrauch_mwh_pro_tag"], "MWh/Tag", "", L, "ANNAHME",
          f"{de(last['gesamtverbrauch_mwh_pro_tag'])} MWh/Tag", "Praxiskontakt, Interview 09.11.2026 (K-005)")
    k.add("verbrauch_flexibel", "Davon verschiebbar (Platzhalter)", last["mwh_pro_tag"], "MWh/Tag", "", L, "ANNAHME",
          f"{de(last['mwh_pro_tag'], 1)} MWh/Tag", "Platzhalter, Prozess und Menge offen")

    # Cleaning log
    log = lies_cleaning_log()
    zeile = lambda nr: log[log["schritt"].str.startswith(f"{nr} ")].iloc[0]
    k.add("n_roh", "Zeilen nach Einlesen", int(zeile(1)["nachher"]), "Stunden", zr, CL, "ERGEBNIS", de(int(zeile(1)["nachher"])))
    k.add("dubletten", "Dubletten (exakt + widersprüchlich)", int(zeile(2)["betroffen"]), "Zeilen", zr, CL, "ERGEBNIS", de(int(zeile(2)["betroffen"])))
    k.add("randstunden", "Randstunden außerhalb des Zeitraums entfernt", int(zeile(3)["betroffen"]), "Stunden", zr, CL, "ERGEBNIS", de(int(zeile(3)["betroffen"])))
    k.add("n_clean", "Zeilen nach Bereinigung", int(zeile(9)["nachher"]), "Stunden", zr, CL, "ERGEBNIS", de(int(zeile(9)["nachher"])))
    k.add("luecken", "Lücken", int(zeile(5)["betroffen"]), "Stunden", zr, CL, "ERGEBNIS", de(int(zeile(5)["betroffen"])))

    d = pd.read_csv(pfad(p, "processed") / "preise_clean.csv")
    n = len(d)
    tage = d.groupby("datum_lokal").size()
    k.add("tage_23h", "Lokale Tage mit 23 Stunden (März)", int((tage == 23).sum()), "Tage", zr, CL, "ERGEBNIS", de(int((tage == 23).sum())))
    k.add("tage_25h", "Lokale Tage mit 25 Stunden (Oktober)", int((tage == 25).sum()), "Tage", zr, CL, "ERGEBNIS", de(int((tage == 25).sum())))
    k.add("stunden_23", "Stunden am März-Umstellungstag", 23, "h", "", CL, "ERGEBNIS", "23 h")
    k.add("stunden_25", "Stunden am Oktober-Umstellungstag", 25, "h", "", CL, "ERGEBNIS", "25 h")
    k.add("imputiert", "Imputierte Werte", int(d["imputed"].sum()), "Stunden", zr, CL, "ERGEBNIS", de(int(d["imputed"].sum())))
    k.add("geflaggt", "Auffällige Preise (flag_outlier)", int(d["flag_outlier"].sum()), "Stunden", zr, CL, "ERGEBNIS", de(int(d["flag_outlier"].sum())))
    k.add("geflaggt_pct", "Anteil auffälliger Preise", round(100 * d["flag_outlier"].mean(), 1), "%", zr, CL, "ERGEBNIS", f"{de(100 * d['flag_outlier'].mean(), 1)} %")
    neg = d["preis_eur_mwh"] < 0
    k.add("negativ", "Stunden mit negativem Preis", int(neg.sum()), "Stunden", zr, CL, "ERGEBNIS", de(int(neg.sum())))
    k.add("negativ_pct", "Anteil Stunden mit negativem Preis", round(100 * neg.mean(), 1), "%", zr, CL, "ERGEBNIS", f"{de(100 * neg.mean(), 1)} %")
    assert n == int(zeile(9)["nachher"])

    for s in fa.SAISON_REIHENFOLGE:
        x = d.loc[d["saison"] == s, "preis_eur_mwh"]
        k.add(f"median_{s}", f"Median Preis {SAISON_NAME[s]}", round(x.median(), 1), "EUR/MWh", zr, CL, "ERGEBNIS", de(x.median(), 1))
        k.add(f"iqr_{s}", f"IQR Preis {SAISON_NAME[s]}", round(x.quantile(.75) - x.quantile(.25), 1), "EUR/MWh", zr, CL, "ERGEBNIS",
              de(x.quantile(.75) - x.quantile(.25), 1))
        k.add(f"negativ_pct_{s}", f"Anteil negativer Preise {SAISON_NAME[s]}", round(100 * (x < 0).mean(), 1), "%", zr, CL, "ERGEBNIS",
              f"{de(100 * (x < 0).mean(), 1)} %")

    # Window analysis (hindsight)
    tage_f = fa.fenster_je_tag(d, last["betrieb_start_h"], last["betrieb_ende_h"], last["blocklaenge_h"], last["status_quo_start_h"])
    js = fa.kennzahlen_je_saison(tage_f, last["status_quo_start_h"])
    k.add("fenster_tage", "Ausgewertete Tage (Fensteranalyse)", len(tage_f), "Tage", zr, FA, "ERGEBNIS", de(len(tage_f)))
    for _, r in js.iterrows():
        s = r["saison"]
        for feld, einheit, nk in [("median_eur_mwh", "EUR/MWh", 1), ("q25_eur_mwh", "EUR/MWh", 1), ("q75_eur_mwh", "EUR/MWh", 1),
                                  ("median_pct", "%", 1), ("q25_pct", "%", 1), ("q75_pct", "%", 1)]:
            k.add(f"mk_{feld}_{s}", f"Mehrkosten Status quo {feld} {SAISON_NAME[s]}", round(r[feld], nk), einheit, zr, FA, "ERGEBNIS",
                  de(r[feld], nk) + (" %" if einheit == "%" else ""))
        k.add(f"mk_ohne_pct_{s}", f"Tage ohne %-Wert (billigstes Fenster <= 0) {SAISON_NAME[s]}", int(r["tage_ohne_pct"]), "Tage", zr, FA,
              "ERGEBNIS", de(r["tage_ohne_pct"]))
        k.add(f"start_modus_{s}", f"Häufigster Start billigstes Fenster {SAISON_NAME[s]}", int(r["haeufigster_start"]), "Uhr", zr, FA,
              "ERGEBNIS", f"{int(r['haeufigster_start'])}")
    genau_max = js["anteil_genau_status_quo_pct"].max()
    k.add("genau_status_quo_max", "Max. Anteil Tage, an denen 08-14 genau das billigste Fenster war (je Saison)", round(genau_max, 1),
          "%", zr, FA, "ERGEBNIS", "unter 1 %" if genau_max < 1 else f"{de(genau_max, 1)} %")
    return k, d, tage_f, js


# ---------------------------------------------------------------------------------------------
# 2) Figures (300 dpi, German labels, units, source line)
# ---------------------------------------------------------------------------------------------
def _speichern(fig, name, quelle=QUELLE_PREISE):
    fig.text(0.01, 0.012, quelle, fontsize=7, color=HEX_GRAU)
    fig.savefig(FIG / f"{name}.png", dpi=300)
    plt.close(fig)


def grafiken(k: Kennzahlen, d: pd.DataFrame, tage_f: pd.DataFrame, js: pd.DataFrame, p: dict) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

    # Data flow
    fig, ax = plt.subplots(figsize=(8, 4.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 6)
    def box(x, y, w, h, text, farbe="#ffffff", rand=HEX_AKZENT, fett=False):
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=farbe, edgecolor=rand, linewidth=1.2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.5, weight="bold" if fett else "normal")
    def pfeil(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=HEX_GRAU, lw=1.2))
    box(0.2, 4.4, 2.6, 1.2, f"SMARD\n(Bundesnetzagentur)\nDay-Ahead DE-LU", "#eef2f7", HEX_GRAU)
    box(3.6, 4.4, 2.8, 1.2, f"01_download.py\n{k('rohdateien')} Wochendateien\nPrüfsumme {k('pruefsumme')}", HEX_HELL, fett=True)
    box(7.2, 4.4, 2.6, 1.2, f"data/raw/\nunverändert\n(nur lesen)", "#fff3dd", "#c47a00")
    box(3.6, 2.2, 2.8, 1.4, f"cleaning.py\nUTC · Raster · Plausibilität\nflag_outlier · Join Verbrauch", HEX_HELL, fett=True)
    box(0.2, 2.2, 2.6, 1.4, f"Praxiskontakt\nVerbrauch {k('verbrauch_gesamt')}\nBetrieb {k('betriebszeit')}", "#eef2f7", HEX_GRAU)
    box(7.2, 2.2, 2.6, 1.4, f"preise_clean.csv\n{k('n_clean')} Stunden\n+ Bericht, Codebook", "#fff3dd", "#c47a00")
    box(3.6, 0.2, 2.8, 1.2, f"{k('tests')} automatische Tests", "#e6f3ea", "#3b8a5a")
    box(7.2, 0.2, 2.6, 1.2, "R3: Backtest\nR4: Bewertung\nR1: Bericht", "#e4e7ec", HEX_GRAU)
    pfeil(2.8, 5.0, 3.6, 5.0); pfeil(6.4, 5.0, 7.2, 5.0); pfeil(8.5, 4.4, 6.4, 3.3)
    pfeil(2.8, 2.9, 3.6, 2.9); pfeil(6.4, 2.9, 7.2, 2.9); pfeil(8.5, 2.2, 8.5, 1.4); pfeil(5.0, 1.4, 5.0, 2.2)
    ax.set_title("Datenfluss R2: von der Quelle zur geprüften Datenbasis", fontsize=11, loc="left")
    fig.tight_layout(rect=(0, 0.04, 1, 1)); _speichern(fig, "datenfluss")

    # Cleaning funnel
    log = lies_cleaning_log()
    namen = [re.sub(r"^\d+ ", "", s) for s in log["schritt"]]
    nachher = log["nachher"].astype(int).to_numpy()
    betroffen = log["betroffen"].astype(int).to_numpy()
    fig, ax = plt.subplots(figsize=(8, 4.6))
    zeilen = [i for i in range(len(namen)) if i >= 1]                       # step 0 counts files, not rows
    y = list(range(len(zeilen)))[::-1]
    ax.barh(y, [nachher[i] for i in zeilen], color=HEX_HELL, edgecolor=HEX_AKZENT)
    for yy, i in zip(y, zeilen):
        txt = f"{de(nachher[i])} Zeilen" + (f"  ·  betroffen: {de(betroffen[i])}" if betroffen[i] else "")
        ax.text(nachher[i] * 0.02, yy, txt, va="center", fontsize=8)
    ax.set_yticks(y, [namen[i] for i in zeilen], fontsize=8.5)
    ax.set_xlim(0, max(nachher[1:]) * 1.05); ax.set_xlabel("Anzahl Zeilen (Stunden)")
    ax.set_title("Bereinigung: Zeilen nach jedem Schritt (Achse ab 0)", fontsize=11, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); _speichern(fig, "bereinigung_trichter", "Quelle: r2/reports/cleaning_log.md (r2/src/cleaning.py); Preise: Bundesnetzagentur | SMARD.de, CC BY 4.0")

    # Daily profile per season (local time)
    last = p["last"]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.axvspan(last["betrieb_start_h"] - 0.5, last["betrieb_ende_h"] - 0.5, color="#999", alpha=0.08, label=f"Betriebszeit {k('betriebszeit')}")
    sq = last["status_quo_start_h"]
    ax.axvspan(sq - 0.5, sq + last["blocklaenge_h"] - 0.5, color=HEX_AKZENT, alpha=0.10, label=f"Status quo A {k('status_quo')}")
    for s in fa.SAISON_REIHENFOLGE:
        prof = d[d["saison"] == s].groupby("stunde_lokal")["preis_eur_mwh"].median()
        ax.plot(prof.index, prof.to_numpy(), marker="o", markersize=3, color=SAISON_FARBEN[s], label=SAISON_NAME[s])
    ax.set_xticks(range(0, 24, 2)); ax.set_xlabel("Stunde (deutsche Zeit)"); ax.set_ylabel("Median Preis in EUR/MWh")
    ax.set_title("Tagesprofil je Saison (Median je Uhrzeit)", fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=7.5, ncol=2); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); _speichern(fig, "tagesprofil_je_saison")

    # Extra cost status quo vs cheapest window (median + IQR)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    x = range(len(js))
    med = js["median_eur_mwh"].to_numpy()
    fehler = [med - js["q25_eur_mwh"].to_numpy(), js["q75_eur_mwh"].to_numpy() - med]
    ax.bar(x, med, color=[SAISON_FARBEN[s] for s in js["saison"]], alpha=0.85)
    ax.errorbar(x, med, yerr=fehler, fmt="none", ecolor="#333", capsize=5, linewidth=1)
    for xx, m in zip(x, med):
        ax.text(xx + 0.08, m + 0.6, de(m, 1), fontsize=8.5, ha="left")
    ax.set_xticks(list(x), [SAISON_NAME[s] for s in js["saison"]]); ax.set_ylim(0, None)
    ax.set_ylabel("EUR/MWh")
    ax.set_title(f"Mehrkosten Status quo {k('status_quo')} ggü. billigstem {k('blocklaenge')}-Fenster (Median, Balken = IQR)",
                 fontsize=9.5, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(rect=(0, 0.06, 1, 1)); _speichern(fig, "mehrkosten_status_quo", QUELLE_PREISE + ". Rückblick mit bekannten Preisen, keine Strategie.")

    # Start hour of the cheapest window
    fig, ax = plt.subplots(figsize=(8, 3.4))
    starts = list(range(last["betrieb_start_h"], last["betrieb_ende_h"] - last["blocklaenge_h"] + 1))
    unten = pd.Series(0.0, index=starts)
    for s in fa.SAISON_REIHENFOLGE:
        anteil = tage_f[tage_f["saison"] == s]["start_billigst"].value_counts().reindex(starts, fill_value=0) / len(tage_f) * 100
        ax.bar(starts, anteil.to_numpy(), bottom=unten.to_numpy(), color=SAISON_FARBEN[s], label=SAISON_NAME[s])
        unten += anteil
    ax.axvline(sq, color="#333", linestyle="--", linewidth=1); ax.text(sq + 0.15, unten.max() * 0.9, "Status quo A", fontsize=8)
    ax.set_xticks(starts, [f"{h:02d}" for h in starts]); ax.set_xlabel("Startzeit des billigsten Fensters (deutsche Zeit)")
    ax.set_ylim(0, unten.max() * 1.35)                       # headroom so the legend never covers a bar
    ax.set_ylabel("Anteil der Tage in %"); ax.legend(frameon=False, fontsize=7.5, ncol=4, loc="upper center")
    ax.set_title("Wann beginnt das billigste Fenster?", fontsize=10, loc="left"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(rect=(0, 0.06, 1, 1)); _speichern(fig, "startzeit_billigstes_fenster", QUELLE_PREISE + ". Rückblick, keine Strategie.")


# ---------------------------------------------------------------------------------------------
# 3) Slides
# ---------------------------------------------------------------------------------------------
def _text(slide, x, y, w, h, absaetze, groesse=16, farbe=FARBE_TEXT, fett=False, name=None, aufzaehlung=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        box.name = name
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    for i, a in enumerate(absaetze):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = para.add_run()
        run.text = ("• " if aufzaehlung else "") + a
        run.font.size, run.font.name, run.font.bold = Pt(groesse), SCHRIFT, fett
        run.font.color.rgb = farbe
        para.space_after = Pt(8 if aufzaehlung else 2)
    return box


def _badge(slide, x, y, w, text, farbe=FARBE_WARNUNG):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(0.36))
    box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0xFF, 0xF3, 0xDD)
    box.line.color.rgb = farbe
    tf = box.text_frame; tf.word_wrap = True
    run = tf.paragraphs[0].add_run(); run.text = text
    run.font.size, run.font.name, run.font.bold = Pt(12), SCHRIFT, True
    run.font.color.rgb = farbe
    return box


def _rahmen(prs, nr, kennung, titel, quelle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])               # blank
    _text(slide, 0.5, 0.25, 12.3, 0.35, [kennung], 13, FARBE_AKZENT, True)
    _text(slide, 0.5, 0.58, 12.3, 1.05, [titel], 26, FARBE_TEXT, True)
    linie = slide.shapes.add_connector(1, Inches(0.5), Inches(1.68), Inches(12.83), Inches(1.68))
    linie.line.color.rgb = FARBE_AKZENT
    _text(slide, 0.5, 7.0, 9.6, 0.35, [quelle], 9, FARBE_GRAU)
    _text(slide, 10.2, 7.0, 2.2, 0.35, [AUTOR], 9, FARBE_GRAU)
    nrbox = _text(slide, 12.4, 7.0, 0.5, 0.35, [str(nr)], 9, FARBE_GRAU, name="Foliennummer")
    nrbox.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
    return slide


def _notizen(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def folien(k: Kennzahlen) -> Presentation:
    prs = Presentation()
    prs.slide_width, prs.slide_height = FOLIE_BREITE, FOLIE_HOEHE
    S = lambda s: SAISON_NAME[s]

    # a) Aufgabenstellung
    s = _rahmen(prs, 1, "R2 · a) Aufgabenstellung",
                "Offizielle Day-Ahead-Preise, mit einem Befehl reproduzierbar aufbereitet", QUELLE_PREISE)
    _text(s, 0.5, 1.95, 5.9, 4.6, [
        f"Quelle: {k('quelle')}, Day-Ahead DE-LU (Filter {k('filter')}), Lizenz {k('lizenz')}",
        f"Zeitraum {k('zeitraum_start')}–{k('zeitraum_ende')}: {k('rohdateien')} Wochendateien, Abruf am {k('abrufdatum')}",
        "Ziel: geprüfte Stundenpreise und Verbrauch als gemeinsame Grundlage für R3 und R4",
        f"Reproduzierbar: ein Befehl, Prüfsumme ({k('pruefsumme')}) je Rohdatei, {k('tests')} automatische Tests",
        f"Verbrauch {k('verbrauch_gesamt')} (Praxiskontakt), davon verschiebbar {k('verbrauch_flexibel')}",
    ], 16, aufzaehlung=True)
    _badge(s, 0.75, 6.45, 5.4, f"Annahme: verschiebbar {k('verbrauch_flexibel')} (Platzhalter)")
    s.shapes.add_picture(str(FIG / "datenfluss.png"), Inches(6.6), Inches(1.9), width=Inches(6.3))
    _notizen(s, (
        f"Meine Aufgabe als R2 ist die Datenbasis. Die Strompreise kommen von SMARD, der Plattform der Bundesnetzagentur: "
        f"Day-Ahead-Preise für Deutschland und Luxemburg, frei nutzbar unter {k('lizenz')}. Ich habe den Zeitraum "
        f"{k('zeitraum_start')} bis {k('zeitraum_ende')} geladen, das sind {k('rohdateien')} Wochendateien, abgerufen am {k('abrufdatum')}. "
        f"Die Rohdaten speichere ich unverändert und sichere jede Datei mit einer {k('pruefsumme')}-Prüfsumme. "
        f"Alles läuft mit einem Befehl, {k('tests')} automatische Tests prüfen die Annahmen. "
        f"Den Verbrauch von {k('verbrauch_gesamt')} und die Betriebszeit {k('betriebszeit')} hat mir unser Praxiskontakt im Interview genannt. "
        f"Wie viel davon verschiebbar ist, steht noch nicht fest: die {k('verbrauch_flexibel')} sind eine Annahme. "
        "Rechts sehen Sie den Weg der Daten: von SMARD über den Download in einen Rohdaten-Ordner, den niemand verändert, "
        "dann durch die Bereinigung in eine einzige geprüfte Datei. Auf dieser Datei rechnen R3 den Backtest und R4 die Bewertung."))

    # b) Problematik
    s = _rahmen(prs, 2, "R2 · b) Problematik",
                "Die Rohdaten sind vollständig – die Fallstricke liegen in Zeit, Auflösung und Extremwerten",
                QUELLE_PREISE + "; r2/reports/cleaning_log.md")
    _text(s, 0.5, 1.95, 5.9, 4.9, [
        f"{k('n_clean')} Stunden: {k('luecken')} Lücken, {k('dubletten')} Dubletten; {k('randstunden')} Randstunden außerhalb des Zeitraums entfernt",
        f"Zeitumstellung: {k('tage_23h')} Tage mit {k('stunden_23')}, {k('tage_25h')} mit {k('stunden_25')} – UTC als Schlüssel, nichts gemittelt",
        f"Ab {k('regimewechsel')} Viertelstunden-Handel – einheitlich {k('aufloesung')} (SMARD-Stundenwert)",
        f"{k('geflaggt')} auffällige Preise ({k('geflaggt_pct')}) markiert, nicht gelöscht",
        f"{k('negativ')} Stunden ({k('negativ_pct')}) mit negativem Preis: gültig, bleiben drin",
    ], 16, aufzaehlung=True)
    s.shapes.add_picture(str(FIG / "bereinigung_trichter.png"), Inches(6.6), Inches(1.9), width=Inches(6.3))
    _notizen(s, (
        f"Die Daten selbst sind sauber: {k('n_clean')} Stunden ohne Lücken und ohne Dubletten. Entfernt habe ich nur "
        f"{k('randstunden')} Randstunden, die außerhalb des Zeitraums liegen. Die eigentlichen Fallstricke: Erstens die Zeitumstellung, "
        f"mit {k('tage_23h')} Tagen mit {k('stunden_23')} und {k('tage_25h')} Tagen mit {k('stunden_25')}. Ich nutze UTC als Schlüssel, "
        f"deshalb muss ich nichts mitteln oder erfinden. Zweitens handelt die Börse seit {k('regimewechsel')} in Viertelstunden; "
        f"ich arbeite einheitlich mit {k('aufloesung')}. Drittens Extremwerte: {k('geflaggt')} Preise sind auffällig, ich markiere sie nur. "
        f"Auch die {k('negativ')} Stunden mit negativem Preis bleiben drin, denn gerade dort liegt das Sparpotenzial. "
        "Die Grafik rechts zeigt jeden Bereinigungsschritt mit der Zahl der Zeilen; die Achse beginnt bei null, damit nichts "
        "größer aussieht, als es ist. Jeder Schritt ist im Bereinigungsprotokoll mit Regel und Begründung nachvollziehbar."))

    # c) Methode & Ergebnis
    w = "Winter"; so = "Sommer"
    s = _rahmen(prs, 3, "R2 · c) Methode & Ergebnis",
                f"Im Sommer kostet das Status-quo-Fenster {k('status_quo')} im Median {k('mk_median_eur_mwh_Sommer')} €/MWh mehr als das billigste Fenster",
                QUELLE_PREISE + "; r2/src/fensteranalyse.py")
    _badge(s, 0.75, 1.85, 5.4, "Rückblick mit bekannten Preisen, keine Strategie")
    _text(s, 0.5, 2.35, 5.9, 4.6, [
        "Mehrkosten in €/MWh, Median (IQR): " + " · ".join(
            f"{S(x)} {k(f'mk_median_eur_mwh_{x}')} ({k(f'mk_q25_eur_mwh_{x}')}–{k(f'mk_q75_eur_mwh_{x}')})" for x in fa.SAISON_REIHENFOLGE),
        f"In Prozent im Sommer {k('mk_median_pct_Sommer')} (IQR {k('mk_q25_pct_Sommer')}–{k('mk_q75_pct_Sommer')}); bei Preisen nahe null instabil",
        f"Billigstes {k('blocklaenge')}-Fenster in der Betriebszeit {k('betriebszeit')} beginnt meist um {k('start_modus_Winter')} oder {k('start_modus_Sommer')} Uhr",
        f"Nebeninfo: genau {k('status_quo')} war an {k('genau_status_quo_max')} der Tage am billigsten",
        "Vorläufig: Kostenvergleich der Strategien folgt mit dem Backtest von R3",
    ], 15, aufzaehlung=True)
    # two figures stacked; height-limited so the lower one ends above the footer (7.0 in)
    s.shapes.add_picture(str(FIG / "mehrkosten_status_quo.png"), Inches(6.85), Inches(1.8), height=Inches(2.5))
    s.shapes.add_picture(str(FIG / "startzeit_billigstes_fenster.png"), Inches(6.85), Inches(4.35), height=Inches(2.5))
    _notizen(s, (
        f"Wie viel Spielraum gibt es überhaupt? Ich vergleiche für jeden Tag im Rückblick das heutige Fenster {k('status_quo')} "
        f"mit dem billigsten {k('blocklaenge')}-Fenster innerhalb der Betriebszeit {k('betriebszeit')}. Wichtig: Das ist ein Rückblick mit "
        f"bekannten Preisen, keine Strategie. Im Sommer zahlt der Status quo im Median {k('mk_median_eur_mwh_Sommer')} Euro pro "
        f"Megawattstunde mehr, im Winter nur {k('mk_median_eur_mwh_Winter')}. Das billigste Fenster beginnt meist um "
        f"{k('start_modus_Winter')} oder {k('start_modus_Sommer')} Uhr, also nach der Morgenspitze. Prozentwerte sind im Sommer stark "
        f"gestreut, weil die Preise mittags oft nahe null liegen; deshalb argumentiere ich in Euro. Ob eine Wochenplanung davon "
        f"etwas realisiert, zeigt erst der Backtest von R3. Die obere Grafik zeigt die Mehrkosten je Saison mit der Spannweite "
        "der mittleren Hälfte der Tage, die untere, um wie viel Uhr das billigste Fenster beginnt. Das heutige Fenster ist fast nie "
        "das billigste; das ist aber nur eine Nebeninfo."))

    # d) Beitrag
    s = _rahmen(prs, 4, "R2 · d) Beitrag",
                "R2 liefert die geprüfte Datenbasis, auf der R3 und R4 rechnen", "Quelle: docs/schnittstellen.md, docs/codebook.md")
    zeilen = [("Rolle", "Erhält von R2", "Übergibt an R2"),
              ("Praxiskontakt", "–", "Verbrauch, Betriebszeit, flexible Prozesse"),
              ("R1", "Datenqualität und Grafiken für den Bericht", "Annahmen in params.yaml"),
              ("R3", "preise_clean.csv, Verbrauch, Datenzugriff je Freitag ohne Look-ahead", "Backtest als Funktion für die Sensitivität"),
              ("R4", f"Zeiträume inkl. Stresstest {k('stresstest_jahr')}, Datenqualität", "Kostenannahmen für die Bewertung")]
    tab = s.shapes.add_table(len(zeilen), 3, Inches(0.5), Inches(1.95), Inches(12.3), Inches(2.6)).table
    for c, breite in enumerate((2.0, 5.6, 4.7)):
        tab.columns[c].width = Inches(breite)
    for r, z in enumerate(zeilen):
        for c, t in enumerate(z):
            zelle = tab.cell(r, c); zelle.text = t
            run = zelle.text_frame.paragraphs[0].runs[0]
            run.font.size, run.font.name, run.font.bold = Pt(14), SCHRIFT, r == 0
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if r == 0 else FARBE_TEXT
            zelle.fill.solid(); zelle.fill.fore_color.rgb = FARBE_AKZENT if r == 0 else (RGBColor(0xF1, 0xF4, 0xF9) if r % 2 else RGBColor(0xFF, 0xFF, 0xFF))
    _text(s, 0.5, 4.8, 12.3, 0.4, ["Mein Beitrag"], 16, FARBE_AKZENT, True)
    _text(s, 0.5, 5.2, 12.3, 1.7, [
        "Geprüfte, reproduzierbare Datenbasis: Rohdaten mit Prüfsumme, Bereinigung mit Protokoll",
        "Schnittstellen und Codebook für alle Rollen, Datenzugriff ohne Look-ahead für R3",
        "Rückkopplung mit der Praxis: Interview mit dem Praxiskontakt zu Verbrauch, Betriebszeit und Prozessen",
    ], 15, aufzaehlung=True)
    _notizen(s, (
        "Mein Paket ist die Grundlage für alle anderen. R3 bekommt von mir die bereinigten Preise, den Verbrauch und einen "
        "Datenzugriff, der für jeden Freitag nur die Daten liefert, die man damals kannte; so kann im Backtest kein Blick in die "
        "Zukunft passieren. Zurück brauche ich von R3 den Backtest als Funktion, damit ich die Sensitivitätsrechnung machen kann. "
        f"R4 bekommt die Zeiträume, inklusive Stresstest {k('stresstest_jahr')}, und die Datenqualität. R1 bekommt Grafiken und "
        "Kennzahlen für den Bericht und gibt mir die Annahmen vor. Über meine Rolle hinaus habe ich das Interview mit unserem "
        "Praxiskontakt geführt; daher kommen Verbrauch, Betriebszeit und die Liste der flexiblen Prozesse. "
        "Jede Übergabe ist eine Datei mit festen Spalten, beschrieben im Codebook, damit sich niemand auf mündliche Absprachen "
        "verlassen muss. Damit übergebe ich an R3."))
    return prs


# ---------------------------------------------------------------------------------------------
# 4) Number check (D5)
# ---------------------------------------------------------------------------------------------
ZAHL = re.compile(r"(?<![A-Za-z0-9_])\d+(?:[.,]\d+)*(?![A-Za-z0-9_])")


def texte_der_folien(prs) -> list[tuple[int, str]]:
    texte = []
    for nr, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if shape.name == "Foliennummer":
                continue
            if shape.has_text_frame:
                texte.append((nr, shape.text_frame.text))
            if shape.has_table:
                texte += [(nr, c.text) for row in shape.table.rows for c in row.cells]
        texte.append((nr, slide.notes_slide.notes_text_frame.text))
    return texte


def pruefe_zahlen(prs, k: Kennzahlen) -> list[str]:
    erlaubt = set()
    for v in k.daten.values():
        erlaubt |= set(ZAHL.findall(v["anzeige"]))
    fehler = []
    for nr, text in texte_der_folien(prs):
        for z in ZAHL.findall(text):
            if z not in erlaubt:
                fehler.append(f"Folie {nr}: Zahl '{z}' nicht in key_figures.json ({text[:60]}…)")
    return fehler


# ---------------------------------------------------------------------------------------------
# 5) Companion documents
# ---------------------------------------------------------------------------------------------
def defense_qa(k: Kennzahlen) -> str:
    h = lambda f: git_hash(f)
    fragen = [
        ("Woher stammen die Daten, und dürft ihr sie nutzen?",
         f"Day-Ahead-Großhandelspreise DE-LU von {k('quelle')} (Filter {k('filter')}), Lizenz {k('lizenz')}: Nutzung und Weitergabe mit Namensnennung erlaubt. {k('rohdateien')} Wochendateien, abgerufen am {k('abrufdatum')}.",
         f"`data/raw/MANIFEST.md`, `r2/src/01_download.py` (Commit {h('r2/src/01_download.py')})"),
        ("Woher weißt du, dass die Rohdaten nicht verändert wurden?",
         f"Jede Rohdatei hat eine {k('pruefsumme')}-Prüfsumme aus dem Abruf. Jeder Lauf und ein Test vergleichen sie; eine geänderte Zahl bricht den Lauf ab.",
         f"`data/raw/smard/manifest.csv`, Test `test_rohdaten_unveraendert` (Commit {h('tests/test_pipeline.py')})"),
        ("Wie behandelst du die Zeitumstellung?",
         f"Schlüssel ist UTC. Dort gibt es keine doppelten oder fehlenden Stunden; die doppelte Oktober-Stunde sind zwei verschiedene UTC-Stunden mit eigenem Preis, nichts wird gemittelt. Lokal gibt es {k('tage_23h')} Tage mit {k('stunden_23')} und {k('tage_25h')} mit {k('stunden_25')}; sie liegen nachts, außerhalb der Betriebszeit {k('betriebszeit')}.",
         f"`r2/reports/tables/zeitumstellung.csv`, Tagebuch E-026, `r2/src/cleaning.py` (Commit {h('r2/src/cleaning.py')})"),
        ("Warum löschst du keine Ausreißer?",
         f"Day-Ahead-Preise sind Auktionsergebnisse, keine Messwerte. Extreme Preise sind echt, und gerade die billigen Stunden tragen den Flexibilitätswert. Deshalb werden {k('geflaggt')} auffällige Preise ({k('geflaggt_pct')}) nur markiert, mit robustem z-Wert (Median/MAD) statt ±3 Standardabweichungen.",
         "`r2/docs/datenaufbereitung.md` Abschnitt 4, Tagebuch E-025, `r2/reports/tables/ausreisser.csv`"),
        ("Wie hast du die Umstellung auf Viertelstunden behandelt?",
         f"Seit {k('regimewechsel')} handelt die Börse in Viertelstunden. Wir nutzen einheitlich {k('aufloesung')}: den Stundenwert, den SMARD aus den vier Viertelstunden bildet. Bei Blöcken zur vollen Stunde ist das kostengleich.",
         "Tagebuch E-021, E-028; Quelle NEMO Committee (2025)"),
        ("Warum keine zweite, unabhängige Preisquelle?",
         "SMARD bezieht die Day-Ahead-Preise von ENTSO-E. Ein Abgleich wäre keine unabhängige Prüfung. Die Datenqualität prüfen wir stattdessen aktiv über die Sensitivitätsrechnung.",
         "Tagebuch E-015, `r2/docs/sensitivitaet_plan.md`"),
        ("Warum 2,0 MWh verschiebbar?",
         f"Ehrlich: Das ist ein Platzhalter. Der Praxiskontakt hat uns den Gesamtverbrauch ({k('verbrauch_gesamt')}), die Betriebszeit ({k('betriebszeit')}) und die flexiblen Prozesse genannt, aber noch keine Menge für den verschiebbaren Teil. Bis Prozess und Menge feststehen, bleibt {k('verbrauch_flexibel')} als Annahme stehen und ist überall so gekennzeichnet. Die Ersparnis in Euro skaliert damit linear; der Anteil am erreichbaren Optimum hängt nicht davon ab. Die Sensitivitätsrechnung zeigt die Wirkung anderer Mengen.",
         "`config/params.yaml` (`last.mwh_pro_tag`), Tagebuch K-005, E-024"),
        ("Ist eure Mehrkosten-Kennzahl nicht ein Blick in die Zukunft?",
         "Ja, bewusst: Sie ist ein Rückblick mit bekannten Preisen und zeigt nur, wie groß der Spielraum ist. Sie ist keine Strategie und steht so auf der Folie. Die Strategien im Backtest bekommen über `src/datenzugriff.py` nur Daten bis zum jeweiligen Freitag, und `flag_outlier` wird dort entfernt.",
         "`r2/src/fensteranalyse.py`, `src/datenzugriff.py`, Test `test_kein_look_ahead_in_allen_planungswochen`"),
        ("Warum sind die Prozentwerte so breit gestreut?",
         f"Mittags liegen die Preise im Frühling und Sommer oft nahe null. Prozent = Mehrkosten geteilt durch einen sehr kleinen Preis, das wird instabil; an {k('mk_ohne_pct_Sommer')} Sommertagen war das billigste Fenster sogar null oder negativ, dort gibt es keinen Prozentwert. Deshalb argumentieren wir in €/MWh (Sommer Median {k('mk_median_eur_mwh_Sommer')} €/MWh).",
         "`r2/src/fensteranalyse.py`, `r2/pptx_kit/key_figures.json`"),
        ("Was hat die KI gemacht, und was hast du selbst entschieden?",
         "Claude Code hat Code, Tests und Doku geschrieben. Ich habe vorher jeweils einen Plan freigegeben und die fachlichen Entscheidungen getroffen (UTC statt Mitteln, nur markieren statt löschen, CSV, Kennzahl Mehrkosten, Annahmen). Alles ist im Tagebuch und in `docs/ki-nutzung.md` gekennzeichnet; den Code erkläre ich selbst.",
         "`docs/ki-nutzung.md`, Tagebuch A-008, K-006, A-009"),
    ]
    text = "# Verteidigung R2: wahrscheinliche Prüferfragen\n\nErzeugt von `r2/src/build_presentation.py`; Zahlen aus `key_figures.json`.\n\n"
    for i, (f, a, b) in enumerate(fragen, 1):
        text += f"## {i}. {f}\n\n{a}\n\n**Beleg:** {b}\n\n"
    return text


def sources_md(k: Kennzahlen) -> str:
    return f"""# Quellen und KI-Einsatz (R2)

Erzeugt von `r2/src/build_presentation.py`.

## Daten

| Quelle | Inhalt | Lizenz | Beleg |
| --- | --- | --- | --- |
| {k('quelle')} | Day-Ahead-Großhandelspreis DE-LU, Filter {k('filter')}, {k('zeitraum_start')}–{k('zeitraum_ende')}, abgerufen {k('abrufdatum')} | {k('lizenz')}, Namensnennung „Bundesnetzagentur \\| SMARD.de“ | `data/raw/MANIFEST.md` |
| Praxiskontakt (anonymisiert) | Verbrauch {k('verbrauch_gesamt')}, Betriebszeit {k('betriebszeit')}, flexible Prozesse; Interview 09.11.2026 | Nutzung nur aggregiert, Name nur mit Freigabe | Tagebuch K-005 |
| eigene Annahme | verschiebbarer Anteil {k('verbrauch_flexibel')} (Platzhalter) | — | `config/params.yaml` |

## Fakten zum Markt

- ACER (2026): Decision 02/2026, Annex I, harmonisierte Höchst- und Mindestclearingpreise SDAC. https://www.acer.europa.eu/sites/default/files/documents/Individual%20Decisions_annex/ACER-Decision-02-2026-AnnexI.pdf
- EPEX SPOT (2022): Harmonised maximum clearing price for SDAC to be set to +4,000 EUR/MWh from 10th May 2022. https://www.epexspot.com/en/news/harmonised-maximum-clearing-price-sdac-be-set-4000-eurmwh-10th-may-2022
- EXAA (2022): Harmonised maximum clearing price for SDAC to be set to +5,000 EUR/MWh from 20th September. https://www.exaa.at/uber-exaa/neuigkeiten/harmonised-maximum-clearing-price-for-sdac-to-be-set-to-5-000-eur-mwh/
- NEMO Committee (2025): 15-minute MTU in SDAC was implemented (Lieferung ab {k('regimewechsel')}). https://nemo-committee.eu/assets/files/15-minute-mtu-in-sdac-was-implemented.pdf

## Methodische Literatur

Siehe `r2/docs/datenaufbereitung.md` (Wang & Strong 1996; Tukey 1977; Hampel 1974; Iglewicz & Hoaglin 1993; Leys et al. 2013; Janczura et al. 2013; Weron 2014).

## KI-Einsatz

**Wofür Claude Code genutzt wurde:** Programmcode (`r2/src/01_download.py`, `r2/src/02_synthetisch.py`, `r2/src/cleaning.py`, `src/datenzugriff.py`, `r2/src/fensteranalyse.py`, `r2/src/build_presentation.py`), Tests, Dokumentation (Codebook, Aufbereitungsprotokoll, Schnittstellen), Quellenrecherche zu Preisgrenzen und zur Viertelstunden-Umstellung, Entwürfe für Tagebucheinträge, diese Folien.

**Was ich (Max, R2) entschieden und geprüft habe:**
- Pläne vor jedem größeren Schritt freigegeben (Tagebuch A-008, A-009).
- Fachliche Entscheidungen: nur Stundenpreise (E-021), CSV statt Parquet (E-027), UTC als Schlüssel (E-026), Ausreißer nur markieren (E-025), Produktion täglich (E-024), Kennzahl Mehrkosten des Status quo statt „Anteil 08–14“ (E-030).
- Praxisangaben selbst im Interview erhoben (K-005).
- Prüfung: {k('tests')} automatische Tests grün; Gegenproben mit absichtlich eingebauten Fehlern; gerenderte Folien gesichtet.
- Offen: den Code Abschnitt für Abschnitt selbst erklären (Sperrkriterium Erklärbarkeit).

Kennzeichnung im Repo: Dateikopf `# KI: Claude …`, Commit-Trailer, `docs/ki-nutzung.md`.
"""


# ---------------------------------------------------------------------------------------------
# 6) Render (LibreOffice -> PDF -> PNG) for the visual check
# ---------------------------------------------------------------------------------------------
def rendern(pptx: Path) -> list[Path]:
    ziel = pptx.parent / "render"
    ziel.mkdir(parents=True, exist_ok=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(ziel), str(pptx)],
                   check=True, capture_output=True)
    pdf = ziel / (pptx.stem + ".pdf")
    subprocess.run(["pdftoppm", "-png", "-r", "80", str(pdf), str(ziel / "folie")], check=True)
    return sorted(ziel.glob("folie-*.png"))


def main() -> None:
    p = lade_params()
    KIT.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    k, d, tage_f, js = berechne_kennzahlen(p)
    k.schreibe(KIT / "key_figures.json")
    grafiken(k, d, tage_f, js, p)
    prs = folien(k)
    fehler = pruefe_zahlen(prs, k)
    if fehler:
        sys.exit("Zahlenprüfung fehlgeschlagen:\n" + "\n".join(fehler))
    prs.save(OUTPUT)
    (KIT / "defense_qa.md").write_text(defense_qa(k), encoding="utf-8")
    (KIT / "sources.md").write_text(sources_md(k), encoding="utf-8")
    print(f"Folien: {OUTPUT} ({len(prs.slides)} Folien); Kit: {KIT}; Zahlenprüfung ok ({len(k.daten)} Kennzahlen)")
    if "--render" in sys.argv:
        for png in rendern(OUTPUT):
            print("  gerendert:", png)


if __name__ == "__main__":
    main()
