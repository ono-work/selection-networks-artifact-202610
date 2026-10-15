# n=10 depth summary notes

## Directly solver/verifier certified values

- `VDepth(2,10)>=6`: `V(2,10)` depth 5 is UNSAT in `experiments/baseline_n10/decisions/V_t2_n10/depth_05/`.
- `VDepth(3,10)<=6`: `V(3,10)` depth 6 is SAT and independently verified in `experiments/baseline_n10/decisions/V_t3_n10/depth_06/`.
- `UDepth(2,10)=5`: depth 4 UNSAT and depth 5 verified SAT in the `U_t2_n10` artifact directories.
- `UDepth(3,10)<=5`, `UDepth(4,10)<=5`, and `UDepth(5,10)<=5`: verified depth-5 witnesses in the corresponding n=10 U artifact directories.

## Derived by monotonicity

- `VDepth(3,10)>=6` from `VDepth(3,9)=6`.
- `VDepth(t,10)>=7` for `t>=4` from `VDepth(4,9)=7` and the V implication direction.
- `UDepth(3,10)>=5` from `UDepth(3,9)=5`.
- `UDepth(4,10)>=5` from `UDepth(4,9)=5`.
- `UDepth(5,10)>=5` from `UDepth(5,9)=5`.

## Derived by U-duality

- `UDepth(5,9)=5` is obtained from `UDepth(4,9)=5`; no direct `U_t5_n9` directory was present.
- `UDepth(6,10)=UDepth(4,10)=5`.
- `UDepth(7,10)=UDepth(3,10)=5`.
- `UDepth(8,10)=UDepth(2,10)=5`.
- `UDepth(9,10)=UDepth(1,10)=4`.

## Sorting-network upper bounds

The V entries for `t>=4` use a known 10-input depth-7 full sorting network as an upper bound. Local notes record the sorting-depth row in `docs/literature/exact_depth_audit.md`, and `docs/literature/references.bib` contains the `DobbelaereSortingNetworks` bibliography key. Full sorting is only an upper bound for selection.

## Scope-limited source reports strengthened here

The integrated report uses consequences across source reports. In particular, an earlier scope-limited `V(2,10)` depth-5 run by itself would leave the exact value open after UNSAT; the integrated report concludes `VDepth(2,10)=6` using the verified `V(3,10)` depth-6 witness, which is also a `V(2,10)` witness.

For U-type selection, the analogous implication from a `U(3,10)` witness to a `U(2,10)` witness is not used and should not be assumed.

## Citation TODOs

- Replace or augment the local sorting-network source note with the preferred paper citation if the final manuscript should avoid citing the online Dobbelaere table directly.
- No fabricated bibliography entry was introduced for the 10-input sorting upper bound.

## Suggested next steps

- Insert `docs/n10/n10_depth_summary.tex` into the paper or appendix.
- Decide whether to add a local 10-input depth-7 sorting-network artifact.
- Create a clean archived evidence bundle for n=10.

## Audit status

`PASSED`

Problems recorded in JSON: `0`.
