"""Run Eon's unmodified full-size TorchModel with a synthetic PoL2 adapter.

The external contract controls simulated stimulation/actuator requests. It is
not learned permission, biological consent, or a physical body simulation.
The third-party model retains its upstream GPL-2.0-or-later license.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
import pyarrow  # upstream requires Arrow before torch on Windows
import numpy as np
import pandas as pd
import torch
from scipy.sparse import coo_matrix

EXPECTED = {
    '2025_Completeness_783.csv': '52b0ac6094cd32c546f8d4c341e094376f48f4e791f8db9b166de5dff8199ea4',
    '2025_Connectivity_783.parquet': 'efeb23fb99098e9c390f6869969b2a121a2ee92c833cfc45ecb2c1d8e1af0347'}
MN9 = [720575940660219265, 720575940618238523]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def facts_at(t_ms):
    return {'scope': 'simulated_sugar_trial',
            'permission': 'DENIED' if 300 <= t_ms < 600 else 'GRANTED',
            'fresh': not 600 <= t_ms < 700,
            'version': 1 if t_ms < 300 else 2 if t_ms < 600 else 3 if t_ms < 700 else 4}


def allowed(facts):
    return (facts['permission'] == 'GRANTED' and facts['fresh']
            and facts['scope'] == 'simulated_sugar_trial')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--upstream', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=20261117)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Choose a new output directory')
    args.output.mkdir(parents=True)
    started = time.perf_counter()
    upstream = args.upstream.resolve()
    hashes = {name: sha(upstream/'data'/name) for name in EXPECTED}
    assert hashes == EXPECTED, 'Official source data checksum mismatch'
    sys.path.insert(0, str(upstream/'code'))
    from run_pytorch import TorchModel, MODEL_PARAMS, DT, get_weights, get_hash_tables
    from benchmark import get_experiment
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if device == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    weights_cpu = get_weights(upstream/'data/2025_Connectivity_783.parquet',
                              upstream/'data/2025_Completeness_783.csv', upstream/'data')
    assert tuple(weights_cpu.shape) == (138639, 138639)
    # Independently reconstruct from the verified raw parquet, not the cache.
    raw_edges = pd.read_parquet(upstream/'data/2025_Connectivity_783.parquet', columns=[
        'Postsynaptic_Index', 'Presynaptic_Index', 'Excitatory x Connectivity'])
    independent = coo_matrix((raw_edges['Excitatory x Connectivity'].to_numpy(dtype=np.float32),
        (raw_edges['Postsynaptic_Index'].to_numpy(), raw_edges['Presynaptic_Index'].to_numpy())),
        shape=(138639, 138639)).tocsr()
    assert np.array_equal(independent.indptr, weights_cpu.crow_indices().numpy())
    assert np.array_equal(independent.indices, weights_cpu.col_indices().numpy())
    assert np.array_equal(independent.data, weights_cpu.values().numpy())
    raw_edge_count = len(raw_edges)
    del independent, raw_edges
    weights = weights_cpu.to(device)
    for method in ('crow_indices', 'col_indices', 'values'):
        assert torch.equal(getattr(weights, method)().cpu(), getattr(weights_cpu, method)())
    ids, _ = get_hash_tables(upstream/'data/2025_Completeness_783.csv')
    experiment = get_experiment('sugar')
    excitation = [ids[n] for n in experiment['neu_exc']]
    monitored = MN9 + experiment['neu_exc']
    monitor_index = torch.tensor([ids[n] for n in monitored], device=device)
    steps = 10000
    permitted = np.array([allowed(facts_at(k*DT)) for k in range(steps)])
    records, totals, online_requests = {}, {}, {}
    prestate = None
    forward_calls = {}
    for name in ('continuous_input', 'pol2_input_guard'):
        model = TorchModel(1, 138639, DT, MODEL_PARAMS, weights,
                           exc_indices=excitation, device=device).eval()
        state = model.state_init()
        generator = torch.Generator(device=device).manual_seed(args.seed)
        rates = torch.zeros((1, 138639), device=device)
        monitor = torch.zeros((steps, len(monitored)), device=device)
        admitted = torch.zeros((steps, 2), device=device)
        neuron_counts = torch.zeros(138639, device=device)
        calls = [0]
        def count_forward(module, values, output):
            calls[0] += 1
        hook = model.register_forward_hook(count_forward)
        with torch.no_grad():  # match upstream; sparse CSR transpose rejects inference tensors
            for k in range(steps):
                rates[:, excitation] = 200.0 if name == 'continuous_input' or permitted[k] else 0.0
                state = model(rates, *state, generator=generator)
                monitor[k] = state[2][0, monitor_index]
                # Synchronous simulated actuator step, immediately after each forward.
                # No physical actuator or body model is present.
                latest = facts_at(k*DT)
                admitted[k] = monitor[k, :2] if allowed(latest) else 0
                neuron_counts += state[2][0]
                if k == 2999:
                    if prestate is None:
                        prestate = tuple(s.clone() for s in state)
                    else:
                        assert all(torch.equal(a, b) for a, b in zip(prestate, state)), 'Branches differ before intervention'
                if (k+1) % 2000 == 0:
                    print(f'{name}: {k+1}/{steps}', flush=True)
        hook.remove()
        if device == 'cuda':
            torch.cuda.synchronize()
        assert calls[0] == steps
        assert all(torch.isfinite(s).all() for s in state)
        records[name] = monitor.cpu().numpy().astype(np.uint8)
        online_requests[name] = admitted.cpu().numpy().astype(np.uint8)
        totals[name] = neuron_counts.cpu().numpy().astype(np.int64)
        forward_calls[name] = calls[0]
    assert np.array_equal(records['continuous_input'][:3000], records['pol2_input_guard'][:3000])
    intervals = ((0, 300), (300, 600), (600, 700), (700, 1000))
    summaries = []
    for arm, source, gate_output in (
            ('raw', 'continuous_input', False),
            ('pol2_output_guard', 'continuous_input', True),
            ('pol2_input_and_output_guard', 'pol2_input_guard', True)):
        trace = records[source][:, :2]
        executed = online_requests[source] if gate_output else trace
        if gate_output:
            assert np.array_equal(executed, trace * permitted[:, None])
        rejected = trace.astype(np.int64)-executed.astype(np.int64)
        item = {'arm': arm, 'neural_source': source,
                'mn9_spikes': trace.sum(0).tolist(),
                'accepted_synthetic_requests': executed.sum(0).tolist(),
                'blocked_synthetic_requests': rejected.sum(0).tolist(),
                'unauthorized_synthetic_requests': int(executed[~permitted].sum()),
                'intervals': []}
        for lo, hi in intervals:
            mask = (np.arange(steps)*DT >= lo) & (np.arange(steps)*DT < hi)
            item['intervals'].append({'start_ms': lo, 'stop_ms': hi,
                'permission': facts_at(lo)['permission'], 'fresh': facts_at(lo)['fresh'],
                'mn9_spikes': trace[mask].sum(0).tolist(),
                'accepted_requests': executed[mask].sum(0).tolist()})
        summaries.append(item)
    np.savez_compressed(args.output/'activity.npz', time_ms=np.arange(steps)*DT,
                        monitor_root_ids=np.array(monitored, dtype=np.int64), allowed=permitted,
                        **records, **{k+'_all_neuron_spike_counts': v for k,v in totals.items()})
    result = {'scope': 'official full-size Eon TorchModel with project-added synthetic input/output authorization',
        'upstream_commit': 'a3db62f9436074e485c0278290c2164ed6150808',
        'source_data_sha256': hashes, 'runner_sha256': sha(__file__),
        'official_model_source_sha256': sha(upstream/'code/run_pytorch.py'),
        'raw_parquet_edges': raw_edge_count,
        'official_cached_csr_exactly_matches_independent_raw_parquet_csr': True,
        'output_gating': 'online synchronous simulated actuator step immediately after every model forward; independently checked against tape afterward',
        'online_gate_checks': sum(forward_calls.values()),
        'model': {'neurons': 138639, 'sparse_weight_nnz': weights._nnz(),
                  'dt_ms': DT, 'steps': steps, 'duration_ms': steps*DT, 'parameters': MODEL_PARAMS},
        'seed': args.seed, 'random_pairing': 'same generator seed and shape at every step, including zero-rate steps',
        'preintervention_state_tensors_identical': True, 'neural_forward_calls': forward_calls,
        'monitored_root_ids': [str(n) for n in monitored],
        'arms': summaries, 'total_spikes': {k:int(v.sum()) for k,v in totals.items()},
        'active_neurons': {k:int((v>0).sum()) for k,v in totals.items()},
        'runtime': {'seconds': time.perf_counter()-started, 'device':device,'torch':torch.__version__,
                    'peak_cuda_allocated_bytes':torch.cuda.max_memory_allocated() if device=='cuda' else None},
        'limits': ['one paired random seed, not statistical efficacy',
            'external simulation authorization; no learned permission or biological ethics',
            'MN9 spikes mapped to synthetic requests by our adapter, no body/physical movement',
            'output-only guard shares the continuous neural trajectory, not an independent neural replicate',
            'input gate changes only rates; official weights and neuron dynamics remain unchanged',
            'gating output does not delete neural state or establish internalization']}
    (args.output/'manifest.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'output':str(args.output),'forward_calls':forward_calls,'arms':summaries}, indent=2))


if __name__ == '__main__':
    main()
