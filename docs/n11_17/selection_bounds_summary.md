# Selection bounds summary for n=11..17

This report propagates existing V/U selection-depth results and sorting upper bounds. It does not run a solver, verifier replay, additional reduction, or new symmetry argument.

Audit status: `WARNING`.

## Propagation rules

- One-selection: `VDepth(1,n)=UDepth(1,n)=ceil(log2 n)`.
- U all-wire case: `UDepth(n,n)=0`.
- Sorting upper bounds apply to both V and U, with full sorting exact for `VDepth(n,n)` and `VDepth(n-1,n)`.
- Lower bounds propagate upward in n; upper bounds do not.
- V witnesses propagate from larger t to smaller t; V lower bounds propagate from smaller t to larger t.
- U-duality is valid only for U. No U t-monotonicity is assumed.
- V-to-U upper bounds apply for the same `(t,n)` only.

## Sorting-depth table

Citation status: `PARTIAL_LOCAL_NOTE_WITH_N17_TODO`. Local notes cover n<=16; n=17 remains a citation TODO under the planning assumption.

| n | SortDepth(n) |
| ---: | ---: |
| 1 | 0 |
| 2 | 1 |
| 3 | 3 |
| 4 | 3 |
| 5 | 5 |
| 6 | 5 |
| 7 | 6 |
| 8 | 6 |
| 9 | 7 |
| 10 | 7 |
| 11 | 8 |
| 12 | 8 |
| 13 | 9 |
| 14 | 9 |
| 15 | 9 |
| 16 | 9 |
| 17 | 10 |

## Compact bounds tables

### n=11

V-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V bounds | 4 | 6-8 | 6-8 | 7-8 | 7-8 | 7-8 | 7-8 | 7-8 | 7-8 | 8 | 8 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT |

U-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| U bounds | 4 | 5-8 | 5-8 | 5-8 | 5-8 | 5-8 | 5-8 | 5-8 | 5-8 | 4 | 0 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT |

### n=12

V-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V bounds | 4 | 6-8 | 6-8 | 7-8 | 7-8 | 7-8 | 7-8 | 7-8 | 7-8 | 8 | 8 | 8 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT | EXACT |

U-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| U bounds | 4 | 5-8 | 5-8 | 5-8 | 5-8 | 5-8 | 5-8 | 5-8 | 5-8 | 5-8 | 4 | 0 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT |

### n=13

V-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V bounds | 4 | 6-9 | 6-9 | 7-9 | 7-9 | 7-9 | 7-9 | 7-9 | 7-9 | 8-9 | 8-9 | 9 | 9 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT |

U-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| U bounds | 4 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 4 | 0 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT |

### n=14

V-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V bounds | 4 | 6-9 | 6-9 | 7-9 | 7-9 | 7-9 | 7-9 | 7-9 | 7-9 | 8-9 | 8-9 | 9 | 9 | 9 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT | EXACT |

U-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| U bounds | 4 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 4 | 0 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT |

### n=15

V-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V bounds | 4 | 6-9 | 6-9 | 7-9 | 7-9 | 7-9 | 7-9 | 7-9 | 7-9 | 8-9 | 8-9 | 9 | 9 | 9 | 9 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT | EXACT | EXACT |

U-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| U bounds | 4 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 4 | 0 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT |

### n=16

V-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V bounds | 4 | 6-9 | 6-9 | 7-9 | 7-9 | 7-9 | 7-9 | 7-9 | 7-9 | 8-9 | 8-9 | 9 | 9 | 9 | 9 | 9 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT | EXACT | EXACT | EXACT |

U-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| U bounds | 4 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 5-9 | 4 | 0 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT |

### n=17

V-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V bounds | 5 | 6-10 | 6-10 | 7-10 | 7-10 | 7-10 | 7-10 | 7-10 | 7-10 | 8-10 | 8-10 | 9-10 | 9-10 | 9-10 | 9-10 | 10 | 10 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT |

U-type:

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| U bounds | 5 | 5-10 | 5-10 | 5-10 | 5-10 | 5-10 | 5-10 | 5-10 | 5-10 | 5-10 | 5-10 | 5-10 | 5-10 | 5-10 | 5-10 | 5 | 0 |
| status | EXACT | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | GAP | EXACT | EXACT |

## Exact entries already derived

- V exact entries for n=11..17: 28.
- U exact entries for n=11..17: 21.

## Major gaps

- V GAP entries: 70.
- U GAP entries: 77.
- The most actionable gaps are listed in `experiments/selection_bounds_n11_17/frontier_experiments.csv`.

## Direction warnings

- Do not use U-duality for V.
- Do not infer U(2,n) from a U(3,n) witness.
- For V, a witness for larger t gives an upper bound for smaller t; a lower bound for smaller t gives lower bounds for larger t.
