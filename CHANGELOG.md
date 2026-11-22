# Changelog

All notable changes to this repository are listed here. Versions follow the release tags; the format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - Unreleased

### Added

- Drawing scripts, layouts and summarized source data that reproduce Figures 3–6 and Table 1 of the paper;
  `./reproduce.sh` writes one 300-dpi PNG per figure to `output/`.
- Brain maps drawn at run time from per-vertex group values (`source_data/<id>/brains.npz`) with nilearn, so no
  rendered images are shipped; figures are composed with idofig 0.14.0 and rasterized with resvg.
- A `README.md` in every `source_data/<id>/` folder, listing each file and whether the figure draws it.
- Citation metadata (`CITATION.cff`) and Zenodo archive metadata (`.zenodo.json`).
