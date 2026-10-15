# U-side depth-8 upper-bound scouting for n=13,14

## Scope

This report records the 8 U-type depth-8 upper-bound scouting runs for n=13,14 that were TIMEOUT at depth 7. Only these 8 listed instances were solved. No depth-7 VERIFIED_SAT row was rerun, and no new reduction, symmetry breaking, pruning rule, or exact-depth certificate is introduced.

Targets: `U(4..6,13)` and `U(3..7,14)`. U-duality is used only for U-type consequences.

## Summary table

| problem | depth | previous depth-7 status | solver status | verifier status | upper-bound conclusion | current interval | artifact directory | runtime | notes |
| --- | ---: | --- | --- | --- | --- | --- | --- | ---: | --- |
| `U(4,13)` | 8 | `TIMEOUT` | `SATISFIABLE` | `VERIFIED_SAT` | `5 <= UDepth(4,13) <= 8` | `[5,8]` | `experiments/baseline_n11_17/decisions/U_t4_n13/depth_08` | 91.441 s | mirror `U(9,13)` |
| `U(5,13)` | 8 | `TIMEOUT` | `UNKNOWN` | `n/a` | `upper bound 8 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t5_n13/depth_08` | 7202.312 s | mirror `U(8,13)` |
| `U(6,13)` | 8 | `TIMEOUT` | `UNKNOWN` | `n/a` | `upper bound 8 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t6_n13/depth_08` | 7202.407 s | mirror `U(7,13)` |
| `U(3,14)` | 8 | `TIMEOUT` | `SATISFIABLE` | `VERIFIED_SAT` | `5 <= UDepth(3,14) <= 8` | `[5,8]` | `experiments/baseline_n11_17/decisions/U_t3_n14/depth_08` | 6323.294 s | mirror `U(11,14)` |
| `U(4,14)` | 8 | `TIMEOUT` | `UNKNOWN` | `n/a` | `upper bound 8 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t4_n14/depth_08` | 7205.608 s | mirror `U(10,14)` |
| `U(5,14)` | 8 | `TIMEOUT` | `UNKNOWN` | `n/a` | `upper bound 8 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t5_n14/depth_08` | 7205.604 s | mirror `U(9,14)` |
| `U(6,14)` | 8 | `TIMEOUT` | `UNKNOWN` | `n/a` | `upper bound 8 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t6_n14/depth_08` | 7205.219 s | mirror `U(8,14)` |
| `U(7,14)` | 8 | `TIMEOUT` | `UNKNOWN` | `n/a` | `upper bound 8 not established` | `[5,?]` | `experiments/baseline_n11_17/decisions/U_t7_n14/depth_08` | 7205.258 s | mirror `U(7,14)` |

## Consequences for n=13

- `U(4,13)`: depth 8 is `VERIFIED_SAT`, so `UDepth(4,13) <= 8`; by U-duality, `UDepth(9,13) <= 8`.
- `U(5,13)`: `TIMEOUT`; upper bound 8 not established from this run.
- `U(6,13)`: `TIMEOUT`; upper bound 8 not established from this run.
- Standard endpoints: `UDepth(1,13)=4`, `UDepth(12,13)=4` by U-duality, and `UDepth(13,13)=0`.

## Consequences for n=14

- `U(3,14)`: depth 8 is `VERIFIED_SAT`, so `UDepth(3,14) <= 8`; by U-duality, `UDepth(11,14) <= 8`.
- `U(4,14)`: `TIMEOUT`; upper bound 8 not established from this run.
- `U(5,14)`: `TIMEOUT`; upper bound 8 not established from this run.
- `U(6,14)`: `TIMEOUT`; upper bound 8 not established from this run.
- `U(7,14)`: `TIMEOUT`; upper bound 8 not established from this run.
- Standard endpoints: `UDepth(1,14)=4`, `UDepth(13,14)=4` by U-duality, and `UDepth(14,14)=0`.

## Comparison with sorting depth

For planning, the sorting-depth upper bound used for n=13,14 is 9. Entries with depth-8 `VERIFIED_SAT` therefore have U-type selection upper bounds one layer shallower than this sorting upper bound. Sorting-depth citation status: `local note candidate: docs/n11_17/selection_bounds_summary.md`.

## Next-step interpretation

- If many depth-8 witnesses are verified, the n=13,14 U-side upper bounds are substantially improved relative to sorting depth 9.
- TIMEOUT rows should be recorded as unresolved upper-bound searches; do not infer UNSAT.
- Any depth-8 UNSAT row would require separate follow-up.
- Exact values still require separate lower-bound or UNSAT certificate work for shallower depths.

## Artifact ledger

### U(4,13), depth 8

- Command: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_08/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_08/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_08/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_08/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_08/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_08/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_08/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t4_n13/depth_08/verifier_trace_summary.json`

### U(5,13), depth 8

- Command: `experiments/baseline_n11_17/decisions/U_t5_n13/depth_08/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t5_n13/depth_08/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t5_n13/depth_08/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t5_n13/depth_08/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t5_n13/depth_08/solver_metadata.json`

### U(6,13), depth 8

- Command: `experiments/baseline_n11_17/decisions/U_t6_n13/depth_08/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t6_n13/depth_08/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t6_n13/depth_08/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t6_n13/depth_08/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t6_n13/depth_08/solver_metadata.json`

### U(3,14), depth 8

- Command: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_08/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_08/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_08/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_08/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_08/solver_metadata.json`
- Network: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_08/network.json`
- Verifier result: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_08/verifier.json`
- Verifier trace summary: `experiments/baseline_n11_17/decisions/U_t3_n14/depth_08/verifier_trace_summary.json`

### U(4,14), depth 8

- Command: `experiments/baseline_n11_17/decisions/U_t4_n14/depth_08/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t4_n14/depth_08/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t4_n14/depth_08/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t4_n14/depth_08/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t4_n14/depth_08/solver_metadata.json`

### U(5,14), depth 8

- Command: `experiments/baseline_n11_17/decisions/U_t5_n14/depth_08/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t5_n14/depth_08/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t5_n14/depth_08/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t5_n14/depth_08/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t5_n14/depth_08/solver_metadata.json`

### U(6,14), depth 8

- Command: `experiments/baseline_n11_17/decisions/U_t6_n14/depth_08/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t6_n14/depth_08/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t6_n14/depth_08/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t6_n14/depth_08/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t6_n14/depth_08/solver_metadata.json`

### U(7,14), depth 8

- Command: `experiments/baseline_n11_17/decisions/U_t7_n14/depth_08/command.txt`
- Solver input: `experiments/baseline_n11_17/decisions/U_t7_n14/depth_08/instance.lp`
- Raw solver JSON: `experiments/baseline_n11_17/decisions/U_t7_n14/depth_08/solver_raw.json`
- Parsed result: `experiments/baseline_n11_17/decisions/U_t7_n14/depth_08/result.json`
- Solver metadata: `experiments/baseline_n11_17/decisions/U_t7_n14/depth_08/solver_metadata.json`

## Caveats

- SAT witnesses are accepted only after independent exhaustive binary simulation.
- TIMEOUT does not imply UNSAT.
- UNSAT, if any, is only a solver artifact for the encoded ASP instance.
- Runtime is operational only.
- This is upper-bound scouting, not an exact-depth certificate.
- U-duality is used only for U-type consequences.
- No new reduction or symmetry argument is introduced.
