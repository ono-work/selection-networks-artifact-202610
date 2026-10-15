# Artifact Inventory: "Exact Depths and Bounds for Small Selection Networks" (CANDAR 2026)

Read-only inventory of the computational evidence on the original experiment
machine (`thor`), produced 2026-10-15. No experiment file was modified, moved,
renamed, or deleted. The only files written are this report and
`artifact_inventory.json` (which additionally carries SHA-256 hashes, sizes,
and mtimes for 148 key files, plus the full machine-readable result records).

The public artifact has **not** been created yet; this report states what
exists and what is missing.

---

## 1. Environment

| Item | Value |
| --- | --- |
| Repository root | `/home/ono/Agent` |
| Git HEAD | `7c06ad41aa6b9037ce471cebc143dae24897f5f5` (`master`, "Add witness rendering dossiers", 2026-06-24) |
| Git status | 165 dirty/untracked entries; full `--porcelain` output embedded in `artifact_inventory.json`. Essentially all experiment data, `manuscript/`, and most of `src/` are **uncommitted**. |
| Machine | `thor`, Linux 6.17.0-1021-nvidia, **aarch64** |
| Python | 3.12.3 (system and `.venv`) |
| clingo | **5.8.0**, available only as the Python module in `.venv` (`.venv/bin/python -m clingo`); no standalone `clingo` binary on PATH |
| Path history | The checkout was formerly `/home/ono/Codex` (the venv's editable install and pre-August recorded commands still say so); runs from 2026-08 onward record `/home/ono/Agent`. |

## 2. Shared generator / encoding sources

All ASP runs use `solver/common.lp` plus `solver/target_v.lp` (ordered) or
`solver/target_u.lp` (unordered), instances from `src/generate_instance.py`,
driver `src/experiment.py` (invoking `.venv/bin/python -m clingo --outf=2
--time-limit=<T> -n 1 <common> <target> <instance.lp>` via `src/solver.py`),
and the independent exhaustive binary verifier `src/verify.py` (re-simulates
all 2^n inputs; does not reuse the ASP encoding). Each run directory holds
`instance.lp`, `solver.json` (raw clingo JSON), `decision.json`/`result.json`,
and for SAT: `network.json` + `verifier.json`.

## 3. ASP-derived lower bounds

| Paper claim | Experiment dir | Decisive UNSAT evidence | Ladder below | Independent audit | Status |
| --- | --- | --- | --- | --- | --- |
| VDepth(2,7) >= 5 | `experiments/n10_selection_depth_completion/jobs/V_t2_n7_d4` | `depth_04/{decision,solver}.json` UNSAT, 0.43 s | depths 0–3 by Nakano corollary, not ASP | `independent_audit.json` | **COMPLETE** |
| VDepth(2,9) >= 6 | `experiments/n10_selection_depth_completion/jobs/V_t2_n9_d5` | `depth_05/{decision,solver}.json` UNSAT, 1008 s | depths 0–4 by Nakano corollary | `independent_audit.json` | **COMPLETE** |
| VDepth(3,5) >= 5 | `experiments/milestone_3b_smoke/V_t3_n5` | `depth_04` UNSAT | full ladder 0–4 all UNSAT | `evidence_audit.json` re-check | **COMPLETE** |
| VDepth(3,7) >= 6 | `experiments/baseline_n7/decisions/V_t3_n7` | `depth_05` UNSAT, 3.98 s (+ mirror in `raw_solver_outputs/`) | full ladder 0–5 all UNSAT | `evidence_audit.json` re-check | **COMPLETE** |
| UDepth(4,6) >= 4 | `experiments/milestone_3b_smoke/U_t4_n6` | `depth_03` UNSAT, 0.05 s (direct run, not duality-derived) | full ladder 0–3 all UNSAT | `evidence_audit.json`; `tests/test_weight_game.py` guards A_U(4,6)=3 | **COMPLETE** |
| VDepth(4,9) >= 7 | `experiments/v49_d6_final` + partition chain | see Section 7 | depth <= 5 via VDepth(3,9) >= 6 + restriction lemma | 588-file manifest `VERIFIED` | **COMPLETE** |

Commands: V_t2 jobs via `.venv/bin/python -m src.complete_n10_selection_depths
--run-job <id>` (clingo time limits 1200 / 7200 s); n <= 6 cells via
`python -m src.experiment --smoke-matrix --output-dir
experiments/milestone_3b_smoke --time-limit 10`; baseline_n7 via the canonical
`src.experiment` driver (1200 s). Exact clingo lines are recorded in each
`decision.json`.

Two wording facts the paper must respect: (i) for V(2,7) and V(2,9) only the
single decisive depth was run with ASP (sufficient by depth monotonicity;
sub-ladder closed analytically); (ii) the manuscript's blanket "depth-4 UNSAT"
phrasing is wrong for VDepth(3,7), whose evidence is depth-5 UNSAT — already
logged in `experiments/n10_selection_depth_completion/manuscript_discrepancies.json`.

## 4. Direct witness upper bounds

All verifier reports read `ok: true, "verified all binary inputs"`, and every
witness was freshly re-verified during the n <= 10 completion audit
(`experiments/n10_selection_depth_completion/evidence_audit.json`).

| Paper claim | Witness | Verifier | Solver log | Runner | Status |
| --- | --- | --- | --- | --- | --- |
| V(2,6) d4 | `experiments/milestone_3b_smoke/V_t2_n6/depth_04/network.json` | `.../verifier.json` | `.../solver.json` | smoke matrix | **COMPLETE** |
| V(3,10) d6 | `experiments/baseline_n10/decisions/V_t3_n10/depth_06/network.json` | `.../verifier.json` + trace (1024 inputs) | `.../solver_raw.json`, `command.txt` | `src/run_baseline_n10_decisions.py --case V_t3_n10_depth6` | **COMPLETE** |
| U(3,6) d3 | `experiments/milestone_3b_smoke/U_t3_n6/depth_03/network.json` | `.../verifier.json` | `.../solver.json` | smoke matrix; dossier `experiments/witnesses/U_n6_t3_d3.{md,tex}` | **COMPLETE** |
| U(3,8) d4 | `experiments/baseline_n8/decisions/U_t3_n8/depth_04/network.json` (+ copy in `baseline_n8/witnesses/`) | `.../verifier.json` | `.../solver.json` + mirror in `baseline_n8/raw/` | `src.experiment` driver, 1800 s | **COMPLETE** |
| U(4,8) d4 | `experiments/baseline_n8/decisions/U_t4_n8/depth_04/network.json` (+ copy) | `.../verifier.json` | `.../solver.json` + mirror | same | **COMPLETE** |
| U(3,10) d5 | `experiments/baseline_n10/decisions/U_t3_n10/depth_05/network.json` | `.../verifier.json` + trace | `.../solver_raw.json`, `command.txt` | `src/run_baseline_n10_u_decision.py --case U_t3_n10_depth5` | **COMPLETE** |
| U(4,10) d5 | `.../U_t4_n10/depth_05/network.json` | same layout | SATISFIABLE, 352.6 s | same runner | **COMPLETE** |
| U(5,10) d5 | `.../U_t5_n10/depth_05/network.json` | same layout | SATISFIABLE, 51.1 s | same runner | **COMPLETE** |
| V(4,9) d7 | `experiments/baseline_n9/decisions/V_t4_n9/depth_07/network.json` | `.../verifier.json`; re-replayed at final-audit time (manifest `v4_depth7_replayed_verifier.ok = true`) | `.../solver.json` | `src.experiment` driver | **COMPLETE** |

Lower-bound sides of the n = 10 cells are derived (monotonicity from the n = 9
UNSAT runs in `experiments/baseline_n9/decisions/`, U(5,10) additionally via
U-duality), documented per cell in `experiments/baseline_n10/n10_depth_table.csv`.

## 5. Later witnesses

| Paper claim | Evidence | Status |
| --- | --- | --- |
| U(2,17) d6, independently verified | `experiments/u2_n17_d6_witness_search/20260808_030007Z/`: `network.json` (42 comparators, layers 8,7,6,6,7,8), **two** verifiers — `verifier_primary.json` (ok) and `verifier_independent.json` (131072 = 2^17 inputs, 0 failures), `command.json`, `preflight.json` (thor, aarch64, clingo 5.8.0, z∈{1,2} reduction argument), `run_summary.json` (SATISFIABLE, 92.3 s, SHA-256 map), `artifact_manifest.sha256`, snapshots of `common.lp`/`target_u.lp`/`instance.lp`, self-contained `run_search.py` | **COMPLETE** (double-verified) |
| U(3,11) d6 | `experiments/baseline_n11_17/decisions/U_t3_n11/depth_06/` — `network.json`, `verifier.json` + trace (2048 inputs), `result.json` VERIFIED_SAT (252.6 s), runner `src/run_u_milestone1_depth6_upper_bounds.py` | **COMPLETE** (single verifier) |
| U(4,11) d6 | `.../U_t4_n11/depth_06/` (321.1 s) | **COMPLETE** (single verifier) |
| U(5,11) d6 | `.../U_t5_n11/depth_06/` (1696.0 s) | **COMPLETE** (single verifier) |

Rollup: `experiments/baseline_n11_17/u_milestone1_depth6_upper_bounds.{json,csv}`;
depth-5 attempts were TIMEOUT (`u_milestone1_n11_n12_summary.json`), so the
recorded intervals are [5,6].

## 6. Weight game and closure

**Weight game** — implementation `src/weight_game.py` (+
`tests/test_weight_game.py`), runner
`python3 -m experiments.weight_game.run_sweep` (resumable, MAX_ROUNDS = 11).

- `experiments/provenance_closure/game_values_n_le_10.json` contains exactly
  the paper's direct inputs: `V_2_5: 4`, `U_3_5: 3`, `U_2_9: 5`, `U_3_9: 5`,
  `U_4_9: 5`. These are the five type-5 irredundant inputs in
  `closure_report.json` (`G_V2_5, G_U3_5, G_U2_9, G_U3_9, G_U4_9`). **COMPLETE.**
- `experiments/weight_game/results_n11_17.json` — 130 cells, all
  `complete: true` (U-type full for t <= n/2, 11 <= n <= 17, including
  `A_U(2,17) = 6`); `sweep_log.txt` is the audit trail. 15 V-type cells
  deliberately unevaluated (wallclock budget); 4 of them (n = 17,
  12 <= t <= 15) are declared unchecked in README and manuscript.
- **Gap:** no artifact enumerates the **44 improved lower endpoints**; that
  list exists only in `manuscript/main.tex` (lines ~1086–1100). **PARTIAL.**

**Closure / bound propagation** — engine `src/selection_bounds.py`.

- n <= 10: `src/complete_n10_selection_depths.py` (`--prepare/--run-all/--generate`)
  produced `experiments/n10_selection_depth_completion/` —
  `bounds_table.{csv,json}`, `evidence_audit.json` (110 exact cells, 0 errors,
  0 unresolved; fresh re-verification of every stored witness),
  `exact_tables.{md,tex}` (value-identical to the manuscript's n <= 10 tables),
  `final_report.md`, `manifest.json`, `tests_result.json` (421 passed).
  Strict provenance closure `experiments/provenance_closure/closure.py` →
  `closure_report.json`: **19 irredundant inputs = 6 UNSAT + 8 witnesses +
  5 game values**; published values used only as verification targets.
  **COMPLETE.**
- 11 <= n <= 17: `experiments/selection_bounds_n11_17/` (bounds, derivation
  graph, frontier plan) and
  `experiments/baseline_n11_17/{constructive_upper_bounds,paper_ready_upper_bounds}/`
  (306 entries, provenance audit). **PARTIAL:** these artifacts (2026-07-10/17)
  predate the weight game (2026-08-04); nothing regenerates the final published
  n = 11..17 tables with game-improved lower endpoints — those tables are
  hand-assembled inline in `main.tex` (zero `\input`); the generated
  `paper_table_{U,V}.tex` are placeholders.

## 7. V(4,9): dependency structure and manifest verification

Certificate layer (`experiments/v49_d6_final/`): `final_certificate.json`
(result `VDepth(4,9)=7`, status `AFFIRMATIVE`, 0 problems),
`proof_dependency_graph.json` (14 nodes, 15 edges), `evidence_manifest.json`
(588 files, status `VERIFIED`), `evidence_index.md`, `bundle/` (frozen copy of
sources, docs, tests, solver files, branch definitions, raw logs),
`bundle.sha256`, and the later tail-leaf analysis set
(`tail_leaf_analysis.json`, `tail_closure_ledger.csv`, `tail_family_summary.csv`,
`tail_leaf_table.csv`; writeups in `docs/v49_d6_final/`).

Reconstructed chain (all stages verified present):

1. **Seed**: VDepth(3,9) >= 6 — `experiments/baseline_n9/decisions/V_t3_n9/depth_05/` UNSAT.
2. **Lemmas**: V4⟹V3 restriction and empty-layer elimination
   (`docs/v_boundary_and_v49_support_partition.md`) ⟹ depth-6 search may
   assume all layers nonempty.
3. **Parent partitions**: direct UNSAT branches in
   `v49_d6_support_partitioned` (T_*), `v49_d6_refined_partitioned`,
   `v49_d6_partner_partitioned`, `v49_d6_bp5_final_layer_partitioned`,
   `v49_d6_six_leaf_reduced` — all **37** branch artifacts cited by absolute
   path from the closure certificate exist (after the documented
   `Codex→Agent` rename).
4. **Closure audit**: `experiments/v49_d6_closure_audit/coverage_certificate.json`
   — `COVERAGE_AUDIT_PASSED`, 15,720 leaf classifications, 0 uncovered,
   residual families A5, B6, B7, B8, B9.
5. **Tail census**: `experiments/v49_d6_l5_tail_census/coverage_certificate.json`
   — `PASSED`; 3 residual parents (`A5_residual_L5eq3`, `B6_residual_L5eq3`,
   `B6_residual_L5eq4`) → **75** pairwise-disjoint children.
6. **Leaf UNSAT**: screening 49/75 UNSAT + 26 TIMEOUT
   (`v49_d6_tail_partitioned/reports/screening_summary.csv`); overnight rerun
   26/26 UNSAT (`overnight/20260707_234125/overnight_summary.csv`,
   `selection_certificate.json`); raw clingo JSON per child under
   `{screening,overnight/...}/raw/<branch>/solver.json`.
7. **Pruning soundness**: `v49_d6_topology_pruning/validation.json` (+ tests).
8. **Post-UNSAT audit**: `post_unsat_audit.json` — `tail_children_all_closed: true`.
9. **Upper bound**: depth-7 witness verified and **re-replayed** at final-audit
   time (`manifest.audit_summary.v4_depth7_replayed_verifier.ok = true`).
   `baseline_n9` depth_06 is TIMEOUT, which is why the partitioned campaign exists.
10. **Post-publication re-audit**: `v49_d6_l5eq1_reaudit/20260807_234847Z`
    (`all_raw_unsat: true`, instance-hash identity checked).

**File-existence and hash verification performed in this inventory:**

| Check | Result |
| --- | --- |
| 179 evidence files referenced by `proof_dependency_graph.json` | **all exist** |
| 197 hash records in the graph | 193 match; 2 files diverged (see below) |
| 588 manifest files, repo side | **all exist** |
| 588 manifest files, bundle side | **all exist, all SHA-256 match** |
| 588 entries in `bundle.sha256` | **0 failures** |
| 37 absolute-path branch artifacts in `coverage_certificate.json` | **all exist** |

Diverged files (both benign, bundle preserves the as-used versions):
`experiments/v49_d6_closure_audit/coverage_certificate.json` differs from its
bundle copy **only** in the `/home/ono/Codex` → `/home/ono/Agent` path prefix
(verified: zero non-path diff lines); `src/experiment.py` was extended after
bundling (adds `run_depth_decision` and stderr capture).

**Not inside the 588-file bundle:** the five parent-partition directories of
stage 3 (the bundle covers `tail_partitioned`, `l5_tail_census`,
`topology_pruning`, the closure certificate, and `baseline_n9` only). The
public artifact must ship them, or the certificate's references dangle.
Earlier generations (`v49_d6_partitioned`, `v49_d6_l5_partitioned`) and the
solver-config benchmark are superseded/non-evidence but referenced by the
re-audit. **Missing:** the output of
`experiments/provenance_closure/audit_v49_d6.py`
(`v49_d6_branch_ledger.csv`) does not exist; the script is read-only and cheap
to rerun, but was not run during this inventory.

## 8. Extra experiment (excluded from artifact claims)

`u3_n11_d5_full_terminal_profile_audit_bundle.tar.gz` (16,570,129 bytes,
SHA-256 in `artifact_inventory.json`) and the `experiments/u3_n11_d5_*`
directories are the preserved U(3,11) depth-5 terminal-profile campaign.
Per instructions, treated as **EXTRA**: not incorporated into the publication
artifact's claimed results. Related note:
`experiments/provenance_closure/depth2_family_verification.json` reports the
retained depth-2 representative family is semantically incomplete (596,326 of
605,305 reachable state sets uncovered) — relevant to that project, not to any
claim of the current paper.

## 9. Missing / risk summary (what the public artifact must address)

1. **(high)** Nothing is committed to git — HEAD predates nearly all evidence
   (165 dirty/untracked entries). The artifact cannot be pinned to a commit as-is.
2. **(high)** The published n = 11..17 tables and the 44-cell improvement list
   have no generating artifact (manuscript-only composition of closure output +
   weight-game values).
3. **(medium)** The five V(4,9) parent-partition dirs are outside the evidence
   bundle though cited by the closure certificate.
4. **(medium)** Stale `/home/ono/Codex` absolute paths inside certificates,
   `command.txt` files, screening CSVs, and `tail_leaf_analysis.json`; need a
   path-mapping note or normalization in the public artifact.
5. **(medium)** `v49_d6_branch_ledger.csv` (post-publication genealogy audit
   output) missing; regenerable.
6. **(low)** U(3/4/5,11) witnesses single-verified; U(2,17) is the only
   double-verified witness.
7. **(low)** V(2,7)/V(2,9) sub-ladders analytic (Nakano), not ASP; VDepth(3,7)
   manuscript phrasing says depth-4 UNSAT, evidence is depth-5 UNSAT (already
   logged in `manuscript_discrepancies.json`).
8. **(low)** No `stderr.log` in June-vintage runs; `V(2,2^k)` citation TODO;
   `baseline_n9/{derived,witnesses}/` empty; rendered dossiers exist only for
   U(3,6) and V(3,6).
9. **(info)** clingo exists only as the Python module (5.8.0); reproduction
   docs must use `.venv/bin/python -m clingo`.

All per-file SHA-256 hashes (148 files), the full per-result records, and the
complete `git status --porcelain` snapshot are in `artifact_inventory.json`.
