# Paper-ready upper-bound tables

## Scope

Solver-free regeneration; no clingo or SAT/UNSAT experiment was run.

## V(2,n) formula correction

The previous closure omitted `VDepth(2,2^k)=k+ceil(log2 k)`. Power-of-two facts through n=32 and padding/restriction are now included. Citation status: **citation TODO**.

| n | upper | lower | status |
|---:|---:|---:|---|
| 10 | 6 | 6 | exact |
| 11 | 6 | 6 | exact |
| 12 | 6 | 6 | exact |
| 13 | 6 | 6 | exact |
| 14 | 6 | 6 | exact |
| 15 | 6 | 6 | exact |
| 16 | 6 | 6 | exact |
| 17 | 8 | 6 | upper_bound_only |

For 10<=n<=16 the upper provenance is `V2_POWER_OF_TWO_FORMULA` plus `PADDING_RESTRICTION`; the lower provenance is `VDepth(2,10)=6` plus `N_MONOTONICITY_LOWER_FROM_N10`. Thus these entries are exact.

## Updated source audit

- V(2,2^k) formula: citation TODO; a paper-ready citation or proof is required.
- V(2,10) lower bound: saved depth-5 UNSAT.
- V(2,10) upper bound: verified V(3,10) depth-6 witness, also valid for V(2,10).

## Updated frontier

V(2,11..16) candidate depth 6 entries were removed.

## U-table impact

V_IMPLIES_U was recomputed; U changes relative to backup: 0.

## Audit and caveats

- exact 10..16: True
- requested removals: True
- no U-duality for V: True
- no V t-monotonicity for U: True
- Upper bounds and exact values remain distinct.
- Formula citation remains TODO.
