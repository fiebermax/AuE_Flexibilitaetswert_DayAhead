# KI: Claude, Zweck: scrollbares HTML-Board R2 (Daten, Bereinigung, Reinigungsfenster) aus den Repo-Daten erzeugen, geprüft von <Name R2> durch Sichtprüfung im Browser und Abgleich mit r2/ergebnisse/
"""Builds r2/ergebnisse/board.html: one scrollable page with everything R2 did. One command:

    python src/build_board.py

Why a generated page and not a hand-made one: every number on the board is read from the files in
the repo (preise_clean.csv, r2/ergebnisse/, the diary), so the board can never disagree with the code.
Run it again after any change and the board is up to date.

Sources of the content:
  * numbers and charts:   data/preise_clean.csv, r2/ergebnisse/*.csv, r2/ergebnisse/cleaning_log.md
  * diagrams:             the ```mermaid blocks in r2/docs/architektur.md (single source, also shown on GitHub)
  * decisions:            the "### E-xxx" headings in docs/projekttagebuch.md
  * test count:           pytest --collect-only

The page needs an internet connection when it is OPENED (it loads Chart.js and Mermaid from public CDNs);
building it works offline.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))     # make the other files in src/ importable
from gemeinsam import ROOT, lade_params, pfad      # noqa: E402
import fensteranalyse as fa                        # noqa: E402

ZIEL = ROOT / "r2" / "ergebnisse" / "board.html"
SAISONS = {"Winter": "Winter", "Fruehling": "Frühling", "Sommer": "Sommer", "Herbst": "Herbst"}


# ---------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------
def de(x: float, nachkomma: int = 0) -> str:
    """German number format: 42.360 / 4,3."""
    s = f"{x:,.{nachkomma}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def mermaid_bloecke() -> list[str]:
    """All mermaid diagrams of r2/docs/architektur.md, in document order."""
    text = (ROOT / "r2" / "docs" / "architektur.md").read_text(encoding="utf-8")
    return re.findall(r"```mermaid\n(.*?)```", text, flags=re.S)


def entscheidungen() -> list[tuple[str, str]]:
    """(ID, title) of every decision entry in the diary, newest first (the diary is ordered that way)."""
    text = (ROOT / "docs" / "projekttagebuch.md").read_text(encoding="utf-8")
    return [(m.group(1), m.group(2).strip()) for m in re.finditer(r"^### (E-\d{3}) · (.+)$", text, flags=re.M)]


def cleaning_log() -> pd.DataFrame:
    zeilen = [z for z in (ROOT / "r2" / "ergebnisse" / "cleaning_log.md").read_text(encoding="utf-8").splitlines()
              if re.match(r"\| \d+ ", z)]
    teile = [[t.strip() for t in z.strip("|").split(" | ")] for z in zeilen]
    return pd.DataFrame(teile, columns=["Schritt", "Regel", "vorher", "nachher", "betroffen", "Begründung"])


def anzahl_tests() -> int:
    out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/"], cwd=ROOT,
                         capture_output=True, text=True).stdout
    return sum(1 for z in out.splitlines() if "::" in z)


def tabelle(df: pd.DataFrame, rechts: tuple[str, ...] = ()) -> str:
    """Plain HTML table; columns named in `rechts` are right-aligned (numbers)."""
    kopf = "".join(f'<th class="{"r" if c in rechts else ""}">{html.escape(str(c))}</th>' for c in df.columns)
    zeilen = "".join("<tr>" + "".join(f'<td class="{"r" if c in rechts else ""}">{html.escape(str(v))}</td>'
                                      for c, v in zip(df.columns, r)) + "</tr>" for r in df.itertuples(index=False))
    return f'<div class="tabwrap"><table><thead><tr>{kopf}</tr></thead><tbody>{zeilen}</tbody></table></div>'


# ---------------------------------------------------------------------------------------------
# Data for tiles and charts (everything computed here, nothing typed in)
# ---------------------------------------------------------------------------------------------
def daten(p: dict) -> dict:
    last = p["last"]
    d = pd.read_csv(pfad(p, "processed") / "preise_clean.csv")
    log = cleaning_log()
    zeile = lambda nr: log[log["Schritt"].str.startswith(f"{nr} ")].iloc[0]

    # Monthly price: median and IQR band (robust, like the quality report)
    d["monat"] = d["datum_lokal"].str[:7]
    m = d.groupby("monat")["preis_eur_mwh"]
    monat = pd.DataFrame({"median": m.median(), "q25": m.quantile(.25), "q75": m.quantile(.75)}).round(1)

    # Daily profile per season (median per local hour)
    profil = {SAISONS[s]: d[d["saison"] == s].groupby("stunde_lokal")["preis_eur_mwh"].median().round(1).tolist()
              for s in SAISONS}

    # Cleaning window: one row per night (look-back, E-037)
    naechte = fa.fenster_je_tag(d, last["fenster_start_h"], last["fenster_ende_h"], last["blocklaenge_h"], last["status_quo_start_h"])
    js = fa.kennzahlen_je_saison(naechte, last["status_quo_start_h"])
    jj = fa.kennzahlen_je_jahr(naechte, last["mwh_pro_tag"])
    roll = naechte.set_index(pd.to_datetime(naechte["datum_lokal"]))["mehrkosten_eur_mwh"].rolling("30D").median()
    roll = roll.iloc[29::7]                                               # one point per week is enough to read the trend
    fenster = list(range(last["fenster_start_h"], 24)) + list(range(0, last["fenster_ende_h"]))
    starts = fenster[:len(fenster) - last["blocklaenge_h"] + 1]
    start_anteil = (naechte["start_billigst"].value_counts(normalize=True).reindex(starts, fill_value=0) * 100).round(1)

    sq_ende = (last["status_quo_start_h"] + last["blocklaenge_h"]) % 24 or 24
    voll = jj[jj["vollstaendig"] & (jj["jahr"] != 2022)]
    return {
        "d": d, "log": log, "naechte": naechte, "js": js, "jj": jj,
        "n": len(d), "luecken": int(zeile(5)["betroffen"]), "dubletten": int(zeile(2)["betroffen"]),
        "geflaggt": int(d["flag_outlier"].sum()), "geflaggt_pct": 100 * d["flag_outlier"].mean(),
        "negativ": int((d["preis_eur_mwh"] < 0).sum()), "negativ_pct": 100 * (d["preis_eur_mwh"] < 0).mean(),
        "von": d["datum_lokal"].min(), "bis": d["datum_lokal"].max(), "tests": anzahl_tests(),
        "sq": f"{last['status_quo_start_h']:02d}–{sq_ende:02d} Uhr",
        "fenster_txt": f"{last['fenster_start_h']:02d}–{last['fenster_ende_h']:02d} Uhr",
        "mk_median": naechte["mehrkosten_eur_mwh"].median(),
        "start_modus": int(naechte["start_billigst"].mode().iloc[0]),
        "eur_min": voll["eur_summe"].min(), "eur_max": voll["eur_summe"].max(),
        "jahre_txt": f"{voll['jahr'].min()}–{voll['jahr'].max()}",
        "charts": {
            "monat_labels": monat.index.tolist(), "monat_median": monat["median"].tolist(),
            "monat_q25": monat["q25"].tolist(), "monat_q75": monat["q75"].tolist(),
            "profil": profil,
            "saison_labels": [SAISONS[s] for s in js["saison"]],
            "saison_median": js["median_eur_mwh"].round(1).tolist(),
            "saison_q25": js["q25_eur_mwh"].round(1).tolist(), "saison_q75": js["q75_eur_mwh"].round(1).tolist(),
            "start_labels": [f"{h:02d}" for h in starts], "start_anteil": start_anteil.tolist(),
            "jahr_labels": [str(j) + ("*" if not v else "") for j, v in zip(jj["jahr"], jj["vollstaendig"])],
            "jahr_eur": (jj["eur_pro_jahr"] / 1000).round(1).tolist(),
            "roll_labels": [t.strftime("%Y-%m-%d") for t in roll.index], "roll_werte": roll.round(1).tolist(),
        },
    }


# ---------------------------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------------------------
CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#1d2330;--muted:#5a6273;--line:#e3e6ec;--accent:#0f7b74;--accent2:#d9932b;
--soft:#e9f2f1;--warn:#9a5b00;--warnbg:#fff4e0}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#11151c;--card:#1a1f29;--ink:#e6e9ef;
--muted:#9aa3b2;--line:#2a313d;--accent:#3cb4aa;--accent2:#e6a84a;--soft:#1d2a2c;--warn:#f0b35a;--warnbg:#2b2416}}
:root[data-theme="dark"]{--bg:#11151c;--card:#1a1f29;--ink:#e6e9ef;--muted:#9aa3b2;--line:#2a313d;--accent:#3cb4aa;
--accent2:#e6a84a;--soft:#1d2a2c;--warn:#f0b35a;--warnbg:#2b2416}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{background:var(--card);border-bottom:1px solid var(--line);padding:28px 16px 18px}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px}
header .wrap{padding:0}
.eyebrow{color:var(--accent);font-weight:700;letter-spacing:.12em;font-size:12px;text-transform:uppercase}
h1{font-size:28px;line-height:1.2;margin:6px 0 8px}
h2{font-size:21px;margin:0 0 4px}
h3{font-size:15px;margin:18px 0 6px}
.sub{color:var(--muted);margin:0}
nav{position:sticky;top:0;z-index:5;background:var(--card);border-bottom:1px solid var(--line);overflow-x:auto;white-space:nowrap}
nav a{display:inline-block;padding:10px 12px;color:var(--muted);text-decoration:none;font-size:14px}
nav a:hover{color:var(--accent)}
section{padding:28px 0 6px}
.lead{color:var(--muted);max-width:820px;margin:4px 0 16px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.tile .v{font-size:24px;font-weight:700;color:var(--accent);line-height:1.15}
.tile .l{color:var(--muted);font-size:13px;margin-top:4px}
.tile.hyp .v{color:var(--accent2)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:12px 0;min-width:0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media (max-width:820px){.grid2{grid-template-columns:1fr}h1{font-size:23px}}
.chart{position:relative;height:300px}
.note{font-size:13px;color:var(--muted);margin:8px 0 0}
.badge{display:inline-block;background:var(--warnbg);color:var(--warn);border:1px solid var(--warn);border-radius:6px;
padding:1px 7px;font-size:12px;font-weight:600;margin-left:6px;vertical-align:middle}
.mermaid{background:#fff;border-radius:8px;padding:8px;overflow-x:auto;text-align:center}
.tabwrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}
td.r,th.r{text-align:right;font-variant-numeric:tabular-nums}
ul.dec{list-style:none;padding:0;margin:0;columns:2;column-gap:24px}
@media (max-width:820px){ul.dec{columns:1}}
ul.dec li{break-inside:avoid;padding:5px 0;border-bottom:1px solid var(--line);font-size:14px}
ul.dec b{color:var(--accent);margin-right:6px}
footer{color:var(--muted);font-size:13px;padding:24px 0 40px}
code{background:var(--soft);padding:1px 5px;border-radius:4px;font-size:.92em}
"""


def seite(p: dict, x: dict) -> str:
    diag = mermaid_bloecke()
    dg = lambda i: f'<div class="mermaid">{html.escape(diag[i])}</div>' if i < len(diag) else ""
    log = x["log"].copy()
    jj = x["jj"].copy()
    jahr_tab = pd.DataFrame({
        "Jahr": jj["jahr"], "Nächte": jj["fenster"], "vollständig": ["ja" if v else "nein" for v in jj["vollstaendig"]],
        "Mittel €/MWh": [de(v, 1) for v in jj["mittel_eur_mwh"]], "Median €/MWh": [de(v, 1) for v in jj["median_eur_mwh"]],
        "Summe €": [de(v) for v in jj["eur_summe"]], "€ auf 365 Nächte": [de(v) for v in jj["eur_pro_jahr"]]})
    dec = "".join(f"<li><b>{i}</b>{html.escape(t)}</li>" for i, t in entscheidungen())
    t = lambda v, l, hyp=False: f'<div class="tile{" hyp" if hyp else ""}"><div class="v">{v}</div><div class="l">{l}</div></div>'

    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Board R2 Datenbasis</title><style>{CSS}</style></head>
<body>
<header><div class="wrap">
  <div class="eyebrow">AuE · Flexibilitätswert Day-Ahead · R2 Datenanalyse &amp; IT</div>
  <h1>Board R2: von SMARD bis zur geprüften Datenbasis</h1>
  <p class="sub">Erzeugt von <code>src/build_board.py</code> aus den Dateien im Repo. Preise: Bundesnetzagentur | SMARD.de, Day-Ahead DE-LU, CC BY 4.0.
  Zeitraum {x['von']} bis {x['bis']}. Einordnung: deskriptive Analytik, DMAIC-Phase Measure.</p>
</div></header>
<nav><div class="wrap"><a href="#kpi">Überblick</a><a href="#workflow">Workflow</a><a href="#bereinigung">Bereinigung</a>
<a href="#preise">Preise</a><a href="#reinigung">Reinigungsfenster</a><a href="#backtest">Backtest-Zugriff</a>
<a href="#dateien">Dateien</a><a href="#entscheidungen">Entscheidungen</a></div></nav>
<main class="wrap">

<section id="kpi"><h2>Überblick</h2>
<p class="lead">Die wichtigsten Zahlen der Datenbasis. Grün: aus den Daten gezählt. Orange: Rückblick-Obergrenze, keine Strategie und kein Ergebnis.</p>
<div class="tiles">
{t(de(x['n']), "Stunden nach Bereinigung (UTC)")}
{t(de(x['luecken']), "Lücken (nichts aufgefüllt)")}
{t(de(x['dubletten']), "Dubletten")}
{t(f"{de(x['geflaggt'])} ({de(x['geflaggt_pct'], 1)} %)", "auffällige Preise, nur markiert")}
{t(f"{de(x['negativ'])} ({de(x['negativ_pct'], 1)} %)", "Stunden mit negativem Preis, gültig")}
{t(str(x['tests']), "automatische Tests")}
{t(f"{de(x['mk_median'], 1)} €/MWh", f"Mehrkosten Reinigung {x['sq']}, Median je Nacht", True)}
{t(f"{de(x['eur_min'] / 1000)}–{de(x['eur_max'] / 1000)} T€", f"Obergrenze je Jahr {x['jahre_txt']} bei 8 MWh/Nacht", True)}
</div></section>

<section id="workflow"><h2>Workflow: jeder Schritt ist ein Knoten</h2>
<p class="lead">Links kommen die Daten herein, rechts gehen sie an die Nachbarpakete. Jeder Kasten ist ein Skript, jeder Zylinder eine Datei.
Ein Befehl (<code>python src/run_all.py</code>) führt alles aus. <code>data/raw/</code> wird nie beschrieben; jede Rohdatei ist per SHA-256 gesichert.</p>
<div class="card">{dg(0)}</div></section>

<section id="bereinigung"><h2>Bereinigung in zehn Schritten</h2>
<p class="lead">Jeder Schritt zählt Zeilen vorher und nachher und begründet, was er tut. Wo etwas nicht stimmt, bricht der Lauf ab, statt still zu reparieren.
Nichts wird gelöscht, gekappt oder erfunden; auffällige Preise werden nur markiert.</p>
<div class="grid2"><div class="card">{dg(1)}</div>
<div class="card"><h3>Protokoll aus <code>r2/ergebnisse/cleaning_log.md</code></h3>{tabelle(log[["Schritt", "Regel", "vorher", "nachher", "betroffen"]], ("vorher", "nachher", "betroffen"))}
<p class="note">Begründung je Schritt und verworfene Alternativen: <code>r2/docs/architektur.md</code> Abschnitt 2, Tagebuch E-024 bis E-029.</p></div></div>
</section>

<section id="preise"><h2>Was die Preise zeigen</h2>
<p class="lead">Rohwerte, nichts geglättet. Median statt Mittelwert, weil einzelne Extremstunden den Mittelwert verziehen.</p>
<div class="card"><h3>Preis je Monat: Median, Band = mittlere Hälfte der Stunden (IQR)</h3><div class="chart"><canvas id="cMonat"></canvas></div>
<p class="note">Das Krisenjahr 2022 ist der Stresstest und nie Teil des Trainings.</p></div>
<div class="card"><h3>Tagesprofil je Saison: Median je Uhrzeit (deutsche Zeit)</h3><div class="chart"><canvas id="cProfil"></canvas></div>
<p class="note">Produktion läuft 06–22 Uhr; die Stunden davor und danach sind das Reinigungsfenster {x['fenster_txt']}. Nachts sinkt der Preis bis etwa 3 Uhr.</p></div>
</section>

<section id="reinigung"><h2>Reinigungsfenster: wie viel Spielraum gibt es? <span class="badge">Rückblick, keine Strategie</span></h2>
<p class="lead">Die Reinigung (4 MW, 2 h = 8 MWh) läuft heute {x['sq']} (vom Praxispartner bestätigt). Für jede Nacht vergleiche ich das mit dem billigsten 2-h-Block in {x['fenster_txt']},
mit den echten Preisen dieser Nacht. Das ist die Obergrenze des Flexibilitätswerts; was eine Wochenplanung davon realisiert, zeigt erst der Backtest von R3.</p>
<div class="card">{dg(2)}</div>
<div class="grid2">
<div class="card"><h3>Mehrkosten des Status quo je Saison (€/MWh, Median)</h3><div class="chart"><canvas id="cSaison"></canvas></div>
<p class="note">Fehlerbalken: 25.–75. Perzentil der Nächte.</p></div>
<div class="card"><h3>Wann beginnt der billigste Block? (Anteil der Nächte)</h3><div class="chart"><canvas id="cStart"></canvas></div>
<p class="note">Meist um {x['start_modus']} Uhr. Das Muster ist stabil; eine feste Regel könnte viel davon holen (Hypothese für H0b).</p></div>
</div>
<div class="grid2">
<div class="card"><h3>Mehrkosten über die Zeit (gleitender Median über 30 Nächte, €/MWh)</h3><div class="chart"><canvas id="cRoll"></canvas></div></div>
<div class="card"><h3>Obergrenze in T€ je Jahr bei 8 MWh je Nacht</h3><div class="chart"><canvas id="cJahr"></canvas></div>
<p class="note">* Jahr unvollständig, auf 365 Nächte hochgerechnet. Ohne Personal und Zuschläge; verschobene Menge voll zum Spotpreis (Annahme A3 „Band“). Bei „proportional“ rund 30 % davon.</p></div>
</div>
<div class="card"><h3>Je Jahr, aus <code>r2/ergebnisse/reinigungsfenster_jahr.csv</code></h3>{tabelle(jahr_tab, tuple(jahr_tab.columns[1:]))}</div>
</section>

<section id="backtest"><h2>Ein Planungsfreitag im Backtest</h2>
<p class="lead">So bekommt R3 die Daten über <code>src/datenzugriff.py</code>: Die Strategie plant nur mit dem, was am Freitagmorgen bekannt war, und wird danach mit der echten Woche bewertet.
Gerät etwas aus der Zukunft in die Historie, bricht der Lauf ab. <code>preisabfrage.py</code> ist nur zum Anschauen und hat diese Grenze bewusst nicht.</p>
<div class="card">{dg(3)}</div></section>

<section id="dateien"><h2>Dateien und Spalten</h2>
<p class="lead">Wer liefert was an wen. Jede Spalte mit Einheit und Quelle steht in <code>docs/codebook.md</code>.</p>
<div class="card">{dg(4)}</div></section>

<section id="entscheidungen"><h2>Entscheidungen im Projekttagebuch</h2>
<p class="lead">Alle E-Einträge, neueste zuerst. Jeder Eintrag nennt die verworfene Alternative und den Beleg.</p>
<div class="card"><ul class="dec">{dec}</ul></div></section>

<footer>Stand der Daten {x['bis']}. Neu erzeugen: <code>python src/build_board.py</code>. KI-Einsatz gekennzeichnet im Projekttagebuch (K-Einträge).</footer>
</main>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<script>
const D = {json.dumps(x["charts"], ensure_ascii=False)};
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const ACC = css('--accent'), ACC2 = css('--accent2'), MUTED = css('--muted'), LINE = css('--line');
const SF = {{"Winter":"#2f6db5","Frühling":"#3b8a5a","Sommer":"#c47a00","Herbst":"#b5483a"}};
const fmt = v => v.toLocaleString('de-DE', {{maximumFractionDigits: 1}});
if (window.Chart) {{
  Chart.defaults.color = MUTED; Chart.defaults.borderColor = LINE; Chart.defaults.font.family = 'system-ui, sans-serif';
  Chart.defaults.maintainAspectRatio = false;
  const tip = {{callbacks: {{label: c => `${{c.dataset.label}}: ${{fmt(c.parsed.y)}}`}}}};
  new Chart(cMonat, {{type:'line', data:{{labels:D.monat_labels, datasets:[
    {{label:'75. Perzentil', data:D.monat_q75, borderWidth:0, pointRadius:0, fill:'+1', backgroundColor:ACC+'33'}},
    {{label:'25. Perzentil', data:D.monat_q25, borderWidth:0, pointRadius:0, fill:false}},
    {{label:'Median €/MWh', data:D.monat_median, borderColor:ACC, borderWidth:2, pointRadius:0}}]}},
    options:{{interaction:{{mode:'index', intersect:false}}, plugins:{{legend:{{display:false}}, tooltip:tip}},
    scales:{{y:{{title:{{display:true, text:'€/MWh'}}}}, x:{{ticks:{{maxTicksLimit:12}}}}}}}}}});
  const h = [...Array(24).keys()].map(i => String(i).padStart(2,'0'));
  new Chart(cProfil, {{type:'line', data:{{labels:h, datasets:Object.entries(D.profil).map(([s,v]) =>
    ({{label:s, data:v, borderColor:SF[s], backgroundColor:SF[s], borderWidth:2, pointRadius:2}}))}},
    options:{{interaction:{{mode:'index', intersect:false}}, plugins:{{tooltip:tip}},
    scales:{{y:{{title:{{display:true, text:'Median €/MWh'}}}}, x:{{title:{{display:true, text:'Uhrzeit'}}}}}}}}}});
  new Chart(cSaison, {{type:'bar', data:{{labels:D.saison_labels, datasets:[
    {{label:'Median €/MWh', data:D.saison_median, backgroundColor:D.saison_labels.map(s => SF[s])}}]}},
    options:{{plugins:{{legend:{{display:false}}, tooltip:{{callbacks:{{label:c =>
      `Median ${{fmt(c.parsed.y)}} €/MWh (IQR ${{fmt(D.saison_q25[c.dataIndex])}}–${{fmt(D.saison_q75[c.dataIndex])}})`}}}}}},
    scales:{{y:{{beginAtZero:true, title:{{display:true, text:'€/MWh'}}}}}}}},
    plugins:[{{id:'iqr', afterDatasetsDraw(ch){{const c=ch.ctx, y=ch.scales.y; ch.getDatasetMeta(0).data.forEach((b,i)=>{{
      const lo=y.getPixelForValue(D.saison_q25[i]), hi=y.getPixelForValue(D.saison_q75[i]);
      c.save(); c.strokeStyle=css('--ink'); c.lineWidth=1.2; c.beginPath(); c.moveTo(b.x,lo); c.lineTo(b.x,hi);
      c.moveTo(b.x-6,lo); c.lineTo(b.x+6,lo); c.moveTo(b.x-6,hi); c.lineTo(b.x+6,hi); c.stroke(); c.restore();}});}}}}]}});
  new Chart(cStart, {{type:'bar', data:{{labels:D.start_labels, datasets:[{{label:'Anteil der Nächte in %', data:D.start_anteil,
    backgroundColor:D.start_labels.map((l,i) => i===0 ? MUTED : ACC)}}]}},
    options:{{plugins:{{legend:{{display:false}}, tooltip:tip}}, scales:{{y:{{beginAtZero:true, title:{{display:true, text:'%'}}}},
    x:{{title:{{display:true, text:'Startzeit (grau = Status quo)'}}}}}}}}}});
  new Chart(cRoll, {{type:'line', data:{{labels:D.roll_labels, datasets:[{{label:'€/MWh', data:D.roll_werte, borderColor:ACC2,
    borderWidth:2, pointRadius:0}}]}}, options:{{plugins:{{legend:{{display:false}}, tooltip:tip}},
    scales:{{y:{{beginAtZero:true, title:{{display:true, text:'€/MWh'}}}}, x:{{ticks:{{maxTicksLimit:10}}}}}}}}}});
  new Chart(cJahr, {{type:'bar', data:{{labels:D.jahr_labels, datasets:[{{label:'T€ pro Jahr', data:D.jahr_eur,
    backgroundColor:D.jahr_labels.map(l => l==='2022' ? MUTED : ACC2)}}]}},
    options:{{plugins:{{legend:{{display:false}}, tooltip:tip}}, scales:{{y:{{beginAtZero:true, title:{{display:true, text:'T€'}}}}}}}}}});
}}
if (window.mermaid) {{ mermaid.initialize({{startOnLoad:true, theme:'neutral', securityLevel:'strict', flowchart:{{useMaxWidth:true}}}}); }}
</script>
</body></html>
"""


def main() -> None:
    p = lade_params()
    x = daten(p)
    ZIEL.write_text(seite(p, x), encoding="utf-8")
    print(f"Board: {ZIEL} ({ZIEL.stat().st_size // 1024} KB), {x['tests']} Tests, {len(mermaid_bloecke())} Diagramme, "
          f"{len(entscheidungen())} Entscheidungen")


if __name__ == "__main__":
    main()
