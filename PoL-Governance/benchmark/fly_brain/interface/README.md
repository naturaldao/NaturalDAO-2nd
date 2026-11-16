# Dynamic authorization interface stress test

This CPU experiment tests an execution protocol using public synthetic events.
It contains no neural controller, pretrained FlyVis model, whole-brain model, or
biological behavior. Its connection to PoL2 is a deliberately narrow engineering
operationalization: scoped consent, current state evidence, independently granted
bounded recovery, and truthful completion. It does not formalize all PoL2.

From the repository root, using the explicit project-approved interpreter:

```powershell
& 'C:/Users/Administrator/AppData/Local/Programs/Python/Python312/python.exe' -m unittest discover -s 'PoL-Governance/benchmark/fly_brain/interface' -p 'test_interface.py' -v
& 'C:/Users/Administrator/AppData/Local/Programs/Python/Python312/python.exe' 'PoL-Governance/benchmark/fly_brain/interface/run_interface.py' --split dev --output 'PoL-Governance/benchmark/fly_brain/interface/results/my-dev-run'
```

An output directory must be new; the runner refuses to overwrite historical
results. No packages need to be installed. The development run is 128 scenarios
with seeds 53170000–53170127; the one public evaluation run is 1,024 scenarios
with seeds 94190000–94191023. These seed ranges are disjoint. Evaluation is to be
run only after code and protocol are committed/frozen; it is a public generated
stress test, not a private or independently authored holdout.

Each scenario has 16 steps, two independently positioned objects A/B, and the
same proposed actions and external fact changes for every arm. The first three
steps are an intentional clean anchor: two legal movements of A and a truthful
completion claim. The remaining steps randomize action kind and object, task
permission (`GRANTED`/`DENIED`/`UNKNOWN`), object scope, evidence freshness,
independent recovery scope/authority, and changes between selection/execution.
The clean prefix ensures an all-stop system cannot appear successful merely
because it has zero violations; it is not naturalistic behavioral data.

| Arm | Behavior |
| --- | --- |
| raw | Applies every non-wait proposal, including false completion claims. |
| physical | Blocks only movements outside the synthetic workspace [0, 1.2]. |
| start_only | Uses the contract at selection, then only physical checks at execution. |
| full_typed | Applies the contract at selection and rechecks execution-time facts. |
| generic_matched | Identical executable rules to full_typed; equality is checked per trajectory. |

Movement requires current evidence and scoped task authorization. Recovery uses
its own object-specific authority and only bounded negative motion; task denial
does not grant recovery. Completion is verified against the environment's true
position (at least 1.0), rather than accepting a controller's claim. The current
environment supplies privileged true position, not a perception subsystem.
Execution rechecks facts even when a ledger version has not changed. Conversely,
a version change does not automatically grant authority or require refusal if
all current contract conditions are explicitly satisfied.

`oracle()` is separately implemented and reads execution-time facts, the actual
pre-execution position, and the concrete action. It does not call `guard()`, read
an arm, or infer violations from a rejection reason. Both implementations still
share the researcher's normative contract; this is implementation conformance,
not independent human labels or proof that the contract is ethically complete.

The JSON contains source/input checksums and the configuration, all per-scenario counts
and final positions, and three full failure traces per failing arm. CSV contains
the aggregate table. Counts distinguish unsafe proposals, actions executed with
one or more violations, legal opportunities, legal executions, and false blocks.
Here a false block means a non-wait proposal legal under *execution-time* facts
that was not executed, including cases where selection-time facts had denied it
and permission/evidence became available later. It therefore measures missed
opportunity under this conservative two-stage protocol, not necessarily an
incorrect selection-time decision. A violating action may carry multiple error
categories but contributes one to the total action-violation count.

Arms can reach different positions, so their later opportunity/error denominators
can differ despite identical proposal/event tapes. Compare them as paired
synthetic scenarios; do not interpret the marginal percentages as identical-state
causal effects. The content-matched arm is intentionally the same rule system:
no gain can be attributed to the PoL2 label, and no neural internalization is
tested.

Development evidence: [results](results/dev-20261117/results.json) and
[summary](results/dev-20261117/summary.csv). Five tests cover execution-time
revocation, independent recovery authority and evidence races, object-specific
truthful completion, positive legal task progress, and same-version freshness
changes. Public evaluation must remain unrun until the parent task records the
freeze commit.

First-party license label: Proof of Love2, following the repository LICENSE.
