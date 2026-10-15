# V(4,9), Depth-6 Partner-Partitioned Pilot Report

This report records branch results only. TIMEOUT rows are not UNSAT evidence.

Actual worker count: 8.

## Proof Summary

The only unresolved refined parents are A: T(L6)=(2,3,4), |L6|=2 and B: T(L6)=(1,2,3,4), |L6|=3.

In every final layer, the selected comparators form a matching, so wire 4 has at most one final-layer partner. Parent constraints require wire 4 to be touched, so partitioning by the exact comparator incident to wire 4 is complete and pairwise disjoint.

For parent A, partner 1 is excluded because it would touch output wire 1, contradicting T(L6)=(2,3,4). The complete possible partners are 2,3,5,6,7,8,9. For parent B, the complete possible partners are 1,2,3,5,6,7,8,9. No suffix-wire permutation symmetry is used.

## Child Branch Definitions

| branch | parent | T(L6) | |L6| | final comparator | exact constraints |
| --- | --- | --- | ---: | --- | --- |
| A_p2 | A | (2, 3, 4) | 2 | (2, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 2 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,2,4).` |
| A_p3 | A | (2, 3, 4) | 2 | (3, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 2 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,3,4).` |
| A_p5 | A | (2, 3, 4) | 2 | (4, 5) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 2 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).` |
| A_p6 | A | (2, 3, 4) | 2 | (4, 6) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 2 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,6).` |
| A_p7 | A | (2, 3, 4) | 2 | (4, 7) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 2 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,7).` |
| A_p8 | A | (2, 3, 4) | 2 | (4, 8) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 2 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,8).` |
| A_p9 | A | (2, 3, 4) | 2 | (4, 9) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 2 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,9).` |
| B_p1 | B | (1, 2, 3, 4) | 3 | (1, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,1,4).` |
| B_p2 | B | (1, 2, 3, 4) | 3 | (2, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,2,4).` |
| B_p3 | B | (1, 2, 3, 4) | 3 | (3, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,3,4).` |
| B_p5 | B | (1, 2, 3, 4) | 3 | (4, 5) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).` |
| B_p6 | B | (1, 2, 3, 4) | 3 | (4, 6) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,6).` |
| B_p7 | B | (1, 2, 3, 4) | 3 | (4, 7) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,7).` |
| B_p8 | B | (1, 2, 3, 4) | 3 | (4, 8) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,8).` |
| B_p9 | B | (1, 2, 3, 4) | 3 | (4, 9) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,9).` |

## Child Branch Results

| branch | status | runtime seconds | peak RSS KB | CPU snapshots | statistics summary | verifier |
| --- | --- | ---: | ---: | ---: | --- | --- |
| A_p2 | UNSAT | 33.983 | 75732 | 31 | stats captured |  |
| A_p3 | UNSAT | 603.019 | 75532 | 548 | stats captured |  |
| A_p5 | TIMEOUT | 1200.742 | 78844 | 1103 | stats captured |  |
| A_p6 | TIMEOUT | 1200.750 | 78768 | 1103 | stats captured |  |
| A_p7 | UNSAT | 1155.739 | 78888 | 1060 | stats captured |  |
| A_p8 | UNSAT | 215.841 | 77196 | 196 | stats captured |  |
| A_p9 | UNSAT | 618.399 | 77204 | 562 | stats captured |  |
| B_p1 | UNSAT | 52.886 | 77380 | 48 | stats captured |  |
| B_p2 | UNSAT | 32.044 | 77112 | 29 | stats captured |  |
| B_p3 | UNSAT | 442.480 | 76932 | 402 | stats captured |  |
| B_p5 | TIMEOUT | 1200.924 | 81088 | 1108 | stats captured |  |
| B_p6 | UNSAT | 1067.358 | 80328 | 988 | stats captured |  |
| B_p7 | UNSAT | 609.437 | 78944 | 562 | stats captured |  |
| B_p8 | UNSAT | 169.477 | 78232 | 154 | stats captured |  |
| B_p9 | UNSAT | 150.855 | 78232 | 137 | stats captured |  |

## SAT Witnesses

None.

## Combined Branch Table

| source | branch | support | |L6| | status | artifact |
| --- | --- | --- | ---: | --- | --- |
| 13 completed UNSAT support branches | T_1 | (1,) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_1/parsed_status.json |
| 13 completed UNSAT support branches | T_2 | (2,) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_2/parsed_status.json |
| 13 completed UNSAT support branches | T_3 | (3,) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_3/parsed_status.json |
| 13 completed UNSAT support branches | T_4 | (4,) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_4/parsed_status.json |
| 13 completed UNSAT support branches | T_12 | (1, 2) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_12/parsed_status.json |
| 13 completed UNSAT support branches | T_13 | (1, 3) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_13/parsed_status.json |
| 13 completed UNSAT support branches | T_14 | (1, 4) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_14/parsed_status.json |
| 13 completed UNSAT support branches | T_23 | (2, 3) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_23/parsed_status.json |
| 13 completed UNSAT support branches | T_24 | (2, 4) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_24/parsed_status.json |
| 13 completed UNSAT support branches | T_34 | (3, 4) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_34/parsed_status.json |
| 13 completed UNSAT support branches | T_123 | (1, 2, 3) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_123/parsed_status.json |
| 13 completed UNSAT support branches | T_124 | (1, 2, 4) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_124/parsed_status.json |
| 13 completed UNSAT support branches | T_134 | (1, 3, 4) |  | UNSAT | /home/ono/Codex/experiments/v49_d6_support_partitioned/branches/T_134/parsed_status.json |
| 3 completed UNSAT refined branches | T_234_L6_3 | (2, 3, 4) | 3 | UNSAT | /home/ono/Codex/experiments/v49_d6_refined_partitioned/branches/T_234_L6_3/parsed_status.json |
| 3 completed UNSAT refined branches | T_1234_L6_2 | (1, 2, 3, 4) | 2 | UNSAT | /home/ono/Codex/experiments/v49_d6_refined_partitioned/branches/T_1234_L6_2/parsed_status.json |
| 3 completed UNSAT refined branches | T_1234_L6_4 | (1, 2, 3, 4) | 4 | UNSAT | /home/ono/Codex/experiments/v49_d6_refined_partitioned/branches/T_1234_L6_4/parsed_status.json |
| partner pilot | A_p2 | (2, 3, 4) | 2 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/A_p2/parsed_status.json |
| partner pilot | A_p3 | (2, 3, 4) | 2 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/A_p3/parsed_status.json |
| partner pilot | A_p5 | (2, 3, 4) | 2 | TIMEOUT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/A_p5/parsed_status.json |
| partner pilot | A_p6 | (2, 3, 4) | 2 | TIMEOUT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/A_p6/parsed_status.json |
| partner pilot | A_p7 | (2, 3, 4) | 2 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/A_p7/parsed_status.json |
| partner pilot | A_p8 | (2, 3, 4) | 2 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/A_p8/parsed_status.json |
| partner pilot | A_p9 | (2, 3, 4) | 2 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/A_p9/parsed_status.json |
| partner pilot | B_p1 | (1, 2, 3, 4) | 3 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/B_p1/parsed_status.json |
| partner pilot | B_p2 | (1, 2, 3, 4) | 3 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/B_p2/parsed_status.json |
| partner pilot | B_p3 | (1, 2, 3, 4) | 3 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/B_p3/parsed_status.json |
| partner pilot | B_p5 | (1, 2, 3, 4) | 3 | TIMEOUT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/B_p5/parsed_status.json |
| partner pilot | B_p6 | (1, 2, 3, 4) | 3 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/B_p6/parsed_status.json |
| partner pilot | B_p7 | (1, 2, 3, 4) | 3 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/B_p7/parsed_status.json |
| partner pilot | B_p8 | (1, 2, 3, 4) | 3 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/B_p8/parsed_status.json |
| partner pilot | B_p9 | (1, 2, 3, 4) | 3 | UNSAT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/B_p9/parsed_status.json |

## Conclusion

INCONCLUSIVE_REMAINING_CHILDREN

## Recommendation

longer runs for named children: B_p5, A_p6, A_p5
