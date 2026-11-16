# Independent agent review of Eon–PoL2 adapter v3

Reviewed on 2026-11-17 by a separate collaborating AI agent. This is an automated implementation and artifact review, not human expert certification or journal peer review. The reviewer did not rerun GPU simulations or change the model/adapter.

## Conclusion

**Passed within the stated one-seed synthetic-interface scope.** The two v2 evidence limits concerning raw-data/cache correspondence and an offline-only output mask have been addressed in the v3 implementation. No blocking implementation mismatch was found.

## Verified provenance and online execution

- The runner verifies the published CSV/parquet byte hashes and uses the unchanged official full-size Eon `TorchModel`: 138,639 neurons and 15,091,983 stored sparse connection coefficients.
- It independently constructs a SciPy COO matrix from the verified raw parquet's postsynaptic indices, presynaptic indices and signed connectivity values, then converts it to CSR. Exact equality checks compare its `indptr`, `indices` and `data` with the official cached Torch CSR. This reconstruction does not obtain its coefficients from the cache being checked.
- CPU-to-GPU copying is separately checked by exact equality of the CSR components. Both neural branches receive the same resulting weight tensor and unchanged official neuron parameters. The intervention changes only sugar-GRN input rates; it does not edit recurrent weights or hidden states.
- Each branch uses a fresh generator seeded with 20261117, with the same random-draw shape at every step. Runtime assertions compare all five complete official state tensors immediately before intervention. Each branch performs 10,000 official model forwards.
- Immediately after every forward, the adapter reads the current synthetic facts and writes `admitted[k]` from the current MN9 outputs or zero. There are 20,000 such synchronous virtual request-gate checks across the two branches. The inline results are independently checked in the runner against the recorded spike tape and permission mask before summarization.
- The schedule remains: withdraw at 300 ms; restore permission at 600 ms while evidence is stale; restore permitted execution/input at 700 ms. This is an external simulation contract, not learned permission or biological consent.
- The v3 manifest's adapter SHA-256 matches the actual script: `502c86101ba84eed7e8db0606220c61f8ed61c64141dc9807bb0443241964850`.

## Reviewer-recomputed v2/v3 equality

The reviewer independently loaded both versions' NPZ files and used elementwise equality across the **entire saved interval**, not only the preintervention prefix:

| Saved array | Shape | v2 equals v3 |
|---|---|---|
| Continuous-input neural monitor | 10,000 × 23 | Exact |
| Input-guarded neural monitor | 10,000 × 23 | Exact |
| Continuous-input all-neuron spike counts | 138,639 | Exact |
| Input-guarded all-neuron spike counts | 138,639 | Exact |
| Time axis, monitored root IDs, permission mask | As saved | Exact |

Thus adding the inline virtual output gate left all saved neural observations and all-neuron spike-count vectors unchanged. The code writes gate results to a separate buffer and does not feed them back into the model. The files do not contain every hidden-state tensor or the complete 138,639-neuron raster at every timestep; this review does not claim an independent elementwise comparison of those unsaved quantities.

## Results and interpretation

The continuous-input simulation retains 17,147 total neural spikes and left/right MN9 counts 90/60. The input-guarded simulation retains 10,249 total spikes and MN9 counts 53/31. During the disallowed period, the latter still has **eight MN9 spikes, four per monitored MN9**, while its online virtual actuator admits **zero** corresponding requests.

The eight spikes are simulated neural activity, not eight physical movements or harmful actions. The virtual request mapping and permission gate are project additions. There is no body model or physical actuator, and output-only gating shares the continuous neural simulation rather than creating an independent replicate. A single paired random seed supports this implementation demonstration; it does not establish general efficacy, internalized authorization, erasure of neural state or biological ethics. v2 and its review remain preserved as the earlier offline-mask version.
