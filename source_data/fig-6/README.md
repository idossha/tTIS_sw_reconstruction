# Figure 6 source data

Modeled field and the shift toward N3 sleep during stimulation.

Summarized by the analysis pipeline (not included) from the study data; the files marked *yes* are drawn in the figure (`brains.npz` as its brain renders); the others are summaries kept with the figure.

| File | Drawn | Contents |
|---|---|---|
| `dose/bands.csv` | yes | 240 rows; columns `field`, `arm`, `x`, `fit`, `lo`, `hi` |
| `dose/maps.json` | no | keys `vmin`, `vmax`, `cmap`, `range_inside` |
| `dose/participants.csv` | yes | 43 rows; columns `subject`, `arm`, `d_stim`, `d_post`, `ti_max`, `hf_max`, `ti_normal`, `group`, `y` |
| `dose/scatter.csv` | yes | 86 rows; columns `field`, `arm`, `subject_id`, `dose`, `response` |
| `dose/stats.json` | yes | keys `median_ti_max`, `groups`, `global`, `dose_arms` |
| `dose/time_clusters.csv` | no | 1 rows; columns `test`, `t_start_s`, `t_stop_s`, `n_steps`, `mass`, `sign`, `p_cluster`, `n` |
| `dose/timecourse.csv` | yes | 66 rows; columns `group`, `t_s`, `mean`, `sem`, `size` |
| `maps/brains.npz` | yes | per-vertex values and nilearn settings of the 12 brain views (rendered by `code/plotting/render.py`) |
| `maps/focality_bands.csv` | no | 300 rows; columns `field`, `arm`, `x`, `fit`, `lo`, `hi` |
| `maps/focality_scatter.csv` | no | 118 rows; columns `field`, `arm`, `subject_id`, `dose`, `response` |
| `maps/stats.json` | yes | keys `vmin`, `vmax`, `cmap`, `forming_p`, `focality`, `maps` |
| `time/stats.json` | no | keys `rho_ti_max_ti_normal`, `rho_ti_max_hf_max`, `n`, `ti_normal_vertices`, `inside_ti_max`, `right_hemisphere` |
| `time/time_clusters.csv` | yes | 2 rows; columns `test`, `t_start_s`, `t_stop_s`, `n_steps`, `mass`, `sign`, `p_cluster`, `n` |
| `time/time_steps.csv` | yes | 20 rows; columns `test`, `t_s`, `effect`, `stat`, `p_step`, `n` |
| `outline/brains.npz` | yes | per-vertex values and nilearn settings of the 4 brain views (rendered by `code/plotting/render.py`) |
| `explore_bh.csv` | yes | 39 rows; columns `family`, `test`, `p`, `q`, `changes` |
