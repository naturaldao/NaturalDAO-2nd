"""Verify published loading/response evidence without Torch, downloads or a GPU."""
import hashlib
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    run=HERE/'results/flyvis-moving-edge-20261117'
    v=json.loads((run/'manifest.json').read_text())
    assert v['script_sha256']==sha(HERE/'run_official.py')
    assert v['n_nodes']==45669 and v['n_edges']==1513231
    assert v['response_cache_used'] is False
    assert all(r['equal'] for r in v['weights_exactly_loaded'].values())
    assert v['final_forward_counter']=={'forward_calls':50,'integrated_frames':16660}
    smoke=np.load(run/'smoke_activity.npz')
    assert smoke['full_space_activity'].shape==(5,45669)
    assert np.isfinite(smoke['full_space_activity']).all()
    final=HERE/'results/eon-pol2-20261117-v3'
    previous=HERE/'results/eon-pol2-20261117-v2'
    m=json.loads((final/'manifest.json').read_text())
    assert m['runner_sha256']==sha(HERE/'run_eon_pol2.py')
    assert m['model']['neurons']==138639 and m['model']['sparse_weight_nnz']==15091983
    assert m['official_cached_csr_exactly_matches_independent_raw_parquet_csr'] is True
    assert m['online_gate_checks']==20000
    assert m['preintervention_state_tensors_identical'] is True
    a,b=np.load(final/'activity.npz'),np.load(previous/'activity.npz')
    assert a.files==b.files
    assert all(np.array_equal(a[k],b[k]) for k in a.files)
    assert all(np.isfinite(a[k]).all() for k in ('continuous_input','pol2_input_guard'))
    for arm,source,gate in (('raw','continuous_input',False),
            ('pol2_output_guard','continuous_input',True),
            ('pol2_input_and_output_guard','pol2_input_guard',True)):
        trace=a[source][:,:2]
        executed=trace*a['allowed'][:,None] if gate else trace
        item=next(x for x in m['arms'] if x['arm']==arm)
        assert trace.sum(0).tolist()==item['mn9_spikes']
        assert executed.sum(0).tolist()==item['accepted_synthetic_requests']
        assert int(executed[~a['allowed']].sum())==item['unauthorized_synthetic_requests']
    original=HERE/'results/eon-original-20261117'
    o=json.loads((original/'manifest.json').read_text())
    for r in o['runs']:
        assert r['sha256']==sha(original/r['output'])
    print(json.dumps({'status':'pass','official_weights_and_forward_manifest':True,
                      'complete_saved_v2_v3_neural_observations_equal':True,
                      'full_brain_counts_and_gate_outcomes_consistent':True}))


if __name__=='__main__':
    main()
