# KI: Claude, Zweck: SMARD-Download mit Cache, Retry und Manifest, geprüft von <Name R2> durch Review, Offline-Lauf und pytest
"""Schritt 1: SMARD-Rohdaten laden (nur falls nicht in data/raw) und unverändert ablegen.

Owner: R2. Ausgabe:
  data/raw/smard/<filter>/<auflösung>/<filter>_<region>_<auflösung>_<ts>.json   (Original-Bytes von SMARD)
  data/raw/smard/manifest.csv   (je Datei: URL, Abrufzeitpunkt, SHA256, Bytes, SMARD-Erstellzeitpunkt)
  data/raw/SOURCES.md           (Zusammenfassung, automatisch erzeugter Abschnitt)

SMARD liefert je Woche eine JSON-Datei. Eine Woche beginnt Montag 00:00 Uhr deutscher Zeit; <ts> ist
dieser Zeitpunkt in Millisekunden seit 1970 (UTC). Darin: {"meta_data": {...}, "series": [[ts_ms, preis], ...]}.

Ablauf:
  1. Benötigte Wochen aus params.yaml berechnen (daten.aufloesungen, zeitraeume.datenstand).
  2. Vorhandene Dateien gegen manifest.csv prüfen (SHA256): Rohdaten dürfen sich nie ändern.
  3. Fehlende Wochen laden (mit Retry). Sind alle Dateien da, läuft der Schritt komplett offline.
  4. Eine Datei, die abgerufen wurde, bevor ihre Woche vorbei war, und der deshalb Werte im benötigten
     Zeitraum fehlen, wird neu geladen; die alte Datei bleibt als *.veraltet-<datum>.json liegen.
"""
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import ROOT, lade_params, pfad  # noqa: E402

MANIFEST_SPALTEN = [
    "datei", "quelle", "filter", "region", "aufloesung", "woche_start_utc_ms", "woche_start_berlin",
    "url", "abgerufen_am_utc", "smard_created_utc", "bytes", "sha256", "status",
]
MARKER_START = "<!-- manifest:start (automatisch von src/01_download.py erzeugt, nicht von Hand ändern) -->"
MARKER_ENDE = "<!-- manifest:ende -->"


class DownloadFehler(RuntimeError):
    """Download nicht möglich: Meldung sagt, welche Datei und was zu tun ist."""


# ---------------------------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------------------------
def sha256(daten: bytes) -> str:
    return hashlib.sha256(daten).hexdigest()


def jetzt_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ms_zu_utc(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def benoetigter_zeitraum(von: str, datenstand: str, tz: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """[Beginn, Ende) in deutscher Zeit: von 00:00 Uhr bis zum Tag nach dem Datenstand 00:00 Uhr."""
    beginn = pd.Timestamp(von).tz_localize(tz)
    ende = (pd.Timestamp(datenstand) + pd.Timedelta(days=1)).tz_localize(tz)
    return beginn, ende


def wochenanfaenge(beginn: pd.Timestamp, ende: pd.Timestamp, tz: str) -> list[pd.Timestamp]:
    """Alle Montage 00:00 Uhr (deutsche Zeit), deren Woche den Zeitraum [beginn, ende) berührt.

    Gerechnet wird mit Kalendertagen ohne Uhrzeit und erst danach die Zeitzone gesetzt. So bleibt der
    Wochenanfang auch in Wochen mit Zeitumstellung exakt auf Montag 00:00 Uhr.
    """
    erster_montag = beginn.tz_localize(None).normalize()
    erster_montag -= pd.Timedelta(days=erster_montag.weekday())
    letzter_tag = (ende - pd.Timedelta(seconds=1)).tz_localize(None).normalize()
    montage = pd.date_range(erster_montag, letzter_tag, freq="7D")  # ohne Zeitzone: echte Kalendertage
    return [m.tz_localize(tz) for m in montage]


def ms(ts: pd.Timestamp) -> int:
    return int(ts.tz_convert("UTC").timestamp() * 1000)


def http_session(versuche: int) -> requests.Session:
    """Session mit automatischem Retry bei Verbindungsfehlern und Serverfehlern (429, 5xx).

    Wartezeiten wachsen exponentiell (1 s, 2 s, 4 s, ...), damit ein kurzer Ausfall von SMARD
    den Lauf nicht abbricht, ein dauerhafter aber schnell gemeldet wird.
    """
    retry = Retry(total=versuche, connect=versuche, read=versuche, status=versuche,
                  backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=("GET",), raise_on_status=False)
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers["User-Agent"] = "aue-strom-analyse (Hochschulprojekt)"
    return s


def lade_url(session: requests.Session, url: str, timeout: int) -> bytes:
    try:
        r = session.get(url, timeout=timeout)
    except requests.exceptions.RequestException as e:
        raise DownloadFehler(
            f"Keine Verbindung zu SMARD nach mehreren Versuchen.\n  URL: {url}\n  Ursache: {e}\n"
            "  Lösung: Internetverbindung prüfen und erneut starten. Bereits geladene Dateien bleiben erhalten."
        ) from e
    if r.status_code == 404:
        raise DownloadFehler(f"SMARD kennt diese Datei nicht (404): {url}\n"
                             "  Prüfen: Filter, Region und Auflösung in config/params.yaml.")
    if r.status_code != 200:
        raise DownloadFehler(f"SMARD antwortet mit HTTP {r.status_code}: {url}")
    return r.content


def fehlende_werte_im_zeitraum(inhalt: bytes, beginn_ms: int, ende_ms: int) -> int:
    """Anzahl Zeitpunkte im benötigten Zeitraum, für die die Datei keinen Preis (null) enthält."""
    serie = json.loads(inhalt)["series"]
    return sum(1 for t, v in serie if beginn_ms <= t < ende_ms and v is None)


# ---------------------------------------------------------------------------------------------
# Manifest und SOURCES.md
# ---------------------------------------------------------------------------------------------
def lies_manifest(datei: Path) -> list[dict]:
    if not datei.exists():
        return []
    with open(datei, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def schreibe_manifest(datei: Path, zeilen: list[dict]) -> None:
    zeilen = sorted(zeilen, key=lambda z: (z["aufloesung"], int(z["woche_start_utc_ms"]), z["datei"]))
    with open(datei, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_SPALTEN, lineterminator="\n")
        w.writeheader()
        w.writerows(zeilen)


def pruefe_integritaet(raw: Path, manifest: list[dict]) -> None:
    """Jede als aktiv geführte Datei muss existieren und denselben SHA256 haben wie beim Abruf."""
    for z in manifest:
        if z["status"] != "aktiv":
            continue
        f = raw / z["datei"]
        if f.exists() and sha256(f.read_bytes()) != z["sha256"]:
            raise DownloadFehler(
                f"Rohdatei wurde verändert: {f}\n  SHA256 laut Manifest: {z['sha256']}\n"
                "  Rohdaten dürfen nie überschrieben werden. Datei aus Git wiederherstellen (git checkout -- <datei>)."
            )


def aktualisiere_sources(sources: Path, manifest: list[dict], manifest_datei: Path) -> None:
    """Schreibt die Zusammenfassung je Auflösung zwischen die Marker in SOURCES.md."""
    df = pd.DataFrame([z for z in manifest if z["status"] == "aktiv"])
    zeilen = [MARKER_START, "",
              "### SMARD-Abrufe (Stand dieses Laufs)", "",
              f"Je Datei URL, Abrufzeitpunkt und SHA256 in `{manifest_datei.relative_to(sources.parent).as_posix()}` "
              f"(SHA256 des Manifests: `{sha256(manifest_datei.read_bytes())}`).", "",
              "| Filter | Region | Auflösung | Dateien (Wochen) | erste Woche ab | letzte Woche ab | Abruf von | Abruf bis |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    if not df.empty:
        for (fi, reg, aufl), g in df.groupby(["filter", "region", "aufloesung"]):
            zeilen.append(f"| {fi} | {reg} | {aufl} | {len(g)} | {g['woche_start_berlin'].min()} | "
                          f"{g['woche_start_berlin'].max()} | {g['abgerufen_am_utc'].min()} | {g['abgerufen_am_utc'].max()} |")
    zeilen += ["", MARKER_ENDE]
    block = "\n".join(zeilen)

    text = sources.read_text(encoding="utf-8") if sources.exists() else "# Datenherkunft\n"
    muster = re.compile(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_ENDE), re.S)
    text = muster.sub(lambda _: block, text) if muster.search(text) else text.rstrip() + "\n\n" + block + "\n"
    sources.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------------------------
# Hauptablauf
# ---------------------------------------------------------------------------------------------
def main() -> None:
    p = lade_params()
    tz = p["markt"]["zeitzone"]
    filt = p["markt"]["smard_filter_preis"]
    region = p["markt"]["gebotszone"]
    basis = p["daten"]["smard_basis_url"].rstrip("/")
    datenstand = p["zeitraeume"]["datenstand"]
    timeout = p["daten"]["http_timeout_s"]

    raw = pfad(p, "raw")
    manifest_datei = raw / "smard" / "manifest.csv"
    manifest_datei.parent.mkdir(parents=True, exist_ok=True)
    manifest = lies_manifest(manifest_datei)
    pruefe_integritaet(raw, manifest)

    if benoetigter_zeitraum(datenstand, datenstand, tz)[1] > pd.Timestamp.now(tz=tz):
        raise DownloadFehler(f"Datenstand {datenstand} liegt nicht vollständig in der Vergangenheit. "
                             "zeitraeume.datenstand in config/params.yaml prüfen.")

    session = None           # wird erst erzeugt, wenn wirklich etwas geladen werden muss (offline-fähig)
    neu, vorhanden = 0, 0
    for aufl, von in p["daten"]["aufloesungen"].items():
        beginn, ende = benoetigter_zeitraum(von, datenstand, tz)
        ordner = raw / "smard" / str(filt) / aufl
        ordner.mkdir(parents=True, exist_ok=True)
        index = None
        for woche in wochenanfaenge(beginn, ende, tz):
            ts = ms(woche)
            name = f"{filt}_{region}_{aufl}_{ts}.json"
            datei = ordner / name
            rel = datei.relative_to(raw).as_posix()
            # nur der Teil der Woche, der im benötigten Zeitraum liegt
            b_ms, e_ms = max(ts, ms(beginn)), min(ms(woche + pd.DateOffset(weeks=1)), ms(ende))

            eintrag = next((z for z in manifest if z["datei"] == rel and z["status"] == "aktiv"), None)
            if datei.exists():
                woche_ende_ms = ms(woche + pd.DateOffset(weeks=1))
                abgerufen = eintrag["abgerufen_am_utc"] if eintrag else ""
                veraltet = (eintrag is not None and abgerufen != "unbekannt"
                            and pd.Timestamp(abgerufen).value // 10**6 < woche_ende_ms
                            and fehlende_werte_im_zeitraum(datei.read_bytes(), b_ms, e_ms) > 0)
                if not veraltet:
                    if eintrag is None:  # Datei ohne Manifest-Zeile (z. B. von Hand kopiert): nachtragen
                        print(f"  Warnung: {rel} fehlt im Manifest, wird mit unbekanntem Abrufdatum nachgetragen.")
                        inhalt = datei.read_bytes()
                        manifest.append(dict(datei=rel, quelle="SMARD", filter=filt, region=region, aufloesung=aufl,
                                             woche_start_utc_ms=ts, woche_start_berlin=woche.strftime("%Y-%m-%d"),
                                             url=f"{basis}/{filt}/{region}/{name}", abgerufen_am_utc="unbekannt",
                                             smard_created_utc=ms_zu_utc(json.loads(inhalt)["meta_data"]["created"]),
                                             bytes=len(inhalt), sha256=sha256(inhalt), status="aktiv"))
                    vorhanden += 1
                    continue
                # Datei stammt aus einer noch laufenden Woche: alte Fassung behalten, neue laden
                alt = datei.with_name(f"{datei.stem}.veraltet-{abgerufen[:10]}.json")
                datei.rename(alt)
                eintrag["status"] = "veraltet"
                eintrag["datei"] = alt.relative_to(raw).as_posix()
                print(f"  {rel}: beim letzten Abruf unvollständig, wird neu geladen (alt: {alt.name})")

            if session is None:
                session = http_session(p["daten"]["http_versuche"])
            if index is None:
                index = set(json.loads(lade_url(session, f"{basis}/{filt}/{region}/index_{aufl}.json", timeout))["timestamps"])
            if ts not in index:
                raise DownloadFehler(f"SMARD bietet für {aufl} keine Woche ab {woche:%Y-%m-%d} an (Zeitstempel {ts}). "
                                     "Zeitraum in config/params.yaml prüfen.")
            url = f"{basis}/{filt}/{region}/{name}"
            inhalt = lade_url(session, url, timeout)
            try:
                meta = json.loads(inhalt)["meta_data"]
            except (ValueError, KeyError) as e:
                raise DownloadFehler(f"Antwort ist kein gültiges SMARD-JSON: {url}") from e
            datei.write_bytes(inhalt)  # Original-Bytes, unverändert
            manifest.append(dict(datei=rel, quelle="SMARD", filter=filt, region=region, aufloesung=aufl,
                                 woche_start_utc_ms=ts, woche_start_berlin=woche.strftime("%Y-%m-%d"), url=url,
                                 abgerufen_am_utc=jetzt_utc(), smard_created_utc=ms_zu_utc(meta["created"]),
                                 bytes=len(inhalt), sha256=sha256(inhalt), status="aktiv"))
            neu += 1
            if neu % 25 == 0:
                print(f"  ... {neu} Dateien geladen")
                schreibe_manifest(manifest_datei, manifest)  # Zwischenstand, falls der Lauf abbricht

    schreibe_manifest(manifest_datei, manifest)
    aktualisiere_sources(raw / "SOURCES.md", manifest, manifest_datei)
    print(f"Download: {neu} neu geladen, {vorhanden} bereits vorhanden ({'offline' if session is None else 'online'}).")


if __name__ == "__main__":
    try:
        main()
    except DownloadFehler as e:
        sys.exit(f"FEHLER in 01_download: {e}")
