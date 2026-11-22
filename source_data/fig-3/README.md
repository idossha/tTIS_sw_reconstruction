# Figure 3 source data

Sensor-space slow-wave density and morphology.

Summarized by the analysis pipeline (not included) from the study data; the files marked *yes* are drawn in the figure (`brains.npz` as its brain renders); the others are summaries kept with the figure.

| File | Drawn | Contents |
|---|---|---|
| `density_maps.npz` | yes | arrays `channels` 183, `stim_vs_pre_active_protocol` 10 × 183, `stim_vs_pre_sham_protocol` 10 × 183, `stim_vs_pre_active_pooled` 183, `stim_vs_pre_sham_pooled` 183, `stim_vs_pre_diff_pooled` 183, `stim_vs_pre_vmax_pooled` scalar, `stim_vs_pre_vmax_protocol` scalar, `stim_vs_pre_sig_active` 183, `stim_vs_pre_sig_sham` 183, `stim_vs_pre_sig_diff` 183, `post_vs_pre_active_protocol` 10 × 183, `post_vs_pre_sham_protocol` 10 × 183, `post_vs_pre_active_pooled` 183, `post_vs_pre_sham_pooled` 183, `post_vs_pre_diff_pooled` 183, `post_vs_pre_vmax_pooled` scalar, `post_vs_pre_vmax_protocol` scalar, `post_vs_pre_sig_active` 183, `post_vs_pre_sig_sham` 183, `post_vs_pre_sig_diff` 183 |
| `density_trend.csv` | yes | 40 rows; columns `metric`, `contrast`, `group`, `episode`, `mean`, `lo`, `hi`, `wilcoxon_p`, `n_slopes` |
| `depth.csv` | yes | 60 rows; columns `arm`, `key`, `bin`, `mean`, `sem`, `n`, `kind`, `pct`, `p_within`, `q_within` |
| `forest.csv` | yes | 24 rows; columns `measure`, `contrast`, `group`, `r`, `lo`, `hi`, `p`, `n` |
| `montage.csv` | yes | 183 rows; columns `channel`, `x`, `y` |
| `stage.csv` | yes | 26 rows; columns `kind`, `arm`, `stage`, `key`, `mean`, `sem`, `n`, `pct`, `p_within`, `q_within` |
| `stage_change.csv` | yes | 8 rows; columns `arm`, `stage`, `key`, `mean`, `median`, `lo`, `hi`, `n` |
| `waveforms.csv` | yes | 121 rows; columns `time`, `active_pre_mean`, `active_stim_mean`, `active_post_mean`, `active_diff_mean`, `active_diff_lo`, `active_diff_hi`, `active_n`, `sham_pre_mean`, `sham_stim_mean`, `sham_post_mean`, `sham_diff_mean`, `sham_diff_lo`, `sham_diff_hi`, `sham_n` |
| `bh_families.csv` | yes | 120 rows; columns `family`, `measure`, `contrast`, `comparison`, `p`, `q` |
