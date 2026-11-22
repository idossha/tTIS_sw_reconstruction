# Figure 5 source data

Modeled received dose and its inter-individual variability.

Summarized by the analysis pipeline (not included) from the study data; the files marked *yes* are drawn in the figure (`brains.npz` as its brain renders); the others are summaries kept with the figure.

| File | Drawn | Contents |
|---|---|---|
| `brains.npz` | yes | per-vertex values and nilearn settings of the 12 brain views (rendered by `code/plotting/render.py`) |
| `insula_cv.csv` | yes | 3 rows; columns `metric`, `region_hemi`, `cv` |
| `intersubject_corr.npz` | yes | arrays `subjects` 32, `ti_max` 32 × 32, `ti_normal` 32 × 32, `hf_max` 32 × 32 |
| `maps.json` | yes | keys `n_subjects`, `metrics` |
| `region_cv.csv` | yes | 204 rows; columns `metric`, `region_hemi`, `cv`, `group_mean` |
| `region_subjects.csv` | yes | 6528 rows; columns `metric`, `region_hemi`, `subject_id`, `value` |
| `regions.csv` | yes | 204 rows; columns `metric`, `rank`, `region_hemi`, `rid`, `mean` |
