# tTIS_sw_reconstruction

Figures and tables for **Transcranial temporal interference stimulation increases slow waves during human NREM sleep** (Haber et al., manuscript submitted).

This repository reproduces the main data figures of the paper (Figures 3–6) and Table 1 from summarized
source data. It contains, for each figure, the drawing script and layout and the summarized data it plots.
Supplementary figures and tables are not included; their source data are available from the corresponding
author on request. It does not contain raw or unprocessed data, or the analysis pipeline that summarized them;
those are available from the corresponding author on reasonable request. Figures 1–2 (stimulation overview and signal-processing pipeline) are not included.

## Reproduce

Requires [uv](https://docs.astral.sh/uv/) (or Python ≥ 3.11 and pip).

```bash
git clone https://github.com/idossha/tTIS_sw_reconstruction.git
cd tTIS_sw_reconstruction
uv sync              # or: python -m venv .venv && .venv/bin/pip install -e .
./reproduce.sh       # every figure; one figure: ./reproduce.sh fig-6
```

This writes `output/fig-3.png` … `output/fig-6.png` at 300 dpi and nothing else. It works in a temporary folder: the
brains are rendered from each figure's `brains.npz` with nilearn (fsaverage5 ships with it; nothing is downloaded),
[idofig](https://github.com/idossha/idofig) runs each figure's `make.py` and composes the panels from `figure.json`,
and the figure is rasterized with resvg; the folder is then deleted. Most recently tested with python 3.11.14, idofig 0.14.0, eegtopo 0.1.1, matplotlib 3.10.9, nilearn 0.13.1, numpy 2.4.6, pandas 3.0.3, pillow 12.2.0, resvg-py 0.5.0, scipy 1.17.1 on macOS.

## Figures

| Paper | Script and layout | Source data | Title |
|---|---|---|---|
| Figure 3 | [`figures/fig-3`](figures/fig-3) | [`source_data/fig-3`](source_data/fig-3) | Sensor-space slow-wave density and morphology |
| Figure 4 | [`figures/fig-4`](figures/fig-4) | [`source_data/fig-4`](source_data/fig-4) | Source-space slow-wave involvement probability |
| Figure 5 | [`figures/fig-5`](figures/fig-5) | [`source_data/fig-5`](source_data/fig-5) | Modeled received dose and its inter-individual variability |
| Figure 6 | [`figures/fig-6`](figures/fig-6) | [`source_data/fig-6`](source_data/fig-6) | Modeled field and the shift toward N3 sleep during stimulation |

`make.py` draws the panels from `source_data/<id>/` only (Figure 6 reads four subfolders, `dose/`, `maps/`, `time/` and `outline/`); `figure.json` places them, and `panels/<panel>/style.json`
holds manual style adjustments. The brain maps of Figures 4–6 are stored as per-vertex group values with their render
settings (`brains.npz`), and the numbers, per-participant values and statistics shown in each panel are in the
`*.csv`, `*.json` and `*.npz` files beside them.
Each `source_data/<id>/README.md` lists its files and which of them the figure draws. Participants are identified by
study codes (`sub-…`) only; ages appear only where a figure plots them. Column names and keys use the pipeline's
internal arm labels: `active`/`ACTIVE` is the tTIS arm (15,000/15,001 Hz) and `sham`/`SHAM` the carrier-only control
(15,000/15,000 Hz, the same carriers without the 1 Hz beat), not a stimulation-free sham.

The scripts share five modules in `code/plotting/`: `render.py` (the brain renders), `brains.py` (placing them,
with view strips and colour scales), `style.py` (colours, text sizes, axis style, number formats), `topomaps.py`
(sensor topomaps and within-night trends) and `dose.py` (the dose panels of Figure 6). Everything else is
[idofig](https://github.com/idossha/idofig), matplotlib and nilearn.

## Tables

| Paper | File | Title |
|---|---|---|
| Table 1 | [`tables/Table_1.csv`](tables/Table_1.csv) | Participant characteristics by arm. |

## Repository layout

```
figures/<id>/          figure.json, make.py and panel style adjustments for each figure
source_data/<id>/      summarized data plotted in that figure, with a README listing its files
tables/                Table 1 as CSV
code/plotting/         the drawing modules the scripts share
code/reproduce.py      what ./reproduce.sh runs
reproduce.sh           writes output/fig-N.png
```

## Data and code availability

Summarized source data for the main data figures (Figures 3–6) and Table 1 are in this repository. Raw and
unprocessed data are available from the corresponding author upon reasonable request. Field modeling used
[TI-Toolbox](https://github.com/idossha/TI-Toolbox).

## Citation and license

Please cite the paper (citation in [CITATION.cff](CITATION.cff); it will be updated on publication). Changes between
releases are in [CHANGELOG.md](CHANGELOG.md). Code is released under the [BSD 3-Clause License](LICENSE).
