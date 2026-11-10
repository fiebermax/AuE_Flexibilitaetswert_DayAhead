"""Führt die Pipeline von den Rohdaten bis zu den Ergebnissen aus: python src/run_all.py"""
import importlib.util
from pathlib import Path

SCHRITTE = ["01_download", "02_synthetisch", "cleaning", "fensteranalyse", "03_merkmale", "04_strategien", "05_bewertung"]

for name in SCHRITTE:
    pfad = Path(__file__).parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    print(f"--> {name}")
    modul.main()
