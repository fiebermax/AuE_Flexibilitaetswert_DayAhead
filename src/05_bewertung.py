# KI: Claude, Zweck: Personalkosten mit Zuschlägen, H0a, Break-even, Kipppunkte, Rücknahmeregel (Phase 4, E-045), geprüft von Caro (R4) durch Erklärzettel, Nachrechnen einer Nacht und pytest
"""Step 5 (R4): is the shift worth it after staff costs, and when does it tip?

Owner: R4 (Caro). Input: ergebnisse/backtest_naechte.csv (R3: chosen block per night and strategy,
electricity cost) and data/preise_clean.csv (R2: calendar of every hour). Output (folder `ergebnisse/`):
  netto_tests.csv        H0a and the net savings of every strategy (electricity minus extra staff cost)
  wirtschaftlichkeit.csv break-even curve: payback time for one-off switching costs (E-044)
  kipppunkte.csv         at which value of a single assumption the net saving of D becomes zero
  kpi_rollierend.csv     the proposed control KPI per week, rolling 13 weeks (recommendation + roll-back rule)
  ce_matrix.csv          C&E matrix: why only the cleaning is studied (weights = team assumption)

Staff cost of one cleaning (A-017, docs/annahmen.md no. 11-15):
  persons x hourly wage x sum over the block hours of (1 + surcharge of that hour)
  surcharge of an hour: night (local hour in kosten.nachtstunden, i.e. 22-06 Uhr), weekend (Saturday or
  Sunday) or Bavarian holiday, each judged by the CALENDAR DAY OF THE HOUR (Sat 22:00 = Saturday,
  Sun 02:00 = Sunday). Rule "hoechster": only the highest applies; "addiert": they add up.
Only the DIFFERENCE to the status quo A matters: the cleaning happens anyway, at night, with the same people.
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
from gemeinsam import lade_params, pfad  # noqa: E402

# Reuse R3's statistics (same t-test, same intervals) instead of a second implementation.
_spec = importlib.util.spec_from_file_location("strategien", SRC / "04_strategien.py")
st = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(st)

BEWERTET = ["D", "B", "B_16", "C"]                 # D = FS1 / H0a, B_16 = FS2, C = daily planning (upper bound)
UMSTELLUNGSKOSTEN_EUR = [0, 5_000, 10_000, 25_000, 50_000, 100_000]   # one-off, grid for the curve (E-044)
KPI_WOCHEN = 13                                   # one quarter: long enough to smooth single weeks


# ---------------------------------------------------------------------------------------------
# Staff cost
# ---------------------------------------------------------------------------------------------
def zuschlag_je_stunde(stunden: pd.DataFrame, kosten: dict) -> pd.Series:
    """Surcharge per hour (0.25 = +25 %). stunden needs stunde_lokal, wochentag, feiertag."""
    nacht = np.where(stunden["stunde_lokal"].isin(kosten["nachtstunden"]), kosten["nachtzuschlag"], 0.0)
    wochenende = np.where(stunden["wochentag"] >= 5, kosten["wochenendzuschlag"], 0.0)
    feiertag = np.where(stunden["feiertag"].astype(bool), kosten["feiertagszuschlag"], 0.0)
    teile = np.vstack([nacht, wochenende, feiertag])
    z = teile.max(axis=0) if kosten["zuschlag_regel"] == "hoechster" else teile.sum(axis=0)
    return pd.Series(z, index=stunden.index)


def personalkosten(naechte: pd.DataFrame, preise: pd.DataFrame, params: dict) -> pd.Series:
    """Staff cost in EUR for every row of backtest_naechte (one cleaning)."""
    k, bh = params["kosten"], params["last"]["blocklaenge_h"]
    kal = preise.set_index("ts_utc")[["stunde_lokal", "wochentag", "feiertag"]]
    start = pd.to_datetime(naechte["start_utc"], utc=True)
    faktor = pd.Series(0.0, index=naechte.index)
    for i in range(bh):                                  # every real hour of the block (UTC: no clock trouble)
        h = kal.loc[(start + pd.Timedelta(hours=i)).dt.strftime("%Y-%m-%dT%H:%M:%SZ")]
        h.index = naechte.index
        faktor += 1 + zuschlag_je_stunde(h, k)
    return k["mitarbeiter"] * k["stundenlohn_eur"] * faktor


def netto_je_woche(naechte: pd.DataFrame, params: dict, vertragsfaktor: float) -> pd.DataFrame:
    """Per week and strategy: electricity saving x contract factor minus extra staff cost, vs. A."""
    w = naechte.groupby(["periode", "woche", "strategie"]).agg(strom=("kosten_eur", "sum"),
                                                                personal=("personal_eur", "sum"),
                                                                n=("nacht", "count")).reset_index()
    w = w[w["n"] == 7]
    a = w[w["strategie"] == "A"].set_index(["periode", "woche"])[["strom", "personal"]]
    x = w[w["strategie"] != "A"].join(a, on=["periode", "woche"], rsuffix="_a")
    x["strom_ersparnis"] = (x["strom_a"] - x["strom"]) * vertragsfaktor
    x["personal_mehr"] = x["personal"] - x["personal_a"]
    x["netto"] = x["strom_ersparnis"] - x["personal_mehr"]
    return x[["periode", "woche", "strategie", "strom_ersparnis", "personal_mehr", "netto"]]


# ---------------------------------------------------------------------------------------------
# Tests, break-even, tipping points, KPI
# ---------------------------------------------------------------------------------------------
def netto_tests(naechte: pd.DataFrame, params: dict) -> pd.DataFrame:
    """H0a (pre-registered: D vs A after staff costs, test_gesamt, contract factor 1.0) plus the same
    numbers for the other strategies, periods and the lower contract factor (descriptive)."""
    alpha = params["statistik"]["alpha_gesamt"] / params["statistik"]["anzahl_hypothesen"]
    zeilen = []
    for art in ("band", "proportional"):
        w = st.mit_testgesamt(netto_je_woche(naechte, params, st.faktor(params, art)))
        for (per, s), g in w.groupby(["periode", "strategie"], sort=False):
            if s not in BEWERTET:
                continue
            d = g["netto"].to_numpy()
            zeilen.append({
                "hypothese": "H0a" if s == "D" else "", "strategie": s, "periode": per, "vertrag": art,
                "konfirmatorisch": s == "D" and per == "test_gesamt" and art == "band",
                "strom_ersparnis_eur_woche": g["strom_ersparnis"].mean(),
                "personal_mehr_eur_woche": g["personal_mehr"].mean(),
                **st.beschreibe(d, params), **st.t_test_einseitig(d, alpha)})
    t = pd.DataFrame(zeilen).rename(columns={"mittel_eur_woche": "netto_eur_woche"})
    t["netto_eur_jahr"] = t["netto_eur_woche"] * 52
    return t


def break_even(tests: pd.DataFrame) -> pd.DataFrame:
    """Payback time of one-off switching costs U: U / net saving per month. Uses the mean and, more
    cautious, the lower end of the 95 % interval. Interface R4 -> R1 (docs/schnittstellen.md)."""
    t = tests[(tests["periode"].isin(["test_gesamt", "stresstest"])) & (tests["strategie"].isin(["D", "B_16"]))]
    zeilen = []
    for _, r in t.iterrows():
        for u in UMSTELLUNGSKOSTEN_EUR:
            monat, monat_vorsichtig = r["netto_eur_woche"] * 52 / 12, r["ki_unten"] * 52 / 12
            zeilen.append({"szenario": f"{r['strategie']} | {r['periode']} | {r['vertrag']}",
                           "strategie": r["strategie"], "periode": r["periode"], "vertrag": r["vertrag"],
                           "ersparnis_eur_jahr": r["netto_eur_jahr"], "umstellungskosten_eur": u,
                           "break_even": round(u / monat, 2) if monat > 0 else np.inf,
                           "break_even_vorsichtig_monate": round(u / monat_vorsichtig, 2) if monat_vorsichtig > 0 else np.inf})
    return pd.DataFrame(zeilen)


def kipppunkte(naechte: pd.DataFrame, params: dict) -> pd.DataFrame:
    """For strategy D in test_gesamt: value of one assumption at which the mean net saving is zero."""
    k, bh = params["kosten"], params["last"]["blocklaenge_h"]
    personalstunden_woche = 7 * k["mitarbeiter"] * bh
    mwh_woche = 7 * params["last"]["mwh_pro_tag"]
    h0c = st.hypothesentests(st.mit_testgesamt(st.je_woche(naechte.drop(columns=["personal_eur"]))), params)
    m_stern = h0c[(h0c["hypothese"] == "H0c") & (h0c["periode"] == "test_gesamt")]["untere_schranke"].iloc[0]
    zeilen = []
    for art in ("band", "proportional"):
        f = st.faktor(params, art)
        d = st.mit_testgesamt(netto_je_woche(naechte, params, f))
        d = d[(d["strategie"] == "D") & (d["periode"] == "test_gesamt")]
        strom, mehr = d["strom_ersparnis"].mean(), d["personal_mehr"].mean()
        zeilen += [{"vertrag": art, **z} for z in _kipp_zeilen(strom, mehr, f, m_stern * f, k, personalstunden_woche, mwh_woche)]
    return pd.DataFrame(zeilen)


def _kipp_zeilen(strom, mehr, f, m_stern, k, personalstunden_woche, mwh_woche) -> list[dict]:
    """One row per assumption; strom = electricity saving per week already times the contract factor f."""
    return [
        {"annahme": "Vertragsfaktor (Anteil der verschobenen MWh am Spot)", "basis": f,
         "kipppunkt": mehr / (strom / f) if strom else np.nan, "einheit": "Faktor",
         "lesart": "darunter frisst der Personal-Mehraufwand die Stromersparnis; <= 0 heißt: kein Kipppunkt"},
        {"annahme": "Aufpreis je Personalstunde für die Verschiebung (zusätzlich zu Lohn und Zuschlägen)",
         "basis": 0.0, "kipppunkt": (strom - mehr) / personalstunden_woche, "einheit": "EUR je Personalstunde",
         "lesart": "so viel mehr pro Stunde dürfte das Personal für 3 statt 22 Uhr kosten"},
        # The real cost driver of moving 22:00 -> 03:00: staff wait after production or come back.
        # Paid extra hours per night (with night surcharge) that eat up the net saving of one night.
        {"annahme": "Zusätzlich bezahlte Stunden je Nacht (Warten oder zweite Anfahrt), mit Nachtzuschlag",
         "basis": 0.0, "kipppunkt": (strom - mehr) / 7 / (k["mitarbeiter"] * k["stundenlohn_eur"] * (1 + k["nachtzuschlag"])),
         "einheit": "Stunden je Person und Nacht",
         "lesart": "muss jede Person länger bezahlt werden als das, kippt die Verschiebung"},
        {"annahme": "Preisunterschied 22-24 Uhr gegen gewählten Block", "basis": strom / f / mwh_woche,
         "kipppunkt": mehr / f / mwh_woche, "einheit": "EUR/MWh",
         "lesart": "fällt die mittlere Spreizung darunter, lohnt die Verschiebung nicht mehr"},
        {"annahme": "Tagesplanung statt Wochenplanung (H0c): Mehrkosten kurzfristiges Personal",
         "basis": np.nan, "kipppunkt": m_stern / personalstunden_woche, "einheit": "EUR je Personalstunde",
         "lesart": "nur wenn kurzfristiges Personal weniger Aufpreis kostet, lohnt die Tagesplanung gegenüber B"},
    ]


def kpi_rollierend(naechte: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Control KPI for the plant: net saving of D vs A per week and rolling over 13 weeks, plus the
    price spread 22-24 Uhr vs. the planned block (EUR/MWh). Roll-back rule: rolling net saving < 0."""
    w = netto_je_woche(naechte, params, 1.0)
    w = w[w["strategie"] == "D"].sort_values("woche").copy()
    w["spreizung_eur_mwh"] = w["strom_ersparnis"] / (7 * params["last"]["mwh_pro_tag"])
    w["netto_rollierend_13w"] = w.groupby("periode")["netto"].transform(lambda x: x.rolling(KPI_WOCHEN).mean())
    w["ruecknahme"] = w["netto_rollierend_13w"] < 0
    return w[["periode", "woche", "strom_ersparnis", "personal_mehr", "netto", "spreizung_eur_mwh",
              "netto_rollierend_13w", "ruecknahme"]]


# ---------------------------------------------------------------------------------------------
# C&E matrix (Operational Intelligence, part E): why only the cleaning is studied (E-043)
# ---------------------------------------------------------------------------------------------
# Team assumption, proposed by Claude, confirmed by Caro in Phase 4 (E-044). Scale 0/1/3/9 = none/weak/
# medium/strong suitability for THIS question (weekly shift plan, day-ahead price). Every criterion is
# phrased so that high = good, so the weighted sum can be ranked directly.
CE_KRITERIEN = {   # criterion: (weight 1-5, why this weight)
    "Steuerbarkeit im Wochenplan": (5, "Kern der Leitfrage: Zeitpunkt muss eine Woche vorher feststehen"),
    "Kein Produktrisiko": (5, "Hygiene, Rohmilch 36-48 h (K-008 P9): ein Risiko für das Produkt schließt einen Prozess aus"),
    "Personalgebunden (Schichtplan relevant)": (4, "nur dann ist es eine Frage des Schichtplans und nicht der Automatik"),
    "Verschiebbare Leistung (MW)": (3, "Hebel in EUR, aber wertlos ohne die drei Kriterien davor"),
    "Datenlage": (2, "belastbare Zahlen vom Partner statt Teamannahmen"),
}
CE_BEWERTUNG = {   # process: ratings in the order of CE_KRITERIEN, with the reason
    "Reinigung (CIP)": ([9, 9, 9, 3, 9], "8-h-Fenster 22-06 Uhr, Pflicht nach 24 h (P10), Zeitarbeit; 4 MW; Zahlen vom Partner (P6, K-012)"),
    "Produktion": ([1, 1, 3, 9, 1], "Rohmilch muss sofort verarbeitet werden (P9), 06-22 Uhr fest; ca. 7 MW; keine Daten zur Verschiebung"),
    "Kälte": ([3, 3, 1, 1, 3], "läuft automatisch, Vorkühlung 2 h nur angenommen (A1); 1 MW; Produkttemperatur als Risiko"),
}


def ce_matrix() -> pd.DataFrame:
    """Weighted sum per process, sorted (Pareto order) with cumulative share."""
    gewichte = [g for g, _ in CE_KRITERIEN.values()]
    zeilen = []
    for prozess, (werte, grund) in CE_BEWERTUNG.items():
        zeilen.append({"prozess": prozess, **dict(zip(CE_KRITERIEN, werte)),
                       "summe_gewichtet": int(np.dot(gewichte, werte)), "begruendung": grund})
    m = pd.DataFrame(zeilen).sort_values("summe_gewichtet", ascending=False)
    m["anteil_pct"] = 100 * m["summe_gewichtet"] / m["summe_gewichtet"].sum()
    m["kumuliert_pct"] = m["anteil_pct"].cumsum()
    gew = pd.DataFrame([{"prozess": "GEWICHT", **{k: g for k, (g, _) in CE_KRITERIEN.items()},
                         "begruendung": " | ".join(f"{k}: {w}" for k, (_, w) in CE_KRITERIEN.items())}])
    return pd.concat([gew, m], ignore_index=True)


def main() -> None:
    p = lade_params()
    ziel = pfad(p, "tables")
    datei = ziel / "backtest_naechte.csv"
    if not datei.exists():
        raise FileNotFoundError(f"{datei} fehlt. Zuerst src/04_strategien.py (R3) ausführen.")
    naechte = pd.read_csv(datei)
    preise = pd.read_csv(pfad(p, "processed") / "preise_clean.csv")
    naechte["personal_eur"] = personalkosten(naechte, preise, p)

    tests = netto_tests(naechte, p)
    be, kp, kpi = break_even(tests), kipppunkte(naechte, p), kpi_rollierend(naechte, p)
    tests.round(4).to_csv(ziel / "netto_tests.csv", index=False)
    be.to_csv(ziel / "wirtschaftlichkeit.csv", index=False)
    kp.round(3).to_csv(ziel / "kipppunkte.csv", index=False)
    kpi.round(2).to_csv(ziel / "kpi_rollierend.csv", index=False)
    ce = ce_matrix()
    ce.round(1).to_csv(ziel / "ce_matrix.csv", index=False)

    print(f"Bewertung R4 -> {ziel}")
    sicht = tests[(tests["vertrag"] == "band") & tests["periode"].isin(["test_gesamt", "stresstest"])]
    print(sicht[["strategie", "periode", "strom_ersparnis_eur_woche", "personal_mehr_eur_woche", "netto_eur_woche",
                 "ki_unten", "ki_oben", "p_t", "h0_verworfen", "netto_eur_jahr"]].round(2).to_string(index=False))
    print("\nKipppunkte (D, Test gesamt):")
    print(kp[["vertrag", "annahme", "basis", "kipppunkt", "einheit"]].round(3).to_string(index=False))
    print(f"\nRücknahmeregel (13 Wochen netto < 0) hätte ausgelöst in {int(kpi['ruecknahme'].sum())} von "
          f"{int(kpi['netto_rollierend_13w'].notna().sum())} Wochen.")
    print("\nC&E-Matrix:")
    print(ce[["prozess", "summe_gewichtet", "anteil_pct", "kumuliert_pct"]].iloc[1:].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
