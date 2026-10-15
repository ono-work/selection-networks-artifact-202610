# n=10 V-selection decisions

This report records exactly two n=10 V-type selection decisions using the
existing ASP encoding and independent verifier pipeline:

- `V(2,10)` at depth 5.
- `V(3,10)` at depth 6.

No new reduction, symmetry argument, or pruning rule is introduced here. Both
solver runs used CPU clingo through `.venv/bin/python -m clingo`; GPU use was
none.

## Summary table

| problem | depth | solver status | verifier status | conclusion | artifact directory | runtime | notes |
| --- | ---: | --- | --- | --- | --- | ---: | --- |
| `V(2,10)` | 5 | `UNSATISFIABLE` | n/a | `VDepth(2,10)=6`, derived from the verified `V(3,10)` depth-6 witness | `experiments/baseline_n10/decisions/V_t2_n10/depth_05` | 3013.647 | depth 5 is UNSAT; the verified depth-6 `V(3,10)` witness also satisfies the `V(2,10)` target |
| `V(3,10)` | 6 | `SATISFIABLE` | `VERIFIED_SAT` | `VDepth(3,10)=6` using monotonicity from the existing `VDepth(3,9)=6` artifact | `experiments/baseline_n10/decisions/V_t3_n10/depth_06` | 159.044 | witness verified on all `2^10 = 1024` binary inputs |

## Consequences

For `V(2,10)` at depth 5, the raw solver output is `UNSATISFIABLE`.
This establishes `VDepth(2,10) >= 6`. The independently verified depth-6
`V(3,10)` witness also satisfies the `V(2,10)` target, establishing
`VDepth(2,10) <= 6`. Hence `VDepth(2,10)=6`; no separate depth-6 solver run for
`V(2,10)` is needed for this conclusion.

For `V(3,10)` at depth 6, the solver found a witness and the independent Python
verifier checked all 1024 binary inputs. The existing `V(3,9)` artifacts record
depth 5 as UNSAT and depth 6 as verified SAT:

- `experiments/baseline_n9/decisions/V_t3_n9/depth_05/solver.json`
- `experiments/baseline_n9/decisions/V_t3_n9/depth_06/network.json`
- `experiments/baseline_n9/decisions/V_t3_n9/depth_06/verifier.json`

Using monotonicity from the `VDepth(3,9)=6` artifact, the verified depth-6
`V(3,10)` witness gives `VDepth(3,10)=6`.

## Preflight

Preflight artifacts:

- `experiments/baseline_n10/preflight.json`
- `experiments/baseline_n10/preflight.md`

The preflight recorded:

- clingo command: `.venv/bin/python -m clingo`
- clingo version: `pyclingo version 5.8.0`
- verifier parameter support for `n=10`, `t=2,3`, `kind=V`
- exhaustive binary verification size: `2^10 = 1024`
- existing pipeline components: `generate_instance`, `target_v.lp`,
  `parse_selected_network`, and `verify_binary`

## Artifact ledger

### V(2,10), depth 5

- command: `experiments/baseline_n10/decisions/V_t2_n10/depth_05/command.txt`
- solver input: `experiments/baseline_n10/decisions/V_t2_n10/depth_05/instance.lp`
- solver raw JSON: `experiments/baseline_n10/decisions/V_t2_n10/depth_05/solver_raw.json`
- parsed solver result: `experiments/baseline_n10/decisions/V_t2_n10/depth_05/result.json`
- solver metadata: `experiments/baseline_n10/decisions/V_t2_n10/depth_05/solver_metadata.json`
- README: `experiments/baseline_n10/decisions/V_t2_n10/depth_05/README.md`

No network or verifier artifact is present for this case because the solver
result was UNSAT.

### V(3,10), depth 6

- command: `experiments/baseline_n10/decisions/V_t3_n10/depth_06/command.txt`
- solver input: `experiments/baseline_n10/decisions/V_t3_n10/depth_06/instance.lp`
- solver raw JSON: `experiments/baseline_n10/decisions/V_t3_n10/depth_06/solver_raw.json`
- parsed solver result: `experiments/baseline_n10/decisions/V_t3_n10/depth_06/result.json`
- solver metadata: `experiments/baseline_n10/decisions/V_t3_n10/depth_06/solver_metadata.json`
- network: `experiments/baseline_n10/decisions/V_t3_n10/depth_06/network.json`
- verifier result: `experiments/baseline_n10/decisions/V_t3_n10/depth_06/verifier.json`
- verifier trace summary: `experiments/baseline_n10/decisions/V_t3_n10/depth_06/verifier_trace_summary.json`
- README: `experiments/baseline_n10/decisions/V_t3_n10/depth_06/README.md`

## Caveats

- UNSAT is recorded as a solver artifact for the corresponding constrained ASP
  instance; no human-readable UNSAT proof or unsat core is claimed.
- SAT witnesses are accepted only after independent exhaustive binary
  simulation by the Python verifier.
- Runtime is an operational observation only.
- This run addresses only the two requested decisions and does not introduce a
  new reduction or partition.

