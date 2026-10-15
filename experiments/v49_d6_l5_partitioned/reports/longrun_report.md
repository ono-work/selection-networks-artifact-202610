# V(4,9), Depth-6 L5 Long-Run Report

Benchmark-selected solver configuration: split_4thread; options: --parallel-mode=4,split.
Worker calculation: min(14, max(1, floor((20 - 2) / 4))) = 4.

## Status Table

| branch | status | runtime seconds | peak RSS KB | verifier |
| --- | --- | ---: | ---: | --- |
| A5_residual_L5eq2 | UNSAT | 495.836 | 151112 |  |
| A5_residual_L5eq3 | TIMEOUT | 3600.850 | 171992 |  |
| A5_residual_L5eq4 | UNSAT | 2990.634 | 170240 |  |
| B6_residual_L5eq2 | UNSAT | 541.383 | 154352 |  |
| B6_residual_L5eq3 | TIMEOUT | 3600.764 | 176356 |  |
| B6_residual_L5eq4 | TIMEOUT | 3600.719 | 175484 |  |
| B7_residual_L5eq2 | UNSAT | 499.108 | 161168 |  |
| B7_residual_L5eq3 | UNSAT | 3178.630 | 173908 |  |
| B7_residual_L5eq4 | UNSAT | 3429.064 | 173720 |  |
| B8_residual_L5eq2 | UNSAT | 585.449 | 154316 |  |
| B8_residual_L5eq3 | UNSAT | 3181.711 | 175204 |  |
| B8_residual_L5eq4 | UNSAT | 3517.774 | 179304 |  |
| B9_residual_L5eq3 | UNSAT | 2469.652 | 172412 |  |
| B9_residual_L5eq4 | UNSAT | 2755.120 | 178212 |  |

## Status Lists

- SAT: None
- UNSAT: A5_residual_L5eq2, A5_residual_L5eq4, B6_residual_L5eq2, B7_residual_L5eq2, B7_residual_L5eq3, B7_residual_L5eq4, B8_residual_L5eq2, B8_residual_L5eq3, B8_residual_L5eq4, B9_residual_L5eq3, B9_residual_L5eq4
- TIMEOUT: A5_residual_L5eq3, B6_residual_L5eq3, B6_residual_L5eq4
- ERROR: None
- VERIFICATION_FAILED: None
- CANCELLED_AFTER_VERIFIED_SAT: None

## Runtime And RSS

- runtime min/max seconds: 495.836 / 3600.850
- peak RSS min/max KB: 151112 / 179304

## Coverage Accounting

- prior closed L5 branches: A5_residual_L5eq1, B6_residual_L5eq1, B7_residual_L5eq1, B8_residual_L5eq1, B9_residual_L5eq1, B9_residual_L5eq2
- newly closed UNSAT branches: A5_residual_L5eq2, A5_residual_L5eq4, B6_residual_L5eq2, B7_residual_L5eq2, B7_residual_L5eq3, B7_residual_L5eq4, B8_residual_L5eq2, B8_residual_L5eq3, B8_residual_L5eq4, B9_residual_L5eq3, B9_residual_L5eq4
- still-open branches: A5_residual_L5eq3, B6_residual_L5eq3, B6_residual_L5eq4

## Conclusion

V49_DEPTH6_INCONCLUSIVE

## Recommended Next Action

run a longer wave on specifically named remaining branches: A5_residual_L5eq3, B6_residual_L5eq3, B6_residual_L5eq4
