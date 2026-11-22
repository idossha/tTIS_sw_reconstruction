"""The house look shared by the figures: colours, text sizes, axis tidying and number formats.

Sizes are the printed ones (Advanced Science: text >= 7 pt, lines >= 0.5 pt); idofig hands each panel at its
printed size, so nothing here is scaled.
"""
from __future__ import annotations

import json
from pathlib import Path

from project import FIGURE_DATA

TTIS_COLOR = "#0072B2"
CARRIER_COLOR = "#5b636e"
E1_COLOR = "#b03030"          # frontal electrode pair / frontal-cingulate parcels
E2_COLOR = "#2a9d8f"          # temporal electrode pair / temporal parcels
LOBE_COL = {"frontal": E1_COLOR, "temporal": E2_COLOR, "other": "#9aa3ad"}
GRID_COLOR = "#eceff3"
TEXT_COLOR = "#374151"
LEADER_COLOR = "#9ca3af"
LEADER = dict(color=LEADER_COLOR, lw=0.5)

LABEL_PT = 7.0
TICK_PT = 7.0
SMALL_PT = 7.0
PT = SMALL_PT                 # 7 pt: every text of the dose figures
MM_PER_IN = 25.4


def data_dir(fig_id: str) -> Path:
    return FIGURE_DATA / fig_id


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def num(x: float) -> str:
    """Two decimals, a true minus and no plus sign."""
    return f"{x:.2f}".replace("-", "−")


def fmt_p(p: float) -> str:
    """Two significant figures, trailing zeros kept."""
    return f"{p:#.2g}"


def tidy(ax, grid: str | None = "both") -> None:
    if grid:
        ax.grid(axis=grid, color=GRID_COLOR, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=TICK_PT, length=2.5, width=0.6, pad=2)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.6)


def zero_line(ax, axis="h"):
    (ax.axhline if axis == "h" else ax.axvline)(0, color=LEADER_COLOR, lw=0.7, ls=(0, (4, 3)), zorder=1)
