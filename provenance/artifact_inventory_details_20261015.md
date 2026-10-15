# Artifact Inventory: Detailed Investigation Notes (2026-10-15)

Supplementary detail behind the consolidated `ARTIFACT_INVENTORY.md` /
`artifact_inventory.json` at the repository root. Produced during the read-only
inventory for the CANDAR 2026 paper "Exact Depths and Bounds for Small
Selection Networks" on the original experiment machine (`thor`). No experiment
file was modified.

Sections 1-2 are the two exploration reports (lightly edited); Section 3 is
the V(4,9) manifest-verification log performed directly in the main session.

---

## 1. Baseline ASP lower bounds and small witnesses

**Naming convention.** Paper notation `V(t,n)` / `VDepth(t,n)` maps to
directories named `{KIND}_t{t}_n{n}` with per-depth subdirectories `depth_NN`.
Note `bounds_table.csv` is keyed `kind,n,t` (n before t).

**Shared encoding files:**

- `solver/common.lp` (2026-06-22) — comparator-selection + 0/1 propagation core
- `solver/target_v.lp` — ordered (V) target constraints
- `solver/target_u.lp` — unordered (U) target constraints
- `src/generate_instance.py` — emits `n/t/depth/input/zero_count/bit` facts into `instance.lp`
- `src/experiment.py`, `src/parse_model.py`, `src/solver.py`, `src/verify.py` (independent exhaustive binary verifier)

**Driver behaviour** (`src/experiment.py`). `_run_one_depth(...)` creates
`output_dir/depth_{depth:02d}/` and writes `instance.lp`, `solver.json`,
`stderr.log` (later revisions only), `decision.json`, and for SAT
`network.json` + `verifier.json`. It shells out via

```
.venv/bin/python -m clingo --outf=2 --time-limit=<T> -n 1 \
    solver/common.lp solver/target_{v|u}.lp <depth_dir>/instance.lp
```

(`CLINGO_COMMAND = (".venv/bin/python","-m","clingo")` in `src/solver.py`).
Status mapping: `UNKNOWN`/python-timeout → `TIMEOUT`; `UNSATISFIABLE` →
`UNSAT`; `SATISFIABLE` → parse model, verify all 2^n binary inputs, `SAT` only
if `verifier_ok`, else `VERIFICATION_FAILED`. `run_exact_depth` loops depths
0,1,2,... writing per-case `summary.csv` + `case_result.json`.

**Path caveat.** Commands recorded before 2026-08 contain
`/home/ono/Codex/...` (former checkout path); only
`n10_selection_depth_completion` records `/home/ono/Agent/...`.

### 1.1 VDepth(2,7) >= 5 — depth-4 UNSAT — COMPLETE

- Directory: `experiments/n10_selection_depth_completion/jobs/V_t2_n7_d4/` —
  authoritative (`baseline_n7` never ran a `t=2` case).
- `depth_04/decision.json`: `status UNSAT`, runtime 0.431 s; `depth_04/solver.json`:
  `Result UNSATISFIABLE`, `pyclingo 5.8.0`; `stderr.log` (0 B); `instance.lp` (15,544 B).
- `independent_audit.json`: `solver_result UNSATISFIABLE`, SHA-256 of decision/instance/raw solver.
- Command: `.venv/bin/python -m clingo --outf=2 --time-limit=1200 -n 1 solver/common.lp solver/target_v.lp .../depth_04/instance.lp`
- Runner: `src/complete_n10_selection_depths.py` Job `V_t2_n7_d4` ("decide VDepth(2,7) in [4,5]").
- Reports: `final_report.md` row `V_t2_n7_d4 | UNSAT | 0.431 | VDepth(2,7)=5`;
  `bounds_table.csv` `V,7,2,5,5,5,EXACT`.
- Ladder: depths 0-3 never run as ASP — closed by the Nakano corollary
  (`lower_sources: NAKANO_LOWER + NEW_DECISION`). Logically sufficient by depth
  monotonicity.

### 1.2 VDepth(2,9) >= 6 — depth-5 UNSAT — COMPLETE

- Directory: `experiments/n10_selection_depth_completion/jobs/V_t2_n9_d5/`.
- `depth_05/decision.json`: `UNSAT`, runtime 1008.15 s; `solver.json`
  `UNSATISFIABLE`; `instance.lp` (79,196 B); `independent_audit.json` UNSAT.
- Command as above with `--time-limit=7200`.
- Ladder: depths 0-4 closed by Nakano corollary, not ASP.

### 1.3 VDepth(3,5) >= 5 — depth-4 UNSAT — COMPLETE, full ladder

- Directory: `experiments/milestone_3b_smoke/V_t3_n5/` (2026-06-22; no
  `baseline_n5` exists).
- `depth_00..04/decision.json` all `UNSAT` (depth_04 runtime 0.034 s);
  `depth_05/decision.json` `SAT, verifier_ok true, 10 comparators`.
- Witness bonus: `depth_05/network.json` (layers 2,2,2,2,2) +
  `depth_05/verifier.json` ok=true.
- Runner: `python -m src.experiment --smoke-matrix --output-dir experiments/milestone_3b_smoke --time-limit 10`.
- `case_result.json`: `minimum_depth 5, MINIMUM_FOUND, tested_depths [0..5]`.
- Re-audit: `n10_selection_depth_completion/evidence_audit.json` previous_exact
  `('V',5,3)` — fresh verification, 32 inputs, matching_layers true.
- No `stderr.log` (June driver vintage).

### 1.4 VDepth(3,7) >= 6 — depth-5 UNSAT — COMPLETE, full ladder

- Directory: `experiments/baseline_n7/decisions/V_t3_n7/` (2026-07-03).
- `depth_00..05/decision.json` all `UNSAT` (depth_05 runtime 3.977 s);
  `depth_06` `SAT, verifier_ok true, 14 comparators`.
- Raw clingo JSON in both `decisions/.../solver.json` and mirror
  `baseline_n7/raw_solver_outputs/V_t3_n7_d05_solver.json` (full d00-d06 set).
- Witness duplicates in `baseline_n7/verified_witnesses/V_t3_n7_d06_{network,verifier}.json`.
- Reports: `baseline_n7/report.md` (rows `V(3,7) | 5 | UNSAT` and `| 6 | SAT`),
  `reports/batch_environment.json`, `reports/decision_reproducibility.json`
  (git HEAD `7c06ad41aa...`, host metadata, per-file SHA-256).
- Manuscript note: blanket "depth-4 UNSAT" phrasing is wrong for this cell;
  the evidence is depth-5 UNSAT — logged in
  `n10_selection_depth_completion/manuscript_discrepancies.json`.

### 1.5 UDepth(4,6) >= 4 — depth-3 UNSAT — COMPLETE, full ladder

- Directory: `experiments/milestone_3b_smoke/U_t4_n6/` — a genuine direct run
  (`include_u_dual_cross_checks` path), not a duality derivation.
- `depth_00..03/decision.json` all `UNSAT` (depth_03 runtime 0.048 s);
  `depth_04` `SAT, verifier_ok true, 8 comparators`, layers 2,2,2,2.
- Cross-check: `bounds_table.json` cell (U,6,4) `exact 4`
  (`PREVIOUS_COMPUTATION` + `U_DUALITY_LOWER: UDepth(2,6)=UDepth(4,6)`).
  `final_report.md` records that an earlier claim `UDepth(4,6)=3` was wrong;
  artifacts confirm 4. `tests/test_weight_game.py` guards `A_U(4,6)=3`.

### 1.6 Direct witness upper bounds (eight cells)

All witness `network.json` carry explicit `{"kind","n","t","depth","layers"}`;
all verifier reports read `ok: true, "verified all binary inputs"`
(`src/verify.py` re-simulates every binary input and independently re-checks
the matching condition; it does not reuse the ASP encoding).

| Claim | Directory | Key files | Status |
|---|---|---|---|
| V(2,6) d4 | `experiments/milestone_3b_smoke/V_t2_n6` | `depth_04/{network,verifier,decision,solver}.json` (10 comparators, layers 3,3,3,1) | COMPLETE |
| V(3,10) d6 | `experiments/baseline_n10/decisions/V_t3_n10` | `depth_06/{network,verifier,result,solver_raw}.json`, `verifier_trace_summary.json`, `command.txt`, `README.md` | COMPLETE |
| U(3,6) d3 | `experiments/milestone_3b_smoke/U_t3_n6` | `depth_03/...` (9 comparators, layers 3,3,3); rendered dossier `experiments/witnesses/U_n6_t3_d3.{md,tex}` | COMPLETE |
| U(3,8) d4 | `experiments/baseline_n8/decisions/U_t3_n8` | `depth_04/...` (15 comparators); mirrors in `baseline_n8/raw/` and `baseline_n8/witnesses/` | COMPLETE |
| U(4,8) d4 | `experiments/baseline_n8/decisions/U_t4_n8` | `depth_04/...` (16 comparators); mirrors as above | COMPLETE |
| U(3,10) d5 | `experiments/baseline_n10/decisions/U_t3_n10` | `depth_05/...` + trace summary (1024 inputs), `preflight.json/.md` | COMPLETE |
| U(4,10) d5 | `experiments/baseline_n10/decisions/U_t4_n10` | `depth_05/...` (SATISFIABLE, 352.6 s) | COMPLETE |
| U(5,10) d5 | `experiments/baseline_n10/decisions/U_t5_n10` | `depth_05/...` (SATISFIABLE, 51.1 s) | COMPLETE |

Runners: smoke matrix for n<=6; `src.experiment` driver (1800 s) for
baseline_n8; `src/run_baseline_n10_decisions.py --case V_t3_n10_depth6
--timeout-seconds 7200` for V(3,10); `src/run_baseline_n10_u_decision.py
--case U_t{3,4,5}_n10_depth5 --timeout-seconds 7200` for the n=10 U cells
(exact clingo lines in each `command.txt`).

Lower-bound sides of the n=10 cells are documented as derived in
`experiments/baseline_n10/n10_depth_table.csv`: monotonicity from the
baseline_n9 UNSAT runs (`V_t3_n9/depth_05`, `U_t3_n9/depth_04`,
`U_t4_n9/depth_04`), with U(5,10) additionally via U-duality from UDepth(4,9).

### 1.7 Cross-cutting provenance for all 13 baseline results

`experiments/n10_selection_depth_completion/` (2026-08-02) consolidates:

- `evidence_audit.json` — 3 new jobs + 53 `previous_exact` entries; every
  stored SAT witness freshly re-verified (`checked_boolean_inputs` 32/64/128/
  256/1024 as appropriate, `matching_layers true`, witness SHA-256);
  `validation: errors [], exact_cells 110, unresolved []`.
- `bounds_table.{csv,json}` — per-cell lower/upper/exact with provenance
  strings; all 13 paper claims match.
- `final_report.md`, `exact_tables.{md,tex}`, `manifest.json` (git commit
  `7c06ad4`, `dirty: true`, full status, source SHA-256s), `tests_result.json`
  (421 passed), `manuscript_discrepancies.json`.
- Reproduction: `.venv/bin/python -m src.complete_n10_selection_depths
  --prepare | --run-all | --generate`.

Minor repo-wide gaps (none invalidate a claim): no `stderr.log` in
June-vintage runs; `baseline_n10` uses a different per-run layout
(`result.json` etc., no `decision.json`); pre-August commands reference
`/home/ono/Codex`; `baseline_n9/{derived,witnesses}/` are empty directories.

---

## 2. Weight game, closure, U(2,17), U(t,11), manuscript

### 2.1 Weight game — COMPLETE (one caveat)

Implementation: `src/weight_game.py` (2026-08-04), `tests/test_weight_game.py`,
`experiments/weight_game/run_sweep.py`.

What it computes: a finite-state parallel integer-weight game. State = count
vector over weights `1..T`, `T = t+1` (absorbing). One round = a matching; a
matched pair `(a,b)` becomes `(min(a,b), min(T, a+b))`. BFS restricted to
maximum matchings with Pareto domination pruning; `compute_A(kind,t,n)`
returns `A_U(t,n)` / `A_V(t,n)`, proved `<= UDepth/VDepth` by the paper's
theorem. Domination targets: U: `counts[T-1] >= n - t`; V: `|{w<T}| <= t` and
sorted ascending `S_i >= i`.

Outputs:

- `experiments/weight_game/results_n11_17.json` — 130 cells keyed
  `{kind}_{t}_{n}`, each `{A, time_seconds, rounds_recorded,
  max_frontier_size, complete}`; all `complete: true`.
- `experiments/weight_game/sweep_log.txt` — one line per cell (incl.
  `U t=2 n=17 (dual t=15): A=6`).
- `experiments/provenance_closure/game_values_n_le_10.json` — the n<=10 values
  used by the closure; contains exactly `V_2_5: 4`, `U_3_5: 3`, `U_2_9: 5`,
  `U_3_9: 5`, `U_4_9: 5`, matching `closure_report.json`
  `by_type[5] = [G_U2_9, G_U3_5, G_U3_9, G_U4_9, G_V2_5]` and the manuscript
  prose verbatim.

Invocation: `python3 -m experiments.weight_game.run_sweep` (resumable,
`MAX_ROUNDS = 11`).

Coverage: U-type complete for `t <= floor(n/2)`, 11<=n<=17 (47 cells). V-type
83 cells; 15 cells deliberately unevaluated under
`V_WALLCLOCK_BUDGET_SECONDS = 60*55`, of which the four `n=17, 12<=t<=15`
cells are declared unchecked in README and manuscript (the other 11 are
already exact by padding/sorting inheritance).

Caveat: **no artifact enumerates the 44 improved lower endpoints** — the list
exists only in `manuscript/main.tex` (~lines 1086-1100: V-type n=17 t=8,9 = 2
cells; U-type 42 cells). `grep` for "forty-four"/"44 cells" over all
md/json/csv/txt returns nothing outside the TeX. No docs/ writeup; README-only.

### 2.2 Closure / bound propagation — COMPLETE (n<=10) / PARTIAL (11-17)

Modules:

| path | role |
|---|---|
| `src/selection_bounds.py` | propagation engine (`Derivation`, `BoundEntry`, `BoundTable`); no solver calls |
| `src/complete_n10_selection_depths.py` | n<=10 audit + completion; JOBS `V_t2_n7_d4`, `U_t2_n9_d4`, `V_t2_n9_d5` |
| `src/plan_selection_frontier_n11_17.py` | n=11-17 derived bounds + frontier plan; read-only |
| `src/constructive_upper_bounds.py` | constructive upper-bound closure to n=17 (two-block composition, sorting fallback, padding); verifies generated networks via `src.verify.verify_binary` |
| `src/generate_paper_ready_upper_bounds.py` | solver-free paper-ready CSV/JSON/TeX with provenance/caveat columns |
| `experiments/provenance_closure/closure.py` | strict provenance closure for n<=10; 7 provenance types; published tables only as VERIFY targets |
| `experiments/provenance_closure/verify_depth2_family.py` | post-hoc check of the U(3,11) depth-2 family |
| `experiments/provenance_closure/audit_v49_d6.py` | read-only V(4,9) genealogy audit (output CSV missing, see 3.5) |

Key outputs:

- n<=10: `experiments/n10_selection_depth_completion/` (see 1.7); the
  paper-ready pair `exact_tables.{md,tex}` is value-identical to the
  manuscript's `tab:v-n10` / `tab:u-n10`.
- `experiments/provenance_closure/closure_report.json` — **19 irredundant
  inputs (6 UNSAT / 8 witnesses / 5 game)**; `claimed_9_unclosed` shows the
  old 9-input set fails (`V(2,5) got [3,4] want 4`, etc.).
- `experiments/provenance_closure/depth2_family_verification.json` — negative
  result: the retained U(3,11) depth-2 family covers 8,979 of 605,305
  reachable state sets (596,326 missing). Relevant to the EXTRA n=11 campaign,
  not to any current paper claim.
- 11-17: `experiments/selection_bounds_n11_17/{bounds_summary.json,
  bounds_table.csv, derivation_graph.json, frontier_experiments.csv/.md}`
  (2026-07-10); `experiments/baseline_n11_17/constructive_upper_bounds/` and
  `.../paper_ready_upper_bounds/` (2026-07-17; `audit_summary.json`
  entry_count 306, `formula_citation_status: citation TODO`).

PARTIAL because: both 11-17 artifact sets predate `weight_game.py`
(2026-08-04); nothing imports `src.weight_game` except the sweep and its test.
The published n=11-17 tables (which include game-improved lower endpoints) are
hand-assembled in the TeX. `paper_table_{U,V}.tex` are degenerate placeholders.

### 2.3 U(2,17) depth-6 witness — COMPLETE, double-verified

`experiments/u2_n17_d6_witness_search/20260808_030007Z/`:

- `network.json` — depth 6, kind U, 42 comparators, layer sizes [8,7,6,6,7,8].
- `verifier_primary.json` — ok=true, all binary inputs.
- `verifier_independent.json` — `checked: 131072` (= 2^17), `failures: []`,
  ok=true; produced by `second_verifier()` inside the self-contained
  `run_search.py`.
- `command.json` — `clingo --outf=2 --stats=2 -n 1 --time-limit=900
  solver/common.lp solver/target_u.lp .../instance.lp`.
- `preflight.json` — clingo/pyclingo 5.8.0, host thor, aarch64,
  `input_zero_counts [1,2]` with a written reduction argument for why
  z in {1,2} is complete; scope statement "SAT witness search only".
- `run_summary.json` — SATISFIABLE, verified_sat true, 92.27 s, SHA-256 map;
  `artifact_manifest.sha256` (13 entries); snapshots of
  `common.lp`/`target_u.lp`/`instance.lp` with source-vs-snapshot hash match.

Combined with `A_U(2,17)=6` this closes `UDepth(2,17) = UDepth(15,17) = 6`.
Only gap: no directory-level README.

### 2.4 U(3,11), U(4,11), U(5,11) depth-6 witnesses — COMPLETE (single verifier)

Runner `src/run_u_milestone1_depth6_upper_bounds.py` (DEPTH=6); prior depth-5
pass `src/run_u_milestone1_n11_n12.py` returned TIMEOUT for all three cells.

Per cell `experiments/baseline_n11_17/decisions/U_t{3,4,5}_n11/depth_06/`:
`network.json`, `result.json` (`VERIFIED_SAT`, `current_interval [5,6]`,
`previous_depth5_status TIMEOUT`), `verifier.json` ok=true,
`verifier_trace_summary.json` (2048 = 2^11 inputs), `solver_raw.json`
(SATISFIABLE; runtimes 252.6 / 321.1 / 1696.0 s), `command.txt` (old
`/home/ono/Codex` prefix), `README.md`.

Rollups: `u_milestone1_depth6_upper_bounds.{json,csv}`, preflight files;
writeups in `docs/n11_17/`. Gap vs 2.3: single verifier only.

### 2.5 Manuscript

Main file `manuscript/main.tex` (IEEEtran conference, 2026-08-08 build with
`main.pdf` etc.; bibliography `manuscript/selection.bib`). **Zero `\input`**
directives — all 7 tables inline: `tab:seeds` (l.1403), `tab:v-n10` (1549),
`tab:u-n10` (1574), `tab:v-depth` (1632), `tab:v-depth-b` (1654),
`tab:u-depth` (1676), `tab:u-depth-b` (1698). The n<=10 pair has a value-
identical generator (`exact_tables.tex`); the four n=11-17 tables have none.

---

## 3. V(4,9) dependency structure and manifest verification (main session)

### 3.1 Certificate layer

`experiments/v49_d6_final/`: `final_certificate.json` (result
`VDepth(4,9)=7`, status AFFIRMATIVE, problems []),
`proof_dependency_graph.json` (14 nodes, 15 edges),
`evidence_manifest.json` (588 files, status VERIFIED; audit_summary includes
`closure_certificate_passed true`, screening counts UNSAT 49 / TIMEOUT 26,
tail census 75, topology validation PASSED, v3 depth-5 UNSATISFIABLE, v4
depth-7 SATISFIABLE with stored and replayed verifier both ok),
`evidence_index.md`, `bundle/` (frozen docs/experiments/scripts/solver/src/
tests), `bundle.sha256` (588 entries), `BLOCKED.md` ("Not Blocked" sentinel),
and the later (2026-07-08 09:33) tail-leaf analysis set
(`tail_leaf_analysis.json`, `tail_closure_ledger.csv`,
`tail_family_summary.csv`, `tail_leaf_table.csv`).

### 3.2 Dependency graph nodes (ids and classifications)

`V3_9_DEPTH5_UNSAT` (SOLVER_UNSAT) → `EMPTY_LAYER_ELIMINATION`
(MATHEMATICAL_LEMMA, with `V4_IMPLIES_V3`) →
`ALL_LAYERS_NONEMPTY_IN_DEPTH6_SEARCH` (DERIVED_CONCLUSION) →
`TERMINAL_PROFILE_COVERAGE` and `NO_REPEAT_REDUCTION` (ARTIFACT_AUDIT, both on
`v49_d6_closure_audit/coverage_certificate.json`) →
`THREE_RESIDUAL_PARENT_COVERAGE` → `TAIL_CENSUS_75_WAY_PARTITION` (77 evidence
files) → `TAIL_CHILDREN_75_UNSAT` (SOLVER_UNSAT, 78 evidence files; also fed
by `TOPOLOGY_PRUNING_UNIQUE_MIN_SOUND` and
`TOPOLOGY_PRUNING_DEPENDENCY_CONE_SOUND`, both EXHAUSTIVE_VERIFIER_CHECK) →
`V4_9_DEPTH6_UNSAT` → `V4_9_EXACT_DEPTH_7` (with
`V4_9_DEPTH7_WITNESS_VERIFIED`).

### 3.3 Verification performed (all read-only)

| Check | Result |
|---|---|
| 179 evidence files referenced by the graph | all exist |
| 197 hash records in the graph | 193 match; 2 diverged files (below) |
| 588 manifest files, repo side | all exist |
| 588 manifest files, bundle side | all exist, all SHA-256 match |
| 588 `bundle.sha256` entries | 0 failures |
| 37 absolute-path branch artifacts cited by `coverage_certificate.json` | all exist (after Codex→Agent mapping) |

Diverged files (benign): `experiments/v49_d6_closure_audit/coverage_certificate.json`
differs from its bundle copy only in `/home/ono/Codex` → `/home/ono/Agent`
path prefixes (verified: zero non-path diff lines, identical size);
`src/experiment.py` was extended after bundling (adds `run_depth_decision`,
stderr capture) — the bundle preserves the as-used version.

### 3.4 Chain facts confirmed from the artifacts

- Closure audit: 15,720 classifications, 0 uncovered, status
  `COVERAGE_AUDIT_PASSED`; scope "V(4,9), depth=6 special hard-instance mode";
  open residuals after prior UNSAT: A5, B6, B7, B8, B9; four closure steps
  (hard-mode definition / direct UNSAT artifacts in support partition /
  matching-size partition in refined partition / repeated-comparator reduction
  backed by `tests/test_v49_d6_closure_audit.py`).
- Referenced parent-partition dirs (by artifact count inside the certificate):
  `v49_d6_support_partitioned` (2654 refs), `v49_d6_partner_partitioned` (12),
  `v49_d6_bp5_final_layer_partitioned` (8), `v49_d6_refined_partitioned` (6),
  `v49_d6_six_leaf_reduced` (1). **These five dirs are NOT inside the 588-file
  bundle**, whose experiment coverage is: `baseline_n9` (6), `v49_d6_closure_audit`
  (1), `v49_d6_l5_tail_census` (5), `v49_d6_tail_partitioned` (535),
  `v49_d6_topology_pruning` (2).
- Tail census: `v49_d6_l5_tail_census/coverage_certificate.json` PASSED; 3
  parents `A5_residual_L5eq3`, `B6_residual_L5eq3`, `B6_residual_L5eq4`.
- Leaf UNSAT: `screening_summary.csv` 75 rows (49 UNSAT, 26 TIMEOUT);
  `overnight/20260707_234125/overnight_summary.csv` 26 rows all UNSAT;
  `selection_certificate.json`
  `every_selected_branch_belongs_to_exactly_one_class: true`;
  `post_unsat_audit.json` `tail_child_count 75, tail_children_all_closed true,
  closure_audit_returncode 0`.
- Upper bound: `baseline_n9/decisions/V_t4_n9/` has depth_06 TIMEOUT (the
  reason for the partitioned campaign) and depth_07 SAT with verifier ok;
  replayed at final-audit time.
- Post-publication re-audit: `v49_d6_l5eq1_reaudit/20260807_234847Z/`
  (`all_raw_unsat: true`, instance-hash identity checked against
  `v49_d6_l5_partitioned` inputs, environment.json records host thor).
- Git state at bundle time (recorded in the manifest): HEAD `7c06ad4`,
  already-dirty tree.

### 3.5 Missing item

`experiments/provenance_closure/audit_v49_d6.py` declares "Writes:
v49_d6_branch_ledger.csv", but that CSV does not exist anywhere in the repo.
The script is read-only over experiments and cheap; it was deliberately not
rerun during this inventory (would create a new file in `experiments/`).

---

For the consolidated per-claim status table, environment record, gap/risk
list, and SHA-256 hashes of 148 key files, see `ARTIFACT_INVENTORY.md` and
`artifact_inventory.json` at the repository root.
