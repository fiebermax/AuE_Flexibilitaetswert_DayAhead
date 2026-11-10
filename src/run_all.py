"""Führt die Pipeline von den Rohdaten bis zu den Ergebnissen aus: python src/run_all.py"""
import importlib.util
from pathlib import Path

# Order of the pipeline. R2's steps live in r2/src/, the team's steps in src/ (diary E-038).
SRC = Path(__file__).resolve().parent
R2 = SRC.parent / "r2" / "src"
SCHRITTE = [R2 / "01_download.py", R2 / "02_synthetisch.py", R2 / "cleaning.py", R2 / "fensteranalyse.py",
            SRC / "03_merkmale.py", SRC / "04_strategien.py", SRC / "05_bewertung.py"]

for pfad in SCHRITTE:
    name = pfad.stem
    spec = importlib.util.spec_from_file_location(name, pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    print(f"--> {name}")
    modul.main()
