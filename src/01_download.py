# KI: Claude, Zweck: SMARD-Download mit Cache, Retry und Manifest, geprüft von <Name R2> durch Review, Offline-Lauf und pytest
"""Step 1: download SMARD raw data (only if not yet in data/raw) and store it unchanged.

Owner: R2. Output:
  data/raw/smard/<filter>/<resolution>/<filter>_<region>_<resolution>_<ts>.json   (original bytes from SMARD)
  data/raw/smard/manifest.csv   (per file: URL, retrieval time, SHA256, size, SMARD creation time)
  data/raw/SOURCES.md           (summary, automatically generated section)

How SMARD organises its data:
  SMARD serves one JSON file per week. A week starts Monday 00:00 German time. <ts> is that moment as
  milliseconds since 1970-01-01 UTC ("Unix time"), e.g. 1759096800000 = Mon 29.09.2025 00:00 in Berlin.
  File content: {"meta_data": {...}, "series": [[ts_ms, price], [ts_ms, price], ...]}
  An index file (index_hour.json) lists all weeks that exist.

Flow of main():
  1. Work out which weeks we need from params.yaml (daten.aufloesungen, zeitraeume.datenstand).
  2. Check files already on disk against manifest.csv (SHA256): raw data must never change.
  3. Download missing weeks (with retry). If everything is already there, the step runs fully offline.
  4. A file fetched before its week was over (so it misses prices in the needed range) is downloaded
     again; the old file is kept as *.veraltet-<date>.json instead of being overwritten.
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

# Make "src/" importable so we can use our shared helper module gemeinsam.py,
# no matter from which folder the script is started.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import ROOT, lade_params, pfad  # noqa: E402

# Column order of manifest.csv. One row per downloaded file.
MANIFEST_SPALTEN = [
    "datei", "quelle", "filter", "region", "aufloesung", "woche_start_utc_ms", "woche_start_berlin",
    "url", "abgerufen_am_utc", "smard_created_utc", "bytes", "sha256", "status",
]
# The script rewrites only the text between these two markers in SOURCES.md; everything else
# in that file (written by hand) stays untouched.
MARKER_START = "<!-- manifest:start (automatisch von src/01_download.py erzeugt, nicht von Hand ändern) -->"
MARKER_ENDE = "<!-- manifest:ende -->"


class DownloadFehler(RuntimeError):
    """Our own error type. At the bottom of the file it is caught and printed as a readable message
    (which file, what to do) instead of a long Python traceback."""


# ---------------------------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------------------------
def sha256(daten: bytes) -> str:
    """Fingerprint of a file. Changing a single character gives a completely different value,
    so comparing it with the value in the manifest proves the file is still the original."""
    return hashlib.sha256(daten).hexdigest()


def jetzt_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ms_zu_utc(ms: int) -> str:
    """Unix milliseconds -> readable UTC time, e.g. 1759096800000 -> '2025-09-28T22:00:00Z'."""
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def benoetigter_zeitraum(von: str, datenstand: str, tz: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Needed period as [start, end) in German time.

    The end is 00:00 on the day AFTER the data cut-off, and is excluded ("half-open interval").
    That way the last day is fully included and we never need "23:59:59" tricks.
    tz_localize attaches the time zone Europe/Berlin to a plain date.
    """
    beginn = pd.Timestamp(von).tz_localize(tz)
    ende = (pd.Timestamp(datenstand) + pd.Timedelta(days=1)).tz_localize(tz)
    return beginn, ende


def wochenanfaenge(beginn: pd.Timestamp, ende: pd.Timestamp, tz: str) -> list[pd.Timestamp]:
    """All Mondays 00:00 (German time) whose week overlaps [start, end).

    Pitfall: if you add "7 days" to a time that already has a time zone, pandas adds exactly 168 hours.
    Across a clock change that lands on Monday 01:00 or Sunday 23:00 instead of Monday 00:00, and the
    file name would be wrong. So we first drop the time zone (tz_localize(None)), step through plain
    calendar dates, and only attach Europe/Berlin at the very end.
    """
    erster_montag = beginn.tz_localize(None).normalize()            # normalize() = set time to 00:00
    erster_montag -= pd.Timedelta(days=erster_montag.weekday())     # weekday(): Monday=0 ... Sunday=6
    letzter_tag = (ende - pd.Timedelta(seconds=1)).tz_localize(None).normalize()
    montage = pd.date_range(erster_montag, letzter_tag, freq="7D")
    return [m.tz_localize(tz) for m in montage]


def ms(ts: pd.Timestamp) -> int:
    """Timestamp -> Unix milliseconds (the format SMARD uses in file names and inside the files)."""
    return int(ts.tz_convert("UTC").timestamp() * 1000)


def http_session(versuche: int) -> requests.Session:
    """HTTP connection that retries automatically.

    Retries on connection errors and on server answers 429 (too many requests) and 5xx (server error).
    backoff_factor=1 means growing waits (1 s, 2 s, 4 s, ...): a short SMARD outage does not stop the
    run, a permanent one is reported after a few attempts. 404 (file does not exist) is NOT retried,
    because trying again would not help.
    """
    retry = Retry(total=versuche, connect=versuche, read=versuche, status=versuche,
                  backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=("GET",), raise_on_status=False)
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers["User-Agent"] = "aue-strom-analyse (Hochschulprojekt)"
    return s


def lade_url(session: requests.Session, url: str, timeout: int) -> bytes:
    """Download one URL and return the raw bytes. Every failure becomes a DownloadFehler with a hint."""
    try:
        r = session.get(url, timeout=timeout)
    except requests.exceptions.RequestException as e:
        # Reached only after all retries failed (no internet, DNS error, timeout, ...)
        raise DownloadFehler(
            f"Keine Verbindung zu SMARD nach mehreren Versuchen.\n  URL: {url}\n  Ursache: {e}\n"
            "  Lösung: Internetverbindung prüfen und erneut starten. Bereits geladene Dateien bleiben erhalten."
        ) from e
    if r.status_code == 404:
        raise DownloadFehler(f"SMARD kennt diese Datei nicht (404): {url}\n"
                             "  Prüfen: Filter, Region und Auflösung in config/params.yaml.")
    if r.status_code != 200:
        raise DownloadFehler(f"SMARD antwortet mit HTTP {r.status_code}: {url}")
    # r.content = bytes exactly as sent by SMARD (r.json() would parse and re-format them)
    return r.content


def fehlende_werte_im_zeitraum(inhalt: bytes, beginn_ms: int, ende_ms: int) -> int:
    """How many points inside the needed range have no price (null in JSON, None in Python)."""
    serie = json.loads(inhalt)["series"]
    return sum(1 for t, v in serie if beginn_ms <= t < ende_ms and v is None)


# ---------------------------------------------------------------------------------------------
# Manifest (list of all raw files) and SOURCES.md
# ---------------------------------------------------------------------------------------------
def lies_manifest(datei: Path) -> list[dict]:
    """Read manifest.csv as a list of rows; each row is a dict {column name: value}."""
    if not datei.exists():
        return []
    with open(datei, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def schreibe_manifest(datei: Path, zeilen: list[dict]) -> None:
    """Write manifest.csv, sorted by resolution and week, so the file looks the same after every run
    and Git diffs only show real changes."""
    zeilen = sorted(zeilen, key=lambda z: (z["aufloesung"], int(z["woche_start_utc_ms"]), z["datei"]))
    with open(datei, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_SPALTEN, lineterminator="\n")
        w.writeheader()
        w.writerows(zeilen)


def pruefe_integritaet(raw: Path, manifest: list[dict]) -> None:
    """Every active file must still have the SHA256 it had when it was downloaded.

    If someone edited a raw file (by hand, by Excel, by a buggy script), we stop here instead of
    silently computing results on changed data.
    """
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
    """Write a summary per resolution (number of files, first/last week, retrieval dates) into
    SOURCES.md, between the two markers."""
    df = pd.DataFrame([z for z in manifest if z["status"] == "aktiv"])
    zeilen = [MARKER_START, "",
              "### SMARD-Abrufe (Stand dieses Laufs)", "",
              f"Je Datei URL, Abrufzeitpunkt und SHA256 in `{manifest_datei.relative_to(sources.parent).as_posix()}` "
              f"(SHA256 des Manifests: `{sha256(manifest_datei.read_bytes())}`).", "",
              "| Filter | Region | Auflösung | Dateien (Wochen) | erste Woche ab | letzte Woche ab | Abruf von | Abruf bis |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    if not df.empty:
        # groupby: one table row per combination of filter, region and resolution
        for (fi, reg, aufl), g in df.groupby(["filter", "region", "aufloesung"]):
            zeilen.append(f"| {fi} | {reg} | {aufl} | {len(g)} | {g['woche_start_berlin'].min()} | "
                          f"{g['woche_start_berlin'].max()} | {g['abgerufen_am_utc'].min()} | {g['abgerufen_am_utc'].max()} |")
    zeilen += ["", MARKER_ENDE]
    block = "\n".join(zeilen)

    # Regular expression: find "MARKER_START ... MARKER_ENDE" (re.S lets "." also match line breaks)
    # and replace it. If the markers are not there yet, append the block at the end of the file.
    text = sources.read_text(encoding="utf-8") if sources.exists() else "# Datenherkunft\n"
    muster = re.compile(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_ENDE), re.S)
    text = muster.sub(lambda _: block, text) if muster.search(text) else text.rstrip() + "\n\n" + block + "\n"
    sources.write_text(text, encoding="utf-8")


def schreibe_manifest_md(ziel: Path, manifest: list[dict]) -> None:
    """Human-readable list of every raw file: file, source, URL, retrieval date, licence, SHA-256."""
    zeilen = ["# Manifest der Rohdaten", "",
              "Automatisch erzeugt von `src/01_download.py` aus `smard/manifest.csv`. `data/raw/` wird nur gelesen, nie überschrieben.",
              "Lizenz aller Dateien: CC BY 4.0, Namensnennung „Bundesnetzagentur | SMARD.de“.", "",
              "| Datei | Quelle | URL | Abrufdatum (UTC) | Lizenz | SHA-256 |", "| --- | --- | --- | --- | --- | --- |"]
    for z in sorted((z for z in manifest if z["status"] == "aktiv"), key=lambda z: z["datei"]):
        zeilen.append(f"| `{z['datei']}` | {z['quelle']} | {z['url']} | {z['abgerufen_am_utc']} | CC BY 4.0 | `{z['sha256']}` |")
    ziel.write_text("\n".join(zeilen) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------------------------
def main() -> None:
    # --- Read all settings from params.yaml (nothing is hard-coded in this file) -------------
    p = lade_params()
    tz = p["markt"]["zeitzone"]
    filt = p["markt"]["smard_filter_preis"]
    region = p["markt"]["gebotszone"]
    basis = p["daten"]["smard_basis_url"].rstrip("/")
    datenstand = p["zeitraeume"]["datenstand"]
    timeout = p["daten"]["http_timeout_s"]

    # --- Load the manifest and check that existing raw files are unchanged --------------------
    raw = pfad(p, "raw")
    manifest_datei = raw / "smard" / "manifest.csv"
    manifest_datei.parent.mkdir(parents=True, exist_ok=True)
    manifest = lies_manifest(manifest_datei)
    pruefe_integritaet(raw, manifest)

    # A cut-off date in the future would give incomplete weeks -> stop with a clear message.
    if benoetigter_zeitraum(datenstand, datenstand, tz)[1] > pd.Timestamp.now(tz=tz):
        raise DownloadFehler(f"Datenstand {datenstand} liegt nicht vollständig in der Vergangenheit. "
                             "zeitraeume.datenstand in config/params.yaml prüfen.")

    # The internet connection is only opened when a file is actually missing.
    # If all files are present, session stays None and the step never touches the network.
    session = None
    neu, vorhanden = 0, 0

    # --- Outer loop: one pass per resolution. Today only "hour" from 2022 (diary E-021: hourly prices only;
    #     the quarter-hour files are no longer downloaded). The loop stays so a resolution can be added back.
    for aufl, von in p["daten"]["aufloesungen"].items():
        beginn, ende = benoetigter_zeitraum(von, datenstand, tz)
        ordner = raw / "smard" / str(filt) / aufl
        ordner.mkdir(parents=True, exist_ok=True)
        index = None   # SMARD's list of available weeks; fetched only if we need to download

        # --- Inner loop: one pass per week ----------------------------------------------------
        for woche in wochenanfaenge(beginn, ende, tz):
            ts = ms(woche)
            name = f"{filt}_{region}_{aufl}_{ts}.json"      # same naming scheme as SMARD
            datei = ordner / name
            rel = datei.relative_to(raw).as_posix()          # path as written into the manifest
            # Part of this week that lies inside the needed period (first/last week are partial).
            # DateOffset(weeks=1) adds a calendar week, i.e. it stays on Monday 00:00 across clock changes.
            b_ms, e_ms = max(ts, ms(beginn)), min(ms(woche + pd.DateOffset(weeks=1)), ms(ende))

            # Manifest row for this file, or None if there is none
            eintrag = next((z for z in manifest if z["datei"] == rel and z["status"] == "aktiv"), None)

            # --- Case A: file is already on disk ----------------------------------------------
            if datei.exists():
                # "Outdated" = fetched before the week was over AND prices in our range are missing.
                # Only then do we download again. A permanent gap at SMARD in a finished week does
                # not trigger a re-download; step 2 counts it as a gap instead.
                woche_ende_ms = ms(woche + pd.DateOffset(weeks=1))
                abgerufen = eintrag["abgerufen_am_utc"] if eintrag else ""
                veraltet = (eintrag is not None and abgerufen != "unbekannt"
                            and pd.Timestamp(abgerufen).value // 10**6 < woche_ende_ms
                            and fehlende_werte_im_zeitraum(datei.read_bytes(), b_ms, e_ms) > 0)
                if not veraltet:
                    if eintrag is None:
                        # File exists but is not in the manifest (e.g. copied by hand): add it,
                        # with retrieval date "unbekannt" because we cannot know it.
                        print(f"  Warnung: {rel} fehlt im Manifest, wird mit unbekanntem Abrufdatum nachgetragen.")
                        inhalt = datei.read_bytes()
                        manifest.append(dict(datei=rel, quelle="SMARD", filter=filt, region=region, aufloesung=aufl,
                                             woche_start_utc_ms=ts, woche_start_berlin=woche.strftime("%Y-%m-%d"),
                                             url=f"{basis}/{filt}/{region}/{name}", abgerufen_am_utc="unbekannt",
                                             smard_created_utc=ms_zu_utc(json.loads(inhalt)["meta_data"]["created"]),
                                             bytes=len(inhalt), sha256=sha256(inhalt), status="aktiv"))
                    vorhanden += 1
                    continue   # nothing to do for this week, go to the next one
                # Outdated: keep the old version under a new name (never overwrite raw data),
                # mark it in the manifest, then fall through to the download below.
                alt = datei.with_name(f"{datei.stem}.veraltet-{abgerufen[:10]}.json")
                datei.rename(alt)
                eintrag["status"] = "veraltet"
                eintrag["datei"] = alt.relative_to(raw).as_posix()
                print(f"  {rel}: beim letzten Abruf unvollständig, wird neu geladen (alt: {alt.name})")

            # --- Case B: file is missing (or outdated) -> download ----------------------------
            if session is None:
                session = http_session(p["daten"]["http_versuche"])
            if index is None:
                # Ask SMARD once per resolution which weeks exist, so a wrong date gives a clear
                # message instead of a confusing 404.
                index = set(json.loads(lade_url(session, f"{basis}/{filt}/{region}/index_{aufl}.json", timeout))["timestamps"])
            if ts not in index:
                raise DownloadFehler(f"SMARD bietet für {aufl} keine Woche ab {woche:%Y-%m-%d} an (Zeitstempel {ts}). "
                                     "Zeitraum in config/params.yaml prüfen.")
            url = f"{basis}/{filt}/{region}/{name}"
            inhalt = lade_url(session, url, timeout)
            try:
                meta = json.loads(inhalt)["meta_data"]   # quick check that SMARD really sent its JSON
            except (ValueError, KeyError) as e:
                raise DownloadFehler(f"Antwort ist kein gültiges SMARD-JSON: {url}") from e
            datei.write_bytes(inhalt)   # save the original bytes, unchanged
            manifest.append(dict(datei=rel, quelle="SMARD", filter=filt, region=region, aufloesung=aufl,
                                 woche_start_utc_ms=ts, woche_start_berlin=woche.strftime("%Y-%m-%d"), url=url,
                                 abgerufen_am_utc=jetzt_utc(), smard_created_utc=ms_zu_utc(meta["created"]),
                                 bytes=len(inhalt), sha256=sha256(inhalt), status="aktiv"))
            neu += 1
            if neu % 25 == 0:
                # Save progress every 25 files: if the run breaks off, the files already
                # downloaded are recorded and will not be fetched again.
                print(f"  ... {neu} Dateien geladen")
                schreibe_manifest(manifest_datei, manifest)

    # --- Finish: write manifest and summary in SOURCES.md -----------------------------------
    schreibe_manifest(manifest_datei, manifest)
    aktualisiere_sources(raw / "SOURCES.md", manifest, manifest_datei)
    schreibe_manifest_md(raw / "MANIFEST.md", manifest)
    print(f"Download: {neu} neu geladen, {vorhanden} bereits vorhanden ({'offline' if session is None else 'online'}).")


# Runs only when the file is started directly (python src/01_download.py) or via run_all.py,
# not when the tests import it to check single functions.
if __name__ == "__main__":
    try:
        main()
    except DownloadFehler as e:
        sys.exit(f"FEHLER in 01_download: {e}")
