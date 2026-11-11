# KI: Claude, Zweck: führt analyse.ipynb aus und exportiert die Analyseseite als HTML (E-053), geprüft von Max (R2)
"""Step 8: execute analyse.ipynb top to bottom and export it as one HTML page (ergebnisse/analyse.html).

Why a script and not "run the notebook by hand": the page must show the numbers of THIS run of the pipeline.
Executing it here, after steps 01-07, guarantees that (a stale notebook output cannot slip through).
Interpretation cells carry the tag "remove_input": the page shows their text, not the code that builds it.
"""
import sys
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor, TagRemovePreprocessor
from traitlets.config import Config

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import ROOT, lade_params, pfad  # noqa: E402


def main() -> None:
    p = lade_params()
    nb = nbformat.read(ROOT / "analyse.ipynb", as_version=4)
    ExecutePreprocessor(timeout=600, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(ROOT)}})
    c = Config()
    c.TagRemovePreprocessor.remove_input_tags = ("remove_input",)
    exporter = HTMLExporter(config=c, template_name="lab")
    exporter.register_preprocessor(TagRemovePreprocessor(config=c), enabled=True)
    html, _ = exporter.from_notebook_node(nb)
    ziel = pfad(p, "tables") / "analyse.html"
    ziel.write_text(html, encoding="utf-8")
    print(f"Analyseseite -> {ziel} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
