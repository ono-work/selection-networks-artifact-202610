# V(4,9), Depth-6 Support-Partitioned Pilot Report

This report records pilot outcomes only. TIMEOUT rows are not lower-bound evidence.

## Proof Summaries

Boundary inputs: for V-type rank r, the target bit changes only between inputs with r-1 and r zeros. Comparator-network output bits are monotone Boolean functions, so checking the boundary layers with at most t zeros is equivalent to checking all binary inputs for V-type t-selection.

Last-layer normal form: a final comparator wholly in wires 5..9 cannot affect output wires 1..4 and can be deleted. If deletion emptied layer 6, the network would have effective depth at most 5 while still solving V(3,9), contradicting the confirmed V(3,9)=6 fact. Therefore the special hard mode forbids suffix-only final comparators without excluding a depth-6 V(4,9) solution.

## Branch Definitions

| branch | T(L6) | exact constraints |
| --- | --- | --- |
| T_1 | (1,) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), touched(D,2).<br>:- depth(D), touched(D,3).<br>:- depth(D), touched(D,4).` |
| T_2 | (2,) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), touched(D,3).<br>:- depth(D), touched(D,4).` |
| T_3 | (3,) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), touched(D,4).` |
| T_4 | (4,) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), touched(D,2).<br>:- depth(D), touched(D,3).<br>:- depth(D), not touched(D,4).` |
| T_12 | (1, 2) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), touched(D,3).<br>:- depth(D), touched(D,4).` |
| T_13 | (1, 3) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), touched(D,4).` |
| T_14 | (1, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), touched(D,2).<br>:- depth(D), touched(D,3).<br>:- depth(D), not touched(D,4).` |
| T_23 | (2, 3) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), touched(D,4).` |
| T_24 | (2, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), touched(D,3).<br>:- depth(D), not touched(D,4).` |
| T_34 | (3, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).` |
| T_123 | (1, 2, 3) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), touched(D,4).` |
| T_124 | (1, 2, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), touched(D,3).<br>:- depth(D), not touched(D,4).` |
| T_134 | (1, 3, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).` |
| T_234 | (2, 3, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).` |
| T_1234 | (1, 2, 3, 4) | `:- layer(L), not active(L).<br>:- depth(D), selected(D,I,J), I >= 5, J >= 5.<br>:- depth(D), not touched(D,1).<br>:- depth(D), not touched(D,2).<br>:- depth(D), not touched(D,3).<br>:- depth(D), not touched(D,4).` |

## Branch Results

| branch | status | runtime seconds | peak RSS KB | CPU snapshots | statistics summary |
| --- | --- | ---: | ---: | ---: | --- |
| T_1 | UNSAT | 45.386 | 74924 | 38 | stats captured |
| T_2 | UNSAT | 28.889 | 75380 | 24 | stats captured |
| T_3 | UNSAT | 33.669 | 75464 | 28 | stats captured |
| T_4 | UNSAT | 77.368 | 75376 | 67 | stats captured |
| T_12 | UNSAT | 43.099 | 76776 | 36 | stats captured |
| T_13 | UNSAT | 55.675 | 76560 | 47 | stats captured |
| T_14 | UNSAT | 58.054 | 76836 | 49 | stats captured |
| T_23 | UNSAT | 67.738 | 77224 | 58 | stats captured |
| T_24 | UNSAT | 76.316 | 77208 | 66 | stats captured |
| T_34 | UNSAT | 592.208 | 77508 | 563 | stats captured |
| T_123 | UNSAT | 59.123 | 78436 | 50 | stats captured |
| T_124 | UNSAT | 77.377 | 78424 | 67 | stats captured |
| T_134 | UNSAT | 421.409 | 79252 | 397 | stats captured |
| T_234 | TIMEOUT | 900.632 | 81348 | 865 | stats captured |
| T_1234 | TIMEOUT | 900.639 | 82576 | 865 | stats captured |

## SAT Branches

None.

## UNSAT Branches

T_1, T_2, T_3, T_4, T_12, T_13, T_14, T_23, T_24, T_34, T_123, T_124, T_134

## Timed-Out Branches Ranked

| rank | branch | runtime seconds | peak RSS KB | statistics summary |
| ---: | --- | ---: | ---: | --- |
| 1 | T_1234 | 900.639 | 82576 | stats captured |
| 2 | T_234 | 900.632 | 81348 | stats captured |

## Recommendation

Recommendation: (b) refine specific timed-out branches by final-layer comparator count first, starting with T_1234, T_234; if still uneven, use (c) exact comparator incident to a designated output wire.
