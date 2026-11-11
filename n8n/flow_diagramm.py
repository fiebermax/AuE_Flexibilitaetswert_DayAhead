# KI: Claude, Zweck: Bild der beiden n8n-Workflows für Folien und Bericht (Control R2, E-057), geprüft von Max (R2)
"""Draws n8n/flow.png: the two n8n workflows as node chains (same nodes as the exported workflow JSONs).

Only a picture of the flow. The logic itself lives in the repo (plan_woche.py, soll_ist.py, control.py);
n8n only triggers, parses, mails and stores. Run: python n8n/flow_diagramm.py
"""
import importlib.util
from pathlib import Path

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("bericht", ROOT / "src" / "07_bericht.py")
br = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(br)                                   # figure standard R1 (colours, fonts)
plt = br.plt

# node kind -> (fill, border); repo nodes stand out because the logic lives there
ART = {"trigger": ("#f0efec", br.GRAU), "n8n": ("#ffffff", br.GRAU), "repo": ("#cde2fb", br.BLAU),
       "mail": ("#ffffff", br.ORANGE), "datei": ("#ffffff", br.TEXT2)}
B, H = 2.15, 0.78                                              # node width and height (data units)


def knoten(ax, x, y, text, art):
    fill, rand = ART[art]
    ax.add_patch(FancyBboxPatch((x - B / 2, y - H / 2), B, H, boxstyle="round,pad=0.02,rounding_size=0.12",
                                facecolor=fill, edgecolor=rand, linewidth=1.8 if art in ("repo", "mail") else 1.2))
    ax.text(x, y, text, ha="center", va="center", fontsize=8.2, color=br.TEXT, linespacing=1.25)


def pfeil(ax, a, b, text=None, bogen=0.0):
    (x1, y1), (x2, y2) = a, b
    if abs(y1 - y2) < 1e-9:
        start, ende = (x1 + B / 2, y1), (x2 - B / 2, y2)
    else:
        start, ende = (x1, y1 - H / 2 if y2 < y1 else y1 + H / 2), (x2 - B / 2, y2)
    ax.add_patch(FancyArrowPatch(start, ende, arrowstyle="-|>", mutation_scale=11, color=br.TEXT2, linewidth=1.1,
                                 connectionstyle=f"arc3,rad={bogen}" if bogen else "arc3"))
    if text:
        ax.text((start[0] + ende[0]) / 2, (start[1] + ende[1]) / 2 + 0.12, text, fontsize=7.5, color=br.TEXT2, ha="center")


def workflow(ax, y0, titel, kette, zweige):
    """kette: main path left to right; zweige: list of (from index, label, [nodes], row offset)."""
    ax.text(-0.9, y0 + 0.75, titel, fontsize=11, fontweight="bold", color=br.TEXT, ha="left")
    pos = []
    for i, (text, art) in enumerate(kette):
        p = (0.2 + i * 2.6, y0)
        knoten(ax, *p, text, art)
        if pos:
            pfeil(ax, pos[-1], p)
        pos.append(p)
    for von, label, knoten_liste, dy in zweige:
        vorher = pos[von]
        for j, (text, art) in enumerate(knoten_liste):
            p = (pos[von][0] + 2.6 * (j + 1), y0 + dy)
            knoten(ax, *p, text, art)
            pfeil(ax, vorher, p, label if j == 0 else None)
            vorher = p


def main() -> Path:
    br.stil()
    fig, ax = plt.subplots(figsize=(13.5, 7.2))
    ax.set_xlim(-1.1, 20.6)
    ax.set_ylim(-7.7, 1.2)
    ax.axis("off")

    workflow(ax, 0, "Workflow 1 · Reinigungsplan Freitag", [
        ("Jeden Freitag\n08:00", "trigger"), ("Konfiguration\nund Datum", "n8n"),
        ("Plan berechnen\nplan_woche.py\n(Regel D, 3–5 Uhr)", "repo"), ("Skript\nerfolgreich?", "n8n"),
        ("Plan-JSON\nparsen", "n8n"), ("Mail Schicht-\nleitung: Plan\nder Woche", "mail")],
        [(4, None, [("Nächte aufteilen,\nLogzeile, CSV", "n8n"), ("plan_log.csv\nanhängen", "datei")], -1.15),
         (3, "nein", [("Mail IT\nFehler (stderr)", "mail")], -2.15)])

    workflow(ax, -4.0, "Workflow 2 · Soll-Ist Montag", [
        ("Jeden Montag\n09:00", "trigger"), ("Konfiguration\nund Woche", "n8n"),
        ("Soll-Ist rechnen\nsoll_ist.py\n(echte Preise)", "repo"), ("Skript\nerfolgreich?", "n8n"),
        ("Soll-Ist-JSON\nparsen", "n8n"), ("Control-Grafik\ncontrol.py\n(13 Wochen)", "repo"),
        ("Rücknahme?\nKennzahl < 0", "n8n")],
        [(4, None, [("Logzeile,\nCSV", "n8n"), ("soll_ist_log.csv\nanhängen", "datei")], -1.15),
         (3, "nein", [("Mail IT\nFehler (stderr)", "mail")], -2.15)])
    # outcome of the roll-back check, drawn below the last node of workflow 2
    xr = 0.2 + 6 * 2.6
    knoten(ax, xr + 2.6, -3.35, "ja: Mail Werks-\nleitung: zurück\nauf 22 Uhr", "mail")
    knoten(ax, xr + 2.6, -4.65, "nein: Wochen-\nmeldung Schicht-\nleitung + Grafik", "mail")
    pfeil(ax, (xr, -4.0), (xr + 2.6, -3.35))
    pfeil(ax, (xr, -4.0), (xr + 2.6, -4.65))

    # legend: what each node colour means
    for i, (art, text) in enumerate([("trigger", "Zeitplan (n8n)"), ("n8n", "n8n-Knoten ohne Rechnung"),
                                     ("repo", "Python aus dem Repo: die ganze Logik"), ("mail", "Mail (Platzhalter example.org)"),
                                     ("datei", "Ablage als CSV")]):
        fill, rand = ART[art]
        ax.add_patch(FancyBboxPatch((-0.9 + i * 4.3, -7.45), 0.5, 0.32, boxstyle="round,pad=0.02,rounding_size=0.06",
                                    facecolor=fill, edgecolor=rand, linewidth=1.5))
        ax.text(-0.3 + i * 4.3, -7.29, text, fontsize=8, va="center", color=br.TEXT2)
    ax.set_title("n8n ruft nur auf und verteilt: Plan am Freitag, Soll-Ist und Kennzahl am Montag (Prototyp)")
    ziel = ROOT / "n8n" / "flow.png"
    # Own save instead of br.speichern: a flow diagram has no data source line, only "own drawing"
    fig.suptitle(ax.get_title(loc="left"), x=0.01, ha="left", fontsize=12, fontweight="bold", color=br.TEXT)
    ax.set_title("", loc="left")
    fig.text(0.01, 0.01, "Eigene Darstellung; Knoten wie in den exportierten n8n-Workflows (Prototyp)", fontsize=7, color=br.TEXT2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(ziel)
    plt.close(fig)
    return ziel


if __name__ == "__main__":
    print(main())
