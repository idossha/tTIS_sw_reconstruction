"""Reproduce the paper's Figures 3-6 as output/fig-3.png ... output/fig-6.png (300 dpi).

Everything is built in a temporary folder that is deleted afterwards: the brains are rendered from each figure's
source_data/<id>/**/brains.npz (code/plotting/render.py), each figure is drawn by its make.py and composed from its
figure.json by idofig, and the composed figure is rasterized with resvg. Only the PNGs are kept.

Usage: ./reproduce.sh [fig-3 fig-6 ...]   (no argument: every figure)
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import idofig
import resvg_py

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True                       # leave nothing behind but output/
sys.path.insert(0, str(ROOT / "code"))
from plotting.render import render_brains  # noqa: E402

FIGURES = sorted(p.name for p in (ROOT / "figures").iterdir() if (p / "figure.json").exists())
DPI = 300
FONTS = Path(idofig.__file__).parent / "fonts"      # the font every figure is drawn with


def build(figures: list[str], work: Path) -> None:
    """Copy the sources to ``work``, render the brains there and build the figures with idofig (the copy's code/
    first on the path, so every script reads the copy's source_data/)."""
    for name in ("pyproject.toml", "figures", "source_data", "code"):
        src = ROOT / name
        (shutil.copytree if src.is_dir() else shutil.copy2)(src, work / name)
    for fig in figures:
        for npz in sorted((work / "source_data" / fig).rglob("brains.npz")):
            render_brains(npz, npz.parent)
    path = os.pathsep.join(filter(None, [str(work / "code"), os.environ.get("PYTHONPATH")]))
    env = {**os.environ, "PYTHONPATH": path}
    subprocess.run([sys.executable, "-m", "idofig", "build", "--force", *figures], cwd=work, env=env, check=True)


def main(figures: list[str]) -> None:
    unknown = sorted(set(figures) - set(FIGURES))
    if unknown:
        sys.exit(f"unknown figure(s) {', '.join(unknown)}; choose from {', '.join(FIGURES)}")
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        build(figures, Path(tmp))
        for fig in figures:
            png = resvg_py.svg_to_bytes(svg_path=str(Path(tmp) / "figures" / fig / "figure.svg"), dpi=float(DPI),
                                        background="#ffffff", skip_system_fonts=True, font_dirs=[str(FONTS)])
            (out / f"{fig}.png").write_bytes(bytes(png))
            print(f"wrote output/{fig}.png")


if __name__ == "__main__":
    main(sys.argv[1:] or FIGURES)
