"""Figure 4: Source-space slow-wave involvement probability

Draws only source_data/fig-4/ (summarized data; nothing is fitted here).
Build: ``idofig build fig-4`` (or ./reproduce.sh).
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
from plotting import dose as K  # noqa: E402
from plotting import topomaps as T  # noqa: E402
from project import FIGURE_DATA  # noqa: E402

DATA = FIGURE_DATA / "fig-4"   # physiological merge rule
METRIC = "involve"
GROUPS = (("within_tTIS", "tTIS", T.COL_ACTIVE), ("within_carrier", "Carrier-only", T.COL_SHAM))
CONTRASTS = (("stim_vs_pre", "STIM − PRE"), ("post_vs_pre", "POST − PRE"))
FS = 7
MONT_X, MONT_W = 38.0, 96.0   # panel A reduced
TOP, ROW_GAP, GROUP_GAP = 1.0, 1.5, 3.5

sc = json.loads((DATA / "scales.json").read_text())[f"P_{METRIC}_within"]
p = idf.panels(METRIC, "change", "amp", "rate", layout=None)
fig = p[METRIC]
W, H = fig.get_figwidth() * 25.4, fig.get_figheight() * 25.4

top = TOP
for g, (test, glab, gcol) in enumerate(GROUPS):
    top += GROUP_GAP if g else 0.0
    g_top = top
    for c, (ct, ct_label) in enumerate(CONTRASTS):
        last = g == len(GROUPS) - 1 and c == len(CONTRASTS) - 1
        name = f"{test.lower()}.{ct}"
        pngs = [B.view_png(DATA, f"P_{METRIC}_{test.lower()}_{ct}", j) for j in range(4)]
        mh = B.montage_height_mm(MONT_W, pngs[0])
        B.montage(fig, MONT_X, H - top - mh, MONT_W, pngs, name=f"{name}.brain", tags=B.VIEW_TAGS if last else None)
        fig.text((MONT_X - 5.0) / W, 1 - (top + mh / 2) / H, ct_label, rotation=90, ha="center", va="center", fontsize=FS,
                 gid=f"{name}.label")
        top += mh + ROW_GAP
    fig.text((MONT_X - 12.0) / W, 1 - (g_top + (top - ROW_GAP - g_top) / 2) / H, glab, rotation=90, ha="center", va="center",
             fontsize=FS, fontweight="bold", color=gcol, gid=f"{test.lower()}.group")

lo, hi = sc["vmin"], sc["vmax"]          # every drawn value is positive: a one-sided red slice
cb_h = 46.0
cax = idf.name(idf.axes_mm(fig, MONT_X + MONT_W + 5.0, (H - cb_h) / 2, 1.8, cb_h), "cbar")
cb = fig.colorbar(plt.cm.ScalarMappable(cmap=K.cluster_cmap(sc), norm=plt.Normalize(lo, hi)), cax=cax)
cb.set_ticks([lo, (lo + hi) / 2, hi], labels=[f"+{lo:.2g}", f"+{(lo + hi) / 2:.2g}", f"+{hi:.2g}"])
cb.set_label("Δ involvement probability", fontsize=FS, labelpad=2)   # no "(share of waves)"
cb.ax.tick_params(labelsize=FS, length=2, pad=1)
cb.outline.set_linewidth(0.5)

# ---------------------------------------------------------------- B-D: per participant
P_ = pd.read_csv(DATA / "participants.csv")
ST = json.loads((DATA / "participants_stats.json").read_text())
# BH q within the 14 tests of panels B-D
_q = pd.read_csv(FIGURE_DATA / "fig-4" / "explore_bh.csv")
Q = dict(zip(_q[_q.family == "fig4"].test, _q[_q.family == "fig4"].q))
ARMS = (("tTIS", T.COL_ACTIVE), ("carrier-only", T.COL_SHAM))
CONS = (("stim", "STIM − PRE"), ("post", "POST − PRE"))
YLIM, BOT, TOPM = (-0.05, 0.14), 10.0, 7.0   # rho only in C and D, as Fig 6D
INKC = "#202124"


def fmt(v: float) -> str:
    if 0.045 <= v < 0.05:               # never round a value under 0.05 up to 0.05
        return f"{v:.3g}"
    return f"{v:.2g}" if v >= 0.001 else "< 0.001"


def style(ax, ylabels: bool) -> None:
    ax.axhline(0, color="0.72", lw=0.5, zorder=0)
    ax.set_ylim(*YLIM)
    ax.set_yticks([-0.05, 0, 0.05, 0.10])
    ax.tick_params(labelsize=FS, length=2, pad=1.5)
    ax.spines[["top", "right"]].set_visible(False)
    if not ylabels:
        ax.set_yticklabels([])


# B: the change itself, both arms on one axis
fb = p["change"]
hb = fb.get_figheight() * 25.4
ax = idf.name(idf.axes_mm(fb, 15.0, BOT, 33.0, hb - BOT - TOPM), "change")
rng = np.random.default_rng(0)
for j, (c, lab) in enumerate(CONS):
    for k, (arm, col) in enumerate(ARMS):
        v = P_[P_.arm == arm][f"d_involve_{c}"].to_numpy()
        x0 = j + (-0.2 if k == 0 else 0.2)
        ax.scatter(x0 + rng.uniform(-0.09, 0.09, v.size), v, s=7, facecolor=col if k == 0 else "none", edgecolor=col,
                   lw=0.6, alpha=0.8, label=f"{arm}-{c}")
        ax.plot([x0 - 0.15, x0 + 0.15], [np.median(v)] * 2, color=INKC, lw=1.3, solid_capstyle="butt")
        qv = Q[f"B within {arm}, {c}"]                 # within-group change against zero
        ax.text(x0, 0.112, "***" if qv < 0.001 else "**" if qv < 0.01 else "*" if qv < 0.05 else "", fontsize=FS,
                color=col, ha="center", va="top", gid=f"change.star.{c}.{k}")
    qb = Q[f"B between arms, {c}"]                      # tTIS vs carrier-only, Mann-Whitney, BH q
    ax.plot([j - 0.2, j - 0.2, j + 0.2, j + 0.2], [0.116, 0.120, 0.120, 0.116], color="0.45", lw=0.6, clip_on=False)
    ax.text(j, 0.1245, f"q = {qb:.2f}", fontsize=FS, color="0.45", ha="center", va="bottom", gid=f"change.between.{c}")
style(ax, True)
ax.set_xticks([0, 1], [c[1] for c in CONS])
ax.set_xlim(-0.55, 1.55)
ax.set_ylabel("Δ whole-cortex\ninvolvement probability", fontsize=FS, labelpad=2)
for k, (arm, col) in enumerate(ARMS):
    fb.text((16.0 + k * 13.0) / 50.0, 1 - 2.5 / hb, "tTIS" if k == 0 else "Carrier-only", fontsize=FS, color=col,
            fontweight="bold", ha="left", va="top", gid=f"change.legend.{k}")

# C, D: the change against amplitude and against rate
for pid, xcol, rkey, pkey, xlabel, xlim in (
        ("amp", "d_amp_{c}", "rho_amp_involve", "C amplitude", "Δ wave amplitude (µV)", (-8, 14)),
        ("rate", "d_rate_pct_{c}", "rho_rate_involve", "D rate", "Δ slow-wave rate (% of PRE)", (-50, 130))):
    f = p[pid]
    hf = f.get_figheight() * 25.4
    for j, (c, lab) in enumerate(CONS):
        ax = idf.name(idf.axes_mm(f, 6.0 + j * 29.0, BOT, 26.0, hf - BOT - TOPM), f"{pid}.{c}")
        ax.axvline(0, color="0.72", lw=0.5, zorder=0)
        for k, (arm, col) in enumerate(ARMS):
            q = P_[P_.arm == arm]
            ax.scatter(q[xcol.format(c=c)], q[f"d_involve_{c}"], s=7, facecolor=col if k == 0 else "none", edgecolor=col,
                       lw=0.6, alpha=0.8, label=arm)
            qv = Q[f"{pkey}, {arm}, {c}"]              # asterisks on the BH q of the 14 tests, as Fig 3D
            star = "***" if qv < 0.001 else "**" if qv < 0.01 else "*" if qv < 0.05 else ""
            ax.text(0.04 + k * 0.5, 0.995, f"ρ = {ST[c][arm][rkey]:.2f}{star}".replace("-", "−"),
                    transform=ax.transAxes, fontsize=FS, color=col, ha="left", va="top", gid=f"{pid}.{c}.rho{k}")
        style(ax, False)
        ax.set_xlim(*xlim)
        ax.set_title(lab, fontsize=FS, pad=2)
    f.text((6.0 + 27.5) / 63.0, 2.0 / hf, xlabel, fontsize=FS, ha="center", va="bottom", gid=f"{pid}.xlabel")

idf.save(p)
