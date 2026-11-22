"""Figure 5: Modeled received dose and its inter-individual variability

Draws only source_data/fig-5/ (summarized data; nothing is fitted here).
Build: ``idofig build fig-5`` (or ./reproduce.sh).
"""
from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import idofig as idf
from plotting.brains import place
from project import FIGURE_DATA

D = FIGURE_DATA / "fig-5"
METRICS = (("ti_max", r"TI$_{max}$"), ("ti_normal", r"TI$_{normal}$"), ("hf_max", r"HF$_{max}$"))
INSULA = "#0072B2"
INSULA_LW = 1.6  # pt; the left-insula bar edge (B1-B3) must read at print size (ES r3.19)
GRID = "#eceff3"
VIOLIN_FACE, VIOLIN_ALPHA = "#b8c2cc", 0.75
FS, FS_SMALL = 7, 7
# B1-B3 region ticks: 6 pt at 70 deg (below the 7 pt text floor). 68 bars at the
# ~1.68 mm pitch the B column allows; 70 deg is the angle with the fewest glyph collisions
# (only 'p' descenders of parsOp/preC/postC... brush a neighbour); below ~67 deg they pile up.
FS_TICK, B_ANGLE = 6, 70
B_LEFT, B_BOTTOM, B_TOP = 8.8, 11.5, 3.0  # mm: y-label + ticks | rotated labels | headroom
# Desikan-Killiany short names for the B rankings: 68 full names cannot print at >= 7 pt across
# 178 mm without overlapping, so each tick is "<hemisphere> <abbreviation>" (fig-7's ABBR style).
DK_ABBR = {
    "bankssts": "BSTS", "caudalanteriorcingulate": "cACC", "caudalmiddlefrontal": "cMFG",
    "cuneus": "CUN", "entorhinal": "ENT", "frontalpole": "FP", "fusiform": "FUS",
    "inferiorparietal": "IPL", "inferiortemporal": "ITG", "insula": "insula",
    "isthmuscingulate": "iCC", "lateraloccipital": "LOC", "lateralorbitofrontal": "lOFC",
    "lingual": "LING", "medialorbitofrontal": "mOFC", "middletemporal": "MTG",
    "paracentral": "PCL", "parahippocampal": "PHG", "parsopercularis": "parsOp",
    "parsorbitalis": "parsOrb", "parstriangularis": "parsTri", "pericalcarine": "PCAL",
    "postcentral": "postC", "posteriorcingulate": "PCC", "precentral": "preC",
    "precuneus": "PCUN", "rostralanteriorcingulate": "rACC", "rostralmiddlefrontal": "rMFG",
    "superiorfrontal": "SFG", "superiorparietal": "SPL", "superiortemporal": "STG",
    "supramarginal": "SMG", "temporalpole": "TP", "transversetemporal": "TTG",
}


def short_region(region_hemi: str) -> str:
    name, hemi = region_hemi.rsplit("-", 1)
    return f"{hemi[0].upper()} {DK_ABBR[name]}"

maps = json.loads((D / "maps.json").read_text())
n_subj = maps["n_subjects"]
limits = maps["metrics"]
regions = pd.read_csv(D / "regions.csv")
region_subj = pd.read_csv(D / "region_subjects.csv")
region_cv = pd.read_csv(D / "region_cv.csv")
insula_cv = pd.read_csv(D / "insula_cv.csv").set_index("metric")["cv"]
corr = np.load(D / "intersubject_corr.npz")

p = idf.panels("a1", "a2", "a3", "b1", "b2", "b3", "c", "d", "e", "f", "g", layout=None)


def mm_w(fig):
    return fig.get_figwidth() * 25.4


def mm_h(fig):
    return fig.get_figheight() * 25.4


# ---------------------------------------------------------------- A1-A3: surfaces
for (key, lab), pid in zip(METRICS, ("a1", "a2", "a3")):
    fig = p[pid]
    w, h = mm_w(fig), mm_h(fig)
    lim = limits[key]
    # Brains are height-limited (~20 mm wide at bh 14.5), so 24 mm boxes lose nothing and keep the
    # panel inside its 54 mm column, clear of the B rankings beside it.
    x0, bw, gap, bh = 5.0, 24.0, 0.5, 14.5
    mid = x0 + bw + gap / 2  # centre of the two view columns: title and colour bar sit on it
    fig.text(mid / w, 1 - 0.5 / h, lab, ha="center", va="top", fontsize=FS, fontweight="bold", gid="title")
    rows = (("left", 25.5), ("right", 10.5))  # hemisphere, box bottom (mm)
    for col, view in enumerate(("lateral", "medial")):
        x = x0 + col * (bw + gap)
        fig.text((x + bw / 2) / w, 40.3 / h, view, ha="center", va="bottom", fontsize=FS_SMALL,
                 gid=f"view.{view}")
        for hemi, y in rows:
            place(fig, D / f"surf_{key}_{hemi}_{view}.png", x, y, bw, bh, f"{hemi[0]}h.{view}")
    for hemi, y in rows:
        fig.text(3.2 / w, (y + bh / 2) / h, f"{hemi[0].upper()}H", ha="center", va="center",
                 rotation=90, fontsize=FS_SMALL, gid=f"hemi.{hemi}")
    cax = idf.name(idf.axes_mm(fig, mid - 20.0, 6.6, 40.0, 1.8), "cbar")
    sm = plt.cm.ScalarMappable(norm=plt.Normalize(lim["vmin"], lim["vmax"]), cmap=lim["cmap"])
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.set_label(f"{lab} dose (V/m)", fontsize=FS_SMALL, labelpad=1)
    cb.ax.tick_params(labelsize=FS_SMALL, length=2, pad=1)
    cb.outline.set_linewidth(0.5)

# ---------------------------------------------------------------- B1-B3: region rankings
for (key, lab), pid in zip(METRICS, ("b1", "b2", "b3")):
    fig = p[pid]
    w, h = mm_w(fig), mm_h(fig)
    lim = limits[key]
    ax = idf.name(idf.axes_mm(fig, B_LEFT, B_BOTTOM, w - B_LEFT - 0.2, h - B_BOTTOM - B_TOP), "main")
    order = regions[regions["metric"] == key].sort_values("rank")
    x = np.arange(len(order))
    means = order["mean"].to_numpy()
    cmap = plt.get_cmap(lim["cmap"])
    ax.bar(x, means, width=0.82, color=cmap(plt.Normalize(lim["vmin"], lim["vmax"])(means)),
           edgecolor="white", linewidth=0.5, zorder=2, label="regions")
    is_ins = (order["region_hemi"] == "insula-lh").to_numpy()
    i = int(np.flatnonzero(is_ins)[0])
    ax.bar(x[i], means[i], width=0.82, facecolor="none", edgecolor=INSULA, linewidth=INSULA_LW, zorder=4,
           label="insula")
    # Per-subject regional means over each bar (cohort variability); jitter seed as before.
    rng = np.random.default_rng(3)
    vals = region_subj[region_subj["metric"] == key]
    top = np.zeros(len(order))
    for xi, region in zip(x, order["region_hemi"]):
        v = vals.loc[vals["region_hemi"] == region, "value"].to_numpy(float)
        v = v[np.isfinite(v)]
        top[xi] = v.max()
        jit = (rng.random(v.size) - 0.5) * 0.5
        ax.scatter(xi + jit, v, s=0.8, color="#14181f", alpha=0.55, edgecolors="none", zorder=3,
                   label=f"subjects.{xi}")
    # Callout sits in the clear space above the dots of the bars it spans (~6 bars at 7 pt).
    ymax = top.max() * 1.04
    ty = top[i + 3:i + 11].max() + 0.04 * ymax
    ymax = max(ymax, ty + 0.1 * ymax)
    ax.annotate("L insula", xy=(x[i], means[i]), xytext=(x[i] + 4, ty), ha="left", va="bottom",
                fontsize=FS, fontweight="bold", color=INSULA, gid="insula.label",
                arrowprops=dict(arrowstyle="-|>", color=INSULA, lw=0.8, mutation_scale=6,
                                shrinkA=1, shrinkB=1))
    ax.set_xticks(x)
    ticks = ax.set_xticklabels([short_region(r) for r in order["region_hemi"]], fontsize=FS_TICK,
                               rotation=B_ANGLE, ha="right", va="center", rotation_mode="anchor")
    for t, ins in zip(ticks, is_ins):
        if ins:
            t.set_color(INSULA)
            t.set_fontweight("bold")
    ax.set_ylabel(f"{lab} dose\n(V/m)", fontsize=FS, labelpad=1)
    ax.set_xlim(-0.55, len(order) - 0.45)
    ax.set_ylim(0, ymax)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=1.5)
    ax.tick_params(axis="y", labelsize=FS_SMALL, length=2, pad=1)

# ---------------------------------------------------------------- C-E: inter-subject correlation
for (key, lab), pid in zip(METRICS, ("c", "d", "e")):
    fig = p[pid]
    left = 6.5 if pid == "c" else 3.9
    ax = idf.name(idf.axes_mm(fig, left, 7.5, 25.0, 25.0), "main")
    im = ax.imshow(corr[key], cmap="magma", vmin=0.3, vmax=1.0, interpolation="none")
    ax.set_title(f"{lab}\ninter-subject corr.", fontsize=FS, pad=2)
    ax.set_xlabel("subj", fontsize=FS_SMALL, labelpad=1)
    if pid == "c":
        ax.set_ylabel("subj", fontsize=FS_SMALL, labelpad=1)
    ax.tick_params(labelsize=FS_SMALL, length=2, pad=1)
    if pid == "e":
        cax = idf.axes_mm(fig, 30.9, 7.5, 1.8, 25.0)
        cb = idf.colorbar(im, cax=cax, name="corr")
        cb.set_label("Pearson r", fontsize=FS_SMALL, labelpad=1)
        cb.ax.tick_params(labelsize=FS_SMALL, length=2, pad=1)
        cb.outline.set_linewidth(0.5)


def style_violins(parts):
    for b in parts["bodies"]:
        b.set_facecolor(VIOLIN_FACE)
        b.set_alpha(VIOLIN_ALPHA)
        b.set_edgecolor("black")
        b.set_linewidth(0.6)


def finish(ax, ylabel, title):
    ax.set_xticks(range(1, len(METRICS) + 1))
    ax.set_xticklabels([lab for _, lab in METRICS])
    ax.set_ylabel(ylabel, fontsize=FS, labelpad=1)
    ax.set_title(title, fontsize=FS, pad=2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=FS_SMALL, length=2, pad=1)


# ---------------------------------------------------------------- F: pattern similarity
ax = idf.name(idf.axes_mm(p["f"], 10.0, 6.0, 26.0, 29.0), "main")
parts = ax.violinplot([corr[k][np.triu_indices(corr[k].shape[0], 1)] for k, _ in METRICS],
                      showmeans=True)
style_violins(parts)
for k in ("cmeans", "cbars", "cmins", "cmaxes"):
    parts[k].set_color("black")
    parts[k].set_linewidth(0.8)
finish(ax, "pairwise pattern corr.", "Inter-subject similarity")

# ---------------------------------------------------------------- G: regional variability
ax = idf.name(idf.axes_mm(p["g"], 10.0, 6.0, 26.0, 29.0), "main")
parts = ax.violinplot([region_cv.loc[region_cv.metric == k, "cv"].to_numpy() for k, _ in METRICS],
                      showmeans=False, showextrema=False)
style_violins(parts)
rng = np.random.default_rng(0)
for i, (key, lab) in enumerate(METRICS, 1):
    sub = region_cv[region_cv.metric == key]
    cv = sub["cv"].to_numpy()
    col = plt.get_cmap(limits[key]["cmap"])(np.clip(sub["group_mean"].to_numpy() / limits[key]["vmax"], 0, 1))
    xj = i + (rng.random(cv.size) - 0.5) * 0.22
    ax.scatter(xj, cv, s=3, c=col, edgecolor="none", alpha=0.6, zorder=3, label=f"regions.{key}")
    # Filled blue diamond on top (a ring was lost among the region dots; ES r3.19); white edge
    # separates it from the dots underneath. Named "L insula" in the legend, as in B1-B3.
    ax.scatter([i], [insula_cv[key]], s=22, marker="D", facecolor=INSULA, edgecolor="white", linewidth=0.6,
               zorder=5, label="insula" if i == 1 else f"insula.{key}")
finish(ax, "across-subject CV by region", "Regional delivery\nvariability")
ax.set_ylim(top=ax.get_ylim()[1] + 0.02)  # headroom so the legend clears the violin tops
handles = [h for h in ax.collections if h.get_label() == "insula"]
ax.legend(handles=handles, labels=["L insula"], fontsize=FS_SMALL, frameon=False, loc="upper left",
          handletextpad=0.2, borderaxespad=0.2)

idf.save(p)
