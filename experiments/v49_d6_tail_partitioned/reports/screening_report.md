# V(4,9), Depth-6 Tail Screening Report

## Reproducibility

Exact command line: `./scripts/run_v49_d6_tail_partitioned.sh --mode screening --enable-topology-pruning --output-dir /home/ono/Codex/experiments/v49_d6_tail_partitioned`

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

## Scheduler Policy

Dynamic worker-pool scheduling with 18 outer workers, one clingo thread per branch, 600 second per-branch timeout, no internal clingo parallel mode, no GPU use, and topology pruning enabled. Within each parent family, children are sorted by ascending census matching count and then stable branch identifier. Dispatch uses parent-family round-robin while multiple queues remain nonempty; workers take the next queued job immediately when free.

## Queue Order

| queue | parent | census | branch | status |
| ---: | --- | ---: | --- | --- |
| 1 | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_6` | TIMEOUT |
| 2 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_7__p6_8` | UNSAT |
| 3 | B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_7` | TIMEOUT |
| 4 | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_7` | TIMEOUT |
| 5 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_7__p6_9` | UNSAT |
| 6 | B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_8` | TIMEOUT |
| 7 | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_8` | TIMEOUT |
| 8 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_8__p6_7` | UNSAT |
| 9 | B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_9` | TIMEOUT |
| 10 | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_9` | TIMEOUT |
| 11 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_8__p6_9` | UNSAT |
| 12 | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_1` | TIMEOUT |
| 13 | A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_2` | TIMEOUT |
| 14 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_9__p6_7` | UNSAT |
| 15 | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_2` | UNSAT |
| 16 | A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_3` | TIMEOUT |
| 17 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_9__p6_8` | UNSAT |
| 18 | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_3` | UNSAT |
| 19 | A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_4` | UNSAT |
| 20 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_2__p6_3` | UNSAT |
| 21 | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_4` | UNSAT |
| 22 | A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_5` | UNSAT |
| 23 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_2__p6_7` | UNSAT |
| 24 | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_5` | UNSAT |
| 25 | A5_residual_L5eq3 | 336 | `A5_residual_L5eq3__wire1_unused` | TIMEOUT |
| 26 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_2__p6_8` | UNSAT |
| 27 | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_6` | TIMEOUT |
| 28 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_2__p6_9` | UNSAT |
| 29 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_3__p6_2` | UNSAT |
| 30 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_3__p6_7` | UNSAT |
| 31 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_3__p6_8` | UNSAT |
| 32 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_3__p6_9` | UNSAT |
| 33 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_4__p6_5` | UNSAT |
| 34 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_4__p6_7` | UNSAT |
| 35 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_4__p6_8` | UNSAT |
| 36 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_4__p6_9` | UNSAT |
| 37 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_5__p6_4` | UNSAT |
| 38 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_5__p6_7` | UNSAT |
| 39 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_5__p6_8` | UNSAT |
| 40 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_5__p6_9` | UNSAT |
| 41 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_7__p6_2` | UNSAT |
| 42 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_7__p6_3` | UNSAT |
| 43 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_7__p6_4` | UNSAT |
| 44 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_7__p6_5` | UNSAT |
| 45 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_8__p6_2` | UNSAT |
| 46 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_8__p6_3` | UNSAT |
| 47 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_8__p6_4` | UNSAT |
| 48 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_8__p6_5` | UNSAT |
| 49 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_9__p6_2` | UNSAT |
| 50 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_9__p6_3` | UNSAT |
| 51 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_9__p6_4` | UNSAT |
| 52 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_9__p6_5` | UNSAT |
| 53 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_2__p6_4` | TIMEOUT |
| 54 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_2__p6_5` | TIMEOUT |
| 55 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_3__p6_4` | UNSAT |
| 56 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_3__p6_5` | TIMEOUT |
| 57 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_4__p6_2` | UNSAT |
| 58 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_4__p6_3` | UNSAT |
| 59 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_5__p6_2` | UNSAT |
| 60 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_5__p6_3` | UNSAT |
| 61 | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_7` | TIMEOUT |
| 62 | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_8` | TIMEOUT |
| 63 | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_9` | TIMEOUT |
| 64 | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_7__p6_0` | TIMEOUT |
| 65 | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_8__p6_0` | TIMEOUT |
| 66 | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_9__p6_0` | TIMEOUT |
| 67 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_2` | TIMEOUT |
| 68 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_3` | UNSAT |
| 69 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_4` | UNSAT |
| 70 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_5` | TIMEOUT |
| 71 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_2__p6_0` | TIMEOUT |
| 72 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_3__p6_0` | TIMEOUT |
| 73 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_4__p6_0` | UNSAT |
| 74 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_5__p6_0` | UNSAT |
| 75 | B6_residual_L5eq3 | 78 | `B6_residual_L5eq3__p1_0__p6_0` | TIMEOUT |

## Outcome Counts

| status | count |
| --- | ---: |
| SAT | 0 |
| UNSAT | 49 |
| TIMEOUT | 26 |
| ERROR | 0 |
| VERIFICATION_FAILED | 0 |
| CANCELLED_AFTER_VERIFIED_SAT | 0 |

## Completed UNSAT Branches

| queue | parent | census | branch | runtime s | peak RSS KB |
| ---: | --- | ---: | --- | ---: | ---: |
| 2 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_7__p6_8` | 174.687 | 74636 |
| 5 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_7__p6_9` | 195.046 | 74644 |
| 8 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_8__p6_7` | 182.425 | 74636 |
| 11 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_8__p6_9` | 131.479 | 74652 |
| 14 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_9__p6_7` | 186.281 | 74644 |
| 15 | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_2` | 126.447 | 72812 |
| 17 | B6_residual_L5eq3 | 8 | `B6_residual_L5eq3__p1_9__p6_8` | 154.493 | 74656 |
| 18 | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_3` | 52.317 | 72744 |
| 19 | A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_4` | 282.366 | 74276 |
| 20 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_2__p6_3` | 488.567 | 72668 |
| 21 | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_4` | 349.191 | 72348 |
| 22 | A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_5` | 393.439 | 74296 |
| 23 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_2__p6_7` | 546.709 | 72580 |
| 24 | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_5` | 591.120 | 72344 |
| 26 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_2__p6_8` | 579.738 | 72608 |
| 28 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_2__p6_9` | 501.004 | 72604 |
| 29 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_3__p6_2` | 150.773 | 72536 |
| 30 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_3__p6_7` | 298.075 | 72448 |
| 31 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_3__p6_8` | 285.364 | 72472 |
| 32 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_3__p6_9` | 248.545 | 72464 |
| 33 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_4__p6_5` | 27.820 | 74596 |
| 34 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_4__p6_7` | 128.040 | 74624 |
| 35 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_4__p6_8` | 124.262 | 74628 |
| 36 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_4__p6_9` | 89.979 | 74628 |
| 37 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_5__p6_4` | 25.332 | 74596 |
| 38 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_5__p6_7` | 156.028 | 74600 |
| 39 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_5__p6_8` | 130.604 | 74628 |
| 40 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_5__p6_9` | 172.423 | 74628 |
| 41 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_7__p6_2` | 346.281 | 74700 |
| 42 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_7__p6_3` | 173.673 | 74688 |
| 43 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_7__p6_4` | 109.028 | 74624 |
| 44 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_7__p6_5` | 136.888 | 74624 |
| 45 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_8__p6_2` | 298.025 | 74692 |
| 46 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_8__p6_3` | 115.268 | 74696 |
| 47 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_8__p6_4` | 103.921 | 74632 |
| 48 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_8__p6_5` | 124.213 | 74624 |
| 49 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_9__p6_2` | 253.561 | 74704 |
| 50 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_9__p6_3` | 161.050 | 74708 |
| 51 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_9__p6_4` | 100.095 | 74640 |
| 52 | B6_residual_L5eq3 | 9 | `B6_residual_L5eq3__p1_9__p6_5` | 144.596 | 74636 |
| 55 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_3__p6_4` | 430.546 | 72444 |
| 57 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_4__p6_2` | 210.592 | 74688 |
| 58 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_4__p6_3` | 125.646 | 74672 |
| 59 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_5__p6_2` | 246.116 | 74684 |
| 60 | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_5__p6_3` | 101.532 | 74676 |
| 68 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_3` | 441.508 | 72692 |
| 69 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_4` | 388.778 | 72628 |
| 73 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_4__p6_0` | 243.294 | 72004 |
| 74 | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_5__p6_0` | 297.829 | 71980 |

## Timeout Branches

Ranked by parent family, census matching count, choices/sec, conflicts/sec, and restarts/sec when available; blank rate fields mean the ranking metric is unavailable for that branch.

| parent | census | branch | runtime s | choices/s | conflicts/s | restarts/s |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_9` | 601.175 | 464.245 | 409.141 | 1.060 |
| A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_6` | 601.095 | 604.259 | 540.810 | 1.427 |
| A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_8` | 601.148 | 606.679 | 539.584 | 1.474 |
| A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_7` | 601.122 | 710.142 | 633.813 | 1.700 |
| A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_3` | 601.214 | 682.488 | 604.088 | 1.695 |
| A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_2` | 601.201 | 715.376 | 634.086 | 1.698 |
| A5_residual_L5eq3 | 336 | `A5_residual_L5eq3__wire1_unused` | 601.251 | 719.072 | 634.475 | 1.698 |
| B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_2__p6_4` | 601.231 | 516.302 | 463.050 | 1.176 |
| B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_3__p6_5` | 600.400 | 562.930 | 508.548 | 1.374 |
| B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_2__p6_5` | 600.690 | 710.258 | 635.300 | 1.700 |
| B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_7` | 600.519 | 538.496 | 478.528 | 1.274 |
| B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_7__p6_0` | 600.283 | 572.032 | 509.503 | 1.293 |
| B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_9` | 600.797 | 635.457 | 567.100 | 1.693 |
| B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_8` | 600.240 | 642.051 | 572.865 | 1.634 |
| B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_8__p6_0` | 600.983 | 652.616 | 583.486 | 1.626 |
| B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_9__p6_0` | 600.991 | 737.009 | 661.423 | 1.697 |
| B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_5` | 601.021 | 536.938 | 481.697 | 1.271 |
| B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_2` | 600.159 | 673.040 | 598.994 | 1.698 |
| B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_3__p6_0` | 600.090 | 777.833 | 693.836 | 1.703 |
| B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_2__p6_0` | 600.785 | 903.213 | 806.972 | 1.912 |
| B6_residual_L5eq3 | 78 | `B6_residual_L5eq3__p1_0__p6_0` | 600.049 | 1255.650 | 1127.417 | 2.806 |
| B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_8` | 601.135 | 586.843 | 512.970 | 1.402 |
| B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_9` | 601.161 | 638.380 | 555.359 | 1.454 |
| B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_7` | 601.108 | 654.619 | 573.040 | 1.589 |
| B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_6` | 600.146 | 630.552 | 550.540 | 1.486 |
| B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_1` | 601.188 | 703.035 | 618.631 | 1.697 |

## Coverage Accounting

| category | count |
| --- | ---: |
| prior closed branches | 0 |
| new screening UNSAT branches | 49 |
| remaining timed-out branches | 26 |

## Final Recommendation

run a longer wave on specifically named timeout branches: `A5_residual_L5eq3__wire1_partner_9`, `A5_residual_L5eq3__wire1_partner_6`, `A5_residual_L5eq3__wire1_partner_8`, `A5_residual_L5eq3__wire1_partner_7`, `A5_residual_L5eq3__wire1_partner_3`, `A5_residual_L5eq3__wire1_partner_2`, `A5_residual_L5eq3__wire1_unused`, `B6_residual_L5eq3__p1_2__p6_4`, `B6_residual_L5eq3__p1_3__p6_5`, `B6_residual_L5eq3__p1_2__p6_5`.

## Stop State

Stop reason: `completed_all_jobs`.
