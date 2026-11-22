"""The dose panels of Figure 7 and its supplementary dose figures: cluster brains with side labels, the
field-specificity forest, dose scatter by arm, dose by arm, and per-parcel partial rho.

Every panel draws only what the figure's data folder holds; the geometry is set in figures/<id>/make.py and every
size here is in mm from the panel's bottom-left. Text is 7 pt, with true minus signs and no plus signs. Brain labels
are placed at draw time from the frozen anchors, in a column beside each brain on its parcel's side.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import idofig as idf
import numpy as np
import pandas as pd
from matplotlib import colormaps
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, Normalize, to_rgba
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

from plotting import brains as B
from plotting import style as S

FIELDS = ("hf_max", "ti_max")
FIELD_TEX = {"hf_max": r"HF$_{max}$", "ti_max": r"TI$_{max}$", "ti_normal": r"TI$_{normal}$"}
FIELD_TITLE = {"hf_max": r"HF$_\mathbf{max}$ (carrier)", "ti_max": r"TI$_\mathbf{max}$ (envelope)"}
DOSE = {"hf_max": r"HF$_{max}$ dose (V/m)", "ti_max": r"TI$_{max}$ dose (V/m)"}
VIEW_TITLE = {(h, v): f"{h[0].upper()}H {v}" for h, v in B.VIEWS}
ARM_STYLE = {"tTIS": ("o", S.TTIS_COLOR, "-", True), "carrier-only": ("^", S.CARRIER_COLOR, "--", False)}


@dataclass
class Data:
    root: Path
    scale: dict
    labels: pd.DataFrame
    parcels: dict          # field -> its 68 DK parcel rows
    stats: dict            # field -> parcel_stats.json block
    spec: dict
    points: dict
    bands: dict
    mod: dict
    zero_ti: dict


def load(fig_id: str) -> Data:
    D = S.data_dir(fig_id)
    parcels = pd.read_csv(D / "parcels.csv")
    return Data(D, S.read_json(D / "a_scale.json"), pd.read_csv(D / "a_labels.csv"),
                {f: parcels[parcels.field == f] for f in FIELDS},
                {f: S.read_json(D / "parcel_stats.json")[f] for f in FIELDS},
                {f: pd.read_csv(D / f"b_roi_specificity_{f}.csv").set_index("field") for f in FIELDS},
                {f: pd.read_csv(D / f"b_points_{f}.csv").rename(columns={f: "dose"}) for f in FIELDS},
                {f: pd.read_csv(D / f"b_bands_{f}.csv") for f in FIELDS},
                S.read_json(D / "moderation_hf_max.json"), S.read_json(D / "c_ti_max.json"))


def panel_mm(fig) -> tuple[float, float]:
    w, h = fig.get_size_inches()
    return w * S.MM_PER_IN, h * S.MM_PER_IN


def overlay(fig, name: str = "labels"):
    """A transparent axes over the whole panel whose data units are the panel's mm, for leaders and labels."""
    w, h = panel_mm(fig)
    ax = idf.name(idf.axes_mm(fig, 0, 0, w, h), name)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_axis_off()
    ax.patch.set_alpha(0.0)
    ax.set_zorder(10)
    return ax


def sub_label(fig, text: str, x_mm: float = 4.0) -> None:
    """A sub-panel label (i, ii) at the panel's top, beside where the panel letter sits."""
    fig.text(x_mm / panel_mm(fig)[0], 1.0, text, ha="left", va="top", fontsize=8, fontweight="bold", color="black",
             gid="sub-letter")


def brain(fig, d: Data, field: str, hemi: str, view: str, cx: float, cy: float, width: float, prefix: str = "a"):
    """One cluster render <prefix>_<field>_<hemi>_<view>.png centred at (cx, cy) mm, `width` mm wide; returns its box
    (x0, y0, w, h) in mm."""
    _, (h_px, w_px) = B.place_centred(fig, d.root / f"{prefix}_{field}_{hemi}_{view}.png", cx, cy, width,
                                         f"{field}-{hemi}-{view}")
    h = width * h_px / w_px
    return cx - width / 2, cy - h / 2, width, h


def side_labels(ov, d: Data, field: str, hemi: str, view: str, box, band, spacing=3.0, gap=0.8) -> None:
    """The frozen labels of one view in a column beside the brain on each parcel's side (the anchors' ha 'right' =
    left of the brain), at the anchors' heights, de-collided to `spacing` mm, recentred on their anchors and kept in
    band = (lo, hi) mm; leaders from anchor to label behind white-backed labels (Fig 7A's style)."""
    x0, y0, w, h = box
    rows = d.labels[(d.labels.field == field) & (d.labels.hemi == hemi) & (d.labels.view == view)]
    a = pd.DataFrame({"text": rows.label.to_numpy(), "x": x0 + rows.anchor_x.to_numpy() * w,
                      "y": y0 + h - rows.anchor_y.to_numpy() * h,
                      "side": np.where(rows.ha.to_numpy() == "right", "left", "right")})
    for side, part in a.groupby("side"):
        part = part.sort_values("y", ascending=False)
        ys = part.y.to_numpy().copy()
        for i in range(1, ys.size):
            ys[i] = min(ys[i], ys[i - 1] - spacing)
        ys += part.y.mean() - ys.mean()
        ys += max(0.0, band[0] + spacing / 2 - ys.min()) - max(0.0, ys.max() - (band[1] - spacing / 2))
        lx = x0 - gap if side == "left" else x0 + w + gap
        for (_, r), ly in zip(part.iterrows(), ys):
            ov.plot([r.x, lx], [r.y, ly], **S.LEADER, zorder=11, gid=f"leader-{field}-{hemi}-{view}-{r.text}")
            ov.text(lx - 0.3 if side == "left" else lx + 0.3, ly, r.text, ha="right" if side == "left" else "left",
                    va="center", fontsize=S.PT, color=S.TEXT_COLOR, gid=f"label-{field}-{hemi}-{view}-{r.text}",
                    zorder=12, bbox=dict(boxstyle="square,pad=0.05", facecolor="white", edgecolor="none"))


def cluster_cmap(scale: dict) -> LinearSegmentedColormap:
    """The clusters' sequential colour map: the a_scale.json slice of its named matplotlib map (renders and scale)."""
    lo, hi = scale["cmap_slice"]
    return LinearSegmentedColormap.from_list("cluster_rho", colormaps[scale["cmap"]](np.linspace(lo, hi, 256)))


def signed_cmap(scale: dict, gap: str = "#e5e7eb") -> ListedColormap:
    """cluster_cmap mirrored for maps with negative clusters, on [-vmax, vmax]: rho >= vmin on the a_scale.json slice
    (Fig 7A's colours), rho <= -vmin on the mirrored slice of the same map, and |rho| < vmin (where no cluster vertex
    lies) in a light grey."""
    lo, hi = scale["cmap_slice"]
    v = np.linspace(-scale["vmax"], scale["vmax"], 1601)
    frac = np.interp(np.abs(v), [scale["vmin"], scale["vmax"]], [lo, hi])
    base = colormaps[scale["cmap"]]
    colors = np.where((v >= 0)[:, None], base(frac), base(1.0 - frac))
    colors[np.abs(v) < scale["vmin"]] = to_rgba(gap)
    return ListedColormap(colors, "cluster_rho_signed")


def scale_bar(fig, d: Data, rect) -> None:
    """A slim horizontal colour scale of the partial rho maps, ticked every 0.1 inside its range, label at the right;
    a signed scale (maps with negative clusters) spans -vmax to vmax on signed_cmap, ticked every 0.2 inside both
    coloured ranges."""
    cax = idf.axes_mm(fig, *rect)
    vmin, vmax = d.scale["vmin"], d.scale["vmax"]
    if d.scale.get("signed"):
        sm = ScalarMappable(norm=Normalize(-vmax, vmax), cmap=signed_cmap(d.scale))
        pos = np.arange(np.ceil(vmin * 5 - 1e-9), np.floor(vmax * 5 + 1e-9) + 1) / 5
        ticks = np.concatenate([-pos[::-1], pos])
    else:
        sm = ScalarMappable(norm=Normalize(vmin, vmax), cmap=cluster_cmap(d.scale))
        ticks = np.arange(np.ceil(vmin * 10 - 1e-9), np.floor(vmax * 10 + 1e-9) + 1) / 10
    cb = idf.colorbar(sm, ax=cax, cax=cax, name="rho", orientation="horizontal")
    cb.set_ticks(ticks)
    cb.set_ticklabels([S.num(t)[:-1] for t in ticks])
    cb.ax.tick_params(labelsize=S.PT, length=2, width=0.5, pad=1)
    cb.outline.set_linewidth(0.5)
    cb.dividers.set_linewidth(0.5)      # empty (no edges drawn), but its default 0.3 pt would read as a thin line
    cax.text(1.03, 0.5, r"partial $\rho$", transform=cax.transAxes, ha="left", va="center", fontsize=S.PT,
             color=S.TEXT_COLOR, gid="scale-label")


def forest(ax, d: Data, region: str, xlabel: bool) -> None:
    """B: partial rho of HF_max, TI_max and TI_normal (each given the other two) in one region's cluster, bootstrap 95 %
    CI, the region's own field in tTIS blue; row labels are named texts."""
    order = ("hf_max", "ti_max", "ti_normal")
    S.zero_line(ax, "v")
    for y, f in enumerate(order):
        r = d.spec[region].loc[f]
        col = S.TTIS_COLOR if f == region else S.CARRIER_COLOR
        ax.plot([r.partial_ci_lo, r.partial_ci_hi], [y, y], color=col, lw=1.2, solid_capstyle="butt", zorder=2,
                gid=f"ci-{f}")
        ax.scatter([r.partial_rho], [y], s=20, color=col, edgecolor="white", lw=0.5, zorder=3, label=f)
        ax.annotate(FIELD_TEX[f], (0, y), xycoords=("axes fraction", "data"), xytext=(-4, 0),
                    textcoords="offset points", ha="right", va="center", fontsize=S.PT, color="black", gid=f"row-{f}")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([])
    ax.set_ylim(len(order) - 0.5, -0.5)
    lo = min(float(d.spec[region].loc[f].partial_ci_lo) for f in order)
    ax.set_xlim(min(-0.7, lo - 0.05), 1.0)              # never clip a CI (the paper's lowest bound is -0.59)
    ax.set_xticks([-0.5, 0.0, 0.5])
    ax.set_xticklabels(["−0.5", "0", "0.5"], fontsize=S.PT)
    if xlabel:
        ax.set_xlabel(r"Partial $\rho$", fontsize=S.PT, labelpad=1)
    else:
        ax.tick_params(labelbottom=False)
    S.tidy(ax, grid="x")


def scatter(ax, d: Data, field: str, arms, ylim, text: str, pad_mm: float) -> None:
    """D: global density change vs cluster dose, OLS fit and 95 % band per arm, the panel
    statistic as the title (as in C, E-G) and the arm legend in the empty upper left of the axes."""
    pts, bands = d.points[field], d.bands[field]
    S.zero_line(ax)
    handles = []
    for arm in arms:
        marker, col, ls, filled = ARM_STYLE[arm]
        band, arm_pts = bands[bands.arm == arm], pts[pts.arm == arm]
        ax.fill_between(band.x, band.lo, band.hi, color=col, alpha=0.12, linewidth=0, zorder=2)
        ax.plot(band.x, band.fit, color=col, lw=1.3, ls=ls, zorder=4, label=f"{arm} fit")
        ax.scatter(arm_pts.dose, arm_pts.density_change, s=16, marker=marker, facecolor=col if filled else "none",
                   edgecolor="white" if filled else col, linewidth=0.5 if filled else 0.8, alpha=0.95, zorder=5,
                   label=arm)
        handles.append(Line2D([], [], marker=marker, color=col, markerfacecolor=col if filled else "none",
                              markeredgecolor="white" if filled else col, lw=1.0, ls=ls, markersize=3, label=arm))
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=S.PT, handlelength=1.6, handletextpad=0.4,
              labelspacing=0.3, borderaxespad=0.3)
    title(ax, text, pad_mm)
    ax.set_ylim(*ylim)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5, steps=[1, 2, 5, 10]))
    ax.set_xlabel(DOSE[field], fontsize=S.PT)
    # response_label: sensitivity replicas whose response is not a waves/min change (absent in the paper's data)
    ax.set_ylabel(d.scale.get("response_label", "$\\Delta$ SW density\n(STIM − PRE)"), fontsize=S.PT)
    S.tidy(ax)


def density_ylim(d: Data) -> tuple[float, float]:
    """One y range for D(i) and D(ii): every point and band of both, 5 % margins."""
    vals = np.concatenate([d.points[f].density_change.to_numpy() for f in FIELDS]
                          + [d.bands[f][["lo", "hi"]].to_numpy().ravel() for f in FIELDS])
    lo, hi = vals.min(), vals.max()
    return lo - 0.05 * (hi - lo), hi + 0.05 * (hi - lo)


def parcel_ylim(d: Data) -> tuple[float, float]:
    """One y range for E, F(i) and F(ii) (HF_max and TI_max parcel partial rho)."""
    rho = pd.concat([d.parcels[f].prho for f in FIELDS])
    return rho.min() - 0.12, rho.max() + 0.12


def title(ax, text: str, pad_mm: float) -> None:
    ax.set_title(text, fontsize=S.PT, pad=idf.pt(pad_mm), color=S.TEXT_COLOR)


def parcels(ax, d: Data, field: str, x: str, xlabel: str, stat: dict, ylim, first: bool, pad_mm: float) -> None:
    """E, F: one field's partial rho per DK parcel (filled = >= 50 % of the parcel in that field's
    cluster region)."""
    S.zero_line(ax)
    lobe_points(ax, d.parcels[field], x, s=12)
    ax.set_ylim(*ylim)
    title(ax, f"$\\rho$ = {S.num(stat['rho'])}, $p$ = {S.fmt_p(stat['p'])}", pad_mm)
    ax.set_xlabel(xlabel, fontsize=S.PT)
    if first:
        ax.set_ylabel(r"Partial $\rho$", fontsize=S.PT)
    else:
        ax.tick_params(labelleft=False)
    S.tidy(ax)


def lobe_points(ax, par: pd.DataFrame, x: str, y: str = "prho", q: str = "q", s=14):
    """Parcels by lobe outline colour, filled when q < 0.05."""
    for lobe in ("other", "temporal", "frontal"):
        d = par[par.lobe == lobe]
        sig, ns = d[d[q] < 0.05], d[d[q] >= 0.05]
        ax.scatter(sig[x], sig[y], s=s, facecolor=S.LOBE_COL[lobe], edgecolor=S.LOBE_COL[lobe], lw=0.8,
                   alpha=0.95, zorder=3, label=f"{lobe} q<0.05")
        ax.scatter(ns[x], ns[y], s=s, facecolor="none", edgecolor=S.LOBE_COL[lobe], lw=0.8, alpha=0.95,
                   zorder=3, label=f"{lobe} n.s.")


def roi_groups(ax, pts, mod):
    """Selected-ROI HF_max by arm (violin, box, points) with the Mann-Whitney p as the title."""
    rng = np.random.default_rng(3)
    arms = list(ARM_STYLE)
    for i, arm in enumerate(arms):
        vals = pts.loc[pts.arm == arm, "hf_max"].to_numpy()
        col = ARM_STYLE[arm][1]
        parts = ax.violinplot([vals], positions=[i], widths=0.7, showextrema=False)
        for pc in parts["bodies"]:
            pc.set_facecolor(col); pc.set_alpha(0.22); pc.set_edgecolor(col); pc.set_linewidth(0.5)
            pc.set_gid(f"violin-{arm}")
        ax.boxplot([vals], positions=[i], widths=0.14, patch_artist=True, showfliers=False,
                   medianprops=dict(color=col, lw=1.0), boxprops=dict(facecolor="white", edgecolor=col, lw=0.7),
                   whiskerprops=dict(color=col, lw=0.7), capprops=dict(color=col, lw=0.7))
        jit = (rng.random(vals.size) - 0.5) * 0.28
        ax.scatter(i - 0.26 + jit, vals, s=5, color=col, alpha=0.6, edgecolors="white", lw=0.5, zorder=3,
                   label=arm)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([f"{a}\n(n={int((pts.arm == a).sum())})" for a in arms], fontsize=S.TICK_PT)
    ax.set_ylabel(r"Selected-ROI HF$_{max}$ dose (V/m)", fontsize=S.LABEL_PT)
    ax.set_title(f"Mann–Whitney $p$ = {mod['hf_group_mwu_p']:.2f}", fontsize=S.SMALL_PT, pad=3, color=S.TEXT_COLOR)
    S.tidy(ax, grid="y")


def groups(ax, d: Data, pad_mm: float) -> None:
    """C: HF_max-cluster dose by arm with the Mann-Whitney p."""
    roi_groups(ax, d.points["hf_max"].rename(columns={"dose": "hf_max"}), d.mod)
    ax.set_xlim(-0.6, 1.6)
    ax.set_xticklabels(["tTIS", "carrier-only"], fontsize=S.PT)
    title(ax, f"$p$ = {S.fmt_p(d.mod['hf_group_mwu_p'])}", pad_mm)
    ax.set_ylabel(DOSE["hf_max"], fontsize=S.PT)


