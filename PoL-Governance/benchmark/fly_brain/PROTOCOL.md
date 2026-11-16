# Frozen evaluation protocol · EVAL-05

Date: 2026-11-17 (Asia/Hong_Kong). This document and executable experiment code
are committed before either public evaluation split is run. The evaluation
results record source hashes; the memory runner also records the freeze commit.
All episodes are public, generated, artificial tasks. There is no private
holdout, biological recording, official fitted FlyVis model, or whole-brain run.

## Questions and failure criteria

1. In a finite authorization contract, does rechecking current facts before an
   atomic action prevent execution violations that selection-only checks miss?
   Report legitimate executions and conservative missed opportunities as well
   as violations. Full typed and content-matched generic implementations share
   code and must be equal. Any full-arm violation is an implementation failure.
2. In an artificial recurrent cue-memory task, can a calibration-based state
   intervention reduce the withdrawn A cue readout while retaining B information?
   Does A remain recoverable by a newly fitted linear critic after the intervention?
   Do effects require the FlyVis type-template topology? No advantage is assumed.

## Interface experiment

The [interface protocol](interface/README.md) defines its finite contract, five
arms and independent scoring implementation. Dev: 128 scenarios, seeds
53170000–53170127. Public evaluation: 1,024 scenarios, seeds
94190000–94191023, 16 atomic steps each. The three-step clean prefix is intentional.
Record action-level violation counts, unsafe proposals, legal opportunities,
legitimate executions and missed opportunities. A step with several error
categories counts as one violating action. Trajectories diverge, so opportunity
denominators are arm-specific. No population/statistical significance claim.

## Memory experiment

### Data, model and fitting

Input: FlyVis commit `0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa`,
`fib25-fib19_v2.2.json`, SHA256
`bfbb0766251ff09e22723d0ebbf7b14793e70b3ae8ad0eea64eac9d28223351a`.
The source has 65 type templates, 605 signed edges and 24 self-loops.
Spatial offsets are summed; `lambda_mult` is certainty and is unused.

All following choices are ours: artificial two-channel A/B encoding into the
eight template input types, row absolute-sum normalization, and dynamics
`h' = .6 h + .4 tanh(.85 W h + U cue)`. Same-input state differences contract
in infinity norm by at most `.94` per step. This is not a persistent-memory
claim. Cues are independently signed, magnitude U[.3,1], shown for 8 or 12 steps.
At cancellation both inputs are removed. No permission concept is encoded by
the network; an external event triggers the state intervention.

Per model seed: train 384 episodes fits one frozen two-target ridge readout;
independent calibration uses 96 paired A+/A− contrasts and 96 paired B+/B−
contrasts with matched nuisance cues/durations to estimate rank-one directions.
The selective oblique projection removes the A calibration component while
preserving the B calibration direction. It never uses decoder weights or eval
labels. An independent 256-episode calibration-probe set fits separate post-
intervention linear critics for each arm and delay. Ridge=.01; observed-state
Gaussian noise SD=.002, paired across arms. Critics are diagnostics and never
generate actions or update the state. Seeds use independent spawned streams for
graph, encoding, training, directions, probes, dev episodes and eval episodes.

Dev model seeds 101–103, 64 episodes each; final model seeds 1001–1012, 128
episodes each. Each model seed defines an encoding and fitted readouts. The
same episodes/encodings/noises are paired across the three graph conditions;
the same pre-event state is copied across five interventions. Final evaluation
thus contains 1,536 distinct cue episodes, repeated across three topologies and
five interventions, rather than 23,040 independent samples.

### Comparisons

- Topologies: source type template; signed in/out-degree-preserving rewiring;
  random sparse graph with the same node/edge/sign counts. All 24 original
  self-loops are fixed. Rewiring uses 20,000 same-sign directed double-swap
  attempts, preserving per-node signed degrees exactly. Original edge weights
  follow their source edge, then rows are renormalized. Weighted degrees are
  not preserved, so this is not a pure topology-only comparison.
- Interventions: output gate (state unchanged); all-state reset; calibration-
  based selective oblique projection; orthogonal A projection; independent
  random state change with the same per-episode L2 norm as selective projection.
  All interventions happen once. Subsequent recurrence really runs; there is
  no repeated clipping of the decoder.

### Outcomes, premises and interpretation

At delays 0/2/4/8/16 record withdrawn-A frozen-head mean absolute readout,
unrelated-B frozen-head MSE, A/B independent-critic R², and initial state change.
R² may be negative and is not an accuracy percentage. Prespecified memory
premise: no-state-change critics have A and B R²≥.5 at both 0 and 8 steps.
Record premise failures and retain every model; do not filter failing seeds.

The same state/rollout is also scored against a counterfactual where A remains
valid (`a_valid_sham_mse`): a mistimed deletion harms a still-legitimate cue.
This is a scoring counterfactual, not a separate biological experiment.
After 8 steps, all branches receive the same NEW independent permitted A cue
for 8 steps. Report reconstruction MSE of the new A, not an invented recovery
time. B receives no new cue; B reconstruction is retention, not task success.

Main comparison is the pair of A cancellation and B retention, without a tuned
composite score. Use 12 model-seed means and their between-seed SD; do not treat
frames or repeated intervention branches as independent replicates. No p-values
or universal/biological advantage claim. Low frozen-head A with high adaptive-
critic A R² means the old information remains linearly recoverable; it is not
memory erasure. Zero execution violations are NOT measured by this memory
script; execution conformance belongs to the separate interface experiment.

## Development changes and final evaluation rule

Memory dev-v1 preceded method review. Before freezing, corrections made weights
follow source edges, paired critic/reauthorization noise, added premise flags,
removed a non-measured constant execution-safety field, and added the valid-A
scoring counterfactual. These are development changes, not independent evidence.
Both dev outputs are retained. Existing .94 contraction, dynamics, rank, noise,
ridge, sample counts and final seeds were not tuned to evaluation results.

Run final evaluation once after committing this protocol and code. Publish all
outcomes, including no memory premise, no selective advantage, no template
advantage, and failures. Post-eval bug fixes, if necessary, must get a new version,
retain old evidence, and disclose the invalidation; do not silently retune.
