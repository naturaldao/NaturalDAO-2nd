# Official pretrained FlyVis functional reproduction

This runner loads the published `flow/0000/000` checkpoint through the official
`NetworkView(...).init_network('best')` API. It runs the complete extent-15 visual
system: **45,669 modeled neurons and 1,513,231 directed edges**. This is the
official learned FlyVis functional model, distinct from our earlier 65-type
structural proxy and from the separate Eon whole-brain LIF simulation. It does not
claim biological consciousness, a complete fly brain, or a trained PoL2 controller.

The runner refuses missing checkpoints, wrong archive/source versions, reduced
connectomes and existing output directories. It verifies the archive and extracted
configuration/checkpoint bytes, then checks every network state tensor against
both the selected checkpoint and the published `best_chkpt`. A failed official
recovery cannot silently fall back to random initialization.

Pinned materials:

- [FlyVis source](https://github.com/TuragaLab/flyvis/tree/0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa),
  commit `0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa`.
- Official pretrained ZIP SHA-256:
  `71c78d4070556a536b13b23ee3139cd2788aa2a9d07d430a223b4edead281db1`.
- [Original moving-edge example](https://github.com/TuragaLab/flyvis/blob/0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa/examples/04_flyvision_moving_edge_responses.ipynb).
- The upstream MIT notice is preserved in [LICENSE-FlyVis](LICENSE-FlyVis).
  First-party runner code follows this repository's Proof of Love2 label.

The dedicated environment uses Python 3.10 and the already verified CUDA Torch
installation. Import order is `pyarrow` before `torch` for Windows DLL compatibility.
From the local experiment root:

```powershell
& 'D:/Codebase/PoL2-FlyVis-Official/.venv/Scripts/python.exe' 'D:/Codebase/PoL2-FlyVis-Official/publication/PoL-Governance/benchmark/fly_brain/official/run_official.py' --results-dir 'D:/Codebase/PoL2-FlyVis-Official/data/results' --archive 'D:/Codebase/PoL2-FlyVis-Official/downloads/results_pretrained_models.zip' --source 'D:/Codebase/PoL2-FlyVis-Official/upstream/flyvis' --output 'D:/Codebase/PoL2-FlyVis-Official/publication/PoL-Governance/benchmark/fly_brain/official/results/my-new-run' --phase moving-edge --device cuda
```

Use `--phase smoke` for only strict loading and a direct 20-frame simulation.
Every run computes live responses through `network.simulate`; no cached response
API is called. Forward calls and integrated frames are counted, including gray
pre-adaptation. The smoke input is a simple gray/white/gray flash of shape
`[1,20,1,721]`; the full-space output must be `[1,20,45669]`, finite and changing.
Only selected full-space frames and central traces are saved, not full response
caches or checkpoints.

The moving-edge phase uses the official dataset and notebook parameters: offsets
[-10,11), intensities 0/1, speed 19, height 80, 12 directions spaced 30 degrees,
one-second pre/post periods, dt=1/200 and batch size 1. Every stimulus is freshly
simulated with all modeled neurons after its own gray pre-adaptation. Central
responses from every cell type are retained. The official `peak_responses`,
`direction_selectivity_index` and `preferred_direction` APIs compute the reported
metrics. All T4/T5 ON/OFF tuning values are reported; model 000 and the expected
T4c ON90 > ON270 contrast were fixed in advance. Failure of that contrast remains
in the result. Space plots use a fixed stimulus midpoint, not a response-selected
peak. Selected cardinal traces in the PNG complement all 24 stimuli in the NPZ.

Windows compatibility: datamate 1.0.0's array writer opens a truncated HDF5 file,
tries to read its nonexistent `data` dataset, and then unlinks the still-open file.
Windows rejects that unlink. The first failed run is retained in
[failure.json](results/flyvis-smoke-20261117/failure.json). The runner applies a
runtime HDF5 write/close shim to datamate's two writer bindings, preserving the
upstream `np.asarray` conversion and native HDF5 dtype handling. It adds no custom
string/object conversion. Bytes, int64, float32 and bool arrays are round-tripped
with identical values, shapes and dtypes; these checks are recorded in the final
manifest. Official graph construction, dynamics and checkpoint tensors are not
modified. The official best-checkpoint API falls back from unavailable validation
`epe` to the provided `loss`; the resolved path and exact weight equality are
recorded.

The successful loading/forward evidence is in
[smoke manifest](results/flyvis-smoke-20261117-v2/manifest.json). It reports two
actual forward calls and 220 integration frames (200 pre-adaptation + 20 input),
finite full-space responses and max final-versus-initial change 1.9586825.
This reproduces execution and one original functional assay; it does not reproduce
training or establish agreement with every biological measurement.

## Download the actual published inputs

Use a new experiment directory; model downloads and caches are external to this
repository. The weights are from the [official download instructions](https://turagalab.github.io/flyvis/install/)
and its [checksum-verified downloader](https://github.com/TuragaLab/flyvis/blob/0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa/flyvis_cli/download_pretrained_models.py).

```powershell
$work = 'D:/Codebase/PoL2-FlyVis-Official'
New-Item -ItemType Directory -Force -Path "$work/downloads", "$work/data" | Out-Null
Invoke-WebRequest 'https://drive.google.com/uc?id=13cJr2nMn89j-jBAd5RduYRJpBcXwoNrC&export=download' -OutFile "$work/downloads/results_pretrained_models.zip"
# Check SHA256 equals the value above before extraction.
Get-FileHash -Algorithm SHA256 "$work/downloads/results_pretrained_models.zip"
Expand-Archive "$work/downloads/results_pretrained_models.zip" "$work/data"
git clone https://github.com/TuragaLab/flyvis.git "$work/upstream/flyvis"
git -C "$work/upstream/flyvis" checkout 0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa
```

The [recorded Windows/Python 3.10 dependency lock](environment-lock-windows-py310.txt)
includes official CUDA Torch and FlyVis source pins. Install into a dedicated
environment, not an unrelated project's environment. This run's dedicated
environment only read the existing CUDA Torch installation through a local
`.pth`; it did not modify that source environment. A clean reproduction can
install Torch directly using the recorded official CUDA wheel index.

## Actual Eon / Shiu whole-brain model

The separate [official whole-brain repository](https://github.com/eonsystemspbc/fly-brain/tree/a3db62f9436074e485c0278290c2164ed6150808)
contains the full input data in its clone. The actual loaded model has **138,639
neurons and 15,091,983 nonzero directed weights**. Its LIF equations and fixed
parameters are not a separately trained checkpoint; its connectome supplies the
official recurrent weights. This differs from FlyVis's trained vision model.

```powershell
git clone https://github.com/eonsystemspbc/fly-brain.git "$work/upstream/fly-brain"
git -C "$work/upstream/fly-brain" checkout a3db62f9436074e485c0278290c2164ed6150808
Set-Location "$work/upstream/fly-brain"
& "$work/.venv/Scripts/python.exe" main.py --pytorch --experiment sugar --t_run 0.1 1 --n_run 1 --rounds 1 --run-label my_new_official_sugar --no_log_file
```

This was actually run through the unmodified official CLI at 0.1 and 1 seconds;
[original evidence](results/eon-original-20261117/manifest.json) includes output
checksums and MN9 spike counts. These runs are one unseeded trial each, not the
full published biological validation suite. They simulate spikes, not a body.
The original [GPL license](LICENSE-Eon) remains applicable to that upstream model.

## PoL2 adapter on the full whole-brain model

`run_eon_pol2.py --upstream <eon-clone> --output <new-directory>` imports the
unmodified official TorchModel. The default seed is 20261117, dt=.1 ms, 10,000
steps per neural branch. Verified raw parquet is independently reconstructed
using SciPy and compared exactly with all three official CSR arrays; CPU/GPU
weights are then compared. Complete hidden states and random streams match
before intervention. The external contract covers only a scoped simulated sugar
trial, current permission and evidence freshness; it does not formalize all PoL2.

The schedule grants permission until 300 ms, withdraws it until 600 ms, restores
permission with stale evidence until 700 ms, then restores fresh evidence. One
branch keeps the original 200 Hz drive; the other gates its 21 sugar-GRN input
rates. After each forward, an online *simulated* actuator gate filters MN9 spike
requests. This is synchronous simulation logic, not a physical device or learned
ethics. Output-only gating shares the original continuous neural trajectory;
there are two neural trajectories, not three independent neural replicates.

The [final v3 manifest](results/eon-pol2-20261117-v3/manifest.json) and
[activity](results/eon-pol2-20261117-v3/activity.npz) include all-neuron spike
counts and all 10,000 monitored frames. Continuous input produced 65 prohibited
requests; output gates admitted zero. Input cancellation alone left 8 MN9 spikes
after withdrawal, so stopping input does not immediately silence downstream state.
New inputs after reauthorization yielded 38 admitted requests in the input-gated
branch. This is one paired seed; generic rules with identical content would agree.

Development history is retained: the initial adapter used `inference_mode`,
which PyTorch sparse transpose rejected. `no_grad` now matches upstream. v2's
output filtering was offline; v3 moved it into every simulated timestep and
added independent raw-weight verification. Saved neural traces and all-neuron
counts agree exactly between v2/v3; these are not independent efficacy repeats.
The [review](results/eon-pol2-20261117-v3/review.md) is an independent AI-agent
code/data check, not human expert certification.

## Whole-brain image, verification and storage

The [whole-brain activity figure](../../../../Research/Brain/figures/eon-whole-brain-20261117.png)
joins all 138,639 root IDs to the actual [FlyWire v783 coordinates](https://storage.googleapis.com/flywire-data/codex/data/fafb/783/coordinates.csv.gz).
Coordinates are the first community-marked anchor per neuron, not somata or
morphology meshes. Source/coverage/checksums accompany the figure. FlyWire's
[CC BY-NC 4.0 public-data terms](https://flywire.ai/guidelines) are retained;
they are not replaced by the first-party Proof of Love2 label.

Run `verify_saved_results.py` to check published evidence without Torch or a GPU
(NumPy only). `plot_eon_pol2.py` renders the saved adapter traces and
`plot_flyvis_saved.py` redraws the saved moving-edge responses. Shared
`figure_style.py` uses Nature's public artwork requirements: final-size Arial,
lowercase panel labels, accessible colours and editable PDF/SVG text. See the
[figure guide and all exports](../../../../Research/Brain/Figure-Guide.md).
The rendering scripts do not rerun the models or change saved experimental data.

Large originals remain under `$work/downloads`, `$work/data` and the upstream
clones/caches. No originals have been deleted. After experiments, these inputs
and generated caches can be cleaned separately while keeping this repository's
source, manifests, compact activity and figures. Third-party source and weights
remain under their own licenses; this submission does not relicense them.

The [complete moving-edge run](results/flyvis-moving-edge-20261117/manifest.json)
finished all 24 stimuli in 48.09 seconds, with 50 real forward calls and 16,660
integration frames including pre-adaptation and smoke. The prespecified T4c ON
peak was 1.032088876 at 90 degrees versus 0.024330050 at 270 degrees. The
[metrics](results/flyvis-moving-edge-20261117/metrics.json) retain every T4/T5
polarity and all 65 central cell types' 24 peak responses.

| Cell/polarity | Official DSI | Preferred direction (degrees) |
| --- | ---: | ---: |
| T4a ON | 0.429780 | 176.476 |
| T4b ON | 0.537967 | 350.728 |
| T4c ON | 0.627362 | 56.236 |
| T4d ON | 0.098756 | 273.664 |
| T5a OFF | 0.778324 | 185.691 |
| T5b OFF | 0.748803 | 349.145 |
| T5c OFF | 0.579232 | 104.398 |
| T5d OFF | 0.529629 | 248.457 |

T4d's weak ON direction selectivity is retained as a limitation of this fixed
model/assay, not discarded. This table does not treat agreement on one contrast
as a full replication of all biological tuning. The
[redrawn central traces](../../../../Research/Brain/figures/flyvis-center-responses-20261117.png)
and [fixed-time spatial maps](../../../../Research/Brain/figures/flyvis-spatial-activity-20261117.png)
use the same small NPZ files. Original run-time PNGs remain in the result
directory; their producing simulation script and the evidence hashes are unchanged.
