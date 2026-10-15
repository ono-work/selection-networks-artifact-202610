# Baseline n=7 Experiment Report

This report records baseline pure-ASP synthesis outcomes only. It does not claim novelty or openness.

## Reproducibility Summary

- Git HEAD: `7c06ad41aa6b9037ce471cebc143dae24897f5f5`
- Dirty worktree status:
```text
M README.md
 M SPEC.md
 M src/experiment.py
 M src/network.py
 M tests/test_calibration_matrix.py
 M tests/test_network.py
?? docs/literature/
?? experiments/baseline_n7/
?? tests/test_u_mirror_duality.py
```
- Canonical experiment driver: `.venv/bin/python -m src.experiment`
- Per-instance timeout: `1200` seconds
- Clingo version: first line `pyclingo version 5.8.0`
- Environment metadata: `experiments/baseline_n7/reports/batch_environment.json`
- Per-decision reproducibility metadata: `experiments/baseline_n7/reports/decision_reproducibility.json`

## Decision Table

| target | depth | status | runtime seconds | witness |
| --- | ---: | --- | ---: | --- |
| U(3,7) | 0 | UNSAT | 0.026293 |  |
| U(3,7) | 1 | UNSAT | 0.028319 |  |
| U(3,7) | 2 | UNSAT | 0.050775 |  |
| U(3,7) | 3 | UNSAT | 0.146915 |  |
| U(3,7) | 4 | SAT | 0.072527 | experiments/baseline_n7/decisions/U_t3_n7/depth_04/network.json |
| V(3,7) | 0 | UNSAT | 0.026537 |  |
| V(3,7) | 1 | UNSAT | 0.029082 |  |
| V(3,7) | 2 | UNSAT | 0.032082 |  |
| V(3,7) | 3 | UNSAT | 0.042631 |  |
| V(3,7) | 4 | UNSAT | 0.307894 |  |
| V(3,7) | 5 | UNSAT | 3.977228 |  |
| V(3,7) | 6 | SAT | 0.088287 | experiments/baseline_n7/decisions/V_t3_n7/depth_06/network.json |
| V(4,7) | 0 | UNSAT | 0.026134 |  |
| V(4,7) | 1 | UNSAT | 0.027803 |  |
| V(4,7) | 2 | UNSAT | 0.034569 |  |
| V(4,7) | 3 | UNSAT | 0.044409 |  |
| V(4,7) | 4 | UNSAT | 0.084562 |  |
| V(4,7) | 5 | UNSAT | 2.738397 |  |
| V(4,7) | 6 | SAT | 0.130488 | experiments/baseline_n7/decisions/V_t4_n7/depth_06/network.json |

## Target Outcomes

| target | outcome | minimum depth | shorter UNSAT depths | first verified SAT depth | timeouts or omitted depths |
| --- | --- | ---: | --- | ---: | --- |
| U(3,7) | EXACT_CONFIRMED | 4 | 0,1,2,3 | 4 | omitted after stop: 5,6 |
| V(3,7) | EXACT_CONFIRMED | 6 | 0,1,2,3,4,5 | 6 | none |
| V(4,7) | EXACT_CONFIRMED | 6 | 0,1,2,3,4,5 | 6 | none |

## Runtime Table

| rank | target | depth | status | runtime seconds |
| ---: | --- | ---: | --- | ---: |
| 1 | V(3,7) | 5 | UNSAT | 3.977228 |
| 2 | V(4,7) | 5 | UNSAT | 2.738397 |
| 3 | V(3,7) | 4 | UNSAT | 0.307894 |
| 4 | U(3,7) | 3 | UNSAT | 0.146915 |
| 5 | V(4,7) | 6 | SAT | 0.130488 |
| 6 | V(3,7) | 6 | SAT | 0.088287 |
| 7 | V(4,7) | 4 | UNSAT | 0.084562 |
| 8 | U(3,7) | 4 | SAT | 0.072527 |
| 9 | U(3,7) | 2 | UNSAT | 0.050775 |
| 10 | V(4,7) | 3 | UNSAT | 0.044409 |
| 11 | V(3,7) | 3 | UNSAT | 0.042631 |
| 12 | V(4,7) | 2 | UNSAT | 0.034569 |
| 13 | V(3,7) | 2 | UNSAT | 0.032082 |
| 14 | V(3,7) | 1 | UNSAT | 0.029082 |
| 15 | U(3,7) | 1 | UNSAT | 0.028319 |
| 16 | V(4,7) | 1 | UNSAT | 0.027803 |
| 17 | V(3,7) | 0 | UNSAT | 0.026537 |
| 18 | U(3,7) | 0 | UNSAT | 0.026293 |
| 19 | V(4,7) | 0 | UNSAT | 0.026134 |

## Verified SAT Witnesses

### U(3,7) depth 4

- Witness path: `experiments/baseline_n7/decisions/U_t3_n7/depth_04/network.json`
- Comparator count: `12`
- Per-layer comparator counts: `3,3,3,3`

- Layer 1: (2,7), (3,4), (5,6)
- Layer 2: (1,5), (2,4), (3,7)
- Layer 3: (1,7), (2,3), (5,6)
- Layer 4: (1,4), (2,6), (3,5)

### V(3,7) depth 6

- Witness path: `experiments/baseline_n7/decisions/V_t3_n7/depth_06/network.json`
- Comparator count: `14`
- Per-layer comparator counts: `2,3,3,3,2,1`

- Layer 1: (2,3), (4,5)
- Layer 2: (1,2), (3,4), (6,7)
- Layer 3: (1,6), (2,7), (3,4)
- Layer 4: (1,3), (2,6), (4,5)
- Layer 5: (2,4), (3,6)
- Layer 6: (2,3)

### V(4,7) depth 6

- Witness path: `experiments/baseline_n7/decisions/V_t4_n7/depth_06/network.json`
- Comparator count: `17`
- Per-layer comparator counts: `3,3,3,3,3,2`

- Layer 1: (1,3), (4,6), (5,7)
- Layer 2: (1,2), (3,4), (5,6)
- Layer 3: (1,5), (2,7), (4,6)
- Layer 4: (2,5), (3,7), (4,6)
- Layer 5: (1,6), (2,3), (4,5)
- Layer 6: (1,2), (3,4)

## Derived U(4,7) Witness

This witness is derived by U-type mirror duality; not independently solver-synthesized.

- Derived witness path: `experiments/baseline_n7/derived/U_t4_n7_from_U_t3_n7_mirror_dual.json`
- Independent verifier result: `True` (verified all binary inputs)
- Source witness: `experiments/baseline_n7/decisions/U_t3_n7/depth_04/network.json`
- Comparator count: `12`
- Per-layer comparator counts: `3,3,3,3`

- Layer 1: (1,6), (4,5), (2,3)
- Layer 2: (3,7), (4,6), (1,5)
- Layer 3: (1,7), (5,6), (2,3)
- Layer 4: (4,7), (2,6), (3,5)

## Observations requiring no novelty claim

- Existing n <= 6 calibration artifacts record `U(3,6)` at depth 3; this batch records `U(3,7)` at depth 4.
- Existing n <= 6 calibration artifacts record `V(3,6)` at depth 5; this batch records `V(3,7)` at depth 6.
- Existing n <= 6 calibration artifacts record `V(4,6)` at depth 5; this batch records `V(4,7)` at depth 6.
- The derived `U(4,7)` artifact has the same depth as the verified `U(3,7)` source witness, as expected from the repository mirror-duality transformation.

## Recommended next computational action

inspect a witness structurally
