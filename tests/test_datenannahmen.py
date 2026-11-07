"""Automatisierte Prüfungen der Datenannahmen (K5 Stufe 5). Laufen mit `pytest tests/`."""
from pathlib import Path

import pandas as pd
import pytest

PREISE = Path("data/processed/preise_h.parquet")

pytestmark = pytest.mark.skipif(not PREISE.exists(), reason="Pipeline noch nicht gelaufen")


@pytest.fixture(scope="module")
def preise():
    return pd.read_parquet(PREISE)


def test_keine_luecken(preise):
    assert preise["preis_eur_mwh"].notna().all(), "Fehlende Preise"


def test_stunden_pro_tag(preise):
    # 24 Stunden, an Zeitumstellungstagen 23 bzw. 25
    n = preise.groupby(preise["zeit"].dt.date).size()
    assert n.isin([23, 24, 25]).all(), f"Unplausible Stundenzahl: {n[~n.isin([23, 24, 25])]}"


def test_preisbereich(preise):
    # Day-Ahead-Grenzen der Börse; negative Preise sind erlaubt und bleiben drin
    assert preise["preis_eur_mwh"].between(-500, 4000).all()


def test_keine_duplikate(preise):
    assert not preise["zeit"].duplicated().any()
