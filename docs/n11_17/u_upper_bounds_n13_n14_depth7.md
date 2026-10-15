# U-side depth-7 upper-bound scouting for n=13,14

## Scope

This report records the 11 listed U-type depth-7 upper-bound scouting runs for n=13,14. Only these 11 listed instances were solved. The user request text said 12 total, but the enumerated target list contains 11 instances. No new reduction, symmetry breaking, pruning rule, or exact-depth certificate is introduced.

Targets: `U(2..6,13)` and `U(2..7,14)`. U-duality is used only for U-type consequences.

## Summary table

| problem | depth | solver status | verifier status | upper-bound conclusion | current interval | artifact directory | runtime | notes |
| --- | ---: | --- | --- | --- | --- | --- | ---: | --- |
| `U(2,13)` | 7 | `SATISFIABLE` | `VERIFIED_SAT` | `5 <= UDepth(2,13) <= 7` | `[5,7]` | `experiments/baseline_n11_17/decisions/U_t2_n13/depth_07` | 99.532 s | mirror `U(11,13)` |
| `U(3,13)` | 7 | `SATISFIABLE` | `VERIFIED_SAT` | `5 <= UDepth(3,13) <= 7` | `[5,7]` | `experiments/baseline_n11_17/decisions/U_t3_n13/depth_07` | 4507.643 s | mirror `U(10,13)` |
| `U(4,13)` | 7 | `UNKNOWN` | `n/a` | `upper bound 7 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t4_n13/depth_07` | 7201.859 s | mirror `U(9,13)` |
| `U(5,13)` | 7 | `UNKNOWN` | `n/a` | `upper bound 7 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t5_n13/depth_07` | 7201.808 s | mirror `U(8,13)` |
| `U(6,13)` | 7 | `UNKNOWN` | `n/a` | `upper bound 7 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t6_n13/depth_07` | 7201.853 s | mirror `U(7,13)` |
| `U(2,14)` | 7 | `SATISFIABLE` | `VERIFIED_SAT` | `5 <= UDepth(2,14) <= 7` | `[5,7]` | `experiments/baseline_n11_17/decisions/U_t2_n14/depth_07` | 977.133 s | mirror `U(12,14)` |
| `U(3,14)` | 7 | `UNKNOWN` | `n/a` | `upper bound 7 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t3_n14/depth_07` | 7204.567 s | mirror `U(11,14)` |
| `U(4,14)` | 7 | `UNKNOWN` | `n/a` | `upper bound 7 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t4_n14/depth_07` | 7204.604 s | mirror `U(10,14)` |
| `U(5,14)` | 7 | `UNKNOWN` | `n/a` | `upper bound 7 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t5_n14/depth_07` | 7204.881 s | mirror `U(9,14)` |
| `U(6,14)` | 7 | `UNKNOWN` | `n/a` | `upper bound 7 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t6_n14/depth_07` | 7204.949 s | mirror `U(8,14)` |
| `U(7,14)` | 7 | `UNKNOWN` | `n/a` | `upper bound 7 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t7_n14/depth_07` | 7204.802 s | mirror `U(7,14)` |

## Consequences for n=13

- `U(2,13)`: depth 7 is `VERIFIED_SAT`, so `UDepth(2,13) <= 7`; by U-duality, `UDepth(11,13) <= 7`.
- `U(3,13)`: depth 7 is `VERIFIED_SAT`, so `UDepth(3,13) <= 7`; by U-duality, `UDepth(10,13) <= 7`.
- `U(4,13)`: `TIMEOUT`; upper bound 7 not established from this run.
- `U(5,13)`: `TIMEOUT`; upper bound 7 not established from this run.
- `U(6,13)`: `TIMEOUT`; upper bound 7 not established from this run.
- Standard endpoints: `UDepth(1,13)=4`, `UDepth(12,13)=4` by U-duality, and `UDepth(13,13)=0`.

## Consequences for n=14

- `U(2,14)`: depth 7 is `VERIFIED_SAT`, so `UDepth(2,14) <= 7`; by U-duality, `UDepth(12,14) <= 7`.
- `U(3,14)`: `TIMEOUT`; upper bound 7 not established from this run.
- `U(4,14)`: `TIMEOUT`; upper bound 7 not established from this run.
- `U(5,14)`: `TIMEOUT`; upper bound 7 not established from this run.
- `U(6,14)`: `TIMEOUT`; upper bound 7 not established from this run.
- `U(7,14)`: `TIMEOUT`; upper bound 7 not established from this run.
- Standard endpoints: `UDepth(1,14)=4`, `UDepth(13,14)=4` by U-duality, and `UDepth(14,14)=0`.

## Comparison with sorting depth

For planning, the sorting-depth upper bound used for n=13,14 is 9. Entries with depth-7 `VERIFIED_SAT` therefore have U-type selection upper bounds at least two layers shallower than this sorting upper bound. Sorting-depth citation status: `local note candidate: docs/n11_17/selection_bounds_summary.md`.

## Next-step interpretation

- If many depth-7 witnesses are verified, the natural next scouting step is the n=15,16,17 U-side frontier at the appropriate planning depths.
- TIMEOUT rows should be recorded as unresolved upper-bound searches; do not infer UNSAT.
- Any depth-7 UNSAT row would require separate follow-up.
- Exact values still require separate lower-bound or UNSAT certificate work for shallower depths.

## Artifact ledger

### U(2,13), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t2_n13/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t2_n13/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t2_n13/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t2_n13/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t2_n13/depth_07/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t2_n13/depth_07/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t2_n13/depth_07/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t2_n13/depth_07/verifier_trace_summary.json`

### U(3,13), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t3_n13/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t3_n13/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t3_n13/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t3_n13/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t3_n13/depth_07/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t3_n13/depth_07/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t3_n13/depth_07/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t3_n13/depth_07/verifier_trace_summary.json`

### U(4,13), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_07/solver_metadata.json`

### U(5,13), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t5_n13/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t5_n13/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t5_n13/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t5_n13/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t5_n13/depth_07/solver_metadata.json`

### U(6,13), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t6_n13/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t6_n13/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t6_n13/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t6_n13/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t6_n13/depth_07/solver_metadata.json`

### U(2,14), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t2_n14/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t2_n14/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t2_n14/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t2_n14/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t2_n14/depth_07/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t2_n14/depth_07/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t2_n14/depth_07/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t2_n14/depth_07/verifier_trace_summary.json`

### U(3,14), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_07/solver_metadata.json`

### U(4,14), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t4_n14/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t4_n14/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t4_n14/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t4_n14/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t4_n14/depth_07/solver_metadata.json`

### U(5,14), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t5_n14/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t5_n14/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t5_n14/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t5_n14/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t5_n14/depth_07/solver_metadata.json`

### U(6,14), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t6_n14/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t6_n14/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t6_n14/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t6_n14/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t6_n14/depth_07/solver_metadata.json`

### U(7,14), depth 7

- Command: `experiments/baseline_n11_17/decisions/U_t7_n14/depth_07/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t7_n14/depth_07/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t7_n14/depth_07/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t7_n14/depth_07/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t7_n14/depth_07/solver_metadata.json`

## Caveats

- SAT witnesses are accepted only after independent exhaustive binary simulation.
- TIMEOUT does not imply UNSAT.
- UNSAT, if any, is only a solver artifact for the encoded ASP instance.
- Runtime is operational only.
- This is upper-bound scouting, not an exact-depth certificate.
- U-duality is used only for U-type consequences.
- No new reduction or symmetry argument is introduced.
