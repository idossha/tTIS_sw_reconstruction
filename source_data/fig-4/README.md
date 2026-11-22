# Figure 4 source data

Source-space slow-wave involvement probability.

Summarized by the analysis pipeline (not included) from the study data; the files marked *yes* are drawn in the figure (`brains.npz` as its brain renders); the others are summaries kept with the figure.

| File | Drawn | Contents |
|---|---|---|
| `brains.npz` | yes | per-vertex values and nilearn settings of the 48 brain views (rendered by `code/plotting/render.py`) |
| `clusters.csv` | yes | 12 rows; columns `kind`, `metric`, `test`, `contrast`, `forming`, `n_tTIS`, `n_carrier`, `n_sig_clusters`, `n_sig_vertices`, `min_p`, `largest_sign`, `clusters` |
| `participants.csv` | yes | 43 rows; columns `subject`, `arm`, `involve_pre`, `amp_pre`, `n_pre`, `rate_pre`, `involve_stim`, `amp_stim`, `n_stim`, `rate_stim`, `involve_post`, `amp_post`, `n_post`, `rate_post`, `d_involve_stim`, `d_amp_stim`, `d_rate_pct_stim`, `d_involve_post`, `d_amp_post`, `d_rate_pct_post` |
| `participants_stats.json` | yes | keys `stim`, `post` |
| `regions.csv` | no | 120 rows; columns `kind`, `metric`, `test`, `contrast`, `rank`, `region`, `label`, `mean_change` |
| `scales.json` | yes | keys `P_origin_within`, `P_origin_between`, `P_involve_within`, `P_involve_between` |
| `explore_bh.csv` | yes | 39 rows; columns `family`, `test`, `p`, `q`, `changes` |
