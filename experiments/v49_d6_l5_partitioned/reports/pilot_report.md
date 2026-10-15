# V(4,9), Depth-6 L5-Cardinality Pilot Report

Generated: 2026-07-07T13:52:45

## Command

./scripts/run_v49_d6_l5_partitioned.sh --mode pilot --timeout-seconds 900 --workers 6 --clingo-threads-per-branch 1

## Policy

- outer worker count: 6
- one clingo thread per worker
- no GPU use
- no internal clingo parallel mode
- 900-second wall-clock timeout per child

## Summary

- SAT: 0
- UNSAT: 6
- TIMEOUT: 14
- ERROR: 0
- VERIFICATION_FAILED: 0

- runtime min/median/max seconds: 98.681 / 900.385 / 900.641
- peak RSS min/median/max KB: 73064 / 74864 / 76452

## Branch Results

| branch | status | runtime seconds | peak RSS KB | CPU snapshots | verifier |
| --- | --- | ---: | ---: | ---: | --- |
| A5_residual_L5eq1 | UNSAT | 116.896 | 73912 | 109 |  |
| A5_residual_L5eq2 | TIMEOUT | 900.382 | 74864 | 840 |  |
| A5_residual_L5eq3 | TIMEOUT | 900.388 | 75032 | 840 |  |
| A5_residual_L5eq4 | TIMEOUT | 900.394 | 75596 | 840 |  |
| B6_residual_L5eq1 | UNSAT | 137.271 | 73660 | 128 |  |
| B6_residual_L5eq2 | TIMEOUT | 900.399 | 74864 | 840 |  |
| B6_residual_L5eq3 | TIMEOUT | 900.348 | 74428 | 840 |  |
| B6_residual_L5eq4 | TIMEOUT | 900.374 | 74456 | 840 |  |
| B7_residual_L5eq1 | UNSAT | 98.681 | 73064 | 92 |  |
| B7_residual_L5eq2 | TIMEOUT | 900.524 | 75176 | 840 |  |
| B7_residual_L5eq3 | TIMEOUT | 900.532 | 75084 | 840 |  |
| B7_residual_L5eq4 | TIMEOUT | 900.539 | 75776 | 840 |  |
| B8_residual_L5eq1 | UNSAT | 111.363 | 73660 | 104 |  |
| B8_residual_L5eq2 | TIMEOUT | 900.559 | 74664 | 840 |  |
| B8_residual_L5eq3 | TIMEOUT | 900.357 | 74692 | 840 |  |
| B8_residual_L5eq4 | TIMEOUT | 900.468 | 75128 | 842 |  |
| B9_residual_L5eq1 | UNSAT | 100.926 | 73088 | 94 |  |
| B9_residual_L5eq2 | UNSAT | 886.305 | 75684 | 852 |  |
| B9_residual_L5eq3 | TIMEOUT | 900.618 | 75928 | 866 |  |
| B9_residual_L5eq4 | TIMEOUT | 900.641 | 76452 | 872 |  |

## UNSAT Branches

A5_residual_L5eq1, B6_residual_L5eq1, B7_residual_L5eq1, B8_residual_L5eq1, B9_residual_L5eq1, B9_residual_L5eq2

## Timed-Out Branches

A5_residual_L5eq2, A5_residual_L5eq3, A5_residual_L5eq4, B6_residual_L5eq2, B6_residual_L5eq3, B6_residual_L5eq4, B7_residual_L5eq2, B7_residual_L5eq3, B7_residual_L5eq4, B8_residual_L5eq2, B8_residual_L5eq3, B8_residual_L5eq4, B9_residual_L5eq3, B9_residual_L5eq4

## Conclusion

L5_PARTITION_PILOT_INCONCLUSIVE
