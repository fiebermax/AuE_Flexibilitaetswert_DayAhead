# KI: Claude, Zweck: Blockkosten-Matrix je Nacht und Startstunde, Kalendermerkmale, saisonaler Block (Phase 1, E-045), geprüft von Susan (R3) durch Erklärzettel, Nachrechnen einer Nacht und pytest
"""Step 3 (R3): features for the cleaning case S1.

Owner: R3 (Susan). Input: data/preise_clean.csv (R2). Output (folder `ergebnisse/`):
  blockkosten_nacht.csv  one row per night x possible 2-h block (the "Blockkosten-Matrix", long format)
  saisonaler_block.csv   best fixed start hour, learned on the TRAINING nights only (all year + per season)

Why a long table (one row per block) instead of a wide one (one column per start hour):
in the October night the clock shows 02:00 twice, in the March night 02:00 is missing. A night has
7, 8 or 6 possible blocks, and two blocks can share the label "2". One row per block with its real
UTC start keeps that exact; a wide view is one pivot away.

Why prices of a night are complete here, including the Sunday night until Monday 06:00 (E-044):
the matrix is built from the full price file. It is used to EVALUATE a plan with real prices and,
restricted to training nights, to LEARN fixed rules. A strategy that plans on a Friday must build
its own matrix from `w.historie` only (Phase 2); the function below accepts any price table.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))     # make the other files in src/ importable
from gemeinsam import fensterstunden, lade_params, pfad  # noqa: E402

SAISONS = ["Winter", "Fruehling", "Sommer", "Herbst"]


# ---------------------------------------------------------------------------------------------
# Blockkosten-Matrix
# ---------------------------------------------------------------------------------------------
def blockkosten(preise: pd.DataFrame, fenster_start: int, fenster_ende: int, block_h: int) -> pd.DataFrame:
    """One row per night and possible block of `block_h` consecutive real hours inside the window.

    preise needs: ts_utc, datum_lokal, stunde_lokal, wochentag, saison, preis_eur_mwh, sonntag, feiertag.
    A night is named after the day it starts (22:00); hours after midnight belong to the previous day,
    exactly as in fensteranalyse.fenster_je_tag (R2), so both tables use the same nights.
    Incomplete nights (data edge, or a history that ends in the middle of a night) are dropped.
    """
    d = preise[["ts_utc", "datum_lokal", "stunde_lokal", "wochentag", "saison", "preis_eur_mwh",
                "sonntag", "feiertag"]].copy()
    d["ts_utc"] = pd.to_datetime(d["ts_utc"], utc=True)
    stunden_fenster = fensterstunden(fenster_start, fenster_ende)          # [22, 23, 0, ..., 5]
    d = d[d["stunde_lokal"].isin(stunden_fenster)].sort_values("ts_utc")   # real time order, not clock order

    # Night date = calendar day of the hour, minus one day for the hours after midnight.
    datum = pd.to_datetime(d["datum_lokal"])
    nach_mitternacht = d["stunde_lokal"] < fenster_start if fenster_start > fenster_ende else False
    d["nacht"] = datum.where(~nach_mitternacht, datum - pd.Timedelta(days=1)).dt.strftime("%Y-%m-%d")

    letzte = stunden_fenster[-1]
    zeilen = []
    for nacht, g in d.groupby("nacht", sort=True):
        h = g["stunde_lokal"].to_numpy()
        lueckenlos = (g["ts_utc"].diff().dropna() == pd.Timedelta(hours=1)).all()
        if not lueckenlos or h[0] != fenster_start or h[-1] != letzte:
            continue                                                     # incomplete night
        preis = g["preis_eur_mwh"].to_numpy()
        so, ft = g["sonntag"].to_numpy(), g["feiertag"].to_numpy()
        erste = g.iloc[0]                                                # 22:00 hour: weekday/season of the night
        for i in range(len(preis) - block_h + 1):
            zeilen.append({
                "nacht": nacht, "wochentag_nacht": int(erste["wochentag"]), "saison": erste["saison"],
                "n_stunden_nacht": len(preis), "pos": i,
                "start_lokal": int(h[i]), "start_utc": g["ts_utc"].iloc[i],
                # constant power over the block -> cost per MWh = mean of the hourly prices
                "preis_eur_mwh": preis[i:i + block_h].mean(),
                # hours of the block that fall on a Sunday / Bavarian holiday (calendar day of the hour,
                # A-017); R4 needs them for the surcharges, R3 does not use them
                "sonntag_h": int(so[i:i + block_h].sum()), "feiertag_h": int(ft[i:i + block_h].sum()),
            })
    m = pd.DataFrame(zeilen)
    if len(m):
        m["start_utc"] = m["start_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return m


def block_fuer_start(matrix: pd.DataFrame, start_h: int, fenster_start: int) -> pd.DataFrame:
    """For every night pick the block that starts at clock time `start_h`.

    Rule for the clock changes: October (02:00 twice) -> the first 02:00 block; March (02:00 missing)
    -> the next block in the night, i.e. the one starting 03:00. Implemented as: first block whose start
    is at or after start_h in NIGHT order (22, 23, 0, 1, ...), so 0 comes after 23, not before 22.
    """
    rang = (matrix["start_lokal"] - fenster_start) % 24                  # 22 -> 0, 23 -> 1, 0 -> 2, ...
    ziel = (start_h - fenster_start) % 24
    kandidat = matrix[rang >= ziel]
    return kandidat.sort_values(["nacht", "pos"]).groupby("nacht", as_index=False).first()


def billigster_block(matrix: pd.DataFrame) -> pd.DataFrame:
    """Per night the cheapest block (earliest one if prices tie, as in fensteranalyse)."""
    return matrix.sort_values(["nacht", "preis_eur_mwh", "pos"]).groupby("nacht", as_index=False).first()


# ---------------------------------------------------------------------------------------------
# Seasonal block (feature for D_saison; learned on training nights only)
# ---------------------------------------------------------------------------------------------
def bester_fester_start(matrix: pd.DataFrame, fenster_start: int, nach_saison: bool) -> pd.DataFrame:
    """Start hour with the lowest mean block price over the given nights (all year, or per season).

    Mean, not median: the plant pays the sum over all nights, and the sum is minimised by the lowest
    MEAN. The median would ignore the expensive nights that make up the bill.
    Each start hour is evaluated with block_fuer_start, i.e. with the clock-change rule above, so the
    learned rule is exactly what D will do later.
    """
    starts = sorted(matrix["start_lokal"].unique(), key=lambda h: (h - fenster_start) % 24)
    gruppen = [(s, matrix[matrix["saison"] == s]) for s in SAISONS] if nach_saison else [("Gesamt", matrix)]
    zeilen = []
    for name, g in gruppen:
        mittel = {h: block_fuer_start(g, h, fenster_start)["preis_eur_mwh"].mean() for h in starts}
        best = min(starts, key=lambda h: (mittel[h], (h - fenster_start) % 24))   # tie -> earlier in the night
        zeilen.append({"saison": name, "naechte": g["nacht"].nunique(), "start_lokal": int(best),
                       "mittel_eur_mwh": mittel[best],
                       **{f"mittel_start_{h:02d}": mittel[h] for h in starts}})
    return pd.DataFrame(zeilen)


def training_naechte(matrix: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Nights that start inside the training period (zeitraeume.training). Nothing from 2025 or 2022."""
    von, bis = params["zeitraeume"]["training"]
    n = pd.to_datetime(matrix["nacht"])
    return matrix[(n >= pd.Timestamp(von)) & (n <= pd.Timestamp(bis))]


def main() -> None:
    p = lade_params()
    last = p["last"]
    preise = pd.read_csv(pfad(p, "processed") / "preise_clean.csv")
    matrix = blockkosten(preise, last["fenster_start_h"], last["fenster_ende_h"], last["blocklaenge_h"])
    train = training_naechte(matrix, p)
    block = pd.concat([bester_fester_start(train, last["fenster_start_h"], nach_saison=False),
                       bester_fester_start(train, last["fenster_start_h"], nach_saison=True)], ignore_index=True)

    ziel = pfad(p, "tables")
    ziel.mkdir(parents=True, exist_ok=True)
    matrix.round(4).to_csv(ziel / "blockkosten_nacht.csv", index=False)
    block.round(2).to_csv(ziel / "saisonaler_block.csv", index=False)
    print(f"Merkmale: {matrix['nacht'].nunique()} Nächte, {len(matrix)} Blöcke -> {ziel / 'blockkosten_nacht.csv'}")
    print(f"Fester Block aus dem Training ({train['nacht'].nunique()} Nächte, nur 2023-2024):")
    print(block[["saison", "naechte", "start_lokal", "mittel_eur_mwh"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
