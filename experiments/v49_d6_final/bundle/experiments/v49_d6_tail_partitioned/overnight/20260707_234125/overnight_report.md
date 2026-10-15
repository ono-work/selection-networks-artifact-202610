# V(4,9), Depth-6 Tail Overnight Report

## Metadata

Exact launch command: `./scripts/run_v49_d6_tail_partitioned.sh --mode overnight --enable-topology-pruning --output-dir /home/ono/Codex/experiments/v49_d6_tail_partitioned`

Clingo version: `pyclingo version 5.8.0
Address model: 64-bit

libclingo version 5.8.0
Configuration: without Python, without Lua

libclasp version 3.4.0 (libpotassco version 1.2.0)
Configuration: WITH_THREADS=1
Copyright (C) Benjamin Kaufmann

License: The MIT License <https://opensource.org/licenses/MIT>`

Host metadata: `{"cpu_count": 20, "gpu_use": "none", "node": "thor", "platform": "Linux-6.17.0-1021-nvidia-aarch64-with-glibc2.39", "python": "3.12.3"}`

Git HEAD: `7c06ad41aa6b9037ce471cebc143dae24897f5f5`

Dirty worktree state: `M README.md
 M SPEC.md
 M src/experiment.py
 M src/generate_instance.py
 M src/network.py
 M tests/test_calibration_matrix.py
 M tests/test_network.py
?? docs/literature/
?? docs/v49_d6/
?? docs/v49_d6_six_leaf_reductions.md
?? docs/v49_d6_terminal_profiles.md
?? docs/v_boundary_and_v49_support_partition.md
?? experiments/baseline_n7/
?? experiments/baseline_n8/
?? experiments/baseline_n9/
?? experiments/v49_d6_bp5_final_layer_partitioned/
?? experiments/v49_d6_closure_audit/
?? experiments/v49_d6_l5_partitioned/
?? experiments/v49_d6_l5_tail_census/
?? experiments/v49_d6_partitioned/
?? experiments/v49_d6_partner_partitioned/
?? experiments/v49_d6_refined_partitioned/
?? experiments/v49_d6_six_leaf_reduced/
?? experiments/v49_d6_solver_config_benchmark/
?? experiments/v49_d6_support_partitioned/
?? experiments/v49_d6_tail_partitioned/
?? experiments/v49_d6_topology_pruning/
?? scripts/benchmark_v49_d6_solver_config.sh
?? scripts/run_v49_d6_bp5_final_layer_partitioned.sh
?? scripts/run_v49_d6_l5_longrun.sh
?? scripts/run_v49_d6_l5_partitioned.sh
?? scripts/run_v49_d6_partitioned.sh
?? scripts/run_v49_d6_partner_partitioned.sh
?? scripts/run_v49_d6_refined_partitioned.sh
?? scripts/run_v49_d6_six_leaf_reduced.sh
?? scripts/run_v49_d6_support_partitioned.sh
?? scripts/run_v49_d6_tail_partitioned.sh
?? src/analyze_v49_d6_six_leaf_reductions.py
?? src/analyze_v49_d6_terminal_profiles.py
?? src/benchmark_v49_d6_solver_config.py
?? src/run_v49_d6_bp5_final_layer_partitioned.py
?? src/run_v49_d6_l5_longrun.py
?? src/run_v49_d6_l5_partitioned.py
?? src/run_v49_d6_partitioned.py
?? src/run_v49_d6_partner_partitioned.py
?? src/run_v49_d6_refined_partitioned.py
?? src/run_v49_d6_six_leaf_reduced.py
?? src/run_v49_d6_support_partitioned.py
?? src/run_v49_d6_tail_partitioned.py
?? src/v49_d6_closure_audit.py
?? src/v49_d6_l5_tail_census.py
?? src/v49_d6_topology_pruning.py
?? tests/test_u_mirror_duality.py
?? tests/test_v49_d6_bp5_final_layer_partitioned.py
?? tests/test_v49_d6_closure_audit.py
?? tests/test_v49_d6_l5_partitioned.py
?? tests/test_v49_d6_l5_tail_census.py
?? tests/test_v49_d6_partitioned.py
?? tests/test_v49_d6_partner_partitioned.py
?? tests/test_v49_d6_refined_partitioned.py
?? tests/test_v49_d6_six_leaf_reductions.py
?? tests/test_v49_d6_solver_config_and_longrun.py
?? tests/test_v49_d6_support_partitioned.py
?? tests/test_v49_d6_tail_screening.py
?? tests/test_v49_d6_topology_pruning.py`

Relevant hashes: `{"/home/ono/Codex/experiments/v49_d6_topology_pruning/validation.json": "c98d362f8184fe2d80d143e5d6e92c3c62ba15819270350a7079ebddb060ccc7", "/home/ono/Codex/solver/common.lp": "2cebdc5d3107f09b77e3ebeaf554b39f25212dbe7a1fb9bd78fa933e0b990fc0", "/home/ono/Codex/solver/target_v.lp": "ddae98e3a4bd702b9d97342ab558f7a4670eb7c7caf5dd726e28aef7cfe77f1a", "src/run_v49_d6_tail_partitioned.py": "9d51b8116b30588c6de6f4bae37a6caec0de925b7b0597ca64f431a16dea9b21", "src/v49_d6_topology_pruning.py": "f9d7cf57ccc4648a1a4f6f1fe2c3fb46eff7cf8945897238a4c78a2b19779e5e", "src/verify.py": "28d353d2cc796bf099f79c4db8e2587677d83e987b0ad3b2e526496b1b389219"}`

## Worker Calculation

Host logical CPUs: 20; reserved for OS: 2; outer workers: 18; clingo threads per branch: 1; internal clingo parallel mode: none; GPU use: none.

## Scheduling Policy

Dynamic worker-pool scheduling. Dispatch one branch from each nonempty operational workload class in round-robin order. When a worker becomes free, dispatch the next branch from the next nonempty class. Within a class, branches are sorted by census matching count and stable branch ID. Exhausted classes are skipped. No artificial waves are imposed.

## Selection Certificate

49 screening UNSAT excluded: True.

26 screening TIMEOUT selected: True.

Each selected branch belongs to exactly one class: True.

## Status Table

| queue | workload class | parent | census | branch | status | runtime s | peak RSS KB |
| ---: | --- | --- | ---: | --- | --- | ---: | ---: |
| 1 | A5_near | A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_2` | UNSAT | 3811.514 | 77060 |
| 2 | A5_tail | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_6` | UNSAT | 1327.140 | 75188 |
| 3 | A5_unused | A5_residual_L5eq3 | 336 | `A5_residual_L5eq3__wire1_unused` | UNSAT | 2046.948 | 76756 |
| 4 | B6eq3_both_used | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_2__p6_4` | UNSAT | 830.348 | 72580 |
| 5 | B6eq3_one_idle_near | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_2` | UNSAT | 1323.377 | 73692 |
| 6 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_7` | UNSAT | 1546.530 | 73448 |
| 7 | B6eq3_both_idle | B6_residual_L5eq3 | 78 | `B6_residual_L5eq3__p1_0__p6_0` | UNSAT | 1659.744 | 73092 |
| 8 | B6eq4_unused_final_endpoint | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_1` | UNSAT | 2661.352 | 77696 |
| 9 | B6eq4_unused_tail | B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_7` | UNSAT | 6210.805 | 81484 |
| 10 | A5_near | A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_3` | UNSAT | 1881.370 | 73812 |
| 11 | A5_tail | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_7` | UNSAT | 1522.434 | 75332 |
| 12 | B6eq3_both_used | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_2__p6_5` | UNSAT | 2989.595 | 73340 |
| 13 | B6eq3_one_idle_near | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_5` | UNSAT | 637.174 | 73032 |
| 14 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_8` | UNSAT | 1174.898 | 73264 |
| 15 | B6eq4_unused_final_endpoint | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_6` | UNSAT | 4387.050 | 79344 |
| 16 | B6eq4_unused_tail | B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_8` | UNSAT | 6512.609 | 82336 |
| 17 | A5_tail | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_8` | UNSAT | 1507.309 | 75460 |
| 18 | B6eq3_both_used | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_3__p6_5` | UNSAT | 822.877 | 72460 |
| 19 | B6eq3_one_idle_near | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_2__p6_0` | UNSAT | 3139.494 | 74060 |
| 20 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_9` | UNSAT | 1843.973 | 73704 |
| 21 | B6eq4_unused_tail | B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_9` | UNSAT | 4633.946 | 81404 |
| 22 | A5_tail | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_9` | UNSAT | 1117.495 | 74924 |
| 23 | B6eq3_one_idle_near | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_3__p6_0` | UNSAT | 1092.768 | 71012 |
| 24 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_7__p6_0` | UNSAT | 1278.782 | 72860 |
| 25 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_8__p6_0` | UNSAT | 1021.014 | 72896 |
| 26 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_9__p6_0` | UNSAT | 1021.897 | 72676 |

## Status Counts

| status | count |
| --- | ---: |
| SAT | 0 |
| UNSAT | 26 |
| TIMEOUT | 0 |
| ERROR | 0 |
| VERIFICATION_FAILED | 0 |
| CANCELLED_AFTER_VERIFIED_SAT | 0 |

## Runtime And RSS Summary

Runtime seconds: `{'count': 26, 'min': 637.1743906949996, 'max': 6512.609304896963, 'mean': 2230.863239523303}`

Peak RSS KB: `{'count': 26, 'min': 71012, 'max': 82336, 'mean': 75112.0}`

## Remaining Timeout Branches

| workload class | branch | runtime s |
| --- | --- | ---: |
|  | No timeout branches. |  |

## Tail-Partition Coverage Accounting

| category | count |
| --- | ---: |
| branches closed in screening | 49 |
| branches newly closed overnight | 26 |
| remaining timeout/error/cancelled branches | 0 |

## Outcome

V49_DEPTH6_UNSAT_COVERAGE_COMPLETE

Stop reason: `completed_all_jobs`.
