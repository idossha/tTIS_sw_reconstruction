"""Brain renders: each hemisphere view drawn offscreen by nilearn's matplotlib engine on the fsaverage5 inflated
surface, on a transparent square canvas with no colorbar or text, and saved as a PNG trimmed to the brain.

A figure's ``brains.npz`` holds everything its renders need: the per-vertex values of every view, the nilearn
arguments and, where a figure outlines regions, the per-vertex labels. ``render_brains`` draws them; the figure's
``make.py`` then places the PNGs (``plotting.brains``). The PNGs of the paper were written by these functions when
the figure data were frozen, and the freeze checks that ``render_brains`` reproduces each of them byte for byte.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image

RENDER_IN = 4.0     # square canvas edge; the brain fills ~70 % of it
N_HEMI = 10242      # fsaverage5 vertices per hemisphere


def fsaverage5():
    from nilearn.datasets import fetch_surf_fsaverage

    return fetch_surf_fsaverage(mesh="fsaverage5")       # ships with nilearn: no download


def cluster_face(corners: np.ndarray) -> float:
    """nilearn avg_method of the cluster renders: a face is in the cluster when at least two of its three corners are,
    coloured by the mean of those corners. nilearn's default mean counts the outside corners as 0, pulling every edge
    face below vmin, where it is left uncoloured: holes and edges looked eroded."""
    inside = corners != 0
    return float(corners[inside].mean()) if inside.sum() >= 2 else 0.0


CAMERA_X = {("left", "lateral"): -1, ("left", "medial"): 1, ("right", "lateral"): 1, ("right", "medial"): -1}


def _outline(ax, mesh, hemi: str, view: str, roi: np.ndarray, color: str, lw: float) -> None:
    """Thin lines along the boundary of ``roi`` on the side facing the camera: a face is in the region when at least
    two of its corners are (the cluster_face rule), and the outline is every edge of exactly one region face, lifted
    0.3 mm off the surface and drawn over it (nilearn's contours fill whole boundary faces and hide the map)."""
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    from nilearn import surface as nsurf

    coords, faces = nsurf.load_surf_mesh(mesh)
    fn = np.cross(coords[faces[:, 1]] - coords[faces[:, 0]], coords[faces[:, 2]] - coords[faces[:, 0]])
    vn = np.zeros_like(coords)
    for k in range(3):
        np.add.at(vn, faces[:, k], fn)
    seen = vn[:, 0] * CAMERA_X[(hemi, view)] > 0
    inr = roi.astype(bool)[faces].sum(1) >= 2
    e = np.sort(np.concatenate([faces[inr][:, [0, 1]], faces[inr][:, [1, 2]], faces[inr][:, [2, 0]]]), axis=1)
    uniq, cnt = np.unique(e, axis=0, return_counts=True)
    edge = uniq[(cnt == 1) & seen[uniq[:, 0]] & seen[uniq[:, 1]]]
    lift = coords + 0.3 * vn / np.linalg.norm(vn, axis=1, keepdims=True)
    ax.computed_zorder = False
    for c in ax.collections:
        c.set_zorder(1)
    ax.add_collection3d(Line3DCollection(lift[edge], colors=color, linewidths=lw, zorder=10))


def draw(fs, hemi: str, view: str, values: np.ndarray, *, dpi: int, contours=None, fill_edges: bool = False,
         outline=None, **kwargs):
    """Draw one hemisphere view; returns the open (figure, 3D axes), already drawn.

    ``values`` has one value per vertex of that hemisphere; ``kwargs`` go to ``plot_surf_stat_map``. ``contours`` =
    (roi_map, levels, colors) outlines regions with ``plot_surf_contours``; ``fill_edges`` paints each face's edge in
    its own colour (no hairline gaps between cluster faces); ``outline`` = (roi_mask, colour, linewidth) draws the
    boundary of a region as thin lines (``_outline``).
    """
    from nilearn import plotting

    mesh = fs.infl_left if hemi == "left" else fs.infl_right
    fig = plt.figure(figsize=(RENDER_IN, RENDER_IN), dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1], projection="3d")
    plotting.plot_surf_stat_map(surf_mesh=mesh, stat_map=values, hemi=hemi, view=view,
                                bg_map=fs.sulc_left if hemi == "left" else fs.sulc_right,
                                colorbar=False, alpha=1.0, axes=ax, figure=fig, **kwargs)
    if fill_edges:
        poly = ax.collections[0]
        poly.set_edgecolor(poly._facecolor3d)
    if contours is not None:
        roi_map, levels, colors = contours
        plotting.plot_surf_contours(surf_mesh=mesh, roi_map=roi_map, hemi=hemi, levels=levels, colors=colors,
                                    axes=ax, figure=fig)
    if outline is not None and np.asarray(outline[0]).any():
        _outline(ax, mesh, hemi, view, np.asarray(outline[0]), outline[1], outline[2])
    ax.set_axis_off()
    ax.patch.set_alpha(0.0)
    fig.canvas.draw()
    return fig, ax


def pixels(fig) -> np.ndarray:
    """The drawn canvas as RGBA; closes the figure."""
    rgba = np.asarray(fig.canvas.buffer_rgba()).copy()
    plt.close(fig)
    return rgba


def trim_box(*alphas: np.ndarray) -> tuple[slice, slice]:
    """The rows and columns any of the images drew (alpha > 0)."""
    ink = np.any([a > 0 for a in alphas], axis=0)
    rows, cols = np.flatnonzero(ink.any(axis=1)), np.flatnonzero(ink.any(axis=0))
    if rows.size == 0:
        raise RuntimeError("empty render")
    return slice(rows[0], rows[-1] + 1), slice(cols[0], cols[-1] + 1)


# --- brains.npz ---------------------------------------------------------------------------------------------------
class Brains:
    """The render inputs of one figure, collected while its data are frozen and saved as brains.npz.

    view(name, ...): one PNG trimmed to its own brain. montage(name, ...): four views of one map; every montage of
    the figure is trimmed to one common box and resized to ``px_width`` (same scale in every brain).
    """

    def __init__(self) -> None:
        self.items: list[dict] = []
        self.arrays: dict[str, np.ndarray] = {}
        self.px_width: int | None = None

    def _array(self, key: str, value) -> str:
        self.arrays[key] = np.asarray(value)
        return key

    def _kwargs(self, name: str, kwargs: dict) -> dict:
        kw = dict(kwargs)
        cmap = kw.get("cmap")
        if isinstance(cmap, LinearSegmentedColormap):   # a colour list built for the figure: keep its samples
            kw["cmap"] = {"name": cmap.name, "colors": self._array(f"{name}.cmap", cmap(np.linspace(0, 1, cmap.N)))}
        if kw.get("avg_method") is cluster_face:
            kw["avg_method"] = "cluster_face"
        return kw

    def view(self, name: str, hemi: str, view: str, values, *, dpi: int, contours=None, fill_edges=False,
             outline=None, **kwargs):
        item = dict(kind="view", name=name, hemi=hemi, view=view, dpi=dpi, fill_edges=fill_edges,
                    values=self._array(f"{name}.values", values), kwargs=self._kwargs(name, kwargs))
        if outline is not None:
            item["outline"] = dict(roi=self._array(f"{name}.outline", np.asarray(outline[0], dtype=np.int8)),
                                   color=outline[1], lw=float(outline[2]))
        if contours is not None:
            roi, levels, colors = contours
            item["contours"] = dict(roi=self._array(f"{name}.roi", roi), levels=[int(v) for v in levels],
                                    colors=list(colors))
        self.items.append(item)

    def montage(self, name: str, hemi: str, view: str, values, *, dpi: int, px_width: int, **kwargs):
        self.px_width = px_width
        self.items.append(dict(kind="montage", name=name, hemi=hemi, view=view, dpi=dpi,
                               values=self._array(f"{name}.values", values), kwargs=self._kwargs(name, kwargs)))

    def save(self, path: Path) -> None:
        spec = json.dumps({"px_width": self.px_width, "items": self.items})
        np.savez_compressed(path, spec=np.array(spec), **self.arrays)


def _kwargs(kw: dict, z) -> dict:
    kw = dict(kw)
    if isinstance(kw.get("cmap"), dict):
        kw["cmap"] = LinearSegmentedColormap.from_list(kw["cmap"]["name"], z[kw["cmap"]["colors"]])
    if kw.get("avg_method") == "cluster_face":
        kw["avg_method"] = cluster_face
    return kw


def render_brains(npz: Path, out_dir: Path) -> list[Path]:
    """Draw every render a brains.npz describes into ``out_dir`` as <name>.png; returns the paths."""
    with np.load(npz, allow_pickle=False) as z:
        spec = json.loads(str(z["spec"]))
        fs = fsaverage5()
        out_dir.mkdir(parents=True, exist_ok=True)
        written, montages = [], {}
        for it in spec["items"]:
            contours = it.get("contours")
            if contours:
                contours = (z[contours["roi"]], contours["levels"], contours["colors"])
            outline = it.get("outline")
            if outline:
                outline = (z[outline["roi"]], outline["color"], outline["lw"])
            fig, _ = draw(fs, it["hemi"], it["view"], z[it["values"]], dpi=it["dpi"], contours=contours,
                          fill_edges=it.get("fill_edges", False), outline=outline, **_kwargs(it["kwargs"], z))
            rgba = pixels(fig)
            path = out_dir / f"{it['name']}.png"
            if it["kind"] == "montage":
                montages[path] = rgba
                continue
            plt.imsave(path, rgba[trim_box(rgba[..., 3])])
            written.append(path)
    if montages:
        box = trim_box(*(r[..., 3] for r in montages.values()))
        width = box[1].stop - box[1].start
        scale = spec["px_width"] / width
        size = (spec["px_width"], round((box[0].stop - box[0].start) * scale))
        for path, rgba in montages.items():
            Image.fromarray(rgba[box]).resize(size, Image.LANCZOS).save(path, optimize=True)
            written.append(path)
    return written
