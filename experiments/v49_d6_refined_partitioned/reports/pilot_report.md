# V(4,9), Depth-6 Refined Support/Size Pilot Report

This report records branch results only. TIMEOUT rows are not UNSAT evidence, and this report does not make a final exactness claim automatically.

## Branch Definitions

| branch | T(L6) | |L6| | exact constraints |
| --- | --- | ---: | --- |
| T_234_L6_2 | (2, 3, 4) | 2 | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 2 != #count { I,J : selected(D,I,J) }.` |
| T_234_L6_3 | (2, 3, 4) | 3 | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.` |
| T_1234_L6_2 | (1, 2, 3, 4) | 2 | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 2 != #count { I,J : selected(D,I,J) }.` |
| T_1234_L6_3 | (1, 2, 3, 4) | 3 | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.` |
| T_1234_L6_4 | (1, 2, 3, 4) | 4 | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 4 != #count { I,J : selected(D,I,J) }.` |

## Completeness And Disjointness

The previous support-partitioned pilot completed every support class except T(L6)=(2,3,4) and T(L6)=(1,2,3,4). This refined run partitions exactly those two surviving classes.

For T=(2,3,4), a matching that touches exactly those three output wires and contains no suffix-only comparator has size 2 or 3. Size 1 cannot touch three distinct output wires, and size 4 would need four non-suffix comparators touching only three matched output wires, impossible in a matching.

For T=(1,2,3,4), the corresponding size is 2, 3, or 4. Size 1 cannot touch four distinct output wires, and size 4 is the maximum because every non-suffix final comparator must be incident to at least one of the four output wires in a matching.

The five branches are pairwise disjoint because each branch fixes the exact pair (T(L6), |L6|); two different supports or two different final-layer sizes cannot hold for the same final layer.

If all five refined branches are UNSAT and the prior thirteen support-pilot UNSAT artifacts are present and verified, then the full depth-6 hard-instance space is UNSAT. If any refined branch is SAT and independently verified, then V(4,9) has a depth-6 witness.

## New Refined Branch Results

| branch | status | runtime seconds | peak RSS KB | CPU snapshots | statistics summary | verifier |
| --- | --- | ---: | ---: | ---: | --- | --- |
| T_234_L6_2 | TIMEOUT | 1800.334 | 83656 | 1734 | stats captured |  |
| T_234_L6_3 | UNSAT | 454.726 | 81316 | 430 | stats captured |  |
| T_1234_L6_2 | UNSAT | 1227.722 | 81856 | 1175 | stats captured |  |
| T_1234_L6_3 | TIMEOUT | 1800.340 | 85952 | 1734 | stats captured |  |
| T_1234_L6_4 | UNSAT | 749.135 | 84024 | 711 | stats captured |  |

## SAT Witnesses

None.

## Combined Support Table

| source | branch | support | |L6| | status | artifact |
| --- | --- | --- | ---: | --- | --- |
| prior support pilot | T_1 | (1,) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_1/parsed_status.json |
| prior support pilot | T_2 | (2,) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_2/parsed_status.json |
| prior support pilot | T_3 | (3,) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_3/parsed_status.json |
| prior support pilot | T_4 | (4,) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_4/parsed_status.json |
| prior support pilot | T_12 | (1, 2) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_12/parsed_status.json |
| prior support pilot | T_13 | (1, 3) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_13/parsed_status.json |
| prior support pilot | T_14 | (1, 4) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_14/parsed_status.json |
| prior support pilot | T_23 | (2, 3) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_23/parsed_status.json |
| prior support pilot | T_24 | (2, 4) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_24/parsed_status.json |
| prior support pilot | T_34 | (3, 4) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_34/parsed_status.json |
| prior support pilot | T_123 | (1, 2, 3) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_123/parsed_status.json |
| prior support pilot | T_124 | (1, 2, 4) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_124/parsed_status.json |
| prior support pilot | T_134 | (1, 3, 4) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_134/parsed_status.json |
| refined pilot | T_234_L6_2 | (2, 3, 4) | 2 | TIMEOUT | /home/ono/Codex/experiments/v49_d6_refined_partitioned/branches/T_234_L6_2/parsed_status.json |
| refined pilot | T_234_L6_3 | (2, 3, 4) | 3 | UNSAT | /home/ono/Codex/experiments/v49_d6_refined_partitioned/branches/T_234_L6_3/parsed_status.json |
| refined pilot | T_1234_L6_2 | (1, 2, 3, 4) | 2 | UNSAT | /home/ono/Codex/experiments/v49_d6_refined_partitioned/branches/T_1234_L6_2/parsed_status.json |
| refined pilot | T_1234_L6_3 | (1, 2, 3, 4) | 3 | TIMEOUT | /home/ono/Codex/experiments/v49_d6_refined_partitioned/branches/T_1234_L6_3/parsed_status.json |
| refined pilot | T_1234_L6_4 | (1, 2, 3, 4) | 4 | UNSAT | /home/ono/Codex/experiments/v49_d6_refined_partitioned/branches/T_1234_L6_4/parsed_status.json |

## Conclusion

INCONCLUSIVE_REMAINING_BRANCHES

## Recommendation

split one named remaining branch by the exact comparator incident to output wire 4: T_1234_L6_3
