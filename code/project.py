"""Paths of the reproduction repository (the drawing scripts and helpers import them from here)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURE_DATA = ROOT / "source_data"
RESULTS = FIGURE_DATA
