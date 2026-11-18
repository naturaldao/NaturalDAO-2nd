# PoL2 × fly connectome templates

**New:** [actual official model loading and full-brain runs](official/README.md)
and [Chinese results](../../../Research/Brain/Experiments/02-Visual-and-Whole-Brain-Models.md)
are separate from the early proxy experiments described below.

Two reproducible artificial experiments examine dynamic execution permissions
and cancellation of a target cue in a recurrent state. The neural experiment
uses a real upstream **type template**, with our own dynamics and task. It is
not official pretrained FlyVis, a whole brain, biological consent, or a proof
of PoL2 internalization. The interface experiment is a separate, non-neural
finite-contract test. PoL2 supplies the narrow contract's normative provenance;
content-matched generic rules have identical behavior.

- [Frozen protocol and interpretation](PROTOCOL.md)
- [Chinese research/result card](../../../Research/Brain/Experiments/01-Revocation-and-State.md)
- [Interface experiment](interface/README.md)
- [Memory evaluation summary](results/memory-eval-20261117/summary.json) and [per-seed data](results/memory-eval-20261117/per_seed.csv)
- [Interface evaluation summary](interface/results/eval-20261117/summary.csv)

## Reproduce

Python 3.12 and the pinned [NumPy dependency](requirements.txt) are sufficient.
Use your chosen Python interpreter explicitly. For example, from the repository
root in PowerShell (replace the interpreter path for your machine):

```powershell
$py = 'C:/Users/Administrator/AppData/Local/Programs/Python/Python312/python.exe'
& $py -m pip install -r PoL-Governance/benchmark/fly_brain/requirements.txt
& $py -m unittest discover -s PoL-Governance/benchmark/fly_brain -p test_memory.py -v
& $py -m unittest discover -s PoL-Governance/benchmark/fly_brain/interface -p test_interface.py -v
& $py PoL-Governance/benchmark/fly_brain/memory_experiment.py --split dev --output PoL-Governance/benchmark/fly_brain/results/my-memory-dev
& $py PoL-Governance/benchmark/fly_brain/memory_experiment.py --split eval --output PoL-Governance/benchmark/fly_brain/results/my-memory-eval
& $py PoL-Governance/benchmark/fly_brain/interface/run_interface.py --split eval --output PoL-Governance/benchmark/fly_brain/interface/results/my-interface-eval
```

Runners reject existing output directories. Training/calibration/evaluation
streams are separate. No external data, weights, API keys, GPU, or model service
is needed at runtime. Results include source hashes; each row in `per_seed.csv`
is one model seed × topology × intervention × delay, aggregated over episodes.
The public eval is reproducible, not a private or independently authored test.
See the protocol for seeds, controls, caveats and development history.

The protocol/executable freeze is commit `981bb4b`; the pre-evaluation public
record is `77304dc`. Both experiments were run once after that record was pushed.
The memory evaluation comprises 12 model seeds, three graph conditions and
1,536 distinct cue episodes. The interface evaluation comprises 1,024 scenarios.

Optional figure regeneration uses [plot dependencies](requirements-plot.txt):
install them and run `plot_results.py` with the same explicit interpreter.
The [PNG](../../../Research/Brain/figures/fly-brain-results.png) and
[PDF](../../../Research/Brain/figures/fly-brain-results.pdf) show means and ±1
between-seed SD for memory measures, plus interface action-violation counts.

## Provenance and licenses

Upstream: [Lappalainen et al., Nature 2024](https://www.nature.com/articles/s41586-024-07939-3),
[FlyVis repository](https://github.com/TuragaLab/flyvis), fixed commit
`0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa`.
Our asset SHA256 is recorded in the protocol and verified on every memory run.
Weights are `alpha * sum(offset synapse counts)`, normalized across all incoming
type edges. Spatial organization and trained parameters are absent.
Original [MIT license and copyright](third_party/flyvis/LICENSE) are retained.
First-party code/materials follow the repository [Proof of Love2 declaration](../../../LICENSE).
Original simulation and all synthetic labels/interventions are AI-assisted
research implementations; no human expert annotation is claimed.
