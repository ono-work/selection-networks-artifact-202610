# Constructive upper-bound closure for selection networks up to n=17

## Scope

This report builds U-type and V-type upper bounds by applying construction and closure rules to existing exact/verified witnesses, theoretical facts, and sorting fallback bounds. No solver run is introduced here. Existing small-t scouting jobs were checked first; the only partial stopped job recorded here is listed in the aborted-job summary when present.

## Closure rules

- `PADDING_RESTRICTION`: if `Depth_K(t,m) <= d` and `t <= n <= m`, then `Depth_K(t,n) <= d`.
- `V2_POWER_OF_TWO_FORMULA`: `VDepth(2,2^k) = k + ceil(log2 k)` for k>=1. Citation status: `citation TODO`.
- `U_DUALITY`: if `UDepth(t,n) <= d`, then `UDepth(n-t,n) <= d`; U only.
- `V_IMPLIES_U`: if `VDepth(t,n) <= d`, then `UDepth(t,n) <= d`.
- `V_T_MONOTONICITY`: if `VDepth(t,n) <= d` and `s <= t`, then `VDepth(s,n) <= d`; not applied to U.
- `U_BINARY_MERGE`: `UDepth(t,n1+n2) <= max(U(t,n1), U(t,n2)) + U(t,2t)`.
- `U_TO_V_BINARY_MERGE`: `VDepth(t,n1+n2) <= max(U(t,n1), U(t,n2)) + V(t,2t)`.
- `V_BINARY_MERGE_GENERIC`: `VDepth(t,n1+n2) <= max(V(t,n1), V(t,n2)) + V(t,2t)`.
- `SORTING_FALLBACK`: full sorting networks provide U/V upper bounds; n=17 sorting citation remains explicit below.

## Initial facts and source audit

- Found sources: `docs/n10/u_selection_decisions.md`, `docs/n10/n10_v_selection_decisions.md`, `docs/n10/n10_depth_summary.md`, `experiments/baseline_n10/n10_depth_summary.json`, `docs/n11_17/u_milestone1_n11_n12.md`, `docs/n11_17/u_milestone1_depth6_upper_bounds.md`, `docs/n11_17/u_n12_central_depth7_upper_bounds.md`, `docs/n11_17/u_upper_bounds_n13_n14_depth7.md`, `docs/n11_17/u_upper_bounds_n13_n14_depth8.md`, `docs/n11_17/selection_bounds_summary.md`, `docs/n11_17/selection_bounds_notes.md`
- Missing sources: `docs/n10/v_selection_decisions.md`
- Sorting-depth citation status: `local note candidate: docs/n11_17/selection_bounds_notes.md; n=17 TODO_SORTING_DEPTH_CITATION`.
- Aborted job records: 1.

## U-type upper-bound table

Rows are n and cells are t=1..n best upper bounds.

| 1 | 0 |
| 2 | 1 | 0 |
| 3 | 2 | 2 | 0 |
| 4 | 2 | 2 | 2 | 0 |
| 5 | 3 | 3 | 3 | 3 | 0 |
| 6 | 3 | 4 | 3 | 4 | 3 | 0 |
| 7 | 3 | 4 | 4 | 4 | 4 | 3 | 0 |
| 8 | 3 | 4 | 4 | 4 | 4 | 4 | 3 | 0 |
| 9 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 0 |
| 10 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 0 |
| 11 | 4 | 5 | 6 | 6 | 6 | 6 | 6 | 6 | 5 | 4 | 0 |
| 12 | 4 | 5 | 6 | 6 | 7 | 7 | 7 | 6 | 6 | 5 | 4 | 0 |
| 13 | 4 | 5 | 7 | 8 | 9 | 9 | 9 | 9 | 8 | 7 | 5 | 4 | 0 |
| 14 | 4 | 5 | 7 | 8 | 9 | 9 | 9 | 9 | 9 | 8 | 7 | 5 | 4 | 0 |
| 15 | 4 | 5 | 7 | 8 | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 7 | 5 | 4 | 0 |
| 16 | 4 | 5 | 7 | 8 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 7 | 5 | 4 | 0 |
| 17 | 5 | 7 | 8 | 9 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 9 | 8 | 7 | 5 | 0 |

## U-type upper-bound table for n=11..17

| 11 | 4 | 5 | 6 | 6 | 6 | 6 | 6 | 6 | 5 | 4 | 0 |
| 12 | 4 | 5 | 6 | 6 | 7 | 7 | 7 | 6 | 6 | 5 | 4 | 0 |
| 13 | 4 | 5 | 7 | 8 | 9 | 9 | 9 | 9 | 8 | 7 | 5 | 4 | 0 |
| 14 | 4 | 5 | 7 | 8 | 9 | 9 | 9 | 9 | 9 | 8 | 7 | 5 | 4 | 0 |
| 15 | 4 | 5 | 7 | 8 | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 7 | 5 | 4 | 0 |
| 16 | 4 | 5 | 7 | 8 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 7 | 5 | 4 | 0 |
| 17 | 5 | 7 | 8 | 9 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 9 | 8 | 7 | 5 | 0 |

## V-type upper-bound table

| 1 | 0 |
| 2 | 1 | 1 |
| 3 | 2 | 3 | 3 |
| 4 | 2 | 3 | 3 | 3 |
| 5 | 3 | 4 | 5 | 5 | 5 |
| 6 | 3 | 4 | 5 | 5 | 5 | 5 |
| 7 | 3 | 5 | 6 | 6 | 6 | 6 | 6 |
| 8 | 3 | 5 | 6 | 6 | 6 | 6 | 6 | 6 |
| 9 | 4 | 6 | 6 | 7 | 7 | 7 | 7 | 7 | 7 |
| 10 | 4 | 6 | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |
| 11 | 4 | 6 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 |
| 12 | 4 | 6 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 |
| 13 | 4 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| 14 | 4 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| 15 | 4 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| 16 | 4 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| 17 | 5 | 8 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 |

## V-type upper-bound table for n=11..17

| 11 | 4 | 6 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 |
| 12 | 4 | 6 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 |
| 13 | 4 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| 14 | 4 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| 15 | 4 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| 16 | 4 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| 17 | 5 | 8 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 |

## Improvements over raw scouting

- `U(2,16) <= 5` via `U_DUALITY`; U(2,n) for n<=16 is covered by the power-of-two formula plus padding/restriction.
- `VDepth(2,n)=6` for 10<=n<=16: upper provenance is `V2_POWER_OF_TWO_FORMULA` plus `PADDING_RESTRICTION`; lower provenance is exact `VDepth(2,10)=6` plus `N_MONOTONICITY_LOWER_FROM_N10`.
- `U(3,14) <= 7` via `U_BINARY_MERGE`; compare against depth-7 ASP scouting artifacts before treating this as a solver result.
- `U(4,14) <= 8` via `U_BINARY_MERGE`; constructive closure records an upper bound even where blind scouting was hard.

## Frontier entries for lower-bound work

| kind | n | t | best D | known L | gap | candidate UNSAT depth | suggested next action |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| U | 11 | 3 | 6 | 5 | 1 | 5 | Check existing depth-5 artifacts, then plan certificate or witness construction. |
| U | 11 | 4 | 6 | 5 | 1 | 5 | Check existing depth-5 artifacts, then plan certificate or witness construction. |
| U | 11 | 5 | 6 | 5 | 1 | 5 | Check existing depth-5 artifacts, then plan certificate or witness construction. |
| U | 11 | 6 | 6 | 5 | 1 | 5 | Check existing depth-5 artifacts, then plan certificate or witness construction. |
| U | 11 | 7 | 6 | 5 | 1 | 5 | Check existing depth-5 artifacts, then plan certificate or witness construction. |
| U | 11 | 8 | 6 | 5 | 1 | 5 | Check existing depth-5 artifacts, then plan certificate or witness construction. |
| V | 11 | 3 | 8 | 6 | 2 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 11 | 4 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 11 | 5 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 11 | 6 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 11 | 7 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 11 | 8 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 11 | 9 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| U | 12 | 3 | 6 | 5 | 1 | 5 | Check existing depth-5 artifacts, then plan certificate or witness construction. |
| U | 12 | 4 | 6 | 5 | 1 | 5 | Check existing depth-5 artifacts, then plan certificate or witness construction. |
| U | 12 | 5 | 7 | 5 | 2 | 6 | Check existing depth-6 artifacts, then plan certificate or witness construction. |
| U | 12 | 6 | 7 | 5 | 2 | 6 | Check existing depth-6 artifacts, then plan certificate or witness construction. |
| U | 12 | 7 | 7 | 5 | 2 | 6 | Check existing depth-6 artifacts, then plan certificate or witness construction. |
| U | 12 | 8 | 6 | 5 | 1 | 5 | Check existing depth-5 artifacts, then plan certificate or witness construction. |
| U | 12 | 9 | 6 | 5 | 1 | 5 | Check existing depth-5 artifacts, then plan certificate or witness construction. |
| V | 12 | 3 | 8 | 6 | 2 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 12 | 4 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 12 | 5 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 12 | 6 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 12 | 7 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 12 | 8 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| V | 12 | 9 | 8 | 7 | 1 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| U | 13 | 3 | 7 | 5 | 2 | 6 | Check existing depth-6 artifacts, then plan certificate or witness construction. |
| U | 13 | 4 | 8 | 5 | 3 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| U | 13 | 5 | 9 | 5 | 4 | 8 | Check existing depth-8 artifacts, then plan certificate or witness construction. |
| U | 13 | 6 | 9 | 5 | 4 | 8 | Check existing depth-8 artifacts, then plan certificate or witness construction. |
| U | 13 | 7 | 9 | 5 | 4 | 8 | Check existing depth-8 artifacts, then plan certificate or witness construction. |
| U | 13 | 8 | 9 | 5 | 4 | 8 | Check existing depth-8 artifacts, then plan certificate or witness construction. |
| U | 13 | 9 | 8 | 5 | 3 | 7 | Check existing depth-7 artifacts, then plan certificate or witness construction. |
| U | 13 | 10 | 7 | 5 | 2 | 6 | Check existing depth-6 artifacts, then plan certificate or witness construction. |
| V | 13 | 3 | 9 | 6 | 3 | 8 | Check existing depth-8 artifacts, then plan certificate or witness construction. |
| V | 13 | 4 | 9 | 7 | 2 | 8 | Check existing depth-8 artifacts, then plan certificate or witness construction. |
| V | 13 | 5 | 9 | 7 | 2 | 8 | Check existing depth-8 artifacts, then plan certificate or witness construction. |
| V | 13 | 6 | 9 | 7 | 2 | 8 | Check existing depth-8 artifacts, then plan certificate or witness construction. |
| V | 13 | 7 | 9 | 7 | 2 | 8 | Check existing depth-8 artifacts, then plan certificate or witness construction. |

## Generated network verification summary

No generated networks were verified in this run; numeric construction bounds are still recorded where applicable.

## Caveats

- This is an upper-bound closure table, not an exact-depth table.
- The V(2,2^k) formula citation is TODO; it needs a paper-ready citation or an included proof before the final manuscript.
- Padding gives upper bounds, not exactness.
- U-duality is U-only.
- V t-monotonicity is not applied to U.
- n=17 sorting-depth citation status remains TODO if the source audit says so.
- Runtime observations from previous scouting are not mathematical evidence except for verified SAT artifacts and saved UNSAT solver outputs.
