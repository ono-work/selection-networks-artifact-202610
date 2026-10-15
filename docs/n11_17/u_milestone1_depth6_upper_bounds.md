# U-side depth-6 upper-bound scouting for n=11,12

This report records depth-6 upper-bound scouting for the seven U-type cases that timed out at depth 5 in the previous Milestone 1 run. Depth 5 was not rerun. No new encoding, reduction, symmetry breaking, or pruning rule was introduced.

## Summary table

| problem | depth | previous depth-5 status | solver status | verifier status | conclusion | artifact directory | runtime | notes |
| --- | ---: | --- | --- | --- | --- | --- | ---: | --- |
| `U(3,11)` | 6 | `TIMEOUT` | `SATISFIABLE` | `VERIFIED_SAT` | `[5,6]` | `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06` | 252.618 s | U-duality mirror: U(8,11) |
| `U(4,11)` | 6 | `TIMEOUT` | `SATISFIABLE` | `VERIFIED_SAT` | `[5,6]` | `experiments/baseline_n11_17/decisions/U_t4_n11/depth_06` | 321.116 s | U-duality mirror: U(7,11) |
| `U(5,11)` | 6 | `TIMEOUT` | `SATISFIABLE` | `VERIFIED_SAT` | `[5,6]` | `experiments/baseline_n11_17/decisions/U_t5_n11/depth_06` | 1695.949 s | U-duality mirror: U(6,11) |
| `U(3,12)` | 6 | `TIMEOUT` | `SATISFIABLE` | `VERIFIED_SAT` | `[5,6]` | `experiments/baseline_n11_17/decisions/U_t3_n12/depth_06` | 1003.173 s | U-duality mirror: U(9,12) |
| `U(4,12)` | 6 | `TIMEOUT` | `SATISFIABLE` | `VERIFIED_SAT` | `[5,6]` | `experiments/baseline_n11_17/decisions/U_t4_n12/depth_06` | 2959.909 s | U-duality mirror: U(8,12) |
| `U(5,12)` | 6 | `TIMEOUT` | `UNKNOWN` | `n/a` | `upper bound 6 not established` | `experiments/baseline_n11_17/decisions/U_t5_n12/depth_06` | 7200.658 s | U-duality mirror: U(7,12) |
| `U(6,12)` | 6 | `TIMEOUT` | `UNKNOWN` | `n/a` | `upper bound 6 not established` | `experiments/baseline_n11_17/decisions/U_t6_n12/depth_06` | 7200.704 s | U-duality mirror: U(6,12) |

## Consequences

### n=11

- `U(3,11)`: depth 6 is `VERIFIED_SAT`, so `5 <= UDepth(3,11) <= 6`; by U-duality, `5 <= UDepth(8,11) <= 6`.
- `U(4,11)`: depth 6 is `VERIFIED_SAT`, so `5 <= UDepth(4,11) <= 6`; by U-duality, `5 <= UDepth(7,11) <= 6`.
- `U(5,11)`: depth 6 is `VERIFIED_SAT`, so `5 <= UDepth(5,11) <= 6`; by U-duality, `5 <= UDepth(6,11) <= 6`.

### n=12

- `U(3,12)`: depth 6 is `VERIFIED_SAT`, so `5 <= UDepth(3,12) <= 6`; by U-duality, `5 <= UDepth(9,12) <= 6`.
- `U(4,12)`: depth 6 is `VERIFIED_SAT`, so `5 <= UDepth(4,12) <= 6`; by U-duality, `5 <= UDepth(8,12) <= 6`.
- `U(5,12)`: depth 6 reached `TIMEOUT`, so upper bound 6 is not established; by U-duality, no upper bound 6 is established for `U(7,12)` from this run.
- `U(6,12)`: depth 6 reached `TIMEOUT`, so upper bound 6 is not established; by U-duality, no upper bound 6 is established for `U(6,12)` from this run.

## Next-step interpretation

- Cases with depth-6 `VERIFIED_SAT` now have an upper bound 6; if a future depth-5 UNSAT certificate is obtained, the exact value becomes 6.
- Cases without a depth-6 upper bound still need SAT witness search or a different upper-bound construction before depth-5 closure has clear payoff.
- Simply rerunning the previous depth-5 TIMEOUT cases with a different seed is not recommended by this report.

## Artifact ledger

### U(3,11), depth 6

- Command: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06/verifier_trace_summary.json`

### U(4,11), depth 6

- Command: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_06/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_06/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_06/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_06/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_06/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_06/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_06/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t4_n11/depth_06/verifier_trace_summary.json`

### U(5,11), depth 6

- Command: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_06/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_06/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_06/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_06/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_06/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_06/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_06/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t5_n11/depth_06/verifier_trace_summary.json`

### U(3,12), depth 6

- Command: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_06/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_06/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_06/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_06/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_06/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_06/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_06/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t3_n12/depth_06/verifier_trace_summary.json`

### U(4,12), depth 6

- Command: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_06/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_06/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_06/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_06/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_06/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_06/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_06/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t4_n12/depth_06/verifier_trace_summary.json`

### U(5,12), depth 6

- Command: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_06/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_06/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_06/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_06/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_06/solver_metadata.json`

### U(6,12), depth 6

- Command: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_06/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_06/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_06/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_06/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_06/solver_metadata.json`

## Caveats

- SAT witnesses are accepted only after independent exhaustive binary simulation.
- TIMEOUT does not imply UNSAT.
- Runtime is an operational observation only.
- This is upper-bound scouting; it does not create a depth-5 UNSAT certificate.
