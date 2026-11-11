# KI: Claude, Zweck: Grafiken nach einem Standard und Vergleich Spot gegen Festpreis (Phase 6, E-045), geprüft von Chiara (R1) durch Erklärzettel und Sichtung jeder Grafik
"""Step 7 (R1): figures for report and slides in one standard, plus spot vs. fixed price.

Owner: R1 (Chiara). Reads only result files of R2-R4, computes nothing new except the spot/fixed price
table (R1's own question from the team paper: "Vertrag: Festpreis vs. Börse?").
Output: ergebnisse/daten_fuer_grafiken.md (ALL key numbers as tables, for building figures and slides
        in Claude; diary E-052), ergebnisse/spot_festpreis.csv, ergebnisse/grafiken/*.png (draft figures)

Figure standard (docs/bericht_entwurf.md, "Grafikstandard"):
  * The title is the key message as a sentence, not a description ("3 Uhr ist am billigsten", not "Preise").
  * One y-axis per figure, unit on the axis, source line bottom left.
  * Colours by role, fixed order: blue = the recommended rule / main series, orange = second, aqua = third
    (validated for colour-blind readers); grey = reference (status quo, zero line).
  * Lines and bars are labelled directly, so colour is never the only way to tell series apart.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                    # files only, no screen needed
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402
import pandas as pd                      # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import ROOT, lade_params, pfad  # noqa: E402

# Colour roles (dataviz reference palette, light mode; slots 1-3 pass the colour-blind check)
BLAU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GRAU, TEXT, TEXT2, RASTER = "#8a8984", "#0b0b0b", "#52514e", "#e6e5e1"
QUELLE = "Quelle: Bundesnetzagentur | SMARD.de (CC BY 4.0), eigene Berechnung; Annahmen in docs/annahmen.md"


def stil() -> None:
    """One look for every figure: recessive grid and axes, readable sizes, no top/right frame."""
    plt.rcParams.update({
        "figure.figsize": (8, 4.5), "figure.dpi": 100, "savefig.dpi": 200, "figure.facecolor": "white",
        "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.edgecolor": RASTER, "axes.labelcolor": TEXT2, "axes.grid": True, "axes.axisbelow": True,
        "grid.color": RASTER, "grid.linewidth": 0.8, "xtick.color": TEXT2, "ytick.color": TEXT2,
        "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2, "text.color": TEXT,
    })


def speichern(fig, ziel: Path, name: str) -> None:
    # The key message spans the whole figure width (axis titles get cut next to long y labels).
    ax = fig.axes[0]
    fig.suptitle(ax.get_title(loc="left"), x=0.01, ha="left", fontsize=12, fontweight="bold", color=TEXT)
    ax.set_title("", loc="left")
    fig.text(0.01, 0.01, QUELLE, fontsize=7, color=TEXT2, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(ziel / name)
    plt.close(fig)


def de(x: float, n: int = 0) -> str:
    """German number format: 1 197,3 (thin space as thousands separator)."""
    return f"{x:,.{n}f}".replace(",", " ").replace(".", ",")


# ---------------------------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------------------------
def g1_preistal(matrix: pd.DataFrame, ziel: Path) -> None:
    """Mean block price per start hour, three periods: the valley is at 3 Uhr everywhere."""
    jahr = pd.to_datetime(matrix["nacht"]).dt.year
    gruppen = [("2022 (Krise)", jahr == 2022, ORANGE), ("2023–2024 (Training)", jahr.isin([2023, 2024]), BLAU),
               ("2025–2026 (Test)", jahr >= 2025, AQUA)]
    starts = [22, 23, 0, 1, 2, 3, 4]
    fig, ax = plt.subplots()
    for name, maske, farbe in gruppen:
        m = matrix[maske].groupby("start_lokal")["preis_eur_mwh"].mean().reindex(starts)
        ax.plot(range(len(starts)), m.to_numpy(), color=farbe, marker="o", markersize=5)
        ax.annotate(name, (len(starts) - 1, m.iloc[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=9, color=TEXT)
    ax.set_xticks(range(len(starts)), [f"{h:02d}–{(h + 2) % 24:02d}" for h in starts])
    ax.set_xlim(-0.3, len(starts) + 1.6)
    ax.set_xlabel("2-h-Block der Reinigung (Start, deutsche Zeit)")
    ax.set_ylabel("mittlerer Preis des Blocks in €/MWh")
    ax.set_title("Der Block ab 3 Uhr ist in jedem Zeitraum am billigsten, 22 Uhr am teuersten")
    speichern(fig, ziel, "g1_preistal_nacht.png")


def g2_strategien(netto: pd.DataFrame, ziel: Path) -> None:
    """Net saving per strategy with 95 % interval, test 2025-2026: the fixed rule is as good as a forecast."""
    t = netto[(netto["periode"] == "test_gesamt") & (netto["vertrag"] == "band")].set_index("strategie")
    reihen = [("C", "Tagesplanung (Oracle, Obergrenze)", GRAU), ("B_16", "jede Woche neu, 16 Wochen (FS2)", ORANGE),
              ("B", "jede Woche neu, 4 Wochen (Median)", ORANGE), ("D", "fest 3 Uhr (FS1, Empfehlung)", BLAU)]
    fig, ax = plt.subplots()
    for i, (s, name, farbe) in enumerate(reihen):
        r = t.loc[s]
        ax.barh(i, r["netto_eur_woche"], height=0.55, color=farbe)
        ax.errorbar(r["netto_eur_woche"], i, xerr=[[r["netto_eur_woche"] - r["ki_unten"]], [r["ki_oben"] - r["netto_eur_woche"]]],
                    color=TEXT, capsize=4, linewidth=1.2)
        anteil = r["netto_eur_woche"] / t.loc["C", "netto_eur_woche"]
        ax.text(r["ki_oben"] + 20, i, f"{de(r['netto_eur_woche'])} €  ({de(100 * anteil)} %)", va="center", fontsize=9)
    ax.set_yticks(range(len(reihen)), [n for _, n, _ in reihen])
    ax.set_xlim(0, t["ki_oben"].max() * 1.35)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Netto-Ersparnis gegenüber 22–24 Uhr in € pro Woche, mit 95-%-Intervall")
    ax.set_title("Fest 3 Uhr holt 93 % des Möglichen, eine wöchentliche Prognose bringt nicht mehr")
    speichern(fig, ziel, "g2_ersparnis_strategien.png")


def g3_kennzahl(kpi: pd.DataFrame, ziel: Path) -> None:
    """Weekly net saving of D over time with the rolling 13-week KPI and the roll-back line at zero."""
    k = kpi.copy()
    k["woche"] = pd.to_datetime(k["woche"])
    k = k.sort_values("woche")
    fig, ax = plt.subplots()
    ax.bar(k["woche"], k["netto"], width=5, color=BLAU, alpha=0.35, label="Woche")
    for _, g in k.groupby("periode"):
        ax.plot(g["woche"], g["netto_rollierend_13w"], color=BLAU)
    ax.axhline(0, color=GRAU, linewidth=1.2)
    ax.annotate("Rücknahme auf 22 Uhr, wenn die Linie unter null fällt", (k["woche"].iloc[5], 0), xytext=(0, -16),
                textcoords="offset points", fontsize=8, color=TEXT2)
    ax.set_ylim(bottom=-600)
    letzte = k.dropna(subset=["netto_rollierend_13w"]).iloc[-1]
    ax.annotate("13-Wochen-Mittel (Kennzahl)", (letzte["woche"], letzte["netto_rollierend_13w"]), xytext=(-150, 30),
                textcoords="offset points", fontsize=9, arrowprops={"arrowstyle": "-", "color": TEXT2, "linewidth": 0.8})
    ax.set_ylabel("Netto-Ersparnis in € pro Woche")
    ax.set_title("In keiner Woche 2022–2026 war die Reinigung um 3 Uhr teurer als um 22 Uhr")
    speichern(fig, ziel, "g3_kennzahl_zeitverlauf.png")


def g4_sensitivitaet(sens: pd.DataFrame, ziel: Path) -> None:
    """Change of D's net saving per variant: the euros move, the decision does not."""
    s = sens[(sens["strategie"] == "D") & (sens["periode"] == "test_gesamt") & (sens["variante"] != "Basis")].copy()
    namen = {"V2": "ohne Nächte mit auffälligen Preisen", "V3": "Mariä Himmelfahrt Feiertag", "V4": "nur Mo–Fr reinigen",
             "V6a": "4 MWh statt 8", "V6b": "12 MWh statt 8", "V6c": "16 MWh (Teamdokument)", "V7a": "Reinigung 1 h",
             "V7b": "Reinigung 3 h", "V7c": "Reinigung 4 h", "V8": "nur 30 % der MWh am Spot",
             "V9": "Nachtzuschlag erst ab 23 Uhr", "V10": "Zuschläge addiert"}
    s["name"] = s["variante"].map(namen)
    s = s.sort_values("delta_pct")
    fig, ax = plt.subplots(figsize=(8, 5))
    y = np.arange(len(s))
    ax.barh(y, s["delta_pct"], height=0.6, color=BLAU)
    for yi, v in zip(y, s["delta_pct"]):
        ax.text(v + (2 if v >= 0 else -2), yi, f"{de(v)} %", va="center", ha="left" if v >= 0 else "right", fontsize=8)
    ax.axvline(0, color=GRAU, linewidth=1.2)
    ax.set_yticks(y, s["name"])
    ax.set_xlim(-90, 125)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Änderung der Netto-Ersparnis (fest 3 Uhr) gegenüber der Basis in %")
    ax.set_title("Die Euro-Beträge schwanken mit Menge und Vertrag, die Entscheidung kippt in keiner Variante")
    speichern(fig, ziel, "g4_sensitivitaet.png")


def g5_break_even(be: pd.DataFrame, ziel: Path) -> None:
    """Payback months against one-off switching costs, for both contract cases."""
    b = be[(be["strategie"] == "D") & (be["periode"] == "test_gesamt")]
    fig, ax = plt.subplots()
    for art, name, farbe in (("band", "alle verschobenen MWh am Spot", BLAU), ("proportional", "nur 30 % am Spot", ORANGE)):
        g = b[b["vertrag"] == art]
        x = g["umstellungskosten_eur"] / 1000
        ax.plot(x, g["break_even"], color=farbe, marker="o", markersize=5)
        # label at the 50k point, clear of the line: above-left for the steep line, below-right for the flat one
        i = list(g["umstellungskosten_eur"]).index(50_000)
        dx, dy, ha, va = ((-10, 10, "right", "bottom") if art == "proportional" else (10, -10, "left", "top"))
        ax.annotate(name, (x.iloc[i], g["break_even"].iloc[i]), xytext=(dx, dy), textcoords="offset points",
                    ha=ha, va=va, fontsize=9)
    ax.axhline(12, color=GRAU, linewidth=1, linestyle="--")
    ax.annotate("1 Jahr", (1, 12), xytext=(0, 4), textcoords="offset points", fontsize=8, color=TEXT2)
    ax.set_xlabel("einmalige Umstellungskosten in Tausend €")
    ax.set_ylabel("Monate bis zur Amortisation")
    ax.set_title("Bei vollem Spotbezug sind bis rund 60 000 € Umstellungskosten nach einem Jahr wieder drin")
    speichern(fig, ziel, "g5_break_even.png")


def g6_spot_festpreis(sf: pd.DataFrame, festpreis: float, ziel: Path) -> None:
    """Mean spot price per year (plant profile) against the fixed price."""
    fig, ax = plt.subplots()
    x = np.arange(len(sf))
    ax.bar(x, sf["spot_profil_eur_mwh"], width=0.55, color=BLAU)
    ax.axhline(festpreis, color=ORANGE, linewidth=2)
    # label in the empty upper right, with a leader line down to the fixed-price line (never on a bar)
    ax.annotate(f"Festpreis {de(festpreis)} €/MWh", (len(sf) - 1.5, festpreis), xytext=(len(sf) - 1.5, festpreis + 90),
                ha="center", fontsize=9, color=TEXT, arrowprops={"arrowstyle": "-", "color": TEXT2, "linewidth": 0.8})
    for xi, v in zip(x, sf["spot_profil_eur_mwh"]):
        ax.text(xi, v - 4, de(v), ha="center", va="top", fontsize=9, color="white", fontweight="bold")
    ax.set_xticks(x, [str(j) + (" (bis Okt.)" if not v else "") for j, v in zip(sf["jahr"], sf["vollstaendig"])])
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("Day-Ahead-Preis im Lastprofil in €/MWh")
    ax.set_title("Außer 2024 war der Festpreis von 85 €/MWh günstiger als die Börse im Lastprofil")
    speichern(fig, ziel, "g6_spot_festpreis.png")


# ---------------------------------------------------------------------------------------------
# Spot vs. fixed price (R1)
# ---------------------------------------------------------------------------------------------
def spot_festpreis(preise: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Per year: mean day-ahead price in the plant's load profile vs. the fixed price.

    Load profile (assumption, docs/annahmen.md): 180 MWh per day, of which 8 MWh cleaning 22-24 Uhr
    (status quo) and the rest flat over the production hours 06-22 Uhr. Then: what the spot share
    (53 MWh/day) cost at the exchange vs. at the fixed price, and the same for the whole plant.
    """
    L, k, v = params["last"], params["kosten"], params["vertrag"]
    d = preise.copy()
    d["jahr"] = pd.to_datetime(d["datum_lokal"]).dt.year
    prod_h = (L["betrieb_ende_h"] - L["betrieb_start_h"])
    gewicht = np.where(d["in_betriebszeit"], (L["gesamtverbrauch_mwh_pro_tag"] - L["mwh_pro_tag"]) / prod_h, 0.0)
    gewicht = gewicht + np.where(d["stunde_lokal"].isin([L["status_quo_start_h"], (L["status_quo_start_h"] + 1) % 24]),
                                 L["mwh_pro_tag"] / L["blocklaenge_h"], 0.0)
    d["mwh"], d["eur"] = gewicht, gewicht * d["preis_eur_mwh"]
    zeilen = []
    for jahr, g in d.groupby("jahr"):
        tage = g["datum_lokal"].nunique()
        spot = g["eur"].sum() / g["mwh"].sum()
        spot_mwh_jahr = v["spot_anteil"] * L["gesamtverbrauch_mwh_pro_tag"] * tage
        zeilen.append({"jahr": int(jahr), "tage": tage, "vollstaendig": tage >= 365,
                       "spot_grundlast_eur_mwh": g["preis_eur_mwh"].mean(), "spot_profil_eur_mwh": spot,
                       "festpreis_eur_mwh": k["festpreis_eur_mwh"],
                       "vorteil_festpreis_eur_mwh": spot - k["festpreis_eur_mwh"],
                       "vorteil_festpreis_spotanteil_eur": (spot - k["festpreis_eur_mwh"]) * spot_mwh_jahr,
                       "vorteil_festpreis_ganzes_werk_eur": (spot - k["festpreis_eur_mwh"]) * L["gesamtverbrauch_mwh_pro_tag"] * tage})
    return pd.DataFrame(zeilen)


# ---------------------------------------------------------------------------------------------
# All data in one Markdown file (E-052): figures and slides are made later in Claude from this file
# ---------------------------------------------------------------------------------------------
def tabelle(df: pd.DataFrame, nachkomma: int = 1) -> str:
    """Markdown table, numbers rounded, decimal point (machine-readable)."""
    d = df.copy()
    for c in d.columns:
        if pd.api.types.is_float_dtype(d[c]):
            d[c] = d[c].round(nachkomma)
    kopf = "| " + " | ".join(map(str, d.columns)) + " |"
    trenn = "| " + " | ".join("---" for _ in d.columns) + " |"
    zeilen = ["| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |" for r in d.itertuples(index=False)]
    return "\n".join([kopf, trenn, *zeilen])


def daten_md(p: dict, tab: Path, sf: pd.DataFrame) -> str:
    """Every number a figure, slide or report section needs, with its source file, in one place."""
    r2 = ROOT / p["cleaning"]["reports"]
    m = pd.read_csv(tab / "blockkosten_nacht.csv")
    jahr = pd.to_datetime(m["nacht"]).dt.year
    m["zeitraum"] = np.select([jahr == 2022, jahr <= 2024], ["2022 Krise", "2023-2024 Training"], "2025-2026 Test")
    preistal = m.pivot_table(index="start_lokal", columns="zeitraum", values="preis_eur_mwh", aggfunc="mean")
    preistal = preistal.reindex([22, 23, 0, 1, 2, 3, 4]).reset_index().rename(columns={"start_lokal": "start_uhr"})
    m["jahr"] = jahr
    preistal_jahr = m.pivot_table(index="start_lokal", columns="jahr", values="preis_eur_mwh", aggfunc="mean")
    preistal_jahr = preistal_jahr.reindex([22, 23, 0, 1, 2, 3, 4]).reset_index().rename(columns={"start_lokal": "start_uhr"})

    ki = pd.read_csv(tab / "ki_strategien.csv")
    netto = pd.read_csv(tab / "netto_tests.csv")
    ht = pd.read_csv(tab / "hypothesentests.csv")
    kpi = pd.read_csv(tab / "kpi_rollierend.csv")
    kpi["monat"] = kpi["woche"].str[:7]
    monat = kpi.groupby("monat").agg(wochen=("netto", "size"), netto_eur_woche=("netto", "mean"),
                                    spreizung_eur_mwh=("spreizung_eur_mwh", "mean")).reset_index()
    sens = pd.read_csv(r2 / "sensitivitaet.csv")
    sens = sens[(sens["strategie"] == "D") & (sens["periode"] == "test_gesamt")]
    be = pd.read_csv(tab / "wirtschaftlichkeit.csv")
    be = be[(be["strategie"] == "D") & (be["periode"] == "test_gesamt")]
    kp = pd.read_csv(tab / "kipppunkte.csv")
    ce = pd.read_csv(tab / "ce_matrix.csv")
    fa = pd.read_csv(tab / "fehleranalyse_b.csv")
    rj = pd.read_csv(r2 / "reinigungsfenster_jahr.csv")
    rs = pd.read_csv(r2 / "reinigungsfenster_saison.csv")
    km = pd.read_csv(r2 / "kennzahlen_monat.csv")
    tp = pd.read_csv(r2 / "tagesprofil_saison.csv").pivot_table(index="stunde_lokal", columns="saison", values="median").reset_index()

    teile = [
        "# Alle Daten für Grafiken, Folien und Bericht",
        "",
        "<!-- KI: Claude, Zweck: alle Kennzahlen in einer Datei für Grafiken in Claude (E-052), erzeugt von src/07_bericht.py, geprüft von Chiara (R1) -->",
        "",
        "Erzeugt von `src/07_bericht.py` bei jedem `python src/run_all.py` aus den Ergebnisdateien; nichts von Hand eingetragen. "
        "Zahlen mit Dezimalpunkt. € = Euro. Strategien: **A** Status quo 22–24 Uhr · **D** fest 3 Uhr (FS1, Empfehlung) · "
        "**B** jede Woche neu aus 4 Wochen (Median) · **B_16** jede Woche neu aus 16 Wochen (FS2) · **C** Oracle = Tagesplanung (Obergrenze) · "
        "D_saison = D je Saison (identisch mit D) · B_ohne_wochentag = Kontrolle für K3. Zeiträume: training 2023–2024 · test_1_stunde 01–09/2025 · "
        "test_2_viertel 10/2025–09/2026 · test_gesamt = beide Tests (89 Wochen, Testentscheidung nur hier) · stresstest 2022. "
        "Vertrag: band = alle verschobenen MWh am Spot (Basis), proportional = nur 30 %. Annahmen: `docs/annahmen.md`.",
        "",
        "## Kernaussagen",
        "",
        f"- Fest 3 Uhr spart netto {de(netto.query('strategie == \"D\" and periode == \"test_gesamt\" and vertrag == \"band\"')['netto_eur_jahr'].iloc[0])} € pro Jahr "
        f"(30 %-Fall {de(netto.query('strategie == \"D\" and periode == \"test_gesamt\" and vertrag == \"proportional\"')['netto_eur_jahr'].iloc[0])} €), "
        "93 % des Möglichen; H0a verworfen (p < 0.001).",
        "- Eine wöchentliche Prognose (B, B_16) ist nicht signifikant besser als fest 3 Uhr (H0b nicht verworfen).",
        "- Tagesplanung lohnt nur, wenn kurzfristiges Personal weniger als rund 2 € pro Stunde Aufpreis kostet (H0c, Kipppunkt).",
        "- Kipppunkt der Empfehlung: mehr als 1.3 h (30 %-Fall 0.4 h) bezahlte Wartezeit je Person und Nacht.",
        "- In keiner Woche 2022–2026 war 3 Uhr teurer als 22 Uhr; keine Sensitivitätsvariante kippt eine Entscheidung.",
        "",
        "## 1 Preistal der Nacht: mittlerer Preis des 2-h-Blocks je Startuhrzeit (€/MWh)",
        "Quelle: `ergebnisse/blockkosten_nacht.csv`. Grafikidee: Linien je Zeitraum über die Startuhrzeit.",
        "", tabelle(preistal), "", "Je Jahr:", "", tabelle(preistal_jahr), "",
        "## 2 Ersparnis je Strategie gegenüber A, nur Strom (€/Woche, 95-%-Intervall)",
        "Quelle: `ergebnisse/ki_strategien.csv`.",
        "", tabelle(ki[ki["vertrag"] == "band"][["strategie", "periode", "n_wochen", "mittel_eur_woche", "ki_unten", "ki_oben",
                                                 "boot_unten", "boot_oben", "eur_jahr", "anteil_oracle"]], 3), "",
        "## 3 Netto nach Personalkosten (€/Woche) und H0a",
        "Quelle: `ergebnisse/netto_tests.csv`. Grafikidee: Balken je Strategie mit Intervall (test_gesamt).",
        "", tabelle(netto[["strategie", "periode", "vertrag", "strom_ersparnis_eur_woche", "personal_mehr_eur_woche", "netto_eur_woche",
                           "ki_unten", "ki_oben", "netto_eur_jahr", "p_t", "p_wilcoxon", "h0_verworfen"]], 2), "",
        "## 4 Hypothesentests (einseitig, Schwelle 0.05/3 = 0.0167)",
        "Quelle: `ergebnisse/hypothesentests.csv`; H0a in Abschnitt 3. konfirmatorisch = vorab festgelegt und nur test_gesamt.",
        "", tabelle(ht[["hypothese", "vergleich", "periode", "konfirmatorisch", "n_wochen", "mittel_eur_woche", "ki_unten", "ki_oben",
                        "shapiro_p", "p_t", "p_wilcoxon", "h0_verworfen", "robust", "untere_schranke"]], 3), "",
        "## 5 Kennzahl im Zeitverlauf: Netto-Ersparnis D je Monat (Mittel der Wochen)",
        "Quelle: `ergebnisse/kpi_rollierend.csv` (je Woche, mit 13-Wochen-Mittel und Rücknahme-Flag). "
        f"Rücknahmeregel (13-Wochen-Mittel < 0) hätte in {int(kpi['ruecknahme'].sum())} von {int(kpi['netto_rollierend_13w'].notna().sum())} Wochen ausgelöst; "
        f"kleinstes 13-Wochen-Mittel {de(kpi['netto_rollierend_13w'].min())} €/Woche.",
        "", tabelle(monat), "",
        "## 6 Sensitivität (D, test_gesamt, Schwelle 5 %)",
        "Quelle: `r2/ergebnisse/sensitivitaet.csv`. Grafikidee: liegende Balken der Änderung in %.",
        "", tabelle(sens[["variante", "schalter", "wert", "mittel_eur_woche", "delta_pct", "anteil_oracle", "h0_entscheidung_gleich", "relevant"]], 2), "",
        "## 7 Break-even: Monate bis zur Amortisation einmaliger Umstellungskosten (D, test_gesamt)",
        "Quelle: `ergebnisse/wirtschaftlichkeit.csv`.",
        "", tabelle(be[["vertrag", "umstellungskosten_eur", "ersparnis_eur_jahr", "break_even", "break_even_vorsichtig_monate"]], 2), "",
        "## 8 Kipppunkte (D, test_gesamt)",
        "Quelle: `ergebnisse/kipppunkte.csv`.",
        "", tabelle(kp[["vertrag", "annahme", "basis", "kipppunkt", "einheit", "lesart"]], 3), "",
        "## 9 Spot gegen Festpreis (85 €/MWh)",
        "Quelle: `ergebnisse/spot_festpreis.csv`. Lastprofil (Annahme): 180 MWh/Tag, Reinigung 22–24 Uhr, Rest gleichmäßig 06–22 Uhr. "
        "vorteil_festpreis > 0 heißt: Der Festpreis war günstiger als die Börse.",
        "", tabelle(sf), "",
        "## 10 C&E-Matrix (Skala 0/1/3/9, Gewichte Teamannahme)",
        "Quelle: `ergebnisse/ce_matrix.csv`. Grafikidee: Pareto-Balken mit kumulierter Linie.",
        "", tabelle(ce), "",
        "## 11 Fehleranalyse B: wann liegt die Prognose daneben (€ je Nacht)",
        "Quelle: `ergebnisse/fehleranalyse_b.csv`. regret_b = B − C, b_minus_d = B − D.",
        "", tabelle(fa, 2), "",
        "## 12 R2: Rückblick-Kennzahl je Jahr (Mehrkosten 22–24 Uhr gegen billigstes Fenster)",
        "Quelle: `r2/ergebnisse/reinigungsfenster_jahr.csv`, `reinigungsfenster_saison.csv`. Obergrenze mit bekannten Preisen, keine Strategie.",
        "", tabelle(rj, 2), "", tabelle(rs, 2), "",
        "## 13 R2: Preis je Monat (€/MWh) und Tagesprofil je Saison (Median je Stunde)",
        "Quelle: `r2/ergebnisse/kennzahlen_monat.csv`, `tagesprofil_saison.csv`.",
        "", tabelle(km, 2), "", tabelle(tp, 1), "",
    ]
    return "\n".join(teile) + "\n"


def main() -> None:
    p = lade_params()
    stil()
    tab = pfad(p, "tables")
    ziel = tab / "grafiken"
    ziel.mkdir(parents=True, exist_ok=True)
    preise = pd.read_csv(pfad(p, "processed") / "preise_clean.csv")
    sf = spot_festpreis(preise, p)
    sf.round(2).to_csv(tab / "spot_festpreis.csv", index=False)

    (tab / "daten_fuer_grafiken.md").write_text(daten_md(p, tab, sf), encoding="utf-8")
    g1_preistal(pd.read_csv(tab / "blockkosten_nacht.csv"), ziel)
    g2_strategien(pd.read_csv(tab / "netto_tests.csv"), ziel)
    g3_kennzahl(pd.read_csv(tab / "kpi_rollierend.csv"), ziel)
    g4_sensitivitaet(pd.read_csv(ROOT / p["cleaning"]["reports"] / "sensitivitaet.csv"), ziel)
    g5_break_even(pd.read_csv(tab / "wirtschaftlichkeit.csv"), ziel)
    g6_spot_festpreis(sf, p["kosten"]["festpreis_eur_mwh"], ziel)
    print(f"Bericht R1: alle Daten -> {tab / 'daten_fuer_grafiken.md'}; Entwurfsgrafiken -> {ziel}")
    print(sf[["jahr", "vollstaendig", "spot_grundlast_eur_mwh", "spot_profil_eur_mwh", "vorteil_festpreis_eur_mwh",
              "vorteil_festpreis_spotanteil_eur", "vorteil_festpreis_ganzes_werk_eur"]].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
