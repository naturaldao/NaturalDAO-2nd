"""Replot published summary values; no model fitting or trial-level reanalysis.

Input: Schmidbauer & Nieder, Figshare 33205326 v2, data_fig1_behavior.mat.
Data/author plotting code: CC BY 4.0. The published Science figure is not copied.
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat

folder = Path(__file__).resolve().parent
data = loadmat(folder / 'data_fig1_behavior.mat')
assert data['meanperf_obs_subj'].shape == (2, 5)
assert data['medianRT_obs_subj'].shape == (2, 5)
assert np.isfinite(data['medianRT_obs_subj']).all()
x = data['x_data'].ravel() * 100
xf = data['x_fitdata'].ravel() * 100
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold'})
fig, axes = plt.subplots(2, 2, figsize=(10.5, 6.6), sharex=True, layout='constrained')
for crow in range(2):
    for row in range(2):
        ax = axes[row, crow]
        if row == 0:
            obs, sem, mean, band = ('meanperf_obs_subj','semperf_obs_subj','mean_psyfit_subj','y_combined_prob_subj')
            scale, ylim, ylabel = 100, (44, 102), 'Accuracy (%)'
        else:
            obs, sem, mean, band = ('medianRT_obs_subj','sem_medianRT_obs_subj','mean_chrofit_median_subj','y_combined_rtmedian_subj')
            scale, ylim, ylabel = 1000, (200, 272), 'Mean session-median RT (ms)'
        ax.fill(data['x_combined_prob_subj'][crow] * 100, data[band][crow] * scale, color='#238255', alpha=.16, edgecolor='none', label='Authors\' model uncertainty')
        ax.plot(xf, data[mean][crow] * scale, color='#238255', lw=2, label='Authors\' supplied curve')
        ax.errorbar(x, data[obs][crow] * scale, yerr=data[sem][crow] * scale, fmt='o', color='#20242a', ms=5, capsize=3, label='Shared summary data ± SEM')
        ax.set(xlim=(-3, 85), ylim=ylim, ylabel=ylabel, xticks=[0, 20, 40, 60, 80])
        ax.grid(axis='y', color='#dddddd', lw=.6)
        if row == 0:
            ax.set_title(f'Crow {crow+1} ({55 if crow == 0 else 102} sessions)')
            ax.set_yticks([50, 75, 100])
        else:
            ax.set_xlabel('Motion coherence (%)')
            ax.set_yticks([200, 220, 240, 260])
        ax.text(-.14, 1.02, 'ABCD'[row*2+crow], transform=ax.transAxes, fontsize=12, fontweight='bold')
axes[1,1].legend(fontsize=7.5, loc='upper right', frameon=False)
fig.suptitle('Avian decisions: shared data replot (Figshare v2)', fontsize=14, fontweight='bold')
fig.supxlabel('Some RT summaries differ from the journal text; see the report.', fontsize=8, color='#6b3d27')
fig.savefig(folder / 'avian_behavior_replot.png', dpi=220, facecolor='white')
plt.close(fig)
with (folder / 'avian_behavior_summary.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.writer(stream)
    writer.writerow(['crow','sessions','coherence_percent','accuracy_percent','accuracy_sem_percentage_points','session_median_rt_mean_ms','session_median_rt_sem_ms'])
    for crow in range(2):
        for j, coherence in enumerate(x):
            writer.writerow([crow+1,55 if crow == 0 else 102,float(coherence),float(data['meanperf_obs_subj'][crow,j]*100),float(data['semperf_obs_subj'][crow,j]*100),float(data['medianRT_obs_subj'][crow,j]*1000),float(data['sem_medianRT_obs_subj'][crow,j]*1000)])
print('Saved avian_behavior_replot.png and avian_behavior_summary.csv')
