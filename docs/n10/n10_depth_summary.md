# n=10 V- and U-selection depth summary

## Scope

This report integrates existing standard-pipeline decisions and derived
consequences for `n=10`. It introduces no new solver run, search, reduction, or
symmetry argument. The source reports remain the V-only and U-only decision
reports; this file records the final combined tables and the derivations that
connect those reports.

Audit status: `PASSED`.

## Definitions

A V-type `t`-selection network places the `t` smallest input values on wires
`1,...,t` in sorted order. A U-type `t`-selection network places the same set of
`t` smallest values on wires `1,...,t` without requiring them to be ordered.
Thus V is stronger than U for the same `t`.

For V-type selection, a V(`t`) witness is also a V(`s`) witness for `s <= t`.
Equivalently, a lower bound for V(`t`) transfers to V(`s`) only for `s >= t`,
not for smaller `s`. For U-type selection, the report uses U-duality
`UDepth(t,n)=UDepth(n-t,n)`. Monotonicity in `n` is used to transfer lower
bounds from smaller `n` to larger `n`.

## V-depth table for n=10

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| VDepth(t,10) | 4 | 6 | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |

For `t=1`, `VDepth(1,10)=ceil(log2 10)=4` by the standard one-selection depth
bound.

For `t=2`, the artifact `experiments/baseline_n10/decisions/V_t2_n10/depth_05/`
records `UNSATISFIABLE`, giving the lower bound `VDepth(2,10)>=6`. The verified
`V(3,10)` depth-6 witness in
`experiments/baseline_n10/decisions/V_t3_n10/depth_06/` is also a `V(2,10)`
witness because V3 implies V2. Hence `VDepth(2,10)=6`.

For `t=3`, the same depth-6 witness is independently verified on all 1024
binary inputs. The n=9 artifacts record `VDepth(3,9)=6`, so monotonicity gives
the matching lower bound for n=10. Hence `VDepth(3,10)=6`.

For `t>=4`, the final V(4,9) certificate records `VDepth(4,9)=7`; monotonicity
gives `VDepth(4,10)>=7`, and the same lower bound applies to all `t>=4` by the
V implication direction. A known 10-input depth-7 sorting network gives a
full-sorting upper bound, hence a V upper bound, for all `t`. Therefore
`VDepth(t,10)=7` for `t=4,...,10`. The local sorting-network source note is
`docs/literature/exact_depth_audit.md`; the bibliography key is
`DobbelaereSortingNetworks`.

## U-depth table for n=10

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| UDepth(t,10) | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 0 |

For `t=1`, `UDepth(1,10)=ceil(log2 10)=4`; for `t=10`, selecting all wires in
arbitrary order is trivial, so `UDepth(10,10)=0`.

For `t=2`, `U(2,10)` depth 4 is `UNSATISFIABLE`, while `U(2,10)` depth 5 is
`SATISFIABLE` and independently verified on all 1024 binary inputs. Therefore
`UDepth(2,10)=5`. This conclusion does not use any automatic implication from a
`U(3,10)` witness to a `U(2,10)` witness.

For `t=3`, the verified `U(3,10)` depth-5 witness gives the upper bound, and
the existing `UDepth(3,9)=5` artifacts give the lower bound by monotonicity.
Therefore `UDepth(3,10)=5`.

For `t=4`, the verified `U(4,10)` depth-5 witness gives the upper bound, and
the existing `UDepth(4,9)=5` artifacts give the lower bound by monotonicity.
Therefore `UDepth(4,10)=5`.

For `t=5`, the verified `U(5,10)` depth-5 witness gives the upper bound. The
lower bound uses `UDepth(5,9)=5`, obtained from `UDepth(4,9)=5` by U-duality on
nine wires, then monotonicity to n=10. Therefore `UDepth(5,10)=5`.

For `t=6,7,8,9`, U-duality on ten wires gives the remaining entries from
`t=4,3,2,1`, respectively.

## Artifact ledger

Source reports:

- `docs/n10/n10_v_selection_decisions.md`
- `docs/n10/u_selection_decisions.md`

Main artifact directories and files:

- `experiments/v49_d6_final/final_certificate.json`
- `experiments/v49_d6_final/evidence_index.md`
- `experiments/baseline_n10/decisions/V_t2_n10/depth_05/`
- `experiments/baseline_n10/decisions/V_t3_n10/depth_06/`
- `experiments/baseline_n10/decisions/U_t2_n10/depth_04/`
- `experiments/baseline_n10/decisions/U_t2_n10/depth_05/`
- `experiments/baseline_n10/decisions/U_t3_n10/depth_05/`
- `experiments/baseline_n10/decisions/U_t4_n10/depth_05/`
- `experiments/baseline_n10/decisions/U_t5_n10/depth_05/`
- `experiments/baseline_n9/decisions/V_t3_n9/depth_05/`
- `experiments/baseline_n9/decisions/V_t3_n9/depth_06/`
- `experiments/baseline_n9/decisions/U_t3_n9/depth_04/`
- `experiments/baseline_n9/decisions/U_t3_n9/depth_05/`
- `experiments/baseline_n9/decisions/U_t4_n9/depth_04/`
- `experiments/baseline_n9/decisions/U_t4_n9/depth_05/`
- `experiments/u_calibration/U_t2_n8/`
- `docs/literature/exact_depth_audit.md`
- `docs/literature/references.bib`

## Caveats

- UNSAT results are solver artifacts for the encoded ASP instances; no
  human-readable UNSAT proof or unsat core is claimed.
- SAT witnesses are independently verified on all `2^10 = 1024` binary inputs.
- The sorting-network upper bound for V uses local literature notes for the
  known 10-input depth-7 full sorting network; full sorting supplies upper
  bounds only.
- U-duality is used only for U-type depths.
- Runtime is an operational observation only.
