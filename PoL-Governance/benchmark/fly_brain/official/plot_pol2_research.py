"""Show the PoL2-informed external contract and saved full-brain evidence.

Only existing v3 observations are read. The input-only cell is a post-hoc
interface contrast on an already saved neural trajectory, not a fourth online
run. Anatomical colours identify the 23 monitored cell roles, not spatial
activity from the separate unseeded whole-brain illustration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from figure_style import (
    MM, INK, GRAY, BLUE, GREEN, ORANGE, apply_style, save_figure,
)
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle

from morphology_support import load_atlas, draw_atlas

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DEFAULT_WORK = Path('D:/Codebase/PoL2-FlyVis-Official')
MN9 = ('720575940660219265', '720575940618238523')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_results(run):
    manifest = json.loads((run/'manifest.json').read_text(encoding='utf-8'))
    with np.load(run/'activity.npz', allow_pickle=False) as source:
        t = source['time_ms'].copy()
        eligible = source['allowed'].copy()
        raw = source['continuous_input'][:, :2].copy()
        input_gated = source['pol2_input_guard'][:, :2].copy()
        ids = [str(int(value)) for value in source['monitor_root_ids']]
    assert raw.shape == input_gated.shape == (10000, 2)
    assert ids == manifest['monitored_root_ids'] and tuple(ids[:2]) == MN9
    assert len(set(ids)) == 23
    assert np.array_equal(eligible, (t < 300) | (t >= 700))
    assert np.array_equal(raw[:3000], input_gated[:3000])
    assert manifest['seed'] == 20261117
    assert manifest['preintervention_state_tensors_identical'] is True
    assert manifest['model']['neurons'] == 138639
    assert manifest['online_gate_checks'] == 20000
    arms = []
    for i, trace in enumerate((raw, input_gated)):
        for j in (0, 1):
            released = trace * eligible[:, None] if j else trace
            legal = int(released[eligible].sum())
            prohibited = int(released[~eligible].sum())
            blocked = int(trace.sum()-released.sum())
            arms.append({'input_gate':i, 'output_gate':j,
                         'generated':int(trace.sum()), 'legal':legal,
                         'prohibited':prohibited, 'blocked':blocked,
                         'derived_post_hoc':bool(i == 1 and j == 0)})
    assert [(r['legal'],r['prohibited']) for r in arms] == [(85,65),(85,0),(76,8),(76,0)]
    for key, index in (('raw',0),('pol2_output_guard',1),('pol2_input_and_output_guard',3)):
        record = next(a for a in manifest['arms'] if a['arm'] == key)
        result = arms[index]
        assert record['unauthorized_synthetic_requests'] == result['prohibited']
        assert sum(record['accepted_synthetic_requests']) == result['legal']+result['prohibited']
        assert sum(record['blocked_synthetic_requests']) == result['blocked']
    residue = t[(input_gated.sum(1) > 0) & ~eligible]
    assert input_gated[~eligible].sum() == 8
    assert residue.max() == 339.5
    assert tuple(raw[t >= 700].sum(0)) == (27,20)
    assert tuple(input_gated[t >= 700].sum(0)) == (23,15)
    return manifest, t, eligible, raw, input_gated, ids, arms


def draw_role_anatomy(ax, atlas, cache, ids):
    angle = np.deg2rad(192)
    c, s = np.cos(angle), np.sin(angle)
    matrix = np.array([[1,0,0],[0,c,-s],[0,s,c]])
    np.testing.assert_allclose(matrix @ matrix.T, np.eye(3), atol=1e-12)
    draw_atlas(ax, atlas, matrix)
    line_counts = {}
    for rid in ids[2:]+ids[:2]:
        with np.load(cache/f'{rid}.npz', allow_pickle=False) as source:
            assert str(source['root_id']) == rid
            vertices = source['vertices_nm'].astype(float)/1000 @ matrix.T
            edges = source['edges']
            assert np.isfinite(vertices).all() and edges.max() < len(vertices)
        path = np.full((len(edges),3,2), np.nan)
        path[:, :2] = vertices[edges, :2]
        line = path.reshape(-1,2)
        ax.plot(line[:,0],line[:,1],color=ORANGE if rid in MN9 else GREEN,
                lw=.25,alpha=.88 if rid in MN9 else .8,
                rasterized=True,zorder=5 if rid in MN9 else 4)
        line_counts[rid] = len(edges)
    all_vertices = np.concatenate([mesh['vertices_nm']/1000 @ matrix.T for mesh in atlas])
    lo, hi = all_vertices[:,:2].min(0), all_vertices[:,:2].max(0)
    ax.set(xlim=(lo[0]-10,hi[0]+10),ylim=(lo[1]-10,hi[1]+10))
    ax.set_aspect('equal',adjustable='box')
    ax.set_axis_off()
    return line_counts


def add_flow(fig, mm, cache, atlas, ids):
    # Geometry in this panel is anatomical context. All cell-role identities
    # come from the paired run's monitored root IDs, never another spike file.
    fig.text(5*MM/fig.get_figwidth(),145*MM/fig.get_figheight(),'a',fontsize=8,weight='bold')
    fig.text(10*MM/fig.get_figwidth(),145*MM/fig.get_figheight(),
             'PoL2-informed external contract',fontsize=7)
    canvas = mm(5,90,173,50)
    canvas.set(xlim=(0,173),ylim=(0,50))
    canvas.axis('off')
    canvas.add_patch(Rectangle((28,38),125,9,facecolor='#F4F6F8',edgecolor='#AEBAC4',lw=.5))
    canvas.text(90.5,42.5,'In scope  AND  current permission  AND  fresh evidence',
                fontsize=6.5,ha='center',va='center')
    # Rules are supplied to the two external interfaces, not inserted into
    # neural weights or interpreted as a learned biological representation.
    for x in (31,148):
        canvas.add_patch(FancyArrowPatch((x,38),(x,29),arrowstyle='-|>',
                         mutation_scale=5,lw=.55,color=GRAY))
    for x,w,text in ((0,17,'Sugar\n200 Hz'),(21,21,'Input\ngate'),
                      (135,27,'Execution\nrecheck')):
        canvas.add_patch(Rectangle((x,17),w,11,facecolor='white',edgecolor=INK,lw=.5,zorder=8))
        canvas.text(x+w/2,22.5,text,ha='center',va='center',fontsize=6.5,zorder=9)
    for start,end in ((17,21),(42,49),(122,135),(162,171)):
        canvas.add_patch(FancyArrowPatch((start,22.5),(end,22.5),arrowstyle='-|>',
                         mutation_scale=6,lw=.65,color=INK,zorder=10))
    canvas.text(128,29.8,'MN9',fontsize=6,ha='center')
    canvas.text(171,12,'Virtual\nrequests',fontsize=6,ha='right',va='top')
    brain = mm(54,93,73,34)
    counts = draw_role_anatomy(brain,atlas,cache,ids)
    canvas.text(85.5,1.8,'Official whole-brain model  ·  138,639 neurons',
                ha='center',fontsize=6.5)
    handles = [Line2D([],[],color=GREEN,lw=.8,label='21 sugar GRNs'),
               Line2D([],[],color=ORANGE,lw=.8,label='2 MN9 neurons')]
    fig.legend(handles=handles,loc='center',bbox_to_anchor=(.496,.586),ncol=2,
               columnspacing=1.6,handlelength=1.5,fontsize=6)
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,default=HERE/'results/eon-pol2-20261117-v3')
    parser.add_argument('--cache-dir',type=Path,default=DEFAULT_WORK/'downloads/morphology-v783')
    parser.add_argument('--atlas',type=Path,default=DEFAULT_WORK/'downloads/morphology-preview/JFRC2NP.surf.fw.zip')
    parser.add_argument('--output',type=Path,default=ROOT/'Research/Brain/figures/pol2-brain-research-20261117')
    args = parser.parse_args()
    input_files = [args.run/'activity.npz',args.run/'manifest.json']
    hashes = {str(path):sha(path) for path in input_files}
    manifest,t,eligible,raw,gated,ids,arms = load_results(args.run)
    apply_style()
    plt.rcParams['path.simplify'] = False
    width,height = 183,149
    fig = plt.figure(figsize=(width*MM,height*MM))
    def mm(left,bottom,w,h):
        return fig.add_axes((left/width,bottom/height,w/width,h/height))
    atlas = load_atlas(args.atlas)
    counts = add_flow(fig,mm,args.cache_dir,atlas,ids)

    b = mm(15,25,89,49)
    fig.text(5/width,80/height,'b',fontsize=8,weight='bold')
    fig.text(15/width,80/height,'Neural persistence and virtual execution',fontsize=7)
    b.axvspan(300,600,color='#ECEFF2',lw=0,zorder=0)
    b.axvspan(600,700,color='#FFF1D4',lw=0,zorder=0)
    curves = ((raw.sum(1),BLUE,'-','Continuous: MN9'),
              (gated.sum(1),GREEN,'-','Input gated: MN9'),
              ((raw*eligible[:,None]).sum(1),BLUE,'--','Output gated: requests'),
              ((gated*eligible[:,None]).sum(1),GREEN,'--','Both gated: requests'))
    for values,color,linestyle,label in curves:
        cumulative = np.cumsum(values)
        # Keep changes and endpoints, preserving the exact step curve while
        # avoiding thousands of duplicate flat SVG vertices. No smoothing.
        changes = np.flatnonzero(np.r_[False,np.diff(cumulative) != 0])
        keep = np.unique(np.r_[0,changes,len(t)-1])
        reconstructed = cumulative[keep][np.searchsorted(t[keep],t,side='right')-1]
        np.testing.assert_array_equal(reconstructed,cumulative)
        b.step(t[keep],cumulative[keep],where='post',color=color,ls=linestyle,
               lw=.8,label=label)
    b.set(xlim=(0,1000),ylim=(0,172),xticks=(0,300,600,700,1000),
          yticks=(0,50,100,150),xlabel='Time (ms)',ylabel='Cumulative count')
    b.text(450,163,'Withdrawn',ha='center',va='center',fontsize=5.5)
    b.text(650,163,'Stale',ha='center',va='center',fontsize=5.5)
    b.text(850,163,'Restored',ha='center',va='center',fontsize=5.5)
    b.annotate('8 residual spikes\nlast at 339.5 ms',xy=(410,42),xytext=(470,16),
               fontsize=6,ha='left',va='bottom',
               arrowprops={'arrowstyle':'-','lw':.5,'color':INK})
    b.plot((410,410),(38,46),color=INK,lw=.5)
    b.plot((400,420),(38,38),color=INK,lw=.5)
    b.plot((400,420),(46,46),color=INK,lw=.5)
    b.legend(loc='upper left',bbox_to_anchor=(-.10,-.25),ncol=2,
             columnspacing=1.0,handlelength=2.0,fontsize=5.5,borderaxespad=0)

    fig.text(114/width,80/height,'c',fontsize=8,weight='bold')
    fig.text(120/width,80/height,'Delivered virtual requests (count)',fontsize=7)
    c = mm(133,27,43,43)
    c.set(xlim=(0,2),ylim=(0,2))
    for result in arms:
        i,j = result['input_gate'],result['output_gate']
        y = 1-i
        c.add_patch(Rectangle((j,y),1,1,facecolor='#FFF1D9' if result['prohibited'] else '#F0F5F8',
                              edgecolor='white',lw=.8))
        derived_mark = '†' if result['derived_post_hoc'] else ''
        c.text(j+.5,y+.61,f"{result['prohibited']} prohibited{derived_mark}",
               ha='center',va='center',fontsize=7,weight='bold')
        c.text(j+.5,y+.34,f"{result['legal']} legal",ha='center',va='center',fontsize=6.5)
    c.set_xticks((.5,1.5),('Off','On'))
    c.set_yticks((1.5,.5),('Off','On'))
    c.tick_params(length=0,pad=4,labelsize=6)
    c.xaxis.tick_top()
    c.xaxis.set_label_position('top')
    c.set_xlabel('Output gate',labelpad=4)
    c.set_ylabel('Input gate',labelpad=6)
    for spine in c.spines.values():
        spine.set_visible(False)
    fig.text(114/width,20/height,'† Input-only: post-hoc interface contrast',fontsize=5.5)
    fig.text(114/width,15/height,'Two neural trajectories; one paired seed',fontsize=5.5)
    paths = save_figure(fig,args.output,'PoL2-informed external contract and saved whole-brain evidence')
    plt.close(fig)
    assert hashes == {str(path):sha(path) for path in input_files}
    metadata = {'outputs':{p.suffix.lstrip('.'):{'filename':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths},'size_mm':[width,height],
          'source_files_unchanged':True,'seed':manifest['seed'],
          'neural_trajectories':2,'conditions':arms,'anatomy_root_ids':ids,
          'anatomy_source_edges':sum(counts.values()),
          'anatomy_encoding':'23 monitored roles only; no spatial activity encoded',
          'request_curves_origin':'reconstructed from saved MN9 traces and frozen eligibility; totals checked against the online v3 manifest',
          'curve_export':'constant-count runs compressed to changes and endpoints; exact reconstruction asserted at all 10000 saved times; no smoothing',
          'atlas_sha256':sha(args.atlas),'script_sha256':sha(__file__),
          'source_hashes':{p.name:sha(p) for p in input_files},
          'scope_warning':'Scope is constant in this run; the scope predicate is implemented but cross-scope violations were not tested',
          'interpretation':'External interface deployment of PoL2-informed conditions; no learned PoL2, no neural state erasure, no PoL2-specific advantage over identical rules',
          'narrative_note':'Input+output gating has 76 legal delivered requests versus 85 with output-only; zero prohibited delivery alone does not establish superiority'}
    args.output.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'outputs':[str(p) for p in paths],'size_mm':[width,height],
                      'neural_trajectories':2,'paired_seeds':1,
                      'source_files_unchanged':True,'anatomical_roles':len(ids)}))


if __name__ == '__main__':
    main()
