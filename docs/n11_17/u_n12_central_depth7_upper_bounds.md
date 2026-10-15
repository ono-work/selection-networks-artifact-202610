# U-side depth-7 upper-bound scouting for central n=12 cases

This report records depth-7 upper-bound scouting for the two central U-type n=12 cases that timed out at depth 6. Depth 5 and depth 6 were not rerun. No new encoding, reduction, symmetry breaking, or pruning rule was introduced.

## Summary table

| problem | depth | previous depth-6 status | solver status | verifier status | conclusion | artifact directory | runtime | notes |
| --- | ---: | --- | --- | --- | --- | --- | ---: | --- |
| `U(5,12)` | 7 | `TIMEOUT` | `SATISFIABLE` | `VERIFIED_SAT` | `[5,7]` | `experiments/baseline_n11_17/decisions/U_t5_n12/depth_07` | 922.913 s | U-duality mirror: U(7,12) |
| `U(6,12)` | 7 | `TIMEOUT` | `SATISFIABLE` | `VERIFIED_SAT` | `[5,7]` | `experiments/baseline_n11_17/decisions/U_t6_n12/depth_07` | 3866.935 s | self-dual central case |

## Consequences

- `U(5,12)`: depth 7 is `VERIFIED_SAT`, so `5 <= UDepth(5,12) <= 7`; by U-duality, `5 <= UDepth(7,12) <= 7`.
- `U(6,12)`: depth 7 is `VERIFIED_SAT`, so `5 <= UDepth(6,12) <= 7`; this is the self-dual central case.

## Next-step interpretation

- If a depth-7 upper bound is obtained, the next issue is either depth-6 witness search or a depth-6/depth-5 UNSAT certificate.
- If depth 7 also times out, the standard pipeline is heavy on the central case and a witness construction, hint, or fixed-layer strategy is needed before drawing stronger conclusions.
- This report is upper-bound scouting; it is not a depth-5 UNSAT certificate.

## Artifact ledger

### U(5,12), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_07/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_07/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_07/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_07/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t5_n12/depth_07/verifier_trace_summary.json`

### U(6,12), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_07/solver_raw.json`
- Parsed solver result: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_07/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_07/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_07/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t6_n12/depth_07/verifier_trace_summary.json`

## Caveats

- SAT witnesses are accepted only after independent exhaustive binary simulation.
- TIMEOUT does not imply UNSAT.
- Runtime is an operational observation only.
- This is upper-bound scouting; it does not rerun depth 5 or depth 6 and does not create a depth-5/6 UNSAT certificate.
