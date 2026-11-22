"""Placing the frozen fsaverage5 brain renders: one view in a box, four views in a strip, and their colour scales.

The renders are PNGs written when a figure's data are frozen (transparent background, trimmed to the brain); here
they are only placed, at their own pixels, and every tag, colorbar and label stays vector matplotlib.
"""
from __future__ import annotations

from pathlib import Path

from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from PIL import Image

import idofig as idf

# LH lateral, LH medial, RH medial, RH lateral: the montage order of every figure.
VIEWS = (("left", "lateral"), ("left", "medial"), ("right", "medial"), ("right", "lateral"))
VIEW_TAGS = ("L lat", "L med", "R med", "R lat")
GAP_MM = 1.5  # between neighbouring views in a strip


def view_png(out_dir: Path, stem: str, i: int) -> Path:
    hemi, view = VIEWS[i]
    return out_dir / f"{stem}_{hemi}_{view}.png"


def place(fig, png: Path, left: float, bottom: float, width: float, height: float, name: str):
    """Show a render centred in a box (mm, from the panel's bottom-left), aspect kept, at its own pixels."""
    return idf.image(fig, png, left, bottom, width, height, name=name, trim=False)


def place_centred(fig, png: Path, cx_mm: float, cy_mm: float, w_mm: float, name: str):
    """A render centred at (cx, cy) mm, ``w_mm`` wide, aspect kept, resampled to the panel; returns the axes and the
    image's (height, width) in pixels."""
    w_px, h_px = Image.open(png).size
    h_mm = w_mm * h_px / w_px
    ax = idf.image(fig, png, cx_mm - w_mm / 2, cy_mm - h_mm / 2, w_mm, h_mm, name=name, trim=False,
                   interpolation="antialiased")
    return ax, (h_px, w_px)


def montage(fig, left_mm: float, bottom_mm: float, width_mm: float, pngs: list[Path],
            *, name: str, tags: tuple[str, ...] | None = None, tag_size: float = 7.0,
            tag_color: str = "#80868b", gap_mm: float = GAP_MM) -> list:
    """Place four view PNGs side by side in a ``width_mm`` strip, ``gap_mm`` apart (each
    keeps its aspect). Returns the four axes; ``tags`` are drawn under them as vector text.
    """
    view_w = (width_mm - gap_mm * (len(pngs) - 1)) / len(pngs)
    axes = []
    for i, png in enumerate(pngs):
        w_px, h_px = Image.open(png).size
        ax = idf.image(fig, png, left_mm + i * (view_w + gap_mm), bottom_mm, view_w, view_w * h_px / w_px,
                       name=f"{name}.view{i}", trim=False)
        if tags:
            ax.text(0.5, -0.02, tags[i], transform=ax.transAxes, ha="center", va="top",
                    fontsize=tag_size, color=tag_color, gid=f"{name}.tag{i}")
        axes.append(ax)
    return axes


def montage_height_mm(width_mm: float, png: Path, n: int = 4, gap_mm: float = GAP_MM) -> float:
    """Height of a ``montage`` strip ``width_mm`` wide."""
    img = Image.open(png)
    return (width_mm - gap_mm * (n - 1)) / n * img.height / img.width


def colorbar(fig, left_mm: float, bottom_mm: float, width_mm: float, height_mm: float, *,
             cmap: str, vmin: float, vmax: float, ticks, ticklabels, label: str, name: str,
             size: float = 7.0):
    """Horizontal colorbar drawn from the limits stored beside the renders (never baked into a render)."""
    cax = idf.axes_mm(fig, left_mm, bottom_mm, width_mm, height_mm)
    sm = ScalarMappable(norm=Normalize(vmin, vmax), cmap=cmap)
    cb = idf.colorbar(sm, cax=cax, ax=cax, orientation="horizontal", name=name)
    cb.set_ticks(ticks, labels=ticklabels)
    cb.set_label(label, fontsize=size, labelpad=1.5)
    cb.ax.tick_params(labelsize=size, length=2, width=0.5, pad=1)
    cb.outline.set_visible(False)
    return cb
