# V(4,9), Depth-6 B_p5 Final-Layer Pilot Report

This report refines only the prior B_p5 TIMEOUT branch. TIMEOUT rows are not UNSAT evidence.

Actual worker count: 8.

## Proof Summary

B_p5 fixes T(L6)=(1,2,3,4), |L6|=3, and final comparator (4,5). Since final layers are matchings, wires 4 and 5 cannot appear in the other two final comparators.

The remaining output wires 1,2,3 must all be touched by the two remaining comparators. Therefore exactly one remaining comparator is an output-output pair among {1,2,3}, and the third output wire is paired with one suffix wire in {6,7,8,9}. This gives 3 output-output choices times 4 suffix choices, exactly 12 branches.

The branches are pairwise disjoint because each fixes a distinct exact final-layer comparator set. Their union covers B_p5 because every B_p5 final matching has exactly one of those output-output pairs and exactly one suffix partner for the remaining output wire. No suffix-wire symmetry or canonicalization is used.

## Branch Definitions

| branch | fixed final layer | exact constraints |
| --- | --- | --- |
| OO_12_OS_36 | ((1, 2), (3, 6), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,2).<br>:- depth(D), not selected(D,3,6).<br>:- depth(D), not selected(D,4,5).` |
| OO_12_OS_37 | ((1, 2), (3, 7), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,2).<br>:- depth(D), not selected(D,3,7).<br>:- depth(D), not selected(D,4,5).` |
| OO_12_OS_38 | ((1, 2), (3, 8), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,2).<br>:- depth(D), not selected(D,3,8).<br>:- depth(D), not selected(D,4,5).` |
| OO_12_OS_39 | ((1, 2), (3, 9), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,2).<br>:- depth(D), not selected(D,3,9).<br>:- depth(D), not selected(D,4,5).` |
| OO_13_OS_26 | ((1, 3), (2, 6), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,3).<br>:- depth(D), not selected(D,2,6).<br>:- depth(D), not selected(D,4,5).` |
| OO_13_OS_27 | ((1, 3), (2, 7), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,3).<br>:- depth(D), not selected(D,2,7).<br>:- depth(D), not selected(D,4,5).` |
| OO_13_OS_28 | ((1, 3), (2, 8), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,3).<br>:- depth(D), not selected(D,2,8).<br>:- depth(D), not selected(D,4,5).` |
| OO_13_OS_29 | ((1, 3), (2, 9), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,3).<br>:- depth(D), not selected(D,2,9).<br>:- depth(D), not selected(D,4,5).` |
| OO_23_OS_16 | ((1, 6), (2, 3), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,6).<br>:- depth(D), not selected(D,2,3).<br>:- depth(D), not selected(D,4,5).` |
| OO_23_OS_17 | ((1, 7), (2, 3), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,7).<br>:- depth(D), not selected(D,2,3).<br>:- depth(D), not selected(D,4,5).` |
| OO_23_OS_18 | ((1, 8), (2, 3), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,8).<br>:- depth(D), not selected(D,2,3).<br>:- depth(D), not selected(D,4,5).` |
| OO_23_OS_19 | ((1, 9), (2, 3), (4, 5)) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).<br>:- depth(D), 3 != #count { I,J : selected(D,I,J) }.<br>:- depth(D), not selected(D,4,5).<br>:- depth(D), not selected(D,1,9).<br>:- depth(D), not selected(D,2,3).<br>:- depth(D), not selected(D,4,5).` |

## Branch Results

| branch | status | runtime seconds | peak RSS KB | CPU snapshots | statistics summary | verifier |
| --- | --- | ---: | ---: | ---: | --- | --- |
| OO_12_OS_36 | UNSAT | 188.911 | 74424 | 175 | stats captured |  |
| OO_12_OS_37 | UNSAT | 122.191 | 74416 | 112 | stats captured |  |
| OO_12_OS_38 | UNSAT | 239.317 | 74428 | 223 | stats captured |  |
| OO_12_OS_39 | UNSAT | 63.791 | 74428 | 58 | stats captured |  |
| OO_13_OS_26 | UNSAT | 47.290 | 74556 | 43 | stats captured |  |
| OO_13_OS_27 | UNSAT | 46.217 | 74568 | 42 | stats captured |  |
| OO_13_OS_28 | UNSAT | 41.842 | 74560 | 38 | stats captured |  |
| OO_13_OS_29 | UNSAT | 41.840 | 74556 | 38 | stats captured |  |
| OO_23_OS_16 | TIMEOUT | 1801.023 | 80480 | 1723 | stats captured |  |
| OO_23_OS_17 | TIMEOUT | 1801.027 | 76940 | 1723 | stats captured |  |
| OO_23_OS_18 | TIMEOUT | 1800.708 | 77764 | 1723 | stats captured |  |
| OO_23_OS_19 | TIMEOUT | 1800.633 | 77792 | 1723 | stats captured |  |

## SAT Witnesses

None.

## Combined Parent/Child Table

| source | branch | fixed final layer | status | artifact |
| --- | --- | --- | --- | --- |
| prior partner pilot parent | B_p5 | T(L6)=(1,2,3,4), |L6|=3, (4,5) | TIMEOUT | /home/ono/Codex/experiments/v49_d6_partner_partitioned/branches/B_p5/parsed_status.json |
| current B_p5 split | OO_12_OS_36 | ((1, 2), (3, 6), (4, 5)) | UNSAT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_12_OS_36/parsed_status.json |
| current B_p5 split | OO_12_OS_37 | ((1, 2), (3, 7), (4, 5)) | UNSAT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_12_OS_37/parsed_status.json |
| current B_p5 split | OO_12_OS_38 | ((1, 2), (3, 8), (4, 5)) | UNSAT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_12_OS_38/parsed_status.json |
| current B_p5 split | OO_12_OS_39 | ((1, 2), (3, 9), (4, 5)) | UNSAT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_12_OS_39/parsed_status.json |
| current B_p5 split | OO_13_OS_26 | ((1, 3), (2, 6), (4, 5)) | UNSAT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_13_OS_26/parsed_status.json |
| current B_p5 split | OO_13_OS_27 | ((1, 3), (2, 7), (4, 5)) | UNSAT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_13_OS_27/parsed_status.json |
| current B_p5 split | OO_13_OS_28 | ((1, 3), (2, 8), (4, 5)) | UNSAT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_13_OS_28/parsed_status.json |
| current B_p5 split | OO_13_OS_29 | ((1, 3), (2, 9), (4, 5)) | UNSAT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_13_OS_29/parsed_status.json |
| current B_p5 split | OO_23_OS_16 | ((1, 6), (2, 3), (4, 5)) | TIMEOUT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_23_OS_16/parsed_status.json |
| current B_p5 split | OO_23_OS_17 | ((1, 7), (2, 3), (4, 5)) | TIMEOUT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_23_OS_17/parsed_status.json |
| current B_p5 split | OO_23_OS_18 | ((1, 8), (2, 3), (4, 5)) | TIMEOUT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_23_OS_18/parsed_status.json |
| current B_p5 split | OO_23_OS_19 | ((1, 9), (2, 3), (4, 5)) | TIMEOUT | /home/ono/Codex/experiments/v49_d6_bp5_final_layer_partitioned/branches/OO_23_OS_19/parsed_status.json |

## Conclusion

BP5_INCONCLUSIVE_REMAINING_CHILDREN

## Recommendation

longer runs for named children: OO_23_OS_17, OO_23_OS_16, OO_23_OS_18, OO_23_OS_19
