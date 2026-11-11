"""Führt die Pipeline von den Rohdaten bis zu den Ergebnissen aus: python src/run_all.py"""
import importlib.util
from pathlib import Path

# Order of the pipeline; all programs live in src/ (diary E-040).
SRC = Path(__file__).resolve().parent
SCHRITTE = [SRC / f"{n}.py" for n in ("01_download", "02_synthetisch", "cleaning", "fensteranalyse",
                                       "03_merkmale", "04_strategien", "05_bewertung", "06_sensitivitaet")]

for pfad in SCHRITTE:
    name = pfad.stem
    spec = importlib.util.spec_from_file_location(name, pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    print(f"--> {name}")
    modul.main()
