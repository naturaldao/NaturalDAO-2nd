# Independent agent review of Eon–PoL2 adapter v2

Reviewed on 2026-11-17 by a separate collaborating AI agent. This is an automated implementation review, not human expert certification or journal peer review. The reviewer read the adapter, manifest, unchanged upstream source status and saved activity; no GPU experiment was rerun.

## Verified implementation and artifact facts

- The adapter imports the upstream `run_pytorch.TorchModel`, `MODEL_PARAMS`, `DT` and `get_weights`. It instantiates the full 138,639-neuron model using the same sparse matrix object for both neural branches, with 15,091,983 stored connection coefficients. Each branch records 10,000 real model-forward calls at dt=0.1 ms.
- The adapter does not change recurrent weights, official neuron parameters or hidden states as an intervention. Its neural intervention changes only the 21 sugar-GRN input rates from 200 Hz to zero when its external synthetic authorization condition fails.
- The loaded CPU CSR and its GPU copy are compared by exact equality of `crow_indices`, `col_indices` and `values`. This establishes exact CPU/GPU copying of the loaded cache, not an independent reconstruction of that cache from the raw parquet. The input CSV/parquet checksums are asserted; a separate raw-parquet-to-cache coefficient comparison is not part of v2.
- Each neural branch creates a fresh `torch.Generator` with seed 20261117 and supplies the same full-shape rates tensor at every step, including zero-rate steps. At step 2999, before intervention, all five complete official state tensors are checked by `torch.equal`. The saved 23-neuron monitored prefixes also independently match for all first 3,000 steps.
- The schedule is implemented as specified: authorization is withdrawn at 300 ms; it is restored at 600 ms while evidence remains stale; both authorization and evidence permit input/output from 700 ms onward. The reviewer independently recomputed the saved 10,000-step permission mask and confirmed 6,000 permitted steps.
- Both recorded SHA-256 values match the current files: adapter `412838611fe87001b42fab904d1ee4d35b3dd14c4825e03bae29def206fba4db`; official model source `699655db7a56045271ba467268be153d0a3318d4cc4cecc0a13f33e69ce79667`. Git shows no source changes to upstream `run_pytorch.py`, `benchmark.py` or `main.py`; the benchmark-results CSV has changed through benchmark execution.
- The successful adapter uses `torch.no_grad()` as the upstream simulation does. The earlier sparse/inference-mode failure is a development failure, not a successful experiment and not evidence of altered official dynamics.

## Independently recounted saved activity

| Neural branch | All-neuron spikes | Left/right MN9 spikes | Left/right MN9 spikes during disallowed periods |
|---|---:|---:|---:|
| Continuous input | 17,147 | 90 / 60 | 37 / 28 |
| Input guarded | 10,249 | 53 / 31 | 4 / 4 |

The eight input-guarded residual MN9 spikes occur after stimulation is withdrawn. They are simulated neural spikes, not eight physical movements, decisions, harmful acts or evidence of persistent goal memory. The continued network state and delays provide a direct alternative explanation.

## Scope and remaining v2 evidence limits

The output-only and input-plus-output guards in v2 are **offline masks of recorded MN9 spike tapes**. The mapping from MN9 spikes to synthetic actuator requests is added by this project. v2 does not execute an online actuator interface, a simulated body or a physical robot. Zero accepted disallowed requests is the mask's construction and implementation result, not a general safety estimate. The output-only arm reuses the continuous neural branch and is not an independent neural replicate.

The two nonblocking provenance/terminology improvements identified for a future version are: independently compare raw-parquet-derived CSR coefficients with the official cached CSR; and, if claiming an online request interface, compute and record the synthetic request gate inside the model-step loop. These should use a new output directory and preserve v2.

The evidence supports a one-seed, full-scale official neural simulation with an externally imposed synthetic input schedule and offline output-request filtering. It does not establish biological consent, learned authorization, PoL2 internalization, erasure of neural state, physical behavior, or statistical efficacy. No blocking model-intervention or timing mismatch was found within this stated v2 scope.
