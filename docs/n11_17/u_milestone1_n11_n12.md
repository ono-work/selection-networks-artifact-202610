# U-side Milestone 1 for n=11,12

This report records the nine requested U-type depth-5 frontier decisions. No new encoding, reduction, symmetry breaking, or pruning rule was introduced.

## Summary table

| problem | depth | solver status | verifier status | conclusion | artifact directory | runtime | notes |
| --- | ---: | --- | --- | --- | --- | ---: | --- |
| `U(2,11)` | 5 | `SATISFIABLE` | `VERIFIED_SAT` | `UDepth(2,11)=5` | `experiments/baseline_n11_17/decisions/U_t2_n11/depth_05` | 57.762 s | lower bound source: bounds table |
| `U(3,11)` | 5 | `UNKNOWN` | `n/a` | `unresolved due to TIMEOUT` | `experiments/baseline_n11_17/decisions/U_t3_n11/depth_05` | 7200.235 s | lower bound source: bounds table |
| `U(4,11)` | 5 | `UNKNOWN` | `n/a` | `unresolved due to TIMEOUT` | `experiments/baseline_n11_17/decisions/U_t4_n11/depth_05` | 7200.266 s | lower bound source: bounds table |
| `U(5,11)` | 5 | `UNKNOWN` | `n/a` | `unresolved due to TIMEOUT` | `experiments/baseline_n11_17/decisions/U_t5_n11/depth_05` | 7200.252 s | lower bound source: bounds table |
| `U(2,12)` | 5 | `SATISFIABLE` | `VERIFIED_SAT` | `UDepth(2,12)=5` | `experiments/baseline_n11_17/decisions/U_t2_n12/depth_05` | 586.394 s | lower bound source: bounds table |
| `U(3,12)` | 5 | `UNKNOWN` | `n/a` | `unresolved due to TIMEOUT` | `experiments/baseline_n11_17/decisions/U_t3_n12/depth_05` | 7200.607 s | lower bound source: bounds table |
| `U(4,12)` | 5 | `UNKNOWN` | `n/a` | `unresolved due to TIMEOUT` | `experiments/baseline_n11_17/decisions/U_t4_n12/depth_05` | 7200.581 s | lower bound source: bounds table |
| `U(5,12)` | 5 | `UNKNOWN` | `n/a` | `unresolved due to TIMEOUT` | `experiments/baseline_n11_17/decisions/U_t5_n12/depth_05` | 7200.653 s | lower bound source: bounds table |
| `U(6,12)` | 5 | `UNKNOWN` | `n/a` | `unresolved due to TIMEOUT` | `experiments/baseline_n11_17/decisions/U_t6_n12/depth_05` | 7200.551 s | lower bound source: bounds table |

## Consequences

### n=11

This milestone certifies `UDepth(2,11)=5`: the depth-5 witness is `VERIFIED_SAT`, and the lower bound 5 comes from the existing n=10 U-depth table by monotonicity. By U-duality, this also gives `UDepth(9,11)=5`. The standard endpoints are `UDepth(1,11)=4`, `UDepth(10,11)=4` by U-duality, and `UDepth(11,11)=0`.

The n=11 table is not complete from this milestone alone: `U(3,11)`, `U(4,11)`, and `U(5,11)` at depth 5 reached TIMEOUT, so no depth-5 UNSAT conclusion or exact value is inferred for those entries.

### n=12

This milestone certifies `UDepth(2,12)=5`: the depth-5 witness is `VERIFIED_SAT`, and the lower bound 5 comes from the existing n=10 U-depth table by monotonicity. By U-duality, this also gives `UDepth(10,12)=5`. The standard endpoints are `UDepth(1,12)=4`, `UDepth(11,12)=4` by U-duality, and `UDepth(12,12)=0`.

The n=12 table is not complete from this milestone alone: `U(3,12)`, `U(4,12)`, `U(5,12)`, and `U(6,12)` at depth 5 reached TIMEOUT, so no depth-5 UNSAT conclusion or exact value is inferred for those entries.

## Artifact ledger

### U(2,11), depth 5

- Command: `experiments/baseline_n11_17/decisions/U_t2_n11/depth_05/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t2_n11/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t2_n11/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t2_n11/depth_05/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t2_n11/depth_05/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t2_n11/depth_05/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t2_n11/depth_05/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t2_n11/depth_05/verifier_trace_summary.json`
- README: `experiments/baseline_n11_17/decisions/U_t2_n11/depth_05/README.md`

### U(3,11), depth 5

- Command: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_05/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_05/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_05/solver_metadata.json`
- README: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_05/README.md`

### U(4,11), depth 5

- Command: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_05/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_05/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_05/solver_metadata.json`
- README: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_05/README.md`

### U(5,11), depth 5

- Command: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_05/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_05/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_05/solver_metadata.json`
- README: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_05/README.md`

### U(2,12), depth 5

- Command: `experiments/baseline_n11_17/decisions/U_t2_n12/depth_05/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t2_n12/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t2_n12/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t2_n12/depth_05/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t2_n12/depth_05/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t2_n12/depth_05/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t2_n12/depth_05/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t2_n12/depth_05/verifier_trace_summary.json`
- README: `experiments/baseline_n11_17/decisions/U_t2_n12/depth_05/README.md`

### U(3,12), depth 5

- Command: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_05/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_05/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_05/solver_metadata.json`
- README: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_05/README.md`

### U(4,12), depth 5

- Command: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_05/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_05/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_05/solver_metadata.json`
- README: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_05/README.md`

### U(5,12), depth 5

- Command: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_05/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_05/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_05/solver_metadata.json`
- README: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_05/README.md`

### U(6,12), depth 5

- Command: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_05/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_05/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_05/solver_metadata.json`
- README: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_05/README.md`

## Caveats

- UNSAT is based on solver artifacts for the encoded ASP instances.
- SAT witnesses are accepted only after independent exhaustive binary simulation.
- Runtime is an operational observation only.
- U-duality is used only for U-type consequences.
- Depth 6 and later were not run in this milestone.
