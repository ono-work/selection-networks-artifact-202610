# Baseline n=8 Experiment Report

This report records internal baseline pure-ASP synthesis outcomes only. It makes no novelty, openness, publication, size-optimality, comparator-count optimality, or structural-representativeness claim.

## Pre-flight Metadata

- Git HEAD: `7c06ad41aa6b9037ce471cebc143dae24897f5f5`
- `git status --short`:
```text
M README.md
 M SPEC.md
 M src/experiment.py
 M src/network.py
 M tests/test_calibration_matrix.py
 M tests/test_network.py
?? docs/literature/
?? experiments/baseline_n7/
?? experiments/baseline_n8/
?? tests/test_u_mirror_duality.py
```
- Solver command: `.venv/bin/python -m clingo`
- Clingo version: `pyclingo version 5.8.0`
- Python version: `3.12.3`
- OS: `Linux-6.17.0-1021-nvidia-aarch64-with-glibc2.39`
- Hostname: `thor`
- Hash and environment metadata: `experiments/baseline_n8/reports/batch_environment.json`
- n=7 untouched check: `True`

## Decision Table

| target | depth | status | runtime seconds | raw output | witness |
| --- | ---: | --- | ---: | --- | --- |
| U(3,8) | 0 | UNSAT | 0.044302 | experiments/baseline_n8/decisions/U_t3_n8/depth_00/solver.json |  |
| U(3,8) | 1 | UNSAT | 0.047579 | experiments/baseline_n8/decisions/U_t3_n8/depth_01/solver.json |  |
| U(3,8) | 2 | UNSAT | 0.065261 | experiments/baseline_n8/decisions/U_t3_n8/depth_02/solver.json |  |
| U(3,8) | 3 | UNSAT | 0.649925 | experiments/baseline_n8/decisions/U_t3_n8/depth_03/solver.json |  |
| U(3,8) | 4 | SAT | 0.437983 | experiments/baseline_n8/decisions/U_t3_n8/depth_04/solver.json | experiments/baseline_n8/decisions/U_t3_n8/depth_04/network.json |
| U(4,8) | 0 | UNSAT | 0.031241 | experiments/baseline_n8/decisions/U_t4_n8/depth_00/solver.json |  |
| U(4,8) | 1 | UNSAT | 0.048322 | experiments/baseline_n8/decisions/U_t4_n8/depth_01/solver.json |  |
| U(4,8) | 2 | UNSAT | 0.065542 | experiments/baseline_n8/decisions/U_t4_n8/depth_02/solver.json |  |
| U(4,8) | 3 | UNSAT | 0.351105 | experiments/baseline_n8/decisions/U_t4_n8/depth_03/solver.json |  |
| U(4,8) | 4 | SAT | 0.210534 | experiments/baseline_n8/decisions/U_t4_n8/depth_04/solver.json | experiments/baseline_n8/decisions/U_t4_n8/depth_04/network.json |
| V(3,8) | 0 | UNSAT | 0.030198 | experiments/baseline_n8/decisions/V_t3_n8/depth_00/solver.json |  |
| V(3,8) | 1 | UNSAT | 0.047149 | experiments/baseline_n8/decisions/V_t3_n8/depth_01/solver.json |  |
| V(3,8) | 2 | UNSAT | 0.051801 | experiments/baseline_n8/decisions/V_t3_n8/depth_02/solver.json |  |
| V(3,8) | 3 | UNSAT | 0.086294 | experiments/baseline_n8/decisions/V_t3_n8/depth_03/solver.json |  |
| V(3,8) | 4 | UNSAT | 0.883726 | experiments/baseline_n8/decisions/V_t3_n8/depth_04/solver.json |  |
| V(3,8) | 5 | UNSAT | 27.378404 | experiments/baseline_n8/decisions/V_t3_n8/depth_05/solver.json |  |
| V(3,8) | 6 | SAT | 0.167301 | experiments/baseline_n8/decisions/V_t3_n8/depth_06/solver.json | experiments/baseline_n8/decisions/V_t3_n8/depth_06/network.json |
| V(4,8) | 0 | UNSAT | 0.029836 | experiments/baseline_n8/decisions/V_t4_n8/depth_00/solver.json |  |
| V(4,8) | 1 | UNSAT | 0.032492 | experiments/baseline_n8/decisions/V_t4_n8/depth_01/solver.json |  |
| V(4,8) | 2 | UNSAT | 0.049986 | experiments/baseline_n8/decisions/V_t4_n8/depth_02/solver.json |  |
| V(4,8) | 3 | UNSAT | 0.080908 | experiments/baseline_n8/decisions/V_t4_n8/depth_03/solver.json |  |
| V(4,8) | 4 | UNSAT | 0.244860 | experiments/baseline_n8/decisions/V_t4_n8/depth_04/solver.json |  |
| V(4,8) | 5 | UNSAT | 8.732931 | experiments/baseline_n8/decisions/V_t4_n8/depth_05/solver.json |  |
| V(4,8) | 6 | SAT | 0.421648 | experiments/baseline_n8/decisions/V_t4_n8/depth_06/solver.json | experiments/baseline_n8/decisions/V_t4_n8/depth_06/network.json |

## Target Outcomes

| target | outcome | minimum depth | shorter UNSAT depths | first verified SAT depth | witness path | omitted depths |
| --- | --- | ---: | --- | ---: | --- | --- |
| U(3,8) | EXACT_CONFIRMED | 4 | 0,1,2,3 | 4 | experiments/baseline_n8/decisions/U_t3_n8/depth_04/network.json | 5,6 |
| U(4,8) | EXACT_CONFIRMED | 4 | 0,1,2,3 | 4 | experiments/baseline_n8/decisions/U_t4_n8/depth_04/network.json | 5,6 |
| V(3,8) | EXACT_CONFIRMED | 6 | 0,1,2,3,4,5 | 6 | experiments/baseline_n8/decisions/V_t3_n8/depth_06/network.json | none |
| V(4,8) | EXACT_CONFIRMED | 6 | 0,1,2,3,4,5 | 6 | experiments/baseline_n8/decisions/V_t4_n8/depth_06/network.json | none |

## Runtime Table

| rank | target | depth | status | runtime seconds |
| ---: | --- | ---: | --- | ---: |
| 1 | V(3,8) | 5 | UNSAT | 27.378404 |
| 2 | V(4,8) | 5 | UNSAT | 8.732931 |
| 3 | V(3,8) | 4 | UNSAT | 0.883726 |
| 4 | U(3,8) | 3 | UNSAT | 0.649925 |
| 5 | U(3,8) | 4 | SAT | 0.437983 |
| 6 | V(4,8) | 6 | SAT | 0.421648 |
| 7 | U(4,8) | 3 | UNSAT | 0.351105 |
| 8 | V(4,8) | 4 | UNSAT | 0.244860 |
| 9 | U(4,8) | 4 | SAT | 0.210534 |
| 10 | V(3,8) | 6 | SAT | 0.167301 |
| 11 | V(3,8) | 3 | UNSAT | 0.086294 |
| 12 | V(4,8) | 3 | UNSAT | 0.080908 |
| 13 | U(4,8) | 2 | UNSAT | 0.065542 |
| 14 | U(3,8) | 2 | UNSAT | 0.065261 |
| 15 | V(3,8) | 2 | UNSAT | 0.051801 |
| 16 | V(4,8) | 2 | UNSAT | 0.049986 |
| 17 | U(4,8) | 1 | UNSAT | 0.048322 |
| 18 | U(3,8) | 1 | UNSAT | 0.047579 |
| 19 | V(3,8) | 1 | UNSAT | 0.047149 |
| 20 | U(3,8) | 0 | UNSAT | 0.044302 |
| 21 | V(4,8) | 1 | UNSAT | 0.032492 |
| 22 | U(4,8) | 0 | UNSAT | 0.031241 |
| 23 | V(3,8) | 0 | UNSAT | 0.030198 |
| 24 | V(4,8) | 0 | UNSAT | 0.029836 |

## internal baseline results; no literature novelty claim

| family | n=6 | n=7 | n=8 | provenance note |
| --- | --- | --- | --- | --- |
| U(3,n) | 3 | 4 | 4 | direct synthesis |
| U(4,n) | 4 | 4 derived from U(3,7) | 4 direct; U(5,8) derived from U(3,8) | n=6 and n=8 direct; n=7 duality as noted |
| V(3,n) | 5 | 6 | 6 | direct synthesis |
| V(4,n) | 5 | 6 | 6 | direct synthesis |

## Verified SAT Witnesses

### U(3,8) depth 4

- Witness path: `experiments/baseline_n8/decisions/U_t3_n8/depth_04/network.json`
- Raw solver output: `experiments/baseline_n8/decisions/U_t3_n8/depth_04/solver.json`
- Independent-verification result: `experiments/baseline_n8/decisions/U_t3_n8/depth_04/verifier.json`
- Comparator count: `15`
- Per-layer comparator counts: `4,4,4,3`

- Layer 1: (1,6), (2,8), (3,7), (4,5)
- Layer 2: (1,3), (2,5), (4,8), (6,7)
- Layer 3: (1,5), (2,3), (4,6), (7,8)
- Layer 4: (1,7), (2,6), (3,4)

### U(4,8) depth 4

- Witness path: `experiments/baseline_n8/decisions/U_t4_n8/depth_04/network.json`
- Raw solver output: `experiments/baseline_n8/decisions/U_t4_n8/depth_04/solver.json`
- Independent-verification result: `experiments/baseline_n8/decisions/U_t4_n8/depth_04/verifier.json`
- Comparator count: `16`
- Per-layer comparator counts: `4,4,4,4`

- Layer 1: (1,4), (2,6), (3,8), (5,7)
- Layer 2: (1,6), (2,4), (3,7), (5,8)
- Layer 3: (1,2), (3,5), (4,6), (7,8)
- Layer 4: (1,8), (2,7), (3,6), (4,5)

### V(3,8) depth 6

- Witness path: `experiments/baseline_n8/decisions/V_t3_n8/depth_06/network.json`
- Raw solver output: `experiments/baseline_n8/decisions/V_t3_n8/depth_06/solver.json`
- Independent-verification result: `experiments/baseline_n8/decisions/V_t3_n8/depth_06/verifier.json`
- Comparator count: `16`
- Per-layer comparator counts: `4,4,3,2,2,1`

- Layer 1: (1,2), (3,7), (4,8), (5,6)
- Layer 2: (1,5), (2,8), (3,4), (6,7)
- Layer 3: (1,4), (2,6), (3,5)
- Layer 4: (1,3), (2,5)
- Layer 5: (1,3), (2,4)
- Layer 6: (2,3)

### V(4,8) depth 6

- Witness path: `experiments/baseline_n8/decisions/V_t4_n8/depth_06/network.json`
- Raw solver output: `experiments/baseline_n8/decisions/V_t4_n8/depth_06/solver.json`
- Independent-verification result: `experiments/baseline_n8/decisions/V_t4_n8/depth_06/verifier.json`
- Comparator count: `20`
- Per-layer comparator counts: `4,4,4,3,3,2`

- Layer 1: (1,3), (2,7), (4,6), (5,8)
- Layer 2: (1,2), (3,8), (4,5), (6,7)
- Layer 3: (1,4), (2,5), (3,6), (7,8)
- Layer 4: (2,6), (3,4), (5,7)
- Layer 5: (2,4), (5,6), (7,8)
- Layer 6: (2,3), (4,5)

## Duality-derived witness artifacts

### U_t5_n8_from_U_t3_n8_mirror_dual.json

- Path: `experiments/baseline_n8/derived/U_t5_n8_from_U_t3_n8_mirror_dual.json`
- Label: derived by U-type mirror duality; not independently solver-synthesized
- Verification status: `True` (verified all binary inputs)
- Source witness: `experiments/baseline_n8/decisions/U_t3_n8/depth_04/network.json`
- Comparator count: `15`
- Per-layer comparator counts: `4,4,4,3`

- Layer 1: (3,8), (1,7), (2,6), (4,5)
- Layer 2: (6,8), (4,7), (1,5), (2,3)
- Layer 3: (4,8), (6,7), (3,5), (1,2)
- Layer 4: (2,8), (3,7), (5,6)

### U_t4_n8_self_dual_consistency_check.json

- Path: `experiments/baseline_n8/derived/U_t4_n8_self_dual_consistency_check.json`
- Label: self-duality consistency-check artifact; not an additional independent solver result
- Verification status: `True` (verified all binary inputs)
- Source witness: `experiments/baseline_n8/decisions/U_t4_n8/depth_04/network.json`
- Comparator count: `16`
- Per-layer comparator counts: `4,4,4,4`

- Layer 1: (5,8), (3,7), (1,6), (2,4)
- Layer 2: (3,8), (5,7), (2,6), (1,4)
- Layer 3: (7,8), (4,6), (3,5), (1,2)
- Layer 4: (1,8), (2,7), (3,6), (4,5)

## Observations requiring no novelty claim

- The n=8 batch used the same pure-ASP baseline driver and clingo command as the n=7 batch, with a larger per-decision timeout.
- `U(3,8)` and `U(4,8)` both verified at depth 4 in this internal batch; `U(3,7)` also verified at depth 4 in the previous internal batch.
- `V(3,8)` verified at depth 6, matching the previous internal `V(3,7)` depth value.
- `V(4,8)` verified at depth 6, matching the previous internal `V(4,7)` depth value.
- The `U(5,8)` artifact is derived from `U(3,8)` by mirror duality and is not an independent solver result.
- The `U(4,8)` mirror artifact is a self-duality consistency check and is not an additional independent solver result.

## Recommended next computational action

inspect one or more witnesses structurally
