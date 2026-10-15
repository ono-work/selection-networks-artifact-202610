# V(4,9), Depth-6 Six-Leaf Reductions

This document records the consecutive-comparator reductions used before any
blind layer-5 partition. No wire relabeling or suffix symmetry is used.

## Lemma

If comparator `e=(i,j)` appears in both `L5` and `L6`, then the copy in `L6`
is redundant. Since both layers are matchings, no comparator between the two
copies touches `i` or `j`. Also `C_e composed with C_e = C_e`. Therefore the
second copy can be deleted from the final layer without changing the network.

## Explicit Reductions

| leaf | repeated comparator in L5 | reduction target |
| --- | --- | --- |
| A5 `{(2,3),(4,5)}` | `(2,3)` | prior UNSAT `T_4` |
| A5 `{(2,3),(4,5)}` | `(4,5)` | prior UNSAT `T_23` |
| A6 `{(2,3),(4,6)}` | `(2,3)` | prior UNSAT `T_4` |
| A6 `{(2,3),(4,6)}` | `(4,6)` | prior UNSAT `T_23` |
| Bs `{(1,s),(2,3),(4,5)}` | `(2,3)` | prior UNSAT `T_14` |
| Bs `{(1,s),(2,3),(4,5)}` | `(4,5)` | prior UNSAT `T_123` |
| Bs `{(1,s),(2,3),(4,5)}` | `(1,s)` | unresolved A5 leaf |

## Residual Branches

| residual | final layer | forbidden in L5 |
| --- | --- | --- |
| A5_residual | `{(2,3),(4,5)}` | `(2,3)`, `(4,5)` |
| A6_residual | `{(2,3),(4,6)}` | `(2,3)`, `(4,6)` |
| B6_residual | `{(1,6),(2,3),(4,5)}` | `(1,6)`, `(2,3)`, `(4,5)` |
| B7_residual | `{(1,7),(2,3),(4,5)}` | `(1,7)`, `(2,3)`, `(4,5)` |
| B8_residual | `{(1,8),(2,3),(4,5)}` | `(1,8)`, `(2,3)`, `(4,5)` |
| B9_residual | `{(1,9),(2,3),(4,5)}` | `(1,9)`, `(2,3)`, `(4,5)` |

## Coverage Argument

A5 and A6 lose no possible solution by forbidding repeated final comparators:
the omitted cases reduce to prior UNSAT support branches `T_4` or `T_23`.

For a Bs leaf, an omitted solution with repeated `(2,3)` or `(4,5)` reduces to
prior UNSAT `T_14` or `T_123`. An omitted solution with repeated `(1,s)`
reduces to the still-unresolved A5 leaf. Therefore, proving A5_residual,
A6_residual, and B6/B7/B8/B9_residual UNSAT closes all six leaves.

The structural cover is tested by enumerating every layer-5 matching directly
in Python in `tests/test_v49_d6_six_leaf_reductions.py`.
