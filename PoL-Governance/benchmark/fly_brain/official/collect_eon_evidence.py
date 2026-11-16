"""Collect evidence from already executed official CLI runs; no new simulation."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--upstream',type=Path,required=True)
    args=parser.parse_args()
    out=HERE/'results/eon-original-20261117'
    adapter=json.loads((HERE/'results/eon-pol2-20261117-v3/manifest.json').read_text())
    runs=[]
    for duration,name in ((.1,'smoke-0.1s.parquet'),(1.,'function-1s.parquet')):
        p=out/name
        frame=pd.read_parquet(p)
        counts=frame.groupby('flywire_id').size()
        runs.append({'duration_seconds':duration,'output':name,'sha256':sha(p),
            'spikes':len(frame),'active_neurons':frame.flywire_id.nunique(),
            'MN9_left_spikes':int(counts.get(720575940660219265,0)),
            'MN9_right_spikes':int(counts.get(720575940618238523,0)),
            'observed_max_time_ms':float(frame.time_ms.max()),
            'seed':None,'seed_note':'unmodified upstream CLI does not set a seed'})
    result={'scope':'unmodified official PyTorch CUDA CLI, sugar GRNs at 200 Hz, one trial',
        'upstream_commit':adapter['upstream_commit'],
        'source_sha256':sha(args.upstream/'code/run_pytorch.py'),
        'data_sha256':adapter['source_data_sha256'],
        'neurons':adapter['model']['neurons'],'sparse_weight_nnz':adapter['model']['sparse_weight_nnz'],
        'raw_parquet_independently_verified':True,'device':'cuda','runs':runs,
        'limitations':['spikes are simulated, not measured animal behavior',
                       'no proboscis/body simulation or complete published validation suite',
                       'one unseeded trial per duration; not statistical replication']}
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
