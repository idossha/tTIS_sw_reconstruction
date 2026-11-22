"""Sensor topomaps and within-night trends (Figure 3 and its supplementary sensor figure).

Reads only the frozen tables under ``source_data/<fig>/``: channel positions (``montage.csv``), per-channel
values, significance masks and per-episode trend rows. Topomaps are drawn with eegtopo's ``plot_topomap``.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from eegtopo import plot_topomap

import idofig as idf

CMAP = "RdBu_r"
MAX_PROTOCOLS = 10
COL_ACTIVE = "#1b9e77"  # Dark2 green/orange: kept apart from the red/blue change scale
COL_SHAM = "#d95f02"
GROUP = {"active": ("tTIS", COL_ACTIVE), "sham": ("Carrier-only", COL_SHAM)}
HEAD_LW = 0.5  # head outline, nose and ears at a ~10-18 mm head (eegtopo draws 1.5 pt)
EPISODES = np.arange(1, MAX_PROTOCOLS + 1)


def house_style() -> None:
    """Open axes (no top/right spines) over idofig's journal rc; call after idf.panels()."""
    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False})


def load_montage(data: Path) -> tuple[np.ndarray, list[str]]:
    m = pd.read_csv(data / "montage.csv")
    return m[["x", "y"]].to_numpy(float), m["channel"].tolist()


def draw_topo(ax, z, xy, ordered, vlim, sig_mask=None, *, sig_dot_size=9.0,
              non_sig_dot_size=0.0):
    """Plot one topomap; mark significant channels as bold dots when given."""
    z = np.where(np.isfinite(z), z, 0.0)
    _, _, im = plot_topomap(
        z, xy, ch_names=ordered, ax=ax, cmap=CMAP, vlim=vlim, colorbar=False,
        head=True, show_labels=False, sig_mask=sig_mask,
        sig_dot_size=sig_dot_size, non_sig_dot_size=non_sig_dot_size,
        sig_alpha=1.0, non_sig_alpha=0.30,
    )
    return im


def head(fig, rect_mm, name: str, values, xy, channels, vmax: float, sig=None, dot: float = 0.4):
    """One topomap at ``rect_mm`` (left, bottom, w, h from the panel's bottom-left); returns the image."""
    ax = idf.name(idf.axes_mm(fig, *rect_mm), name)
    im = draw_topo(ax, values, xy, channels, (-vmax, vmax), sig_mask=sig, sig_dot_size=dot)
    for artist in [*ax.patches, *ax.lines]:
        artist.set_linewidth(HEAD_LW)
    return im


def row_label(fig, x_mm: float, y_mm: float, text: str, color: str, gid: str, size: float = 7):
    """A rotated group label centred at (x, y) mm."""
    w, h = fig.get_figwidth() * 25.4, fig.get_figheight() * 25.4
    return fig.text(x_mm / w, y_mm / h, text, rotation=90, ha="center", va="center",
                    fontsize=size, fontweight="bold", color=color, gid=gid)


def colorbar(fig, im, rect_mm, name: str, label: str | None = None, ticks=None, ticklabels=None):
    cax = idf.axes_mm(fig, *rect_mm)
    cb = idf.colorbar(im, cax=cax, name=name)
    cb.outline.set_linewidth(0.5)
    cb.ax.tick_params(width=0.5, length=1.5, pad=1)
    if ticks is not None:
        cb.set_ticks(ticks)
    if ticklabels is not None:
        cb.ax.set_yticklabels(ticklabels)
    if label:
        cb.set_label(label, labelpad=2)
    return cb


def trend(ax, rows: pd.DataFrame, tag: str, ms: float = 2.2, lw: float = 1.0):
    """Per-episode group mean ± 95% CI, tTIS and carrier-only, with a one-row legend just above the
    axes whose entries carry each group's within-night trend p (``wilcoxon_p``, nominal; two
    significant figures), so each p sits on its own group's marker and colour."""
    handles, labels = [], []
    for group in ("active", "sham"):
        label, color = GROUP[group]
        g = rows[rows.group == group].sort_values("episode")
        ok = np.isfinite(g["mean"].to_numpy())
        x = g["episode"].to_numpy(float)[ok]
        ax.fill_between(x, g["lo"].to_numpy()[ok], g["hi"].to_numpy()[ok], color=color, alpha=0.15,
                        lw=0, gid=f"{tag}-ci-{group}")
        handles += ax.plot(x, g["mean"].to_numpy()[ok], "-o", color=color, ms=ms, lw=lw, label=label)
        labels.append(f"{label} (trend $p$ = {g['wilcoxon_p'].iloc[0]:#.2g})")
    ax.legend(handles=handles, labels=labels, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2,
              handlelength=0.9, handletextpad=0.3, columnspacing=0.8, borderaxespad=0.15, borderpad=0.0)
    ax.axhline(0.0, color="0.6", lw=0.5, ls=":", gid=f"{tag}-zero")
    ax.set_xlim(0.5, MAX_PROTOCOLS + 0.5)
    ax.set_xticks(EPISODES)
