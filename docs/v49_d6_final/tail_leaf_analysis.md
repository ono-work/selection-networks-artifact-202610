# V(4,9) Depth-6 Tail Leaf Analysis

Analysis status: `PASSED`

This report organizes the 75 constrained tail leaves used on the depth-6 side of the final `VDepth(4,9)=7` certificate. Solver UNSAT is used only as a computational result for the corresponding constrained ASP instance; no human-readable UNSAT reason or unsat core is claimed.

The `terminal_profile` column records the `leaf_id` present in each existing `branch_definition.json`; this report does not infer additional meaning from that name.

## Coverage Checks

| check | value |
| --- | --- |
| leaf count | 75 |
| screening leaves | 49 |
| overnight leaves | 26 |
| parent leaf counts | {"A5_residual_L5eq3": 9, "B6_residual_L5eq3": 57, "B6_residual_L5eq4": 9} |
| problems | none |

## A. A5_residual_L5eq3

Under the recorded A5 residual condition, each listed category was closed by an existing raw UNSAT solver artifact. This statement is category-local and is not asserted as a general necessary condition.

| category | census matching count | closure phase | runtime | solver result |
| --- | --- | --- | --- | --- |
| wire1_partner_2 | 95 | OVERNIGHT | 3811.514 | UNSATISFIABLE |
| wire1_partner_3 | 95 | OVERNIGHT | 1881.370 | UNSATISFIABLE |
| wire1_partner_4 | 95 | SCREENING | 282.366 | UNSATISFIABLE |
| wire1_partner_5 | 95 | SCREENING | 393.439 | UNSATISFIABLE |
| wire1_partner_6 | 86 | OVERNIGHT | 1327.140 | UNSATISFIABLE |
| wire1_partner_7 | 86 | OVERNIGHT | 1522.434 | UNSATISFIABLE |
| wire1_partner_8 | 86 | OVERNIGHT | 1507.309 | UNSATISFIABLE |
| wire1_partner_9 | 86 | OVERNIGHT | 1117.495 | UNSATISFIABLE |
| wire1_unused | 336 | OVERNIGHT | 2046.948 | UNSATISFIABLE |

## B. B6_residual_L5eq3

Rows are `p1`; columns are `p6`. A cell marked `INFEASIBLE_BY_CENSUS` is absent from the census categories and is distinct from solver UNSAT.

| p1 \ p6 | 0 | 2 | 3 | 4 | 5 | 7 | 8 | 9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | UNSAT; count=78; OVERNIGHT; 1659.744s | UNSAT; count=39; OVERNIGHT; 1323.377s | UNSAT; count=39; SCREENING; 441.508s | UNSAT; count=39; SCREENING; 388.778s | UNSAT; count=39; OVERNIGHT; 637.174s | UNSAT; count=34; OVERNIGHT; 1546.530s | UNSAT; count=34; OVERNIGHT; 1174.898s | UNSAT; count=34; OVERNIGHT; 1843.973s |
| 2 | UNSAT; count=39; OVERNIGHT; 3139.494s | INFEASIBLE_BY_CENSUS | UNSAT; count=9; SCREENING; 488.567s | UNSAT; count=10; OVERNIGHT; 830.348s | UNSAT; count=10; OVERNIGHT; 2989.595s | UNSAT; count=9; SCREENING; 546.709s | UNSAT; count=9; SCREENING; 579.738s | UNSAT; count=9; SCREENING; 501.004s |
| 3 | UNSAT; count=39; OVERNIGHT; 1092.768s | UNSAT; count=9; SCREENING; 150.773s | INFEASIBLE_BY_CENSUS | UNSAT; count=10; SCREENING; 430.546s | UNSAT; count=10; OVERNIGHT; 822.877s | UNSAT; count=9; SCREENING; 298.075s | UNSAT; count=9; SCREENING; 285.364s | UNSAT; count=9; SCREENING; 248.545s |
| 4 | UNSAT; count=39; SCREENING; 243.294s | UNSAT; count=10; SCREENING; 210.592s | UNSAT; count=10; SCREENING; 125.646s | INFEASIBLE_BY_CENSUS | UNSAT; count=9; SCREENING; 27.820s | UNSAT; count=9; SCREENING; 128.040s | UNSAT; count=9; SCREENING; 124.262s | UNSAT; count=9; SCREENING; 89.979s |
| 5 | UNSAT; count=39; SCREENING; 297.829s | UNSAT; count=10; SCREENING; 246.116s | UNSAT; count=10; SCREENING; 101.532s | UNSAT; count=9; SCREENING; 25.332s | INFEASIBLE_BY_CENSUS | UNSAT; count=9; SCREENING; 156.028s | UNSAT; count=9; SCREENING; 130.604s | UNSAT; count=9; SCREENING; 172.423s |
| 7 | UNSAT; count=34; OVERNIGHT; 1278.782s | UNSAT; count=9; SCREENING; 346.281s | UNSAT; count=9; SCREENING; 173.673s | UNSAT; count=9; SCREENING; 109.028s | UNSAT; count=9; SCREENING; 136.888s | INFEASIBLE_BY_CENSUS | UNSAT; count=8; SCREENING; 174.687s | UNSAT; count=8; SCREENING; 195.046s |
| 8 | UNSAT; count=34; OVERNIGHT; 1021.014s | UNSAT; count=9; SCREENING; 298.025s | UNSAT; count=9; SCREENING; 115.268s | UNSAT; count=9; SCREENING; 103.921s | UNSAT; count=9; SCREENING; 124.213s | UNSAT; count=8; SCREENING; 182.425s | INFEASIBLE_BY_CENSUS | UNSAT; count=8; SCREENING; 131.479s |
| 9 | UNSAT; count=34; OVERNIGHT; 1021.897s | UNSAT; count=9; SCREENING; 253.561s | UNSAT; count=9; SCREENING; 161.050s | UNSAT; count=9; SCREENING; 100.095s | UNSAT; count=9; SCREENING; 144.596s | UNSAT; count=8; SCREENING; 186.281s | UNSAT; count=8; SCREENING; 154.493s | INFEASIBLE_BY_CENSUS |

Endpoint usage summary:

| endpoint_usage_class | leaf count | census matching count total | runtime total |
| --- | --- | --- | --- |
| BOTH_UNUSED | 1 | 78 | 1659.744 |
| BOTH_USED | 42 | 380 | 12801.526 |
| ONLY_1_USED | 7 | 258 | 8095.078 |
| ONLY_6_USED | 7 | 258 | 7356.239 |

## C. B6_residual_L5eq4

| unused wire | census matching count | closure phase | runtime | solver result |
| --- | --- | --- | --- | --- |
| 1 | 78 | OVERNIGHT | 2661.352 | UNSATISFIABLE |
| 2 | 78 | SCREENING | 126.447 | UNSATISFIABLE |
| 3 | 78 | SCREENING | 52.317 | UNSATISFIABLE |
| 4 | 78 | SCREENING | 349.191 | UNSATISFIABLE |
| 5 | 78 | SCREENING | 591.120 | UNSATISFIABLE |
| 6 | 78 | OVERNIGHT | 4387.050 | UNSATISFIABLE |
| 7 | 68 | OVERNIGHT | 6210.805 | UNSATISFIABLE |
| 8 | 68 | OVERNIGHT | 6512.609 | UNSATISFIABLE |
| 9 | 68 | OVERNIGHT | 4633.946 | UNSATISFIABLE |

The wire 1--4 and wire 5--9 grouping below is only a display grouping, not a symmetry claim.

| display group | leaf count | census matching count total | runtime total |
| --- | --- | --- | --- |
| OUTPUT_1_TO_4 | 4 | 312 | 3189.307 |
| OTHER_5_TO_9 | 5 | 360 | 22335.529 |

## Closure Ledger

This ledger separates mathematical reduction and derived coverage from solver-leaf closure.

| node_id | parent_node_id | condition | child count | L5 count | method | status |
| --- | --- | --- | --- | --- | --- | --- |
| DEPTH6_CANDIDATE_SPACE |  | V(4,9), depth 6 candidate space before final reductions | 1 |  | MATHEMATICAL_REDUCTION | VERIFIED |
| CLOSURE_TERMINAL_PROFILE_REDUCTION | DEPTH6_CANDIDATE_SPACE | closure certificate status COVERAGE_AUDIT_PASSED; residual cases retained | 3 |  | DERIVED_COVERAGE | VERIFIED |
| A5_residual_L5eq3 | CLOSURE_TERMINAL_PROFILE_REDUCTION | residual parent A5_residual_L5eq3; pairwise_disjoint=True; union_covers_parent=True | 9 | 1060 | EXHAUSTIVE_CENSUS | VERIFIED |
| A5_residual_L5eq3__wire1_partner_2 | A5_residual_L5eq3 | wire1_partner_2 | 0 | 95 | SOLVER_UNSAT | UNSATISFIABLE |
| A5_residual_L5eq3__wire1_partner_3 | A5_residual_L5eq3 | wire1_partner_3 | 0 | 95 | SOLVER_UNSAT | UNSATISFIABLE |
| A5_residual_L5eq3__wire1_partner_4 | A5_residual_L5eq3 | wire1_partner_4 | 0 | 95 | SOLVER_UNSAT | UNSATISFIABLE |
| A5_residual_L5eq3__wire1_partner_5 | A5_residual_L5eq3 | wire1_partner_5 | 0 | 95 | SOLVER_UNSAT | UNSATISFIABLE |
| A5_residual_L5eq3__wire1_partner_6 | A5_residual_L5eq3 | wire1_partner_6 | 0 | 86 | SOLVER_UNSAT | UNSATISFIABLE |
| A5_residual_L5eq3__wire1_partner_7 | A5_residual_L5eq3 | wire1_partner_7 | 0 | 86 | SOLVER_UNSAT | UNSATISFIABLE |
| A5_residual_L5eq3__wire1_partner_8 | A5_residual_L5eq3 | wire1_partner_8 | 0 | 86 | SOLVER_UNSAT | UNSATISFIABLE |
| A5_residual_L5eq3__wire1_partner_9 | A5_residual_L5eq3 | wire1_partner_9 | 0 | 86 | SOLVER_UNSAT | UNSATISFIABLE |
| A5_residual_L5eq3__wire1_unused | A5_residual_L5eq3 | wire1_unused | 0 | 336 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3 | CLOSURE_TERMINAL_PROFILE_REDUCTION | residual parent B6_residual_L5eq3; pairwise_disjoint=True; union_covers_parent=True | 57 | 974 | EXHAUSTIVE_CENSUS | VERIFIED |
| B6_residual_L5eq3__p1_0__p6_0 | B6_residual_L5eq3 | p1_0__p6_0 | 0 | 78 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_0__p6_2 | B6_residual_L5eq3 | p1_0__p6_2 | 0 | 39 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_0__p6_3 | B6_residual_L5eq3 | p1_0__p6_3 | 0 | 39 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_0__p6_4 | B6_residual_L5eq3 | p1_0__p6_4 | 0 | 39 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_0__p6_5 | B6_residual_L5eq3 | p1_0__p6_5 | 0 | 39 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_0__p6_7 | B6_residual_L5eq3 | p1_0__p6_7 | 0 | 34 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_0__p6_8 | B6_residual_L5eq3 | p1_0__p6_8 | 0 | 34 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_0__p6_9 | B6_residual_L5eq3 | p1_0__p6_9 | 0 | 34 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_2__p6_0 | B6_residual_L5eq3 | p1_2__p6_0 | 0 | 39 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_2__p6_3 | B6_residual_L5eq3 | p1_2__p6_3 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_2__p6_4 | B6_residual_L5eq3 | p1_2__p6_4 | 0 | 10 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_2__p6_5 | B6_residual_L5eq3 | p1_2__p6_5 | 0 | 10 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_2__p6_7 | B6_residual_L5eq3 | p1_2__p6_7 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_2__p6_8 | B6_residual_L5eq3 | p1_2__p6_8 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_2__p6_9 | B6_residual_L5eq3 | p1_2__p6_9 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_3__p6_0 | B6_residual_L5eq3 | p1_3__p6_0 | 0 | 39 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_3__p6_2 | B6_residual_L5eq3 | p1_3__p6_2 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_3__p6_4 | B6_residual_L5eq3 | p1_3__p6_4 | 0 | 10 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_3__p6_5 | B6_residual_L5eq3 | p1_3__p6_5 | 0 | 10 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_3__p6_7 | B6_residual_L5eq3 | p1_3__p6_7 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_3__p6_8 | B6_residual_L5eq3 | p1_3__p6_8 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_3__p6_9 | B6_residual_L5eq3 | p1_3__p6_9 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_4__p6_0 | B6_residual_L5eq3 | p1_4__p6_0 | 0 | 39 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_4__p6_2 | B6_residual_L5eq3 | p1_4__p6_2 | 0 | 10 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_4__p6_3 | B6_residual_L5eq3 | p1_4__p6_3 | 0 | 10 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_4__p6_5 | B6_residual_L5eq3 | p1_4__p6_5 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_4__p6_7 | B6_residual_L5eq3 | p1_4__p6_7 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_4__p6_8 | B6_residual_L5eq3 | p1_4__p6_8 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_4__p6_9 | B6_residual_L5eq3 | p1_4__p6_9 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_5__p6_0 | B6_residual_L5eq3 | p1_5__p6_0 | 0 | 39 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_5__p6_2 | B6_residual_L5eq3 | p1_5__p6_2 | 0 | 10 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_5__p6_3 | B6_residual_L5eq3 | p1_5__p6_3 | 0 | 10 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_5__p6_4 | B6_residual_L5eq3 | p1_5__p6_4 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_5__p6_7 | B6_residual_L5eq3 | p1_5__p6_7 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_5__p6_8 | B6_residual_L5eq3 | p1_5__p6_8 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_5__p6_9 | B6_residual_L5eq3 | p1_5__p6_9 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_7__p6_0 | B6_residual_L5eq3 | p1_7__p6_0 | 0 | 34 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_7__p6_2 | B6_residual_L5eq3 | p1_7__p6_2 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_7__p6_3 | B6_residual_L5eq3 | p1_7__p6_3 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_7__p6_4 | B6_residual_L5eq3 | p1_7__p6_4 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_7__p6_5 | B6_residual_L5eq3 | p1_7__p6_5 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_7__p6_8 | B6_residual_L5eq3 | p1_7__p6_8 | 0 | 8 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_7__p6_9 | B6_residual_L5eq3 | p1_7__p6_9 | 0 | 8 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_8__p6_0 | B6_residual_L5eq3 | p1_8__p6_0 | 0 | 34 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_8__p6_2 | B6_residual_L5eq3 | p1_8__p6_2 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_8__p6_3 | B6_residual_L5eq3 | p1_8__p6_3 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_8__p6_4 | B6_residual_L5eq3 | p1_8__p6_4 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_8__p6_5 | B6_residual_L5eq3 | p1_8__p6_5 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_8__p6_7 | B6_residual_L5eq3 | p1_8__p6_7 | 0 | 8 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_8__p6_9 | B6_residual_L5eq3 | p1_8__p6_9 | 0 | 8 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_9__p6_0 | B6_residual_L5eq3 | p1_9__p6_0 | 0 | 34 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_9__p6_2 | B6_residual_L5eq3 | p1_9__p6_2 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_9__p6_3 | B6_residual_L5eq3 | p1_9__p6_3 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_9__p6_4 | B6_residual_L5eq3 | p1_9__p6_4 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_9__p6_5 | B6_residual_L5eq3 | p1_9__p6_5 | 0 | 9 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_9__p6_7 | B6_residual_L5eq3 | p1_9__p6_7 | 0 | 8 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq3__p1_9__p6_8 | B6_residual_L5eq3 | p1_9__p6_8 | 0 | 8 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq4 | CLOSURE_TERMINAL_PROFILE_REDUCTION | residual parent B6_residual_L5eq4; pairwise_disjoint=True; union_covers_parent=True | 9 | 672 | EXHAUSTIVE_CENSUS | VERIFIED |
| B6_residual_L5eq4__unused_wire_1 | B6_residual_L5eq4 | unused_wire_1 | 0 | 78 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq4__unused_wire_2 | B6_residual_L5eq4 | unused_wire_2 | 0 | 78 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq4__unused_wire_3 | B6_residual_L5eq4 | unused_wire_3 | 0 | 78 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq4__unused_wire_4 | B6_residual_L5eq4 | unused_wire_4 | 0 | 78 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq4__unused_wire_5 | B6_residual_L5eq4 | unused_wire_5 | 0 | 78 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq4__unused_wire_6 | B6_residual_L5eq4 | unused_wire_6 | 0 | 78 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq4__unused_wire_7 | B6_residual_L5eq4 | unused_wire_7 | 0 | 68 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq4__unused_wire_8 | B6_residual_L5eq4 | unused_wire_8 | 0 | 68 | SOLVER_UNSAT | UNSATISFIABLE |
| B6_residual_L5eq4__unused_wire_9 | B6_residual_L5eq4 | unused_wire_9 | 0 | 68 | SOLVER_UNSAT | UNSATISFIABLE |
| V4_9_DEPTH6_UNSAT | TAIL_CHILDREN_75_UNSAT | derived from audited residual coverage and all 75 constrained tail leaves with raw UNSAT | 75 | 2706 | DERIVED_COVERAGE | VERIFIED |

## Operational observations

Runtime, memory, and solver statistics are operational observations only. They are not used here as mathematical evidence for why a leaf is UNSAT.

| section | group | leaf count | census total | runtime total | runtime median | runtime maximum | peak RSS maximum | Pearson | Spearman | CPU-seconds approx |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| parent_family | A5_residual_L5eq3 | 9 | 1060 | 13890.014 | 1507.309 | 3811.514 | 77060 |  |  |  |
| parent_family | B6_residual_L5eq3 | 57 | 974 | 29912.587 | 246.116 | 3139.494 | 74708 |  |  |  |
| parent_family | B6_residual_L5eq4 | 9 | 672 | 25524.836 | 2661.352 | 6512.609 | 82336 |  |  |  |
| closure_phase | SCREENING | 49 | 1008 | 11324.993 | 174.687 | 591.120 | 74708 |  |  |  |
| closure_phase | OVERNIGHT | 26 | 1698 | 58002.444 | 1534.482 | 6512.609 | 82336 |  |  |  |
| all | all_leaves | 75 | 2706 | 69327.437 | 298.075 | 6512.609 | 82336 |  |  | 69327.437 |
| correlation | all_leaves | 75 | 2706.0 | 69327.437 | 298.075 | 6512.609 | 82336 | 0.407 | 0.636 |  |

## Mathematically certified structure

The recorded structure certifies the closure/terminal-profile reduction to the three residual parents, the exhaustive and pairwise-disjoint tail census categories under each parent, and the coverage chain recorded in the dependency graph.

## Computationally certified closure

For each of the 75 tail categories, this analysis directly parsed the existing raw solver JSON selected by the final certificate path and confirmed `Result=UNSATISFIABLE`.

## Operational observations

The screening/overnight split, runtime summaries, peak RSS values, and solver statistics are reported only as run metadata. They are not interpreted as structural causes of UNSAT or as general laws about the search space.
