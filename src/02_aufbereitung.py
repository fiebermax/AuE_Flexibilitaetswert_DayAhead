# KI: Claude, Zweck: Aufbereitung SMARD-Preise (Zeitzone, Zeitumstellung, 15->60 min, Werktage, Datenqualität), geprüft von <Name R2> durch Review, Nachrechnen einzelner Tage und pytest
"""Schritt 2: SMARD-Rohdaten -> aufbereitete Preisreihen und Datenqualitätstabelle.

Owner: R2. Eingabe: data/raw/smard/ (aus Schritt 1). Ausgabe (Spalten siehe docs/schnittstellen.md):
  data/interim/preise_utc.parquet        stündliche Reihe in UTC, vor der Umrechnung in deutsche Zeit
  data/processed/preise_h.parquet        zeit, preis_eur_mwh, regime, werktag   (Übergabe an R3)
  data/processed/preise_15min.parquet    dieselben Spalten, 15-min-Werte ab Regimewechsel (Sensitivität)
  data/processed/zeitumstellung.csv      Tage mit Zeitumstellung und wie sie behandelt wurden
  results/tables/datenqualitaet.csv      Lücken, Duplikate, negative Preise, Aggregationsprüfung

Regeln (Begründung im Projekttagebuch):
  * Zeit: SMARD liefert UTC. Ausgabe in Europe/Berlin, `zeit` = Beginn der Stunde bzw. Viertelstunde.
  * Zeitumstellung Oktober: die doppelte Stunde 02:00-03:00 wird gemittelt (ein Wert je Uhrzeit).
  * Zeitumstellung März: 02:00 Uhr existiert nicht; der Tag hat 23 Zeilen. Nichts wird aufgefüllt;
    die Tage stehen in zeitumstellung.csv und in der Datenqualitätstabelle.
  * Echte Lücken (SMARD liefert null) bleiben als Zeile mit leerem Preis stehen und werden gezählt.
  * Ab Regimewechsel: Stundenpreis = Mittel der vier Viertelstunden, nur wenn alle vier vorhanden sind.
  * Negative Preise sind echte Marktergebnisse und bleiben drin.
"""
import csv
import json
import sys
from pathlib import Path

import holidays
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import lade_params, pfad  # noqa: E402

SPALTEN = ["zeit", "preis_eur_mwh", "regime", "werktag"]  # exakt laut docs/schnittstellen.md


class AufbereitungsFehler(RuntimeError):
    pass


# ---------------------------------------------------------------------------------------------
# Einlesen
# ---------------------------------------------------------------------------------------------
def lies_roh(raw: Path, aufl: str) -> tuple[pd.Series, pd.DatetimeIndex]:
    """Alle aktiven SMARD-Dateien einer Auflösung zu einer Reihe (Index UTC) zusammenfügen.

    Gibt zusätzlich die doppelten UTC-Zeitstempel zurück (gleicher Zeitpunkt zweimal geliefert).
    Gleiche Werte: ein Exemplar bleibt. Unterschiedliche Werte: Abbruch, weil unklar ist, welcher stimmt.
    """
    manifest = raw / "smard" / "manifest.csv"
    if not manifest.exists():
        raise AufbereitungsFehler(f"{manifest} fehlt. Zuerst Schritt 1 ausführen: python src/01_download.py")
    with open(manifest, newline="", encoding="utf-8") as f:
        dateien = [raw / z["datei"] for z in csv.DictReader(f) if z["aufloesung"] == aufl and z["status"] == "aktiv"]
    if not dateien:
        raise AufbereitungsFehler(f"Keine Rohdateien für Auflösung '{aufl}' im Manifest.")

    teile = []
    for d in dateien:
        if not d.exists():
            raise AufbereitungsFehler(f"Rohdatei fehlt: {d}. Schritt 1 erneut ausführen.")
        serie = json.loads(d.read_bytes())["series"]
        teile.append(pd.DataFrame(serie, columns=["ms", "preis"]))
    df = pd.concat(teile, ignore_index=True)
    df["zeit_utc"] = pd.to_datetime(df["ms"], unit="ms", utc=True)

    dup = df["zeit_utc"].duplicated(keep="first")
    doppelte = pd.DatetimeIndex(df.loc[dup, "zeit_utc"])
    if len(doppelte):
        widerspruch = df[df["zeit_utc"].duplicated(keep=False)].groupby("zeit_utc")["preis"].nunique(dropna=False)
        if (widerspruch > 1).any():
            raise AufbereitungsFehler(f"Doppelte Zeitstempel mit unterschiedlichen Preisen in '{aufl}':\n"
                                      f"{widerspruch[widerspruch > 1].head()}")
        df = df[~dup]
    s = df.set_index("zeit_utc")["preis"].astype(float).sort_index()
    return s, doppelte


# ---------------------------------------------------------------------------------------------
# Kernlogik (auch in tests/ direkt mit kleinen Beispielen geprüft)
# ---------------------------------------------------------------------------------------------
def viertel_zu_stunde(s15: pd.Series) -> tuple[pd.Series, int]:
    """Stundenmittel aus Viertelstunden (Index UTC). Fehlt eine der vier Viertelstunden, bleibt die Stunde leer.

    Gerechnet wird in UTC: dort hat jede Stunde genau vier Viertelstunden, auch an Tagen mit Zeitumstellung.
    Rückgabe: Stundenreihe und Anzahl unvollständiger Stunden.
    """
    stunde = s15.index.floor("h")
    gruppe = s15.groupby(stunde)
    mittel = gruppe.mean()
    vollstaendig = gruppe.count() == 4
    return mittel.where(vollstaendig), int((~vollstaendig).sum())


def zu_ortszeit(s_utc: pd.Series, tz: str) -> tuple[pd.Series, int]:
    """UTC-Reihe -> Reihe mit einem Wert je Uhrzeit in deutscher Zeit (Europe/Berlin).

    Oktober: Die Uhr zeigt 02:00-03:00 zweimal. Beide Werte werden gemittelt und unter der ersten
    (Sommerzeit-)Fassung von 02:00 abgelegt. Fehlt einer der beiden Werte, bleibt das Ergebnis leer.
    März: 02:00-03:00 gibt es nicht. Diese Uhrzeit taucht nicht auf, es wird nichts erfunden.
    Rückgabe: Reihe mit Index Europe/Berlin und Anzahl gemittelter (doppelter) Uhrzeiten.
    """
    wanduhr = s_utc.index.tz_convert(tz).tz_localize(None)       # Uhrzeit, wie sie auf der Uhr steht
    gruppe = s_utc.groupby(wanduhr)
    mittel = gruppe.mean()
    hat_luecke = s_utc.isna().groupby(wanduhr).any()
    mittel[hat_luecke] = np.nan                                  # kein stilles Auffüllen durch skipna
    n_doppelt = int((gruppe.size() > 1).sum())
    zeit = mittel.index.tz_localize(tz, ambiguous=np.ones(len(mittel), dtype=bool), nonexistent="raise")
    return pd.Series(mittel.to_numpy(), index=zeit), n_doppelt


def erwartetes_raster(beginn: pd.Timestamp, ende: pd.Timestamp, freq: str, tz: str) -> pd.DatetimeIndex:
    """Alle Uhrzeiten (deutsche Zeit) in [beginn, ende), nach derselben Regel wie zu_ortszeit."""
    utc = pd.date_range(beginn.tz_convert("UTC"), ende.tz_convert("UTC"), freq=freq, inclusive="left")
    wanduhr = utc.tz_convert(tz).tz_localize(None).unique()
    return wanduhr.tz_localize(tz, ambiguous=np.ones(len(wanduhr), dtype=bool), nonexistent="raise")


def werktage(daten: pd.DatetimeIndex, mariae_himmelfahrt: bool) -> np.ndarray:
    """Mo-Fr und kein gesetzlicher Feiertag in Bayern. Mariä Himmelfahrt (15.08.) gilt nur in Gemeinden
    mit überwiegend katholischer Bevölkerung, deshalb als Variante schaltbar (params.yaml)."""
    kategorien = ("public", "catholic") if mariae_himmelfahrt else ("public",)
    jahre = range(daten.min().year, daten.max().year + 1)
    feiertage = holidays.Germany(subdiv="BY", years=jahre, categories=kategorien)
    tage = daten.tz_localize(None).normalize()
    ist_feiertag = np.array([t.date() in feiertage for t in tage])
    return (tage.weekday < 5) & ~ist_feiertag


def baue_tabelle(s_ort: pd.Series, raster: pd.DatetimeIndex, wechsel: pd.Timestamp, mariae: bool) -> pd.DataFrame:
    s = s_ort.reindex(raster)  # echte Lücken werden hier zu sichtbaren leeren Zeilen
    df = pd.DataFrame({"zeit": raster, "preis_eur_mwh": s.to_numpy()})
    df["regime"] = np.where(df["zeit"] >= wechsel, "viertel", "stunde")
    df["werktag"] = werktage(pd.DatetimeIndex(df["zeit"]), mariae)
    return df[SPALTEN]


# ---------------------------------------------------------------------------------------------
# Datenqualität
# ---------------------------------------------------------------------------------------------
def zeitumstellungstage(s_utc: pd.Series, df: pd.DataFrame, pro_tag: int, aufl: str, tz: str) -> pd.DataFrame:
    """Tage, an denen SMARD mehr oder weniger als pro_tag Zeitpunkte liefert (Zeitumstellung), mit Behandlung."""
    roh = pd.Series(s_utc.index.tz_convert(tz).date).value_counts()
    roh = roh[roh != pro_tag].sort_index()
    nachher = df.groupby(df["zeit"].dt.date).size()
    return pd.DataFrame({
        "aufloesung": aufl,
        "datum": [str(d) for d in roh.index],
        "zeitpunkte_roh": roh.to_numpy(),
        "zeitpunkte_aufbereitet": [int(nachher.get(d, 0)) for d in roh.index],
        "art": np.where(roh.to_numpy() < pro_tag, "Maerz: 02-03 Uhr existiert nicht, nicht aufgefuellt",
                        "Oktober: doppelte 02-03 Uhr gemittelt"),
    })


def qualitaet(df: pd.DataFrame, aufl: str, doppelte_roh: pd.DatetimeIndex, zu: pd.DataFrame, tz: str,
              extra: dict | None = None) -> pd.DataFrame:
    """Eine Zeile je Jahr und Regime: Vollständigkeit, Duplikate, Zeitumstellung, negative Preise."""
    zeilen = []
    df = df.assign(jahr=df["zeit"].dt.year)
    dup_jahr = pd.Series(doppelte_roh.tz_convert(tz).year).value_counts() if len(doppelte_roh) else pd.Series(dtype=int)
    zu_jahr = zu.assign(jahr=pd.to_datetime(zu["datum"]).dt.year)
    for (jahr, regime), g in df.groupby(["jahr", "regime"]):
        p = g["preis_eur_mwh"]
        tage = set(g["zeit"].dt.date.astype(str))
        zj = zu_jahr[zu_jahr["datum"].isin(tage)]
        z = {
            "aufloesung": aufl, "jahr": jahr, "regime": regime,
            "zeitpunkte": len(g),
            "mit_preis": int(p.notna().sum()),
            "luecken": int(p.isna().sum()),
            "doppelte_zeitstempel_roh": int(dup_jahr.get(jahr, 0)),
            "zeitumstellung_maerz_tage": int(zj["art"].str.startswith("Maerz").sum()),
            "zeitumstellung_oktober_tage": int(zj["art"].str.startswith("Oktober").sum()),
            "negative_preise": int((p < 0).sum()),
            "anteil_negativ_pct": round(100 * float((p < 0).mean()), 2),
            "preis_null": int((p == 0).sum()),
            "preis_min": p.min(), "preis_mittel": round(p.mean(), 2), "preis_max": p.max(),
        }
        z.update((extra or {}).get(regime, {}))
        zeilen.append(z)
    return pd.DataFrame(zeilen)


# ---------------------------------------------------------------------------------------------
# Hauptablauf
# ---------------------------------------------------------------------------------------------
def main() -> None:
    p = lade_params()
    tz = p["markt"]["zeitzone"]
    mariae = bool(p["last"]["feiertagsvariante_mariae_himmelfahrt"])
    raw, interim, processed, tables = (pfad(p, k) for k in ("raw", "interim", "processed", "tables"))
    for o in (interim, processed, tables):
        o.mkdir(parents=True, exist_ok=True)

    beginn = pd.Timestamp(p["daten"]["aufloesungen"]["hour"]).tz_localize(tz)
    ende = (pd.Timestamp(p["zeitraeume"]["datenstand"]) + pd.Timedelta(days=1)).tz_localize(tz)
    wechsel = pd.Timestamp(p["markt"]["regimewechsel"]).tz_localize(tz)
    if pd.Timestamp(p["daten"]["aufloesungen"]["quarterhour"]).tz_localize(tz) > wechsel:
        raise AufbereitungsFehler("Viertelstunden müssen spätestens ab markt.regimewechsel geladen sein.")

    # 1) Rohdaten einlesen
    s_h_roh, dup_h = lies_roh(raw, "hour")
    s_q_roh, dup_q = lies_roh(raw, "quarterhour")

    # 2) Stundenregime: SMARD-Stundenwerte; Viertelstundenregime: eigene Stundenmittel aus 15 min
    s_h_alt = s_h_roh[(s_h_roh.index >= beginn) & (s_h_roh.index < wechsel)]
    s_q = s_q_roh[(s_q_roh.index >= wechsel) & (s_q_roh.index < ende)]
    s_h_neu, n_unvollst = viertel_zu_stunde(s_q)

    # Aggregationsprüfung: unser Stundenmittel gegen die Stundenwerte, die SMARD selbst ausweist.
    # Gleiche Quelle, also keine unabhängige Prüfung, sondern eine Prüfung auf Rechen-/Übertragungsfehler.
    vergleich = pd.concat([s_h_neu.rename("eigen"), s_h_roh.rename("smard")], axis=1, join="inner").dropna()
    abw = (vergleich["eigen"] - vergleich["smard"]).abs()
    pruefung = {"viertel": {"unvollstaendige_stunden_aus_15min": n_unvollst,
                            "abw_smard_stunde_max_eur": round(abw.max(), 4) if len(abw) else np.nan,
                            "abw_smard_stunde_mittel_eur": round(abw.mean(), 4) if len(abw) else np.nan,
                            "abw_smard_stunde_n": len(abw)}}

    s_utc = pd.concat([s_h_alt, s_h_neu]).sort_index()
    pd.DataFrame({"zeit_utc": s_utc.index, "preis_eur_mwh": s_utc.to_numpy(),
                  "quelle": np.where(s_utc.index < wechsel, "smard_hour", "mittel_aus_quarterhour")}
                 ).to_parquet(interim / "preise_utc.parquet", index=False)

    # 3) Deutsche Zeit, Zeitumstellung, Raster, Werktage
    s_ort, _ = zu_ortszeit(s_utc, tz)
    preise_h = baue_tabelle(s_ort, erwartetes_raster(beginn, ende, "h", tz), wechsel, mariae)

    s_q_ort, _ = zu_ortszeit(s_q, tz)
    preise_15 = baue_tabelle(s_q_ort, erwartetes_raster(wechsel, ende, "15min", tz), wechsel, mariae)

    # 4) Speichern
    preise_h.to_parquet(processed / "preise_h.parquet", index=False)
    preise_15.to_parquet(processed / "preise_15min.parquet", index=False)

    zu_h = zeitumstellungstage(s_utc, preise_h, 24, "hour", tz)
    zu_q = zeitumstellungstage(s_q, preise_15, 96, "quarterhour", tz)
    pd.concat([zu_h, zu_q]).to_csv(processed / "zeitumstellung.csv", index=False)

    dq = pd.concat([
        qualitaet(preise_h, "hour", dup_h.append(dup_q[dup_q >= wechsel]), zu_h, tz, pruefung),
        qualitaet(preise_15, "quarterhour", dup_q[dup_q >= wechsel], zu_q, tz),
    ], ignore_index=True)
    dq.to_csv(tables / "datenqualitaet.csv", index=False)

    print(f"Aufbereitung: {len(preise_h)} Stunden ({preise_h['preis_eur_mwh'].isna().sum()} Lücken), "
          f"{len(preise_15)} Viertelstunden; Datenqualität -> {tables / 'datenqualitaet.csv'}")


if __name__ == "__main__":
    try:
        main()
    except AufbereitungsFehler as e:
        sys.exit(f"FEHLER in 02_aufbereitung: {e}")
