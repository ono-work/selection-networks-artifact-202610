## n=10 U-selection decisions

This report records the requested standard-pipeline decisions. No new
reduction, symmetry argument, or pruning rule was used.

### Summary table

| problem | depth | solver status | verifier status | conclusion | artifact directory | runtime | notes |
| --- | ---: | --- | --- | --- | --- | ---: | --- |
| `U(2,10)` | 4 | `UNSATISFIABLE` | n/a | depth-4 lower bound for `UDepth(2,10)=5` | `experiments/baseline_n10/decisions/U_t2_n10/depth_04` | 440.547 s | raw solver JSON and metadata saved |
| `U(2,10)` | 5 | `SATISFIABLE` | `VERIFIED_SAT` | `UDepth(2,10)=5` | `experiments/baseline_n10/decisions/U_t2_n10/depth_05` | 7.659 s | witness verified on all `2^10 = 1024` binary inputs |
| `U(3,10)` | 5 | `SATISFIABLE` | `VERIFIED_SAT` | `UDepth(3,10)=5` | `experiments/baseline_n10/decisions/U_t3_n10/depth_05` | 40.398 s | witness verified on all `2^10 = 1024` binary inputs |
| `U(4,10)` | 5 | `SATISFIABLE` | `VERIFIED_SAT` | `UDepth(4,10)=5` | `experiments/baseline_n10/decisions/U_t4_n10/depth_05` | 352.645 s | witness verified on all `2^10 = 1024` binary inputs |
| `U(5,10)` | 5 | `SATISFIABLE` | `VERIFIED_SAT` | `UDepth(5,10)=5` | `experiments/baseline_n10/decisions/U_t5_n10/depth_05` | 51.080 s | witness verified on all `2^10 = 1024` binary inputs |

### Consequence for UDepth(2,10)

The standard ASP instance for `U(2,10)` at depth 4 is UNSATISFIABLE, as
recorded in the raw solver artifact. The existing calibration establishes
`UDepth(2,8)=4`: its summary records depths 0 through 3 as UNSAT and depth 4 as
SAT with successful independent verification:

- `experiments/u_calibration/U_t2_n8/summary.csv`
- `experiments/u_calibration/U_t2_n8/depth_03/solver.json`
- `experiments/u_calibration/U_t2_n8/depth_04/network.json`
- `experiments/u_calibration/U_t2_n8/depth_04/verifier.json`

Monotonicity gives `UDepth(2,10)>=4`, while the depth-4 UNSAT result strengthens
this to `UDepth(2,10)>=5`. The standard depth-5 ASP instance is satisfiable,
and the extracted network was accepted by the independent verifier on all
1024 binary inputs. Therefore

`UDepth(2,10)=5`.

### Consequence for UDepth(3,10)

The standard ASP instance for `U(3,10)` at depth 5 is satisfiable. The
independent Python verifier exhaustively checked the extracted network on all
1024 binary inputs and accepted it, establishing `UDepth(3,10) <= 5`.

The existing artifacts for `U(3,9)` record depth 4 as UNSAT and a depth-5
witness as independently verified:

- `experiments/baseline_n9/decisions/U_t3_n9/depth_04/solver.json`
- `experiments/baseline_n9/decisions/U_t3_n9/depth_04/decision.json`
- `experiments/baseline_n9/decisions/U_t3_n9/depth_05/network.json`
- `experiments/baseline_n9/decisions/U_t3_n9/depth_05/verifier.json`

Thus `UDepth(3,9)=5`; monotonicity in the number of wires gives
`UDepth(3,10) >= 5`. Together with the verified depth-5 witness, this yields

`UDepth(3,10)=5`.

### Consequence for UDepth(4,10)

The standard ASP instance for `U(4,10)` at depth 5 is satisfiable. The
independent Python verifier exhaustively checked the extracted network on all
1024 binary inputs and accepted it, establishing `UDepth(4,10) <= 5`.

The existing artifacts for `U(4,9)` record depth 4 as UNSAT and a depth-5
witness as independently verified:

- `experiments/baseline_n9/decisions/U_t4_n9/depth_04/decision.json`
- `experiments/baseline_n9/decisions/U_t4_n9/depth_04/solver.json`
- `experiments/baseline_n9/decisions/U_t4_n9/depth_05/network.json`
- `experiments/baseline_n9/decisions/U_t4_n9/depth_05/verifier.json`

Thus `UDepth(4,9)=5`; monotonicity in the number of wires gives
`UDepth(4,10) >= 5`. Together with the verified depth-5 witness, this yields

`UDepth(4,10)=5`.

### Consequence for UDepth(5,10)

The standard ASP instance for `U(5,10)` at depth 5 is satisfiable. The
independent Python verifier exhaustively checked the extracted network on all
1024 binary inputs and accepted it, establishing `UDepth(5,10) <= 5`.

No direct `experiments/baseline_n9/decisions/U_t5_n9/` directory was present.
For the lower bound, the certificate uses U-duality on nine wires: `U(5,9)` is
the dual central counterpart of `U(4,9)`. The existing `U(4,9)` artifacts record
depth 4 as UNSAT and a depth-5 witness as independently verified:

- `experiments/baseline_n9/decisions/U_t4_n9/depth_04/decision.json`
- `experiments/baseline_n9/decisions/U_t4_n9/depth_04/solver.json`
- `experiments/baseline_n9/decisions/U_t4_n9/depth_05/network.json`
- `experiments/baseline_n9/decisions/U_t4_n9/depth_05/verifier.json`

Thus `UDepth(5,9)=5`; monotonicity in the number of wires gives
`UDepth(5,10) >= 5`. Together with the verified depth-5 witness, this yields

`UDepth(5,10)=5`.

### Artifact ledger

#### U(2,10), depth 4

- Command: `experiments/baseline_n10/decisions/U_t2_n10/depth_04/command.txt`
- Solver input: `experiments/baseline_n10/decisions/U_t2_n10/depth_04/instance.lp`
- Raw solver JSON: `experiments/baseline_n10/decisions/U_t2_n10/depth_04/solver_raw.json`
- Parsed solver result: `experiments/baseline_n10/decisions/U_t2_n10/depth_04/result.json`
- Solver metadata: `experiments/baseline_n10/decisions/U_t2_n10/depth_04/solver_metadata.json`
- Preflight JSON: `experiments/baseline_n10/decisions/U_t2_n10/depth_04/preflight.json`
- Preflight report: `experiments/baseline_n10/decisions/U_t2_n10/depth_04/preflight.md`
- README: `experiments/baseline_n10/decisions/U_t2_n10/depth_04/README.md`

No network or verifier artifact is present because the instance is UNSAT.

#### U(2,10), depth 5

- Command: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/command.txt`
- Solver input: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/result.json`
- Solver metadata: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/solver_metadata.json`
- Network: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/network.json`
- Verifier result: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/verifier.json`
- Verifier trace summary: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/verifier_trace_summary.json`
- Preflight JSON: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/preflight.json`
- Preflight report: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/preflight.md`
- README: `experiments/baseline_n10/decisions/U_t2_n10/depth_05/README.md`

#### U(3,10), depth 5

- Command: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/command.txt`
- Solver input: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/result.json`
- Solver metadata: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/solver_metadata.json`
- Network: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/network.json`
- Verifier result: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/verifier.json`
- Verifier trace summary: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/verifier_trace_summary.json`
- Preflight JSON: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/preflight.json`
- Preflight report: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/preflight.md`
- README: `experiments/baseline_n10/decisions/U_t3_n10/depth_05/README.md`

#### U(4,10), depth 5

- Command: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/command.txt`
- Solver input: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/result.json`
- Solver metadata: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/solver_metadata.json`
- Network: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/network.json`
- Verifier result: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/verifier.json`
- Verifier trace summary: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/verifier_trace_summary.json`
- Preflight JSON: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/preflight.json`
- Preflight report: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/preflight.md`
- README: `experiments/baseline_n10/decisions/U_t4_n10/depth_05/README.md`

#### U(5,10), depth 5

- Command: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/command.txt`
- Solver input: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/instance.lp`
- Raw solver JSON: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/solver_raw.json`
- Parsed solver result: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/result.json`
- Solver metadata: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/solver_metadata.json`
- Network: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/network.json`
- Verifier result: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/verifier.json`
- Verifier trace summary: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/verifier_trace_summary.json`
- Preflight JSON: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/preflight.json`
- Preflight report: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/preflight.md`
- README: `experiments/baseline_n10/decisions/U_t5_n10/depth_05/README.md`


### n=10 U-depth table

The table below uses the directly verified n=10 decisions for `t=2,3,4,5`;
`UDepth(1,10)=4` is the standard minimum-depth bound for selecting one item,
and `UDepth(10,10)=0` is trivial. The entries for `t=6,7,8,9` are filled by
U-duality from `t=4,3,2,1`, respectively.

| t | UDepth(t,10) | source |
| ---: | ---: | --- |
| 1 | 4 | standard one-selection bound |
| 2 | 5 | `U(2,10)` depth 4 UNSAT and depth 5 verified SAT |
| 3 | 5 | `U(3,10)` depth 5 verified SAT plus n=9 lower bound |
| 4 | 5 | `U(4,10)` depth 5 verified SAT plus n=9 lower bound |
| 5 | 5 | `U(5,10)` depth 5 verified SAT plus n=9 lower bound by U-duality |
| 6 | 5 | U-duality from `UDepth(4,10)=5` |
| 7 | 5 | U-duality from `UDepth(3,10)=5` |
| 8 | 5 | U-duality from `UDepth(2,10)=5` |
| 9 | 4 | U-duality from `UDepth(1,10)=4` |
| 10 | 0 | trivial all-wire selection |

### Caveats

- The `U(2,10)` UNSAT result is based on the raw solver artifact for the
  encoded instance.
- The SAT witness was checked by independent exhaustive binary simulation.
- Runtime is an operational observation, not evidence of mathematical
  difficulty.
- This report now includes `U(2,10)` at depths 4 and 5, `U(3,10)` at
  depth 5, `U(4,10)` at depth 5, and `U(5,10)` at depth 5; no new
  reduction was introduced.
- For U-type selection, a `U(3,10)` witness does not automatically provide a
  `U(2,10)` witness; the latter was decided independently here.

- The verified `V(3,10)` depth-6 witness is also a `V(2,10)` witness and hence
  a valid `U(2,10)` upper bound; this implication is separate from the U-type
  non-implication above.
- U duality is not used for the `U(4,10)` depth-5 decision itself.
- A `U(4,10)` depth-5 witness does not automatically provide a `U(5,10)` depth-5 witness; `U(5,10)` was decided independently.
- U duality is used to fill the final table, while the `U(5,10)` decision itself is based on direct solver/verifier artifacts.
