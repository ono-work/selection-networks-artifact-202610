# V(4,9), Depth-6 Tail Overnight Plan

Exact command: `./scripts/run_v49_d6_tail_partitioned.sh --mode overnight --enable-topology-pruning --output-dir /home/ono/Codex/experiments/v49_d6_tail_partitioned`

Configuration: topology pruning enabled; 18 outer workers; one clingo thread per branch; no internal clingo parallel mode; 14,400 second per-branch timeout; no GPU use; fixed seed recorded in metadata.

Worker calculation: host logical CPUs 20; reserved logical CPUs 2; outer workers 18.

Selection: excluded 49 screening UNSAT branches and selected 26 screening TIMEOUT branches.

| queue | workload class | parent | census | branch |
| ---: | --- | --- | ---: | --- |
| 1 | A5_near | A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_2` |
| 2 | A5_tail | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_6` |
| 3 | A5_unused | A5_residual_L5eq3 | 336 | `A5_residual_L5eq3__wire1_unused` |
| 4 | B6eq3_both_used | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_2__p6_4` |
| 5 | B6eq3_one_idle_near | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_2` |
| 6 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_7` |
| 7 | B6eq3_both_idle | B6_residual_L5eq3 | 78 | `B6_residual_L5eq3__p1_0__p6_0` |
| 8 | B6eq4_unused_final_endpoint | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_1` |
| 9 | B6eq4_unused_tail | B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_7` |
| 10 | A5_near | A5_residual_L5eq3 | 95 | `A5_residual_L5eq3__wire1_partner_3` |
| 11 | A5_tail | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_7` |
| 12 | B6eq3_both_used | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_2__p6_5` |
| 13 | B6eq3_one_idle_near | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_0__p6_5` |
| 14 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_8` |
| 15 | B6eq4_unused_final_endpoint | B6_residual_L5eq4 | 78 | `B6_residual_L5eq4__unused_wire_6` |
| 16 | B6eq4_unused_tail | B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_8` |
| 17 | A5_tail | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_8` |
| 18 | B6eq3_both_used | B6_residual_L5eq3 | 10 | `B6_residual_L5eq3__p1_3__p6_5` |
| 19 | B6eq3_one_idle_near | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_2__p6_0` |
| 20 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_0__p6_9` |
| 21 | B6eq4_unused_tail | B6_residual_L5eq4 | 68 | `B6_residual_L5eq4__unused_wire_9` |
| 22 | A5_tail | A5_residual_L5eq3 | 86 | `A5_residual_L5eq3__wire1_partner_9` |
| 23 | B6eq3_one_idle_near | B6_residual_L5eq3 | 39 | `B6_residual_L5eq3__p1_3__p6_0` |
| 24 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_7__p6_0` |
| 25 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_8__p6_0` |
| 26 | B6eq3_one_idle_tail | B6_residual_L5eq3 | 34 | `B6_residual_L5eq3__p1_9__p6_0` |
