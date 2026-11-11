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
    for art, name, farbe in (("band", "Reinigung 100 % am Day-Ahead (A-018)", BLAU),):
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
    ax.set_title("Bis rund 60 000 € Umstellungskosten sind nach einem Jahr wieder drin")
    speichern(fig, ziel, "g5_break_even.png")


def g7_kumuliert(wochen: pd.DataFrame, ziel: Path) -> None:
    """Cumulative electricity saving vs A over the test weeks: fixed rule and weekly forecast run together."""
    w = wochen[wochen["periode"].isin(["test_1_stunde", "test_2"])].sort_values("woche").copy()
    w["woche"] = pd.to_datetime(w["woche"])
    fig, ax = plt.subplots()
    for s, name, farbe in (("C", "Tagesplanung (Oracle)", GRAU), ("B_16", "jede Woche neu, 16 Wochen", ORANGE),
                           ("D", "fest 3 Uhr", BLAU)):
        kum = (w["kosten_A"] - w[f"kosten_{s}"]).cumsum() / 1000
        ax.plot(w["woche"], kum, color=farbe, label=f"{name}: {de(kum.iloc[-1])} T€")
    # The three lines nearly overlap, so a legend (top left, empty area) instead of labels at the line ends
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.set_ylabel("Stromersparnis kumuliert in Tausend €")
    ax.set_title("Fest 3 Uhr und wöchentliche Planung laufen im Test fast deckungsgleich")
    speichern(fig, ziel, "g7_kumuliert_test.png")


# ---------------------------------------------------------------------------------------------
# Further figures (team suggestions, E-054): distributions, heatmaps, waterfall, Pareto
# ---------------------------------------------------------------------------------------------
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402

# Sequential = one hue light -> dark (blue ramp); diverging = blue <-> red with a neutral grey midpoint
SEQ = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
DIV = LinearSegmentedColormap.from_list("div", ["#104281", "#3987e5", "#f0efec", "#e66767", "#a8282a"])
STRATEGIE_NAME = {"A": "22–24 Uhr (heute)", "D": "fest 3 Uhr", "B": "jede Woche neu, 4 W.",
                  "B_16": "jede Woche neu, 16 W.", "C": "Tagesplanung (Oracle)"}


def g8_heatmap_preistal(preise: pd.DataFrame, ziel: Path) -> None:
    """Hour x calendar month, price minus the monthly mean: shows the night valley AND the midday solar valley,
    and how both move over the seasons. Deviation instead of level, so 2022 does not swamp the colour scale."""
    d = preise.copy()
    d["monat"] = pd.to_datetime(d["datum_lokal"]).dt.month
    d["jahr"] = pd.to_datetime(d["datum_lokal"]).dt.year
    d = d[d["jahr"] >= 2023]                                    # 2022 crisis would dominate; shown elsewhere
    d["abw"] = d["preis_eur_mwh"] - d.groupby(["jahr", "monat"])["preis_eur_mwh"].transform("mean")
    m = d.pivot_table(index="stunde_lokal", columns="monat", values="abw", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(8, 5.5))
    grenze = np.nanmax(np.abs(m.to_numpy()))
    bild = ax.imshow(m.to_numpy(), aspect="auto", cmap=DIV, norm=TwoSlopeNorm(0, -grenze, grenze))
    ax.set_xticks(range(12), ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"])
    ax.set_yticks(range(0, 24, 2), [f"{h:02d}:00" for h in range(0, 24, 2)])
    for y in (-0.5 + 22, -0.5 + 6):                             # cleaning window 22-06 Uhr
        ax.axhline(y, color=TEXT, linewidth=1, linestyle="--")
    ax.grid(False)
    fig.colorbar(bild, ax=ax, label="Abweichung vom Monatsmittel in €/MWh", shrink=0.85)
    ax.set_ylabel("Uhrzeit (Stundenbeginn)")
    ax.set_xlabel("Monat (2023–2026); gestrichelt: Reinigungsfenster 22–06 Uhr")
    ax.set_title("Im Winter ist die Nacht das Preistal, im Sommer der Mittag; 3 Uhr ist stets billiger als 22 Uhr")
    speichern(fig, ziel, "g8_heatmap_stunde_monat.png")


def g9_heatmap_startwahl(naechte: pd.DataFrame, ziel: Path) -> None:
    """Strategy x start hour, share of test nights: D always 3 Uhr, the oracle spreads over 1-4 Uhr."""
    n = naechte[naechte["periode"].isin(["test_1_stunde", "test_2"])]
    starts = [22, 23, 0, 1, 2, 3, 4]
    reihen = ["A", "D", "B", "B_16", "C"]
    w = pd.crosstab(n["strategie"], n["start_lokal"], normalize="index").mul(100).reindex(index=reihen, columns=starts, fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.imshow(w.to_numpy(), aspect="auto", cmap=SEQ, vmin=0, vmax=100)
    for i in range(len(reihen)):
        for j in range(len(starts)):
            v = w.iat[i, j]
            if v >= 0.5:
                ax.text(j, i, f"{v:.0f} %", ha="center", va="center", fontsize=9, color="white" if v > 45 else TEXT)
    ax.set_xticks(range(len(starts)), [f"{h:02d}–{(h + 2) % 24:02d}" for h in starts])
    ax.set_yticks(range(len(reihen)), [STRATEGIE_NAME[r] for r in reihen])
    ax.grid(False)
    ax.set_xlabel("gewählter 2-h-Block (Start, deutsche Zeit), Anteil der Testnächte")
    ax.set_title("Fest 3 Uhr trifft das Zentrum dessen, was die Tagesplanung im Nachhinein wählt")
    speichern(fig, ziel, "g9_heatmap_startwahl.png")


def g10_box_wochen(wochen: pd.DataFrame, ziel: Path) -> None:
    """Distribution of the weekly electricity saving vs A in the test: box plus every single week."""
    w = wochen[wochen["periode"].isin(["test_1_stunde", "test_2"])]
    reihen = [("D", BLAU), ("B", ORANGE), ("B_16", ORANGE), ("C", GRAU)]
    daten = [(w["kosten_A"] - w[f"kosten_{s}"]).dropna().to_numpy() for s, _ in reihen]
    fig, ax = plt.subplots()
    rng = np.random.default_rng(42)                              # fixed jitter, reproducible picture
    for i, ((s, farbe), d) in enumerate(zip(reihen, daten)):
        ax.scatter(i + rng.uniform(-0.18, 0.18, len(d)), d, s=10, color=farbe, alpha=0.45, linewidths=0)
        ax.boxplot(d, positions=[i], widths=0.5, showfliers=False, medianprops={"color": TEXT, "linewidth": 2},
                   boxprops={"color": TEXT2}, whiskerprops={"color": TEXT2}, capprops={"color": TEXT2})
        ax.text(i + 0.3, np.median(d), f"Median {de(np.median(d))} €", va="center", fontsize=8, color=TEXT)
    ax.set_xticks(range(len(reihen)), [STRATEGIE_NAME[s] for s, _ in reihen])
    ax.set_xlim(-0.5, len(reihen) - 0.2)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("Stromersparnis gegenüber 22–24 Uhr in € je Woche")
    ax.set_title("Die Wochen streuen stark und schief, alle Strategien gleich: deshalb Wilcoxon zusätzlich")
    speichern(fig, ziel, "g10_verteilung_wochen.png")


def g11_differenz_h0b(wochen: pd.DataFrame, ziel: Path) -> None:
    """H0b: weekly difference B - D (electricity saving) as histogram and QQ plot against the normal distribution."""
    from scipy import stats as sps
    w = wochen[wochen["periode"].isin(["test_1_stunde", "test_2"])]
    d = (w["kosten_D"] - w["kosten_B"]).dropna().to_numpy()        # > 0: B saves more than D
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4))
    a1.hist(d, bins=25, color=BLAU, edgecolor="white", linewidth=1)
    a1.axvline(0, color=GRAU, linewidth=1.2)
    a1.axvline(d.mean(), color=TEXT, linewidth=1.2, linestyle="--")
    a1.annotate(f"Mittel {de(d.mean())} €", (d.mean(), a1.get_ylim()[1] * 0.92), xytext=(-6, 0), textcoords="offset points",
                ha="right", fontsize=8)
    a1.set_xlabel("Ersparnis B minus Ersparnis D in € je Woche")
    a1.set_ylabel("Anzahl Wochen")
    (osm, osr), (steigung, achse, _) = sps.probplot(d, dist="norm")
    a2.scatter(osm, osr, s=12, color=BLAU)
    a2.plot(osm, steigung * np.asarray(osm) + achse, color=GRAU, linewidth=1.2)
    a2.set_xlabel("theoretische Quantile der Normalverteilung")
    a2.set_ylabel("beobachtete Differenz in €")
    a1.set_title("Die Prognose B liegt um null und leicht unter fest 3 Uhr; die Ränder sind breiter als normal")
    speichern(fig, ziel, "g11_differenz_b_minus_d.png")


def g12_wasserfall(netto: pd.DataFrame, ziel: Path) -> None:
    """From the oracle (best possible) down to the net saving of D: where the euros get lost."""
    t = netto[(netto["periode"] == "test_gesamt") & (netto["vertrag"] == "band")].set_index("strategie")
    oracle, d_strom = t.loc["C", "strom_ersparnis_eur_woche"], t.loc["D", "strom_ersparnis_eur_woche"]
    personal, d_netto = t.loc["D", "personal_mehr_eur_woche"], t.loc["D", "netto_eur_woche"]
    schritte = [("Tagesplanung\n(Oracle)", 0, oracle, GRAU), ("Planung eine\nWoche vorher", d_strom, oracle - d_strom, ORANGE),
                ("fest 3 Uhr\nnur Strom", 0, d_strom, BLAU), ("Zuschläge\nPersonal", min(d_strom, d_netto), abs(personal), ORANGE),
                ("fest 3 Uhr\nnetto", 0, d_netto, BLAU)]
    fig, ax = plt.subplots()
    for i, (name, unten, hoehe, farbe) in enumerate(schritte):
        ax.bar(i, hoehe, bottom=unten, width=0.55, color=farbe)
        wert = {1: -(oracle - d_strom), 3: -personal}.get(i, unten + hoehe)
        ax.text(i, unten + hoehe + 20, (f"{de(wert)} €" if i not in (1, 3) else f"{'+' if wert > 0 else '−'}{de(abs(wert))} €"),
                ha="center", fontsize=9)
    ax.set_xticks(range(len(schritte)), [s[0] for s in schritte])
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, oracle * 1.12)
    ax.set_ylabel("Ersparnis gegenüber 22–24 Uhr in € je Woche (Test)")
    ax.set_title("Verloren geht nur, was eine Woche vorher nicht absehbar ist; die Zuschläge kosten fast nichts")
    speichern(fig, ziel, "g12_wasserfall.png")


def g13_kalender(kpi: pd.DataFrame, ziel: Path) -> None:
    """Net saving of D per calendar week x year: 2022 and the summers stand out."""
    k = kpi.copy()
    dt = pd.to_datetime(k["woche"])
    k["jahr"], k["kw"] = dt.dt.isocalendar().year, dt.dt.isocalendar().week
    m = k.pivot_table(index="jahr", columns="kw", values="netto", aggfunc="mean").reindex(columns=range(1, 54))
    fig, ax = plt.subplots(figsize=(9, 3.2))
    bild = ax.imshow(m.to_numpy(), aspect="auto", cmap=SEQ, vmin=0, vmax=np.nanpercentile(m.to_numpy(), 98))
    ax.set_yticks(range(len(m.index)), m.index.astype(str))
    ax.set_xticks([0, 8, 17, 26, 34, 43, 52], ["KW 1", "KW 9", "KW 18", "KW 27", "KW 35", "KW 44", "KW 53"])
    ax.grid(False)
    fig.colorbar(bild, ax=ax, label="€ je Woche", shrink=0.9)
    ax.set_title("Netto-Ersparnis fest 3 Uhr je Kalenderwoche: 2022 und die Sommer am größten, nie negativ")
    speichern(fig, ziel, "g13_kalender_ersparnis.png")


def g14_pareto_ce(ce: pd.DataFrame, ziel: Path) -> None:
    """Pareto of the C&E matrix without a second axis: share as bars, cumulative share as label."""
    c = ce[ce["prozess"] != "GEWICHT"]
    fig, ax = plt.subplots(figsize=(7, 4))
    farben = [BLAU] + [GRAU] * (len(c) - 1)
    ax.bar(range(len(c)), c["anteil_pct"], width=0.55, color=farben)
    for i, (a, k) in enumerate(zip(c["anteil_pct"], c["kumuliert_pct"])):
        ax.text(i, a + 1.5, f"{de(a)} %  (kumuliert {de(k)} %)", ha="center", fontsize=9)
    ax.set_xticks(range(len(c)), c["prozess"])
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, 75)
    ax.set_ylabel("Anteil an der gewichteten Summe in %")
    ax.set_title("C&E-Matrix: Die Reinigung vereint 62 % der Eignung, darum nur sie")
    speichern(fig, ziel, "g14_pareto_ce.png")


def g15_scatter_22_3(matrix: pd.DataFrame, ziel: Path) -> None:
    """Every night: price of the 22 Uhr block against the 3 Uhr block. Below the diagonal = 3 Uhr cheaper."""
    a = mk_block(matrix, 22).set_index("nacht")["preis_eur_mwh"]
    d = mk_block(matrix, 3).set_index("nacht")["preis_eur_mwh"]
    jahr = pd.to_datetime(a.index).year
    fig, ax = plt.subplots(figsize=(6.5, 6))
    for maske, name, farbe in ((jahr == 2022, "2022", ORANGE), (jahr >= 2023, "2023–2026", BLAU)):
        ax.scatter(a[maske], d[maske], s=6, color=farbe, alpha=0.4, linewidths=0, label=name)
    grenze = [min(a.min(), d.min()), max(a.max(), d.max())]
    ax.plot(grenze, grenze, color=GRAU, linewidth=1)
    anteil = (d < a).mean()
    ax.text(grenze[1], grenze[0], f"3 Uhr billiger in {de(100 * anteil)} % der Nächte", ha="right", va="bottom", fontsize=9)
    ax.legend(loc="upper left", frameon=False, fontsize=9, markerscale=3)
    ax.set_xlabel("Preis Block 22–24 Uhr in €/MWh")
    ax.set_ylabel("Preis Block 03–05 Uhr in €/MWh")
    ax.set_title("Jede Nacht ein Punkt: fast alle liegen unter der Diagonalen")
    speichern(fig, ziel, "g15_scatter_22_gegen_3.png")


def mk_block(matrix: pd.DataFrame, start_h: int) -> pd.DataFrame:
    """Block of a given start hour per night (same clock-change rule as R3's block_fuer_start)."""
    rang = (matrix["start_lokal"] - 22) % 24
    return matrix[rang >= (start_h - 22) % 24].sort_values(["nacht", "pos"]).groupby("nacht", as_index=False).first()


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
    pr = pd.read_csv(pfad(p, "processed") / "preise_clean.csv")
    pr["monat"], pr["jahr"] = pd.to_datetime(pr["datum_lokal"]).dt.month, pd.to_datetime(pr["datum_lokal"]).dt.year
    pr = pr[pr["jahr"] >= 2023]
    pr["abw"] = pr["preis_eur_mwh"] - pr.groupby(["jahr", "monat"])["preis_eur_mwh"].transform("mean")
    heat = pr.pivot_table(index="stunde_lokal", columns="monat", values="abw", aggfunc="mean").reset_index()
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
        "test_2 10/2025–09/2026 · test_gesamt = beide Tests (89 Wochen, Testentscheidung nur hier) · stresstest 2022. "
        "Vertrag (A-018): Festpreis deckt den Grundverbrauch, die Reinigung wird zu 100 % am Day-Ahead gekauft (vertrag = band); nur in der Sensitivität V8 zählen 30 %. Annahmen: `docs/annahmen.md`.",
        "",
        "## Kernaussagen",
        "",
        f"- Fest 3 Uhr spart netto {de(netto.query('strategie == \"D\" and periode == \"test_gesamt\" and vertrag == \"band\"')['netto_eur_jahr'].iloc[0])} € pro Jahr "
        "93 % des Möglichen; H0a verworfen (p < 0.001).",
        "- Eine wöchentliche Prognose (B, B_16) ist nicht signifikant besser als fest 3 Uhr (H0b nicht verworfen).",
        "- Tagesplanung lohnt nur, wenn kurzfristiges Personal weniger als rund 2 € pro Stunde Aufpreis kostet (H0c, Kipppunkt).",
        "- Kipppunkt der Empfehlung: mehr als 1.3 h bezahlte Wartezeit je Person und Nacht.",
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
        "## 14 Heatmap Stunde × Monat: Abweichung vom Monatsmittel in €/MWh (2023–2026)",
        "Quelle: `data/preise_clean.csv`; negativ = billiger als der Monatsdurchschnitt.",
        "", tabelle(heat), "",
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
    g7_kumuliert(pd.read_csv(tab / "backtest_wochen.csv"), ziel)
    g8_heatmap_preistal(preise, ziel)
    g9_heatmap_startwahl(pd.read_csv(tab / "backtest_naechte.csv"), ziel)
    g10_box_wochen(pd.read_csv(tab / "backtest_wochen.csv"), ziel)
    g11_differenz_h0b(pd.read_csv(tab / "backtest_wochen.csv"), ziel)
    g12_wasserfall(pd.read_csv(tab / "netto_tests.csv"), ziel)
    g13_kalender(pd.read_csv(tab / "kpi_rollierend.csv"), ziel)
    g14_pareto_ce(pd.read_csv(tab / "ce_matrix.csv"), ziel)
    g15_scatter_22_3(pd.read_csv(tab / "blockkosten_nacht.csv"), ziel)
    print(f"Bericht R1: alle Daten -> {tab / 'daten_fuer_grafiken.md'}; Entwurfsgrafiken -> {ziel}")
    print(sf[["jahr", "vollstaendig", "spot_grundlast_eur_mwh", "spot_profil_eur_mwh", "vorteil_festpreis_eur_mwh",
              "vorteil_festpreis_spotanteil_eur", "vorteil_festpreis_ganzes_werk_eur"]].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
