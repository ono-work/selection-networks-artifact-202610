# Paper Claims and Their Evidence

Every computational claim of the paper, mapped to its evidence in this
artifact. Paths are relative to the artifact root. The "Verification /
audit" column distinguishes two different kinds of assurance. For SAT
witnesses it means **independent exhaustive verification**: re-simulation
of the witness on all 2^n binary inputs by `src/verify.py`, which is
independent of the ASP encoding. For ASP UNSAT results, which are
solver-based computational evidence and not independently checkable proof
certificates, it lists the **coverage/closure audits** that were performed:
these audit search-space coverage and provenance, they do not independently
re-prove unsatisfiability. Rerun cost:
**cheap** = seconds to minutes on a laptop, **moderate** = up to a few
hours, **expensive** = the original run took many hours to days and is not
required (stored evidence suffices).

Original solver commands are recorded per run in `decision.json`
(`command` field), `command.txt`, or `command.json` inside each run
directory; the generic form is
`python -m clingo --outf=2 --time-limit=<T> -n 1 solver/common.lp solver/target_{v|u}.lp <instance.lp>`.

## A. Six ASP-derived lower bounds

| Claim | Decisive instance | Evidence | Verification / audit | Status / rerun |
| --- | --- | --- | --- | --- |
| VDepth(2,7) >= 5 | V(2,7) depth 4 UNSAT | `experiments/n10_selection_depth_completion/jobs/V_t2_n7_d4/depth_04/{decision,solver}.json`, `instance.lp`; audit: `../independent_audit.json` | n/a (UNSAT) | COMPLETE; cheap (0.43 s) |
| VDepth(2,9) >= 6 | V(2,9) depth 5 UNSAT | `experiments/n10_selection_depth_completion/jobs/V_t2_n9_d5/depth_05/...` | n/a | COMPLETE; moderate (1008 s) |
| VDepth(3,5) >= 5 | V(3,5) depth 4 UNSAT | `experiments/milestone_3b_smoke/V_t3_n5/depth_00..04/` (full ladder, all UNSAT) | n/a | COMPLETE; cheap |
| VDepth(3,7) >= 6 | V(3,7) **depth 5** UNSAT | `experiments/baseline_n7/decisions/V_t3_n7/depth_00..05/` (full ladder); mirror in `baseline_n7/raw_solver_outputs/` | n/a | COMPLETE; cheap (4 s) |
| VDepth(4,9) >= 7 | depth-6 partitioned nonexistence | `experiments/v49_d6_final/` + partition chain (README section) | coverage/closure audits; manifest `VERIFIED` | COMPLETE; **expensive** (do not rerun; verify with `scripts/check_v49_references.py`) |
| UDepth(4,6) >= 4 | U(4,6) depth 3 UNSAT | `experiments/milestone_3b_smoke/U_t4_n6/depth_00..03/` (full ladder) | n/a | COMPLETE; cheap (0.05 s) |

Notes required for correct interpretation:

- For **V(2,7)** and **V(2,9)** only the decisive depth was run with ASP;
  the shallower depths are excluded analytically by Nakano's t=2 lower
  bound (recorded in `bounds_table.json` `lower_sources`). A single-depth
  UNSAT suffices by depth monotonicity.
- **The six bounds do not all come from depth-4 UNSAT instances.** The
  decisive depths are 4, 5, 4, 5, 6(partitioned), 3 respectively, as listed.
- UDepth(4,6): `A_U(4,6) = 3 < 4`, so this cell rests on its own UNSAT
  search (guarded by `tests/test_weight_game.py`); the game does not cover it.

Runner commands: n10 jobs via
`python -m src.complete_n10_selection_depths --run-job {V_t2_n7_d4|V_t2_n9_d5}`;
n <= 6 cells via `python -m src.experiment --smoke-matrix ...`;
baseline_n7 via the `src.experiment` driver (see
`experiments/baseline_n7/report.md`).

## B. Eight direct witness upper bounds (irredundant n <= 10 inputs)

All eight are confirmed irredundant inputs of the n <= 10 closure
(`experiments/provenance_closure/closure_report.json`, type-4 set). Each
row's witness re-verified during packaging (103/103 pass, see
`generated/witness_verification_report.json`). Rerun of the searches:
cheap-to-moderate; re-verification: cheap.

| Claim | Witness | Stored verifier | Solver log |
| --- | --- | --- | --- |
| V(2,6) depth 4 | `experiments/milestone_3b_smoke/V_t2_n6/depth_04/network.json` | `.../verifier.json` ok | `.../solver.json` |
| V(3,10) depth 6 | `experiments/baseline_n10/decisions/V_t3_n10/depth_06/network.json` | `.../verifier.json` + trace (1024 inputs) | `.../solver_raw.json`, `command.txt` |
| U(3,6) depth 3 | `experiments/milestone_3b_smoke/U_t3_n6/depth_03/network.json` | `.../verifier.json` ok | `.../solver.json` |
| U(3,8) depth 4 | `experiments/baseline_n8/decisions/U_t3_n8/depth_04/network.json` | `.../verifier.json` ok | `.../solver.json` + `baseline_n8/raw/` mirror |
| U(4,8) depth 4 | `experiments/baseline_n8/decisions/U_t4_n8/depth_04/network.json` | `.../verifier.json` ok | same layout |
| U(3,10) depth 5 | `experiments/baseline_n10/decisions/U_t3_n10/depth_05/network.json` | `.../verifier.json` + trace | `.../solver_raw.json`, `command.txt` |
| U(4,10) depth 5 | `experiments/baseline_n10/decisions/U_t4_n10/depth_05/network.json` | same | SATISFIABLE, 352.6 s |
| U(5,10) depth 5 | `experiments/baseline_n10/decisions/U_t5_n10/depth_05/network.json` | same | SATISFIABLE, 51.1 s |

The V(4,9) depth-7 witness (the matching upper bound for claim A.5) is at
`experiments/baseline_n9/decisions/V_t4_n9/depth_07/` and was additionally
re-verified at final-audit time (`evidence_manifest.json`
`audit_summary.v4_depth7_replayed_verifier.ok = true`).

## C. U(2,17) depth-6 witness (doubly verified)

`experiments/u2_n17_d6_witness_search/20260808_030007Z/`:
`network.json` (depth 6, 42 comparators, layer sizes 8,7,6,6,7,8);
**two** verifiers — `verifier_primary.json` (src/verify.py) and
`verifier_independent.json` (structurally independent second verifier
inside the run's own `run_search.py`; 131072 = 2^17 inputs, 0 failures);
`command.json`, `preflight.json` (with the z in {1,2} completeness
argument), `run_summary.json` (SATISFIABLE, 92.3 s, SHA-256 map),
`artifact_manifest.sha256`, snapshots of the encodings and instance.
Status COMPLETE; search rerun cheap (~90 s with clingo), verification cheap.

With `A_U(2,17) = 6` (section E) this closes
`UDepth(2,17) = UDepth(15,17) = 6` exactly.

## D. n = 11 upper-bound witnesses (upper bounds only)

| Claim | Evidence | Verification / audit | Status |
| --- | --- | --- | --- |
| U(3,11) <= 6 | `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06/` (`result.json` VERIFIED_SAT, 252.6 s) | `verifier.json` + trace, 2048 inputs (single verifier) | COMPLETE; moderate |
| U(4,11) <= 6 | `.../U_t4_n11/depth_06/` (321.1 s) | same | COMPLETE; moderate |
| U(5,11) <= 6 | `.../U_t5_n11/depth_06/` (1696.0 s) | same | COMPLETE; moderate |

The depth-5 attempts TIMED OUT (`u_milestone1_n11_n12_summary.json`); the
published intervals are [5,6] and **the timeouts are not lower bounds**.
These three cells have one exhaustive verifier (not two as in section C).

Further witness runs used by the n = 11..17 upper-bound closure (for
example `U_t2_n11/depth_05`, `U_t6_n12/depth_07`, `U_t5_n13/depth_08`)
are under `experiments/baseline_n11_17/decisions/` with rollup reports
beside them; all their witnesses are covered by the 103-witness
re-verification.

## E. Weight-game direct inputs for the n <= 10 closure

`weight_game/results/game_values_n_le_10.json` (identical copy at
`experiments/provenance_closure/game_values_n_le_10.json`) contains

```
A_V(2,5) = 4,  A_U(3,5) = 3,  A_U(2,9) = A_U(3,9) = A_U(4,9) = 5
```

exactly the five type-5 irredundant inputs of
`experiments/provenance_closure/closure_report.json`
(`G_V2_5, G_U3_5, G_U2_9, G_U3_9, G_U4_9`). Implementation:
`src/weight_game.py`; tests: `tests/test_weight_game.py`. Status COMPLETE;
rerun cheap (`python3 experiments/provenance_closure/closure.py` re-derives
the full n <= 10 table and re-checks irredundancy in seconds).

## F. Weight-game values for 11 <= n <= 17 and the 44 improvements

- Values: `weight_game/results/results_n11_17.json` (130 cells, all
  `complete: true`; includes `A_U(2,17) = 6`); audit trail
  `weight_game/results/sweep_log.txt`. Rerun:
  `python3 -m experiments.weight_game.run_sweep` — moderate (the stored run
  used a 55-minute V-type wall-clock budget). The runner is resumable and
  consumes/extends the results file next to it. To reproduce the sweep from
  scratch, run it in a fresh working copy of this artifact or direct its
  outputs to a separate location; do not overwrite the preserved results
  bundled with this artifact.
- Coverage: every U-type cell at 11 <= n <= 17 is covered via
  `t <= floor(n/2)` plus mirror duality. V-type: every non-exact cell
  through n <= 16 and every t <= 11 at n = 17; the four cells n = 17,
  12 <= t <= 15 were **not evaluated** (state spaces T >= 13) and the paper
  reports them as not checked. (The stored sweep additionally contains an
  evaluation at n = 17, t = 12 with `A_V(12,17) = 8`, below the
  structural lower bound 9, so it affects no bound; see
  `weight_game/results/sweep_log.txt`.)
- The 44 improved lower endpoints are reconstructed mechanically by
  `scripts/reconstruct_final_tables.py` into
  `generated/weight_game_improvements.csv`
  (columns `kind,n,t,before_lower,game_bound,after_lower,upper,mechanism`),
  verified to be exactly 44 cells (42 U-type; 2 V-type at n=17, t=8,9),
  each raised by exactly one layer. Status COMPLETE; cheap.
- Mechanism note: at 42 of the 44 cells, the improved endpoint follows
  directly from the game value at that cell or its mirror dual. At
  **U(5,14)** and **U(9,14)**, one additional application of
  n-monotonicity is needed: the raw game value at these cells is 5, and
  the final bound 6 is propagated from the game-improved bound at
  U(4,13) = U(9,13), together with mirror duality
  (`UDepth(9,14) >= UDepth(9,13) >= A_U(4,13) = 6`). The published values
  are correct and unchanged; this concerns only the provenance route,
  recorded in the `mechanism` column.

## G. Closure / bound propagation

**n <= 10 exact tables.** `experiments/n10_selection_depth_completion/`:
`bounds_table.{csv,json}` (110 exact cells), `exact_tables.{md,tex}`
(value-identical to the paper's Tables tab:v-n10 / tab:u-n10),
`evidence_audit.json` (fresh re-verification of every witness; 0 errors,
0 unresolved), `final_report.md`. Strict provenance closure:
`experiments/provenance_closure/closure.py` -> `closure_report.json` —
**19 irredundant inputs: 6 UNSAT (section A) + 8 witnesses (section B) +
5 game values (section E)**; published tables are used only as
verification targets. Status COMPLETE; rerun cheap and byte-identical
(see `VERIFICATION_REPORT.md`).

**Final 11 <= n <= 17 tables.** Reconstructed mechanically by
`scripts/reconstruct_final_tables.py` from (i) the exact n <= 10 table,
(ii) the audited upper bounds
`experiments/baseline_n11_17/paper_ready_upper_bounds/`, (iii) the
weight-game values, (iv) the verified U(2,17) witness, and (v) structural
rules with literature constants (sorting depths for 11 <= n <= 17, Nakano
t=2). Output `generated/final_bounds_n11_17.{csv,json}` and
`generated/final_tables_n11_17.tex`; verified cell-by-cell against a hand
transcription of the manuscript tables
(`scripts/expected_paper_tables_n11_17.json`), which is never used as an
input. Status COMPLETE; cheap.

## V(4,9) summary row

| Claim | Method | Evidence | Verification / audit |
| --- | --- | --- | --- |
| VDepth(4,9) = 7 | depth-6 partitioned UNSAT campaign + verified depth-7 witness | `experiments/v49_d6_final/` (certificate AFFIRMATIVE, 588-file manifest VERIFIED, dependency graph), partition dirs, closure + census certificates, 75 raw UNSAT leaf logs, `generated/v49_d6_branch_ledger.csv` | witness: exhaustive 2^9 verification, replayed at audit time; UNSAT side: audited coverage certificates (computational evidence, not a proof certificate) |

Rerunning the depth-6 campaign is **expensive** (overnight-scale solver
runs) and is not needed: `scripts/check_v49_references.py` re-verifies all
stored hashes and references in minutes.
