"""Publication-size figure from saved Eon–PoL2 v3 activity; no simulation."""
from pathlib import Path
import json
import numpy as np
from figure_style import apply_style, panel_label, save_figure, MM, INK, GRAY, BLUE, ORANGE
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
RUN = HERE / 'results/eon-pol2-20261117-v3'
DEST = HERE.parents[3] / 'Research/Brain/figures/eon-pol2-20261117'
REVOKED, STALE = '#ECECEC', '#FFF1D4'


def load_data():
    meta = json.loads((RUN / 'manifest.json').read_text())
    with np.load(RUN / 'activity.npz') as saved:
        t, allowed = saved['time_ms'].copy(), saved['allowed'].copy()
        raw = saved['continuous_input'][:, :2].copy()
        gated = saved['pol2_input_guard'][:, :2].copy()
    assert t.shape == allowed.shape == (10000,)
    assert raw.shape == gated.shape == (10000, 2)
    assert np.array_equal(allowed, (t < 300) | (t >= 700))
    assert np.array_equal(raw[:3000], gated[:3000])
    arms = []
    for key, label, source, use_gate in (
        ('raw', 'Raw', raw, False),
        ('pol2_output_guard', 'Output gate', raw, True),
        ('pol2_input_and_output_guard', 'Input + output gates', gated, True),
    ):
        accepted = source * allowed[:, None] if use_gate else source.copy()
        record = next(row for row in meta['arms'] if row['arm'] == key)
        assert source.sum(0).tolist() == record['mn9_spikes']
        assert accepted.sum(0).tolist() == record['accepted_synthetic_requests']
        assert (source-accepted).sum(0).tolist() == record['blocked_synthetic_requests']
        unauthorized = int(accepted[~allowed].sum())
        assert unauthorized == record['unauthorized_synthetic_requests']
        arms.append({'label': label, 'accepted': accepted,
                     'allowed_count': int(accepted[allowed].sum()),
                     'unauthorized_count': unauthorized,
                     'blocked_count': int((source-accepted).sum())})
    assert [a['allowed_count'] for a in arms] == [85, 85, 76]
    assert [a['unauthorized_count'] for a in arms] == [65, 0, 0]
    assert int(gated[~allowed].sum()) == 8
    return t, allowed, raw, gated, arms


def shade(ax):
    ax.axvspan(300, 600, facecolor=REVOKED, edgecolor='none', zorder=0)
    ax.axvspan(600, 700, facecolor=STALE, edgecolor='none', zorder=0)
    ax.set_xlim(0, 1000)


def spike_ticks(ax, times, y, color, half_height=.16):
    ax.vlines(times, y-half_height, y+half_height, linewidth=.5, color=color, zorder=3)


def main():
    apply_style()
    t, allowed, raw, gated, arms = load_data()
    fig = plt.figure(figsize=(183*MM, 153*MM))
    grid = fig.add_gridspec(4, 1, left=.205, right=.978, bottom=.077, top=.953,
                           height_ratios=[.82, 1.35, 1.08, 1.25], hspace=.58)
    a = fig.add_subplot(grid[0])
    b = fig.add_subplot(grid[1], sharex=a)
    c = fig.add_subplot(grid[2], sharex=a)
    d = fig.add_subplot(grid[3])
    for ax, letter, title in zip((a,b,c,d), 'abcd',
            ('Stimulus input', 'MN9 neural spikes', 'Virtual actuator requests', 'Request counts')):
        panel_label(ax, letter, x=-.235, y=1.055)
        ax.set_title(title, loc='left', pad=6)
    for ax in (a,b,c):
        shade(ax)
        ax.set_xticks(np.arange(0, 1001, 200))
    for ax in (a,b):
        ax.tick_params(axis='x', bottom=False, labelbottom=False)
        ax.spines['bottom'].set_visible(False)

    a.plot(t, np.full(t.shape, 200), color=GRAY, linestyle=(0,(3,2)), linewidth=.7, label='Continuous')
    a.step(t, allowed.astype(float)*200, where='post', color=BLUE, linewidth=.9, label='Input gated')
    a.set_ylim(-15, 285)
    a.set_yticks([0,200])
    a.set_ylabel('GRN input\n(Hz)')
    a.text(450,245,'Permission withdrawn',ha='center',va='center',fontsize=6)
    a.text(650,245,'Stale',ha='center',va='center',fontsize=6)
    a.legend(loc='upper right',bbox_to_anchor=(1,1.24),ncol=2,columnspacing=1.3,handlelength=2.2)

    for y, source, side in ((3,raw,0),(2,raw,1),(1,gated,0),(0,gated,1)):
        spike_ticks(b,t[source[:,side]>0],y,INK if y>=2 else BLUE)
    b.set_yticks([3,2,1,0],['Continuous, L','Continuous, R','Input gated, L','Input gated, R'])
    b.tick_params(axis='y',length=0,pad=5)
    b.set_ylim(-.55,3.55)
    b.spines['left'].set_visible(False)
    residue=t[(gated.sum(1)>0)&~allowed]
    b.annotate('8 residual spikes',xy=(float(residue.max()),.55),xytext=(420,.55),
               ha='left',va='center',fontsize=6,
               arrowprops={'arrowstyle':'-','color':INK,'lw':.5,'shrinkA':3,'shrinkB':2})

    for row,item in enumerate(arms):
        y=2-row
        for side in (0,1):
            present=item['accepted'][:,side]>0
            offset=.085 if side==0 else -.085
            spike_ticks(c,t[present&allowed],y+offset,BLUE,half_height=.11)
            spike_ticks(c,t[present&~allowed],y+offset,ORANGE,half_height=.11)
    c.set_yticks([2,1,0],[item['label'] for item in arms])
    c.tick_params(axis='y',length=0,pad=5)
    c.set_ylim(-.5,2.5)
    c.spines['left'].set_visible(False)
    c.set_xlabel('Time (ms)')

    for row,item in enumerate(arms):
        y=2-row
        yes,no=item['allowed_count'],item['unauthorized_count']
        d.barh(y,yes,height=.48,color=BLUE,edgecolor='none')
        if no:
            d.barh(y,no,left=yes,height=.48,color=ORANGE,edgecolor='none')
        d.text(yes/2,y,str(yes),ha='center',va='center',color='white',fontsize=6)
        if no:
            d.text(yes+no/2,y,str(no),ha='center',va='center',fontsize=6)
        if item['blocked_count']:
            d.text(yes+no+4,y,f"{item['blocked_count']} blocked",ha='left',va='center',fontsize=6)
    d.set_yticks([2,1,0],[item['label'] for item in arms])
    d.tick_params(axis='y',length=0,pad=5)
    d.spines['left'].set_visible(False)
    d.set_xlim(0,160)
    d.set_ylim(-.55,2.55)
    d.set_xticks([0,50,100,150])
    d.set_xlabel('Virtual requests (count)')
    d.legend(handles=[Patch(facecolor=BLUE,label='Allowed'),Patch(facecolor=ORANGE,label='Not authorized')],
             loc='upper right',bbox_to_anchor=(1,1.40),ncol=2,columnspacing=1.3)
    paths=save_figure(fig,DEST,'Eon full-brain activity and PoL2 virtual execution interface')
    print(json.dumps({'files':[str(p) for p in paths],'width_mm':183,'height_mm':153,
                      'allowed_counts':[i['allowed_count'] for i in arms],
                      'unauthorized_counts':[i['unauthorized_count'] for i in arms]}))
    plt.close(fig)


if __name__=='__main__':
    main()
