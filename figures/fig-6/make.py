"""Figure 6: Modeled field and the shift toward N3 sleep during stimulation

Draws only source_data/fig-6/ (summarized data; nothing is fitted here).
Build: ``idofig build fig-6`` (or ./reproduce.sh).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import idofig as idf  # noqa: E402
from plotting import brains as B  # noqa: E402
from plotting import topomaps as T  # noqa: E402
from project import FIGURE_DATA  # noqa: E402

P = FIGURE_DATA / "fig-6"
DT, DM = P / "dose", P / "maps"
FS = 7
MUTED, GRID, SHADE, INK = "#6b7280", "#eceff3", "#e5e7eb", "#111827"
LOW = "#8fd3bd"
FIELDS = (("ti_max", r"TI$_{max}$"), ("hf_max", r"HF$_{max}$"))
MAP_FIELDS = (FIELDS[0], ("ti_normal", r"TI$_{normal}$"), FIELDS[1])
VIEWS = (("left", "lateral"), ("left", "medial"), ("right", "lateral"), ("right", "medial"))
mp = json.loads((DM / "stats.json").read_text())
S = json.loads((DT / "stats.json").read_text())
sc, bd = pd.read_csv(DT / "scatter.csv"), pd.read_csv(DT / "bands.csv")
tc, tcl = pd.read_csv(DT / "timecourse.csv"), pd.read_csv(DT / "time_clusters.csv")
_bh = pd.read_csv(FIGURE_DATA / "fig-6" / "explore_bh.csv")
_q = _bh[_bh.family == "n3_dose"].set_index("test").q                       # BH within the 13 N3-dose tests
p = idf.panels("time", "dose", "maps", "arms", layout=None)


def clean(ax):
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=FS, length=2, pad=1)


def stars(q):
    return "***" if q < 0.001 else "**" if q < 0.01 else "*" if q < 0.05 else ""


# ---------------------------------------------------------------- A: when
fig = p["time"]
W, H = fig.get_figwidth() * 25.4, fig.get_figheight() * 25.4
XL = (-216, 450)
ax = idf.name(idf.axes_mm(fig, 13.0, 25.0, W - 15.5, H - 25.0 - 7.0), "time.axes")
ax.axvspan(0, 216, color=SHADE, linewidth=0, zorder=0)
ax.axhline(0, color="#9ca3af", linewidth=0.7, linestyle=(0, (5, 4)), zorder=1)
for g, lab, col, ls in (("tTIS, higher dose", "tTIS, field above median", T.COL_ACTIVE, "-"),
                        ("tTIS, lower dose", "tTIS, field below median", LOW, "-"),
                        ("carrier-only", "Carrier-only", T.COL_SHAM, "--")):
    d = tc[tc.group == g]
    ax.fill_between(d.t_s, d["mean"] - d["sem"], d["mean"] + d["sem"], color=col, alpha=0.18, linewidth=0, zorder=2)
    ax.plot(d.t_s, d["mean"], color=col, linewidth=1.3, ls=ls, zorder=4, label=lab)
for x, lab in ((-108, "PRE"), (108, "STIM"), (324, "POST")):
    ax.text(x, 1.0, lab, transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=FS, color=MUTED)
ax.set_xlim(*XL)
ax.set_xticks([-216, 0, 216, 432])
ax.tick_params(labelbottom=False)
ax.set_ylabel("Δ N3 share\n(% of N2 + N3)", fontsize=FS, labelpad=1)
ax.legend(fontsize=FS, frameon=False, loc="upper left", handlelength=1.4, borderaxespad=0.2, handletextpad=0.4,
          labelspacing=0.2)
ax.grid(axis="y", color=GRID, linewidth=0.6)
clean(ax)
ax.tick_params(labelbottom=False)
# the tested statistic on the same axis: rho(field, shift) per step across the 32 tTIS participants, TI_max and HF_max
# paired; full color inside each field's cluster, pale outside; dotted = the rho at which one step reaches p = 0.05
from scipy import stats as sps  # noqa: E402
DTM, DO = P / "time", P / "outline"
st2, cl2 = pd.read_csv(DTM / "time_steps.csv"), pd.read_csv(DTM / "time_clusters.csv")
HFC = "#3f4b5b"                                        # HF_max bars: slate, kept apart from the arm colors
ar = idf.name(idf.axes_mm(fig, 13.0, 9.0, W - 15.5, 13.5, sharex=ax), "time.rho")
ar.axvspan(0, 216, color=SHADE, linewidth=0, zorder=0)
for k_, (f, col, pale, lab, qkey) in enumerate((("ti_max", T.COL_ACTIVE, "#a7dccb", r"TI$_{max}$", "time course TI_max"),
                                                 ("hf_max", HFC, "#c4c9d1", r"HF$_{max}$", "time course HF_max"))):
    d = st2[st2.test == f]
    c = cl2[(cl2.test == f) & (cl2.p_cluster < 0.05)].iloc[0]
    inc = (d.t_s >= c.t_start_s) & (d.t_s <= c.t_stop_s)
    ar.bar(d.t_s + (k_ - 0.5) * 12, d.effect, width=11, color=np.where(inc, col, pale), linewidth=0, zorder=2)
    yb = 0.62 + k_ * 0.22
    ar.plot([c.t_start_s, c.t_stop_s], [yb, yb], color=col, linewidth=1.5, solid_capstyle="butt")
    ar.text(c.t_stop_s + 8, yb, f"{lab}, q = {_q[qkey]:.3f}", fontsize=FS, va="center", color=col,
            gid=f"time.cluster.{f}")
ar.axhline(0, color="#9ca3af", linewidth=0.5)
n_ = int(st2.n.iloc[0])
tcrit = sps.t.ppf(0.975, n_ - 2)
rcrit = tcrit / np.sqrt(tcrit ** 2 + n_ - 2)
ar.axhline(rcrit, color=MUTED, linewidth=0.5, linestyle=(0, (1.5, 1.5)), zorder=1)
ar.text(XL[0] + 6, rcrit + 0.02, "single-step p = 0.05", fontsize=FS, color=MUTED, va="bottom")
ar.set_ylim(-0.12, 0.98)
ar.set_yticks([0, 0.4])
ar.set_ylabel(r"$\rho$ with" "\n" "field", fontsize=FS, labelpad=1)
ar.set_xticks([-216, 0, 216, 432], ["−3.6", "0", "3.6", "7.2"])
ar.set_xlabel("Time from stimulation onset (min)", fontsize=FS, labelpad=1)
clean(ar)

# ---------------------------------------------------------------- B: how much (whole-cortex field, no selection)
fig = p["dose"]
W, H = fig.get_figwidth() * 25.4, fig.get_figheight() * 25.4
X0, GAPX = 13.0, 6.0                                   # left edge, gap (mm); dose by arm is panel D
AW = (W - X0 - GAPX - 2.0) / 2
AH = H - 9.0 - 6.0
first = None
for k, (f, flab) in enumerate(FIELDS):
    x0 = X0 + k * (AW + GAPX)
    ax = idf.name(idf.axes_mm(fig, x0, 9.0, AW, AH, sharey=first), f"dose.{f}")
    first = first or ax
    ax.axhline(0, color="#9ca3af", linewidth=0.7, linestyle=(0, (5, 4)), zorder=1)
    g = S["global"][f]
    for i, (arm, col, filled, ls) in enumerate((("tTIS", T.COL_ACTIVE, True, "-"),
                                                ("carrier-only", T.COL_SHAM, False, "--"))):
        d, b = sc[(sc.field == f) & (sc.arm == arm)], bd[(bd.field == f) & (bd.arm == arm)]
        ax.fill_between(b.x, b.lo, b.hi, color=col, alpha=0.12, linewidth=0, zorder=2)
        ax.plot(b.x, b.fit, color=col, linewidth=1.3, ls=ls, zorder=4)
        ax.scatter(d.dose, d.response, s=11, facecolor=col if filled else "white", edgecolor="white" if filled else col,
                   linewidth=0.5 if filled else 0.8, zorder=5)
    q = float(_q[f"whole cortex {f} d_stim, tTIS"])
    ax.text(0.03, 0.97, rf"$\rho$ = {g['rho_tTIS']:.2f}{stars(q)}", transform=ax.transAxes, fontsize=FS,
            color=T.COL_ACTIVE, va="top", gid=f"dose.{f}.rho.tTIS")
    ax.text(0.03, 0.88, rf"$\rho$ = {g['rho_carrier']:.2f}".replace("-", "−"), transform=ax.transAxes, fontsize=FS,
            color=T.COL_SHAM, va="top", gid=f"dose.{f}.rho.carrier")
    ax.set_xlabel(rf"Whole-cortex {flab} (V/m)", fontsize=FS, labelpad=1)
    ax.xaxis.set_major_locator(plt.MaxNLocator(4))
    ax.margins(x=0.06)
    ax.grid(color=GRID, linewidth=0.6)
    clean(ax)
    ax.set_ylim(-13.5, 21.5)                           # headroom for the rho labels above the points
    if k:
        ax.tick_params(labelleft=False)
    else:
        ax.set_ylabel("Δ N3 share during STIM\n(% of N2 + N3)", fontsize=FS, labelpad=1)

# ---------------------------------------------------------------- C: where (local field, cluster test)
# two fields, as in A and B; the clusters of the separate TI_normal test are outlined (blue) on the TI_max map, where
# 44 of their 56 vertices lie
from matplotlib.lines import Line2D  # noqa: E402
fig = p["maps"]
W, H = fig.get_figwidth() * 25.4, fig.get_figheight() * 25.4
BW, BH, GX, GY, BX0, BLK = 16.5, 12.1, 0.4, 0.8, 5.0, 5.5          # smaller brains, C in the left column
for j_, (f, flab) in enumerate(FIELDS):
    bx = BX0 + j_ * (2 * BW + GX + BLK)
    fig.text((bx + BW + GX / 2) / W, (H - 1.0) / H, flab, ha="center", va="top", fontsize=FS + 0.5, fontweight="bold",
             gid=f"maps.{f}.label")
    for v, (hemi, view) in enumerate(VIEWS):
        c_, r_ = v // 2, v % 2
        x = bx + c_ * (BW + GX)
        y = H - 5.5 - (r_ + 1) * BH - r_ * GY
        png = DO / f"ti_max_tin_{hemi}_{view}.png" if f == "ti_max" else DM / f"{f}_n3_{hemi}_{view}.png"
        B.place(fig, png, x, y, BW, BH, f"maps.{f}.{hemi[0]}h.{view}")
        if j_ == 0 and c_ == 0:
            fig.text((x - 0.8) / W, (y + BH / 2) / H, view, rotation=90, ha="right", va="center", fontsize=FS,
                     color=MUTED, gid=f"maps.{view}")
        if r_ == 1:
            fig.text((x + BW / 2) / W, (y - 0.6) / H, hemi, ha="center", va="top", fontsize=FS, color=MUTED,
                     gid=f"maps.{f}.{hemi}")
cx = BX0 + 2 * (2 * BW + GX + BLK) - BLK + 2.0
cax = idf.name(idf.axes_mm(fig, cx, H - 5.5 - 2 * BH - GY, 1.6, 2 * BH + GY), "maps.cbar")
cb = fig.colorbar(plt.cm.ScalarMappable(cmap=mp["cmap"], norm=plt.Normalize(mp["vmin"], mp["vmax"])), cax=cax)
cb.set_ticks([mp["vmin"], mp["vmax"]])
cb.set_label(r"Spearman $\rho$", fontsize=FS, labelpad=-4)
cb.ax.tick_params(labelsize=FS, length=2, pad=1)
cb.outline.set_linewidth(0.5)
bx0 = BX0                                              # the TI_max block: legend beside its title
fig.legend(handles=[Line2D([], [], color="#0072B2", linewidth=1.2)], labels=[r"TI$_{normal}$ clusters"],
           loc="upper left", bbox_to_anchor=((bx0 + BW + GX / 2 + 6.0) / W, (H - 1.4) / H), fontsize=FS,
           frameon=False, handlelength=1.4, handletextpad=0.4, borderaxespad=0.0, borderpad=0.1)
# ---------------------------------------------------------------- D: the whole-cortex field each arm received
# violin, box (median, quartiles) and participants; tTIS above the median TI_max dark, below light (the split of A);
# between-arm Mann-Whitney p over each pair
td = pd.read_csv(DT / "participants.csv")
fig = p["arms"]
W, H = fig.get_figwidth() * 25.4, fig.get_figheight() * 25.4
dx0, dgap = 13.0, 6.0                                  # same axes columns as B, so D lines up under it
DW = (W - dx0 - dgap - 2.0) / 2
rng = np.random.default_rng(0)
for k, (f, flab) in enumerate(FIELDS):
    ax = idf.name(idf.axes_mm(fig, dx0 + k * (DW + dgap), 9.0, DW, H - 9.0 - 7.0), f"arms.{f}")
    for i, (arm, col, filled) in enumerate((("tTIS", T.COL_ACTIVE, True), ("carrier-only", T.COL_SHAM, False))):
        d = td[td.arm == arm]
        v = ax.violinplot(d[f], positions=[i + 0.16], widths=0.6, showextrema=False)
        for bdy in v["bodies"]:
            bdy.set_facecolor(col), bdy.set_alpha(0.18), bdy.set_edgecolor("none")
        ax.boxplot(d[f], positions=[i + 0.16], widths=0.14, showfliers=False, medianprops=dict(color=col, linewidth=0.9),
                   boxprops=dict(color=col, linewidth=0.7), whiskerprops=dict(color=col, linewidth=0.7),
                   capprops=dict(color=col, linewidth=0.7))
        face = np.where(d.group == "tTIS, higher dose", T.COL_ACTIVE, np.where(d.group == "tTIS, lower dose", LOW, "white"))
        ax.scatter(i - 0.24 + rng.uniform(-0.08, 0.08, len(d)), d[f], s=6, facecolor=face,
                   edgecolor=col if not filled else "white", linewidth=0.6 if not filled else 0.5, zorder=5)
    lo_, hi_ = td[f].min(), td[f].max()
    yb, tick = hi_ + 0.07 * (hi_ - lo_), 0.025 * (hi_ - lo_)
    ax.plot([-0.04, -0.04, 1.04, 1.04], [yb - tick, yb, yb, yb - tick], color=MUTED, linewidth=0.5, clip_on=False)
    ax.text(0.5, yb + tick * 0.6, f"p = {S['dose_arms'][f]:.2f}", ha="center", va="bottom", fontsize=FS,
            color=MUTED, gid=f"arms.{f}.p")
    ax.set_ylim(top=hi_ + 0.22 * (hi_ - lo_))
    ax.set_xticks([0, 1], ["tTIS", "Carrier-\nonly"])
    ax.set_xlim(-0.55, 1.6)
    ax.set_ylabel(rf"Whole-cortex {flab} (V/m)", fontsize=FS, labelpad=1)
    ax.yaxis.set_major_locator(plt.MaxNLocator(3))
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    clean(ax)
    ax.tick_params(labelsize=FS)
idf.save(p)
