# V(4,9), Depth-6 Six-Leaf Reduced Pilot Report

Actual worker count: 6.

## Terminal Profiles

| leaf | final layer | profile clauses |
| --- | --- | --- |
| A5 | ((2, 3), (4, 5)) | (2,3): z<=1 -> y2=y3=1; z=2 -> exactly one zero; z>=3 -> y2=y3=0; (4,5): z<=3 -> y4=y5=1; z>=4 -> y4=0 or y5=0; wire 1 untouched: z=0 -> y1=1; z>=1 -> y1=0 |
| A6 | ((2, 3), (4, 6)) | (2,3): z<=1 -> y2=y3=1; z=2 -> exactly one zero; z>=3 -> y2=y3=0; (4,6): z<=3 -> y4=y6=1; z>=4 -> y4=0 or y6=0; wire 1 untouched: z=0 -> y1=1; z>=1 -> y1=0 |
| B6 | ((1, 6), (2, 3), (4, 5)) | (2,3): z<=1 -> y2=y3=1; z=2 -> exactly one zero; z>=3 -> y2=y3=0; (4,5): z<=3 -> y4=y5=1; z>=4 -> y4=0 or y5=0; (1,6): z=0 -> y1=y6=1; z>=1 -> y1=0 or y6=0 |
| B7 | ((1, 7), (2, 3), (4, 5)) | (2,3): z<=1 -> y2=y3=1; z=2 -> exactly one zero; z>=3 -> y2=y3=0; (4,5): z<=3 -> y4=y5=1; z>=4 -> y4=0 or y5=0; (1,7): z=0 -> y1=y7=1; z>=1 -> y1=0 or y7=0 |
| B8 | ((1, 8), (2, 3), (4, 5)) | (2,3): z<=1 -> y2=y3=1; z=2 -> exactly one zero; z>=3 -> y2=y3=0; (4,5): z<=3 -> y4=y5=1; z>=4 -> y4=0 or y5=0; (1,8): z=0 -> y1=y8=1; z>=1 -> y1=0 or y8=0 |
| B9 | ((1, 9), (2, 3), (4, 5)) | (2,3): z<=1 -> y2=y3=1; z=2 -> exactly one zero; z>=3 -> y2=y3=0; (4,5): z<=3 -> y4=y5=1; z>=4 -> y4=0 or y5=0; (1,9): z=0 -> y1=y9=1; z>=1 -> y1=0 or y9=0 |

## Redundancy Lemma

If the same comparator e occurs in L5 and L6, the L6 copy is redundant: both layers are matchings, no intervening comparator touches its endpoints, and C_e composed with C_e equals C_e.

## Reduction Table

| residual | final layer | forbidden in L5 | coverage note |
| --- | --- | --- | --- |
| A5_residual | ((2, 3), (4, 5)) | ((2, 3), (4, 5)) | repeated (2,3) or (4,5) reduces to prior UNSAT T_4 or T_23 |
| A6_residual | ((2, 3), (4, 6)) | ((2, 3), (4, 6)) | repeated (2,3) or (4,6) reduces to prior UNSAT T_4 or T_23 |
| B6_residual | ((1, 6), (2, 3), (4, 5)) | ((1, 6), (2, 3), (4, 5)) | repeated (2,3)/(4,5) reduces to prior UNSAT T_14/T_123; repeated (1,6) reduces to A5 |
| B7_residual | ((1, 7), (2, 3), (4, 5)) | ((1, 7), (2, 3), (4, 5)) | repeated (2,3)/(4,5) reduces to prior UNSAT T_14/T_123; repeated (1,7) reduces to A5 |
| B8_residual | ((1, 8), (2, 3), (4, 5)) | ((1, 8), (2, 3), (4, 5)) | repeated (2,3)/(4,5) reduces to prior UNSAT T_14/T_123; repeated (1,8) reduces to A5 |
| B9_residual | ((1, 9), (2, 3), (4, 5)) | ((1, 9), (2, 3), (4, 5)) | repeated (2,3)/(4,5) reduces to prior UNSAT T_14/T_123; repeated (1,9) reduces to A5 |

## Coverage Of Original Six Leaves

The six residual branches are not a direct partition. A5/A6 omitted cases reduce to prior UNSAT support branches. Bs omitted cases with repeated (2,3) or (4,5) reduce to prior UNSAT support branches; omitted cases with repeated (1,s) reduce to A5. Therefore UNSAT for all six residual branches closes all six original leaves.

## Branch Results

| branch | status | runtime seconds | peak RSS KB | CPU snapshots | statistics summary | verifier |
| --- | --- | ---: | ---: | ---: | --- | --- |
| A5_residual | TIMEOUT | 1800.449 | 77272 | 1689 | stats captured |  |
| A6_residual | UNSAT | 1052.940 | 74668 | 983 | stats captured |  |
| B6_residual | TIMEOUT | 1800.457 | 77332 | 1689 | stats captured |  |
| B7_residual | TIMEOUT | 1800.468 | 77684 | 1689 | stats captured |  |
| B8_residual | TIMEOUT | 1800.475 | 77472 | 1689 | stats captured |  |
| B9_residual | TIMEOUT | 1800.486 | 77868 | 1689 | stats captured |  |

## SAT Witnesses

None.

## Conclusion

SIX_LEAF_REDUCED_PILOT_INCONCLUSIVE

## Recommendation

longer runs for named residual branches: B9_residual, B8_residual, B7_residual, B6_residual, A5_residual
