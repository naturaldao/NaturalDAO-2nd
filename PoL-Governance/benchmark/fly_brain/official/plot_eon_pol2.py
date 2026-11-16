"""Render saved full-brain activity and synchronous simulated execution counts."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RUN = HERE/'results/eon-pol2-20261117-v3'
DEST = HERE.parents[3]/'Research/Brain/figures'
d = np.load(RUN/'activity.npz')
meta = json.loads((RUN/'manifest.json').read_text())
t, permitted = d['time_ms'], d['allowed']
raw = d['continuous_input'][:, :2]
gated = d['pol2_input_guard'][:, :2]
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10,
                     'axes.spines.top':False, 'axes.spines.right':False})
fig, axes = plt.subplots(3, 1, figsize=(12, 8.5), sharex=True, constrained_layout=True,
                         gridspec_kw={'height_ratios':[.8, 1.2, 1.1]})
for ax in axes:
    ax.axvspan(300, 600, color='#de775f', alpha=.13)
    ax.axvspan(600, 700, color='#d9a743', alpha=.18)
    ax.grid(axis='x', alpha=.15)
axes[0].plot(t, np.full_like(t,200), '--', color='#64748b', label='Continuous sugar input')
axes[0].plot(t, permitted*200, color='#247d71', label='Input authorization gate')
axes[0].set(ylabel='GRN drive (Hz)', ylim=(-15,255), title='A  External stimulus authorization; official neural dynamics unchanged')
axes[0].legend(loc='upper right',frameon=False)
for j, (trace, label, color) in enumerate(((raw,'Continuous input','#64748b'),(gated,'Input gated','#247d71'))):
    for k, side in enumerate(('L','R')):
        y = 3-j*2-k
        axes[1].scatter(t[trace[:,k]>0], np.full(int(trace[:,k].sum()), y), marker='|', s=65, color=color)
axes[1].set(yticks=[0,1,2,3],yticklabels=['Gated: MN9 R','Gated: MN9 L','Raw: MN9 R','Raw: MN9 L'],
            ylim=(-.7,3.7),title='B  Actual spikes of the full 138,639-neuron model: residual spikes can outlast the input')
for row, (name, trace, use_gate, color) in enumerate((
        ('raw',raw,False,'#64748b'),('pol2_output_guard',raw,True,'#367eb6'),
        ('pol2_input_and_output_guard',gated,True,'#247d71'))):
    accepted = trace*permitted[:,None] if use_gate else trace
    recorded = next(a for a in meta['arms'] if a['arm']==name)
    assert accepted.sum(0).tolist()==recorded['accepted_synthetic_requests']
    for k in (0,1):
        times=t[accepted[:,k]>0]
        axes[2].scatter(times,np.full(len(times),2-row+(k-.5)*.1),s=45,marker='|',color=color)
    axes[2].text(1005,2-row,f"{recorded['unauthorized_synthetic_requests']} unauthorized",va='center',fontsize=9)
axes[2].set(yticks=[0,1,2],yticklabels=['Input + output gate','Output gate only','Raw requests'],
            ylim=(-.6,2.6),xlim=(0,1150),xlabel='Simulation time (ms)',
            title='C  Synchronous virtual actuator requests; no physical body is simulated')
axes[0].text(450,235,'Permission withdrawn',ha='center',fontsize=9)
axes[0].text(650,235,'Stale evidence',ha='center',fontsize=8)
fig.suptitle('PoL2 adapter on the official full-brain model: one paired random seed',fontsize=15)
fig.supxlabel('Same official weights and same random stream; full hidden state identical before 300 ms.\n'
              'Red/orange bands prohibit simulated requests. Output gating does not erase neural activity.',fontsize=9)
DEST.mkdir(parents=True,exist_ok=True)
fig.savefig(DEST/'eon-pol2-20261117.png',dpi=160)
fig.savefig(DEST/'eon-pol2-20261117.pdf')
print(DEST/'eon-pol2-20261117.png')
