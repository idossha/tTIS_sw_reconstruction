"""Figure 3: Sensor-space slow-wave density and morphology

Draws only source_data/fig-3/ (summarized data; nothing is fitted here).
Build: ``idofig build fig-3`` (or ./reproduce.sh).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter, MaxNLocator

import idofig as idf
from plotting import topomaps as T
from project import FIGURE_DATA, RESULTS

DATA = FIGURE_DATA / "fig-3"
CONTRASTS = {"stim": ("stim_vs_pre", "STIM − PRE"), "post": ("post_vs_pre", "POST − PRE")}
OVL = {"pre": "#8a8f98", "stim": "#1b9e77", "post": "#6a51a3"}
GRIDC = "#eceff3"

p = idf.panels("stim", "post", "waves", "forest", layout=None)
T.house_style()
xy, channels = T.load_montage(DATA)
maps = np.load(DATA / "density_maps.npz")
trend = pd.read_csv(DATA / "density_trend.csv")
# the data may name the colorbar unit; the paper's maps are in waves/min
UNIT = str(maps["unit"]) if "unit" in maps.files else "Δ density (waves/min)"

# ---- A/B: one row per contrast (mm from the panel's bottom-left) --------------------------
POOL_X, POOL_D = 9.0, 17.0           # pooled heads: left edge, diameter
POOL_Y = (40.0, 21.5, 3.0)           # bottoms of tTIS, carrier-only, difference
STRIP_X0, SLOT, HEAD = 49.0, 11.4, 10.8
STRIP_Y = (50.5, 38.0)               # bottoms of the tTIS and carrier-only strips
for pid, (c, title) in CONTRASTS.items():
    fig = p[pid]
    h, Wp = fig.get_figheight() * 25.4, fig.get_figwidth() * 25.4
    vb, vs = float(maps[f"{c}_vmax_pooled"]), float(maps[f"{c}_vmax_protocol"])
    im = None
    for (key, label, color), y in zip(
            [("active", "tTIS", T.COL_ACTIVE), ("sham", "Carrier-only", T.COL_SHAM),
             ("diff", "tTIS −\nCarrier-only", "#333333")], POOL_Y):
        im = T.head(fig, (POOL_X, y, POOL_D, POOL_D), f"pooled-{key}", maps[f"{c}_{key}_pooled"],
                    xy, channels, vb, sig=maps[f"{c}_sig_{key}"], dot=0.35)
        T.row_label(fig, POOL_X - 3.0, y + POOL_D / 2, label, color, f"pooled-label-{key}", size=7)
    fig.text((POOL_X + POOL_D / 2) / Wp, (POOL_Y[0] + POOL_D + 2.2) / h, "Pooled average (all episodes)",
             ha="center", va="bottom", fontsize=7, gid="pooled-title")
    T.colorbar(fig, im, (POOL_X + POOL_D + 2.5, POOL_Y[2] + 1, 1.6, POOL_Y[0] + POOL_D - POOL_Y[2] - 2),
               "pooled")

    for (group, cube), y in zip([("active", maps[f"{c}_active_protocol"]),
                                 ("sham", maps[f"{c}_sham_protocol"])], STRIP_Y):
        for k in range(cube.shape[0]):
            im = T.head(fig, (STRIP_X0 + k * SLOT + (SLOT - HEAD) / 2, y, HEAD, HEAD),
                        f"{group}-ep{k + 1}", cube[k], xy, channels, vs)
        label, color = T.GROUP[group]
        T.row_label(fig, STRIP_X0 - 1.8, y + HEAD / 2, label, color, f"strip-label-{group}", size=7)
    right = STRIP_X0 + 10 * SLOT
    fig.text((STRIP_X0 + right) / 2 / Wp, (STRIP_Y[0] + HEAD + 2.0) / h, title, ha="center",
             va="bottom", fontsize=8, fontweight="bold", gid="contrast-title")
    T.colorbar(fig, im, (right + 2.0, 8.0, 1.6, STRIP_Y[0] + HEAD - 8.0), "episodes", UNIT)

    ax = idf.name(idf.axes_mm(fig, STRIP_X0, 8.0, right - STRIP_X0, 26.0), "trend")
    T.trend(ax, trend[trend.contrast == c], "trend")
    ax.set_ylabel(UNIT.replace(" (", "\n(", 1), labelpad=6.5)  # clears the −2 tick after style.json dx_mm 2
    ax.set_xlabel("Stimulation episode (protocol 1–10)", labelpad=1.5)

# ---- C: density by trough depth when the figure data have it (story Fig 3), else the grand-average waveforms -------
DEPTH = DATA / "depth.csv"
STAGE = DATA / "stage.csv"
if DEPTH.exists():
    dd = pd.read_csv(DEPTH)
    d_bottom, d_height = (33.5, 32.5) if STAGE.exists() else (15.0, 49.0)   # with the stage row C stays 70 mm tall
    bins = list(dict.fromkeys(dd.loc[dd.kind == "rate", "bin"]))
    xb = np.arange(len(bins))
    edges = [b.split("–")[0] for b in bins] + [bins[-1].split("–")[1]]     # bin edges as horizontal tick labels
    off = {"pre": -0.15, "stim": 0.0, "post": 0.15}
    fig = p["waves"]
    first = None
    for j, grp in enumerate(("active", "sham")):
        label, color = T.GROUP[grp]
        arm = "tTIS" if grp == "active" else "carrier-only"
        ax = idf.name(idf.axes_mm(fig, 12.0 + j * 38.0, d_bottom, 34.0, d_height, sharey=first),
                      f"depth-{arm.split('-')[0].lower()}")
        first = first or ax
        for seg in ("pre", "stim", "post"):
            g = dd[(dd.kind == "rate") & (dd.arm == arm) & (dd.key == seg)].set_index("bin").loc[bins]
            c_seg = color if seg == "stim" else OVL[seg]      # STIM in the group's colour (carrier-only orange)
            ax.errorbar(xb + off[seg], g["mean"], yerr=g["sem"], color=c_seg, lw=0.9, marker="o", ms=2.2,
                        elinewidth=0.5, capsize=0, label=label if seg == "stim" else seg.upper())
            if seg == "pre":
                continue
            t_ = dd[(dd.kind == "test") & (dd.arm == arm) & (dd.key == f"{seg}_vs_pre")].set_index("bin").loc[bins]
            for i, (b, q) in enumerate(zip(bins, t_["q_within"])):
                if q < 0.05:
                    ax.text(i + off[seg], g.loc[b, "mean"] + g.loc[b, "sem"], "*", color=c_seg, ha="center",
                            va="bottom", fontsize=7, gid=f"sig-{grp}-{seg}-{i}")
        ax.set_xticks(np.arange(len(edges)) - 0.5, edges)
        ax.set_xlim(-0.6, len(bins) - 0.4)
        ax.set_xlabel("Trough depth (µV)", labelpad=1.5)
        ax.legend(loc="upper right", handlelength=1.0, borderaxespad=0.2)    # PRE, the group (= STIM), POST
        if j == 0:
            ax.set_ylabel("Waves/min per channel")
        else:
            ax.tick_params(labelleft=False)
    if STAGE.exists():                  # change from PRE within N2 and within N3, both groups on one percent scale
        sd, sc = pd.read_csv(STAGE), pd.read_csv(DATA / "stage_change.csv")
        first = None
        for j, stg in enumerate(("N2", "N3")):
            ax = idf.name(idf.axes_mm(fig, 12.0 + j * 38.0, 6.0, 34.0, 18.5, sharey=first), f"stage-{stg.lower()}")
            first = first or ax
            ax.axhline(0, color="0.6", lw=0.5, ls="--", zorder=0)
            for grp, shift in (("active", -0.1), ("sham", 0.1)):
                label, color = T.GROUP[grp]
                arm = "tTIS" if grp == "active" else "carrier-only"
                g = sc[(sc.arm == arm) & (sc.stage == stg)].set_index("key").loc[["stim", "post"]]
                ax.errorbar(np.arange(2) + shift, g["mean"], yerr=[g["mean"] - g["lo"], g["hi"] - g["mean"]],
                            color=color, ls="none", marker="o", ms=2.6, elinewidth=0.7, capsize=0, label=label)
                t_ = sd[(sd.kind == "test") & (sd.arm == arm) & (sd.stage == stg)].set_index("key")
                for i, seg in enumerate(("stim", "post")):
                    if t_.loc[f"{seg}_vs_pre", "q_within"] < 0.05:
                        ax.text(i + shift, g.loc[seg, "hi"], "*", color=color, ha="center", va="bottom", fontsize=7,
                                gid=f"sig-{stg.lower()}-{grp}-{seg}")
            ax.text(0.04, 0.99, stg, transform=ax.transAxes, fontsize=7, fontweight="bold", va="top", ha="left",
                    gid=f"stage-label-{stg.lower()}")
            if j == 1:                                     # the group key of the stage row
                for k, grp in enumerate(("active", "sham")):
                    label, color = T.GROUP[grp]
                    ax.text(0.98, 0.99 - k * 0.15, label, transform=ax.transAxes, fontsize=7, fontweight="bold",
                            color=color, va="top", ha="right", gid=f"group-{grp}")
            ax.set_xticks(range(2), ["STIM", "POST"])
            ax.set_xlim(-0.5, 1.5)
            ax.yaxis.set_major_locator(MaxNLocator(4))
            if j == 0:
                ax.set_ylabel("Δ density\nfrom PRE (%)")
            else:
                ax.tick_params(labelleft=False)
        lo, hi = first.get_ylim()
        first.set_ylim(lo, hi + 0.22 * (hi - lo))           # headroom for the stage label and the stars
else:
    w = pd.read_csv(DATA / "waveforms.csv")
    t = w["time"].to_numpy()
    fig = p["waves"]
    ax_wa = idf.name(idf.axes_mm(fig, 11.0, 34.0, 34.0, 32.0), "wave-ttis")
    ax_ws = idf.name(idf.axes_mm(fig, 48.0, 34.0, 34.0, 32.0, sharex=ax_wa, sharey=ax_wa), "wave-carrier")
    ax_d = idf.name(idf.axes_mm(fig, 11.0, 8.0, 71.0, 22.0, sharex=ax_wa), "difference")
    for ax, grp in ((ax_wa, "active"), (ax_ws, "sham")):
        label, color = T.GROUP[grp]
        for seg in ("pre", "stim", "post"):
            ax.plot(t, w[f"{grp}_{seg}_mean"], color=OVL[seg], lw=1.1, label=seg.upper())
        ax.axvline(0, color="0.7", lw=0.5, ls=":")
        ax.axhline(0, color=GRIDC, lw=0.6, zorder=0)
        ax.text(0.04, 0.97, label, transform=ax.transAxes, fontsize=7, fontweight="bold", va="top",
                ha="left", color=color, gid=f"group-{grp}")
        ax.tick_params(labelbottom=False)
    ax_wa.set_ylabel("Amplitude (µV)")
    ax_ws.tick_params(labelleft=False)
    ax_wa.legend(loc="lower right", handlelength=1.2, borderaxespad=0.2)
    for grp in ("active", "sham"):
        label, color = T.GROUP[grp]
        ax_d.fill_between(t, w[f"{grp}_diff_lo"], w[f"{grp}_diff_hi"], color=color, alpha=0.18, lw=0,
                          gid=f"ci-{grp}")
        ax_d.plot(t, w[f"{grp}_diff_mean"], color=color, lw=1.0, label=f"{label} STIM − PRE")
    ax_d.axvline(0, color="0.7", lw=0.5, ls=":")
    ax_d.axhline(0, color="0.45", lw=0.6, ls="--")
    ax_d.set_xticks(np.arange(-0.4, 0.81, 0.2))
    ax_d.set_xlabel("Time from negative peak (s)", labelpad=1.5)
    ax_d.set_ylabel("Δ amplitude (µV)")
    ax_d.legend(loc="lower left", handlelength=1.4, borderaxespad=0.2)

# ---- D: effect-size forest ----------------------------------------------------------------
f = pd.read_csv(DATA / "forest.csv")
# stars from the BH q across the 24 within-cluster tests, as the text reports them (bh_families.csv)
_b = pd.read_csv(FIGURE_DATA / "fig-3" / "bh_families.csv")
_b = _b[_b.family == "withincluster"]
_M = {"Slow-wave density": "density", "Negative-peak amplitude": "ValNegPeak", "Positive-peak amplitude": "ValPosPeak",
      "Peak-to-peak amplitude": "PTP", "Slope": "Slope", "Frequency": "Frequency"}
QW = {(m, c, g): q for m, c, g, q in zip(_b.measure, _b.contrast, _b.comparison, _b.q)}
fig = p["forest"]
ax = idf.name(idf.axes_mm(fig, 33.0, 19.0, 52.0, 47.0), "forest")
order = list(dict.fromkeys(f["measure"]))
ypos = {m: len(order) - 1 - i for i, m in enumerate(order)}
off = {("active", "STIM/PRE"): 0.24, ("active", "POST/PRE"): 0.08,
       ("sham", "STIM/PRE"): -0.08, ("sham", "POST/PRE"): -0.24}
ax.axvline(0, color="#9ca3af", lw=0.6, zorder=1)
for row in f.itertuples():
    y = ypos[row.measure] + off[(row.group, row.contrast)]
    color = T.GROUP[row.group][1]
    tag = f"{row.group}-{row.contrast.split('/')[0].lower()}-{order.index(row.measure)}"
    ax.plot([row.lo, row.hi], [y, y], color=color, lw=0.9, alpha=0.9, zorder=2, gid=f"ci-{tag}")
    ax.scatter([row.r], [y], s=12, facecolor=color if row.contrast == "STIM/PRE" else "white",
               edgecolor=color, lw=0.8, zorder=3, gid=f"r-{tag}")
    qv = QW[(_M[row.measure], row.contrast.split("/")[0].lower(), row.group)]
    assert abs(float(_b[(_b.measure == _M[row.measure]) & (_b.contrast == row.contrast.split("/")[0].lower()) & (_b.comparison == row.group)].p.iloc[0]) - row.p) < 1e-9
    stars = "***" if qv < 0.001 else "**" if qv < 0.01 else "*" if qv < 0.05 else ""  # BH q
    if stars:
        ax.text(row.hi + 0.02, y, stars, fontsize=7, va="center", color="#374151", gid=f"stars-{tag}")
ax.axhline(ypos["Slow-wave density"] - 0.5, color="#d1d5db", lw=0.5)
ax.set_yticks([ypos[m] for m in order], order)
ax.set_ylim(-0.5, len(order) - 0.5)
ax.set_xlim(min(-0.9, f["lo"].min() - 0.05), max(1.05, f["hi"].max() + 0.05))  # never clip a CI
ax.set_xlabel("Within-group effect size (r)", labelpad=1.5)
ax.grid(axis="x", color=GRIDC, lw=0.5)
ax.set_axisbelow(True)
handles = [
    Line2D([], [], marker="o", ls="", ms=3.5, mfc=T.COL_ACTIVE, mec=T.COL_ACTIVE, label="tTIS STIM/PRE"),
    Line2D([], [], marker="o", ls="", ms=3.5, mfc="white", mec=T.COL_ACTIVE, label="tTIS POST/PRE"),
    Line2D([], [], marker="o", ls="", ms=3.5, mfc=T.COL_SHAM, mec=T.COL_SHAM, label="Carrier-only STIM/PRE"),
    Line2D([], [], marker="o", ls="", ms=3.5, mfc="white", mec=T.COL_SHAM, label="Carrier-only POST/PRE"),
]
ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.35, -0.16), ncol=2,
          columnspacing=1.0, handletextpad=0.2)

idf.save(p)
