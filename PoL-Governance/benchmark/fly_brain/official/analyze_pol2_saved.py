"""Derive interface ablations from two saved neural trajectories; no simulation.

The input-only arm is explicitly post-hoc. An output gate has no feedback to the
LIF network, so the saved neural request tape determines its ungated interface
counterfactual. It is not a fourth neural run or an efficacy replicate.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json

import numpy as np

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def summed_sides(trace):
    values = trace.sum(axis=0).astype(np.int64)
    return {'left':int(values[0]),'right':int(values[1]),'total':int(values.sum())}


def event_timing(trace, t, mask, origin):
    # Preserve separate L and R events even when their timestamps coincide.
    step, side = np.nonzero(trace * mask[:,None])
    events = [{'time_ms':round(float(t[k]), 6), 'side':('L','R')[int(s)]}
              for k,s in zip(step,side)]
    return {'count':len(events), 'event_times_and_sides':events,
            'first_time_ms':events[0]['time_ms'] if events else None,
            'last_time_ms':events[-1]['time_ms'] if events else None,
            'last_event_time_minus_origin_ms':round(events[-1]['time_ms']-origin,6) if events else None,
            'origin_ms':origin,
            'duration_interpretation':'last observed event timestamp minus intervention onset, not a guaranteed state-clearance or biological reaction time'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, default=HERE/'results/eon-pol2-20261117-v3')
    parser.add_argument('--output-dir', type=Path, default=HERE/'analysis/pol2-2x2-20261117')
    parser.add_argument('--check', action='store_true', help='Recompute and check the published derived files without writing')
    args = parser.parse_args()
    RUN, OUT = args.run_dir, args.output_dir
    if RUN.resolve() == OUT.resolve():
        parser.error('Keep derived outputs separate from the original run directory')
    inputs = (RUN/'activity.npz',RUN/'manifest.json')
    before = {p.name:sha(p) for p in inputs}
    m = json.loads(inputs[1].read_text(encoding='utf-8'))
    with np.load(inputs[0], allow_pickle=False) as z:
        t = z['time_ms'].copy()
        permitted = z['allowed'].copy()
        sources = {key:z[key][:,:2].astype(np.int64)
                   for key in ('continuous_input','pol2_input_guard')}
        totals = {key:z[key+'_all_neuron_spike_counts'].copy() for key in sources}
        monitor_ids = z['monitor_root_ids'].astype(str).tolist()
    assert t.shape == permitted.shape == (10000,)
    assert np.array_equal(t,np.arange(10000)*.1)
    assert np.array_equal(permitted,(t<300)|(t>=700))
    assert monitor_ids[:2] == m['monitored_root_ids'][:2]
    assert all(a.shape==(10000,2) and np.isin(a,[0,1]).all() for a in sources.values())
    assert np.array_equal(sources['continuous_input'][:3000],sources['pol2_input_guard'][:3000])
    assert all(int(totals[key].sum())==m['total_spikes'][key] for key in sources)
    assert all(int((totals[key]>0).sum())==m['active_neurons'][key] for key in sources)
    original = {a['arm']:a for a in m['arms']}
    phases = ((0,300,'granted_fresh'),(300,600,'permission_withdrawn'),
              (600,700,'permission_granted_evidence_stale'),(700,1000,'reauthorized_fresh'))
    arms, phase_rows = [], []
    for name, source, output_gate, recorded_arm in (
        ('continuous_raw','continuous_input',False,'raw'),
        ('output_only','continuous_input',True,'pol2_output_guard'),
        ('input_only_posthoc','pol2_input_guard',False,None),
        ('input_and_output','pol2_input_guard',True,'pol2_input_and_output_guard')):
        requests = sources[source]
        delivered = requests*permitted[:,None] if output_gate else requests.copy()
        blocked = requests-delivered
        if recorded_arm:
            ref = original[recorded_arm]
            assert requests.sum(0).tolist()==ref['mn9_spikes']
            assert delivered.sum(0).tolist()==ref['accepted_synthetic_requests']
            assert blocked.sum(0).tolist()==ref['blocked_synthetic_requests']
            assert int(delivered[~permitted].sum())==ref['unauthorized_synthetic_requests']
        arm = {'arm':name,'input_gate':source=='pol2_input_guard','output_gate':output_gate,
            'neural_source':source,'recorded_manifest_arm':recorded_arm,
            'evidence_status':'derived post-hoc ungated-interface counterfactual from saved input-gated trajectory' if recorded_arm is None
                              else 'existing manifest arm, reconstructed from its saved neural request tape',
            'neural_generated_requests':summed_sides(requests),
            'delivered_requests':summed_sides(delivered),
            'permitted_delivered':summed_sides(delivered[permitted]),
            'prohibited_delivered':summed_sides(delivered[~permitted]),
            'blocked_requests':summed_sides(blocked),
            'request_event_frames':int((requests.sum(1)>0).sum()),
            'request_events':int(requests.sum()),
            'simultaneous_L_R_spike_frames':int((requests.sum(1)==2).sum()),
            'phases':[]}
        for lo,hi,label in phases:
            mask = (t>=lo)&(t<hi)
            phase = {'phase':label,'start_ms':lo,'stop_ms':hi,
                     'generated_requests':summed_sides(requests[mask]),
                     'delivered_requests':summed_sides(delivered[mask]),
                     'blocked_requests':summed_sides(blocked[mask])}
            arm['phases'].append(phase)
            if recorded_arm:
                ref = next(p for p in original[recorded_arm]['intervals'] if p['start_ms']==lo)
                assert requests[mask].sum(0).tolist()==ref['mn9_spikes']
                assert delivered[mask].sum(0).tolist()==ref['accepted_requests']
            phase_rows.append({'arm':name,'input_gate':arm['input_gate'],'output_gate':output_gate,
                'phase':label,'start_ms':lo,'stop_ms':hi,
                'neural_L':int(requests[mask,0].sum()),'neural_R':int(requests[mask,1].sum()),
                'neural_total':int(requests[mask].sum()),
                'delivered_L':int(delivered[mask,0].sum()),'delivered_R':int(delivered[mask,1].sum()),
                'delivered_total':int(delivered[mask].sum()),'blocked_total':int(blocked[mask].sum()),
                'posthoc_only':recorded_arm is None})
        arms.append(arm)
    residual = event_timing(sources['pol2_input_guard'], t, (t>=300)&(t<700),300)
    assert residual['count']==8
    out = {'source_hashes':before,'derived_script_sha256':sha(__file__),
        'seed':m['seed'],'independent_paired_seeds':1,'neural_trajectories':2,
        'source_run_neural_forward_calls':m['neural_forward_calls'],
        'new_neural_forward_calls':0, 'no_model_call_made_by_this_analysis':True,
        'all_existing_manifest_arm_counts_and_phases_match':True,
        'all_neuron_totals_match_saved_manifest':True,
        'before_300ms_saved_MN9_traces_equal':True,
        'runtime_full_preintervention_state_equality_reported_by_manifest':m['preintervention_state_tensors_identical'],
        'arms':arms, 'input_gated_postwithdrawal_residual':residual,
        'phase_boundaries_ms':[0,300,600,700,1000],
        'counterfactual_validity':'Output gating does not feed back to the neural simulation. For the fixed saved neural trajectory and one-spike/one-request adapter, removing the output gate delivers exactly the saved MN9 spike requests. The input-only arm was not separately recorded online and must be labelled post-hoc.',
        'limits':['one paired seed; no confidence intervals, significance or population efficacy claims',
                  'four interface conditions reuse two neural trajectories; they are not four neural replicates',
                  'weights and dynamics unchanged; external gates do not imply learned permission or PoL2 internalization',
                  'zero prohibited delivery is a deterministic interface property, not evidence of PoL2-specific advantage over identical generic rules',
                  'MN9 spikes map to synthetic virtual requests, not physical actions or observed animal behavior',
                  'last residual spike time does not establish all hidden state was erased or permanently silent']}
    assert before == {p.name:sha(p) for p in inputs}
    if args.check:
        expected = json.loads((OUT/'saved_2x2_analysis.json').read_text(encoding='utf-8'))
        assert expected == out, 'Published derived JSON differs from the saved neural evidence'
        with (OUT/'saved_2x2_phases.csv').open(encoding='utf-8',newline='') as f:
            assert list(csv.DictReader(f)) == [{key:str(value) for key,value in row.items()} for row in phase_rows]
    else:
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'saved_2x2_analysis.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
        with (OUT/'saved_2x2_phases.csv').open('w',encoding='utf-8',newline='') as f:
            writer = csv.DictWriter(f,fieldnames=list(phase_rows[0]),lineterminator='\n')
            writer.writeheader();writer.writerows(phase_rows)
    print(json.dumps({'status':'pass','checked_existing_outputs':args.check,
        'new_neural_forward_calls':0,'neural_trajectories':2,'paired_seeds':1,
        'prohibited_delivered':[a['prohibited_delivered']['total'] for a in arms],
        'permitted_delivered':[a['permitted_delivered']['total'] for a in arms],
        'last_residual_ms':residual['last_time_ms']}))


if __name__=='__main__':
    main()
