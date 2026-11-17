"""Render actual FlyWire v783 neurite skeletons with a registered atlas context.

The image is a projection of real skeleton edges, not an anchor-to-anchor graph.
Colours identify neurons in the saved simulation, not measured signal travelling
along these branches. Model equations and original experimental outputs are read
only. Atlas surfaces are a registered reference, not this specimen's EM surface.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from download_morphology import decode_skeleton, validate_info
from figure_style import MM, INK, apply_style, save_figure
from render_whole_brain import load_data, MN9
from morphology_support import load_atlas, draw_atlas

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ATLAS_URL = ('https://raw.githubusercontent.com/navis-org/fafbseg-py/'
             'b62bed6572afb98ac6e64e738b8805341e7ee027/fafbseg/data/JFRC2NP.surf.fw.zip')
COLORS = {'context': '#B4BECA', 'active': '#3D729B',
          'input': '#009786', 'mn9': '#D46F36'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def roots(selection, canonical, legacy):
    return set(selection.get(canonical, selection.get(legacy, [])))


def matrix_for(tilt):
    # A proper rigid rotation about X preserves every distance and handedness.
    angle = np.deg2rad(180 + tilt)
    c, s = np.cos(angle), np.sin(angle)
    matrix = np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)
    np.testing.assert_allclose(matrix @ matrix.T, np.eye(3), atol=1e-12)
    assert np.linalg.det(matrix) > .999999999
    return matrix


def skeleton_path(vertices, edges, matrix):
    """One NaN-separated path; every source edge appears once, without fitting."""
    projected = vertices.astype(np.float64) / 1000 @ matrix.T
    lines = np.full((len(edges), 3, 2), np.nan, dtype=np.float64)
    lines[:, :2, :] = projected[edges, :2]
    return lines.reshape(-1, 2), projected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--eon-root', required=True, type=Path)
    parser.add_argument('--coordinates', required=True, type=Path)
    parser.add_argument('--cache-dir', required=True, type=Path)
    parser.add_argument('--atlas', required=True, type=Path)
    parser.add_argument('--spikes', type=Path,
                        default=HERE/'results/eon-original-20261117/function-1s.parquet')
    parser.add_argument('--output', type=Path,
                        default=ROOT/'Research/Brain/figures/eon-brain-morphology-20261117.png')
    parser.add_argument('--tilt', type=float, default=12)
    parser.add_argument('--preview', action='store_true', help='Allow explicitly reported partial morphology downloads')
    args = parser.parse_args()
    apply_style()
    plt.rcParams['path.simplify'] = False
    plan = json.loads((args.cache_dir/'selection.json').read_text(encoding='utf-8'))
    selection = plan['selection']
    active_ids = roots(selection, 'active_root_ids', 'active_roots')
    context_ids = roots(selection, 'context_root_ids', 'background_roots')
    input_ids = roots(selection, 'input_root_ids', 'input_roots')
    if not input_ids:
        raise ValueError('Rerun download_morphology.py to record the official sugar-input IDs')
    mn9_ids = set(MN9.values())
    assert input_ids <= active_ids and mn9_ids <= active_ids
    brain, spikes, evidence = load_data(args.eon_root, args.coordinates, args.spikes)
    assert set(brain.loc[brain.spike_count > 0, 'root_id']) == active_ids
    assert not active_ids & context_ids
    assert len(active_ids) == 393 and len(context_ids) == 512
    assert len(input_ids) == 21
    validate_info(json.loads((args.cache_dir/'info.json').read_text()))
    matrix = matrix_for(args.tilt)
    atlas = load_atlas(args.atlas)
    groups = {'context': [], 'active': [], 'input': [], 'mn9': []}
    missing, records = [], []
    for rid in sorted(active_ids | context_ids):
        path = args.cache_dir/f'{rid}.npz'
        raw_path = args.cache_dir/f'{rid}.precomputed'
        if not path.exists() or not raw_path.exists():
            missing.append(rid)
            continue
        vertices, edges, radius = decode_skeleton(raw_path.read_bytes())
        with np.load(path, allow_pickle=False) as saved:
            assert str(saved['root_id']) == rid
            for key, value in (('vertices_nm', vertices), ('edges', edges), ('radius_nm', radius)):
                np.testing.assert_array_equal(saved[key], value)
        group = ('mn9' if rid in mn9_ids else 'input' if rid in input_ids
                 else 'active' if rid in active_ids else 'context')
        line, projected = skeleton_path(vertices, edges, matrix)
        groups[group].append((rid, line, projected))
        records.append({'root_id': rid, 'group': group, 'vertices': len(vertices),
                        'edges': len(edges), 'raw_sha256': sha(raw_path), 'npz_sha256': sha(path)})
    if missing and not args.preview:
        raise ValueError(f'{len(missing)} requested morphologies are missing; finish the documented download first')
    if not all(any(r[0] == rid for r in groups['mn9']) for rid in mn9_ids):
        raise ValueError('Both MN9 morphologies are required even for a preview')

    fig = plt.figure(figsize=(183*MM, 110*MM))
    ax = fig.add_axes((.015, .13, .97, .84))
    draw_atlas(ax, atlas, matrix)
    # Reference surfaces establish the outline; neurites retain native geometry.
    # Fixed-width lines encode group membership, never an invented radius change.
    styles = {'context': (.25, .08, 2), 'active': (.25, .055, 3),
              'input': (.25, .80, 4), 'mn9': (.25, .85, 5)}
    extents = []
    for group in ('context', 'active', 'input', 'mn9'):
        width, alpha, order = styles[group]
        for rid, line, projected in groups[group]:
            ax.plot(line[:, 0], line[:, 1], color=COLORS[group], lw=width,
                    alpha=alpha, rasterized=True, zorder=order,
                    solid_capstyle='round', solid_joinstyle='round')
            extents.append(projected[:, :2])
    atlas_xy = np.concatenate([a['vertices_nm']/1000 @ matrix.T for a in atlas])[:, :2]
    all_extents = np.concatenate(extents + [atlas_xy])
    lo, hi = all_extents.min(0), all_extents.max(0)
    pad = np.array([16, 15])
    ax.set(xlim=(lo[0]-pad[0], hi[0]+pad[0]), ylim=(lo[1]-pad[1], hi[1]+pad[1]))
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    for label, rid in MN9.items():
        anchor = brain.loc[brain.root_id == rid, ['x_um','y_um','z_um']].to_numpy()[0] @ matrix.T
        left = label.endswith('R')
        ax.annotate(label, xy=anchor[:2],
                    xytext=(anchor[0]+(-125 if left else 125), lo[1]+35),
                    fontsize=7, ha='center', va='center',
                    arrowprops={'arrowstyle':'-', 'lw':.5, 'color':INK,
                                'shrinkA':3, 'shrinkB':1},
                    bbox={'facecolor':'white','edgecolor':'none','pad':1.0}, zorder=9)
    x0, y0 = lo[0]+30, lo[1]+12
    ax.plot([x0,x0+100],[y0,y0], color=INK, lw=1, clip_on=False, zorder=10)
    ax.text(x0+50,y0-10,'100 µm',ha='center',va='top',fontsize=7)
    handles = [Patch(facecolor='#E2E7EC',edgecolor='none',label='Registered atlas'),
               Line2D([],[],color=COLORS['context'],lw=.8,label='Context neurites'),
               Line2D([],[],color=COLORS['active'],lw=.8,label='Other spiking neurons'),
               Line2D([],[],color=COLORS['input'],lw=.8,label='Sugar GRNs'),
               Line2D([],[],color=COLORS['mn9'],lw=.8,label='MN9')]
    fig.legend(handles=handles,ncol=5,loc='lower center',bbox_to_anchor=(.5,.045),
               columnspacing=1.5,handlelength=1.8)
    if args.preview:
        fig.text(.02,.98,f'Preview: {len(records)} / 905 requested neuron skeletons',
                 fontsize=7,va='top')
    paths = save_figure(fig,args.output,'Real FlyWire v783 neuronal arbors in registered whole-brain context')
    plt.close(fig)
    sidecar = args.output.with_suffix('.json')
    metadata = {'status':'preview' if args.preview else 'complete',
        'modeled_population':138639, 'saved_simulation_spikes':len(spikes),
        'active_neurons':len(active_ids), 'context_neurons':len(context_ids),
        'simulation_duration_ms':evidence['simulation_duration_ms'],
        'displayed_skeletons':len(records), 'missing_root_ids':missing,
        'drawn_edges':sum(r['edges'] for r in records),
        'group_counts':{key:len(value) for key,value in groups.items()},
        'selection':selection,
        'geometry':'all source skeleton vertices and edges retained; no imputed branches, smoothing, graph layout, branch pruning, or artificial connecting edges',
        'projection':{'matrix':matrix.tolist(),'tilt_degrees':args.tilt,
                      'units':'micrometres; original nanometres divided by 1000; orthographic rigid rotation'},
        'encoding':'neuron-group membership; colours do not show observed activity travelling along neurites',
        'context_warning':'JFRC2 registered neuropil atlas, not the specimen EM surface; 512 context neurons are a spatial display sample, not an anatomical-density estimate',
        'atlas':{'source_url':ATLAS_URL,'original_atlas':'https://doi.org/10.5281/zenodo.10567',
                 'sha256':sha(args.atlas),'neuropils':len(atlas)},
        'skeleton_source':plan['source_doc'],'skeleton_archive':plan['public_archive'],
        'terms':plan['terms'],
        'source_hashes':{'spikes':sha(args.spikes),'coordinates':sha(args.coordinates),
                         'renderer':sha(__file__),'support':sha(HERE/'morphology_support.py'),
                         'downloader':sha(HERE/'download_morphology.py'),
                         'selection':sha(args.cache_dir/'selection.json')},
        'figure':{'size_mm':[183,110],'png_dpi':600,'text_font':'Arial',
                  'sources_rasterized':'neurite and atlas geometry only; all labels remain editable'},
        'records':records,
        'outputs':{p.suffix.lstrip('.'):{'filename':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths}}
    sidecar.write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:metadata[key] for key in ('status','displayed_skeletons','drawn_edges','group_counts')}))
    print(sidecar)


if __name__ == '__main__':
    main()
