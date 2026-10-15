# Packaging Report: CANDAR 2026 Public Computational Artifact

Consolidated report of the inventory and packaging work that produced this
artifact for the paper **"Exact Depths and Bounds for Small Selection
Networks"** (CANDAR 2026). All work was performed on the original
experiment machine (`thor`, aarch64, Linux, Python 3.12.3, clingo 5.8.0 as
the pyclingo module) on 2026-10-15, with the source repository
`/home/ono/Agent` (git HEAD `7c06ad41aa6b`, dirty working tree) treated as
strictly read-only.

Companion documents in this directory:

- `ARTIFACT_INVENTORY.md` / `artifact_inventory.json` — the read-only
  pre-packaging inventory (phase 1 output).
- `artifact_inventory_details_20261015.md` — file-level inventory notes.
- `COPY_AUDIT.md`, `copy_log.json`, `original_file_checksums.sha256` —
  copy provenance (phase 2).
- `../VERIFICATION_REPORT.md` — the packaging-stage verification results
  (phase 3), summarized again below.

---

## Phase 1: Read-only inventory (2026-10-15)

Every computational result used by the paper was located in the original
repository and mapped to its evidence files, generator sources, recoverable
commands, and verification reports; SHA-256 hashes of 148 key files were
recorded. Findings that drove the packaging:

- All 14 baseline results (6 ASP UNSAT lower bounds, incl. V(4,9) via the
  partitioned campaign, and 8 verified n <= 10 witnesses), the U(2,17)
  doubly verified witness, the three U(t,11) depth-6 witnesses, the weight
  game, and the n <= 10 closure were COMPLETE in the original record.
- The V(4,9) final certificate verified end to end: 588-file evidence
  manifest (repo and frozen bundle sides), 588 `bundle.sha256` entries,
  179 dependency-graph evidence files, and the 37 branch artifacts cited
  by the closure coverage certificate.
- Two benign divergences between the live tree and the frozen bundle
  (coverage-certificate path-prefix rewrite `/home/ono/Codex ->
  /home/ono/Agent`; post-bundle extension of `src/experiment.py`).
- Gaps: (i) no program reconstructed the final n = 11..17 tables with the
  44 weight-game lower-endpoint improvements (manuscript-only
  composition); (ii) the output of the post-hoc genealogy audit
  `audit_v49_d6.py` (`v49_d6_branch_ledger.csv`) was missing; (iii) the
  five V(4,9) parent-partition directories were outside the frozen bundle;
  (iv) nothing was committed to git in the original repository.

## Phase 2: Staging (what was copied, and the one structural decision)

4,178 files (188 MB of evidence) were copied byte-for-byte
(`shutil.copy2`, hash-logged at copy time) into
`/home/ono/candar2026-selection-networks-artifact`. Scope:

- the complete V(4,9) campaign: `v49_d6_final` (frozen bundle untouched)
  plus all five parent-partition directories, closure audit, tail census,
  tail partition runs, topology pruning, the later `l5eq1` re-audit, and
  the superseded-but-referenced `v49_d6_l5_partitioned`;
- all baseline evidence n <= 10 (smoke matrix, baselines n = 7..10,
  calibration runs, the n10 completion jobs) and `baseline_n9` for the
  V(4,9) seed and witness;
- the n = 11..17 witness runs referenced by the upper-bound closure
  (whole `baseline_n11_17/decisions/`, excluding the two unused UNSAT
  campaign subdirectories), both upper-bound closures, the pre-game bound
  propagation record, and the U(2,17) run;
- weight game, strict provenance closure, relevant docs, sources, tests,
  encodings, and the original V(4,9) stage runners.

Excluded (per instructions and documented in `COPY_AUDIT.md`): the
U(3,11) depth-5 campaign in its entirety, the unused `unsat_v4_n11_d7`
attempt, superseded scratch not referenced by any final certificate,
prompt files, manuscript build products, and empty directories.

**Structural decision.** The task sketch placed evidence under
`asp/`, `witnesses/`, `closure/`. During verification it became clear that
the certificates, the proof dependency graph, `src/v49_d6_closure_audit.py`,
`audit_v49_d6.py`, and several tests all resolve evidence via the original
repository-relative `experiments/...` paths. Invoking the sketch's own
escape clause ("preserve enough of that structure that references remain
understandable", "structure is a guideline"), the evidence was placed in a
single top-level `experiments/` + `docs/` mirror preserving original
relative paths, so every stored reference resolves at the artifact root
and every audit tool runs unmodified. The claim-oriented view is provided
by `PAPER_RESULTS.md` (and `weight_game/` remains as a curated directory).

## Phase 3: New programs written for the artifact

1. **`scripts/reconstruct_final_tables.py`** (+
   `tests/test_reconstruct_final_tables.py`,
   `scripts/expected_paper_tables_n11_17.json`): mechanically rebuilds all
   196 cells of the final n = 11..17 tables from stored inputs only —
   exact n <= 10 table, audited paper-ready upper bounds, weight-game
   values, the verified U(2,17) witness, and structural rules with
   literature constants. Pre-game lower bounds are recomputed from scratch
   and cross-checked against the stored `lower_bound_if_known` column.
   Hard failure gates: exactly 44 improvements (42 U-type, 2 V-type at
   (n,t) = (17,8), (17,9)), each exactly one layer; U(2,17) and U(15,17)
   exact at 6; lower <= upper everywhere; cell-by-cell equality with the
   hand-transcribed manuscript tables (verification target only, never an
   input). Outputs in `generated/`.
2. **`scripts/verify_all_witnesses.py`**: exhaustive re-verification of
   every stored SAT witness on all 2^n binary inputs.
3. **`scripts/check_v49_references.py`**: one-command integrity check of
   the V(4,9) evidence (manifest, bundle checksums, dependency graph,
   closure-certificate branch references).
4. **`tests/conftest.py`**: gates the two tests that regenerate the live
   V(4,9) coverage certificate in place (original tool behavior), so a
   plain `pytest` run leaves all copied evidence untouched
   (`ARTIFACT_ALLOW_CERT_REBUILD=1` opts in).

## Phase 4: Verification results (all green)

| Check | Result |
| --- | --- |
| Test suite (`pytest`) | 186 passed, 2 skipped (the opt-in certificate-rebuild tests) |
| Stored SAT witnesses, exhaustive re-verification | 103/103 ok; every verdict agrees with the stored verifier reports |
| n <= 10 strict closure rerun (scratch) | regenerated report identical to the preserved one; irredundant inputs confirmed: 6 UNSAT + 8 witnesses + 5 game values |
| Final n = 11..17 table reconstruction | RECONSTRUCTION OK; 44 improvements (42 U / 2 V); manuscript agreement on all 196 cells; U(2,17) = U(15,17) = 6 exact |
| V(4,9) integrity | 588/588 manifest files, 588/588 bundle checksums, 179 graph evidence files, 193 hash records, 37/37 branch references; only the two documented divergences |
| V(4,9) branch ledger (newly generated, `generated/v49_d6_branch_ledger.csv`) | 20 branches: 17 direct UNSAT, 3 handed to the 75-leaf tail, all leaves UNSAT; rerun instances byte-identical; no unresolved branch |
| Copy integrity | 144/144 applicable inventory hashes match; post-packaging spot check of 307 copies unchanged; `CHECKSUMS.sha256` verifies |

Not rerun by design: the expensive V(4,9) depth-6 solver campaign, the
full weight-game sweep, and the baseline searches (stored evidence
verified instead; individual reruns documented in `REPRODUCIBILITY.md`).

## Phase 5: Findings worth the authors' attention

1. **U(5,14) and U(9,14) improvement mechanism.** The paper states that
   all 44 improved cells follow from "a directly computed game value at
   that cell, its dual n-t, or both". For exactly these two cells the raw
   game value is 5; the published bound 6 follows from the game-improved
   cell U(4,13) = U(9,13) by n-monotonicity and mirror duality. The
   published values are correct and unchanged; the prose is imprecise for
   these two cells. If the camera-ready can still be edited, a one-phrase
   adjustment would make it exact. Recorded in the `mechanism` column of
   `generated/weight_game_improvements.csv`.
2. **The closure-audit tool regenerates its certificate in place.**
   `build_certificate()` writes `coverage_certificate.json` as a side
   effect; this also explains the historical path-prefix divergence in the
   original repository (the live certificate was regenerated there after
   the repository moved). In the artifact this is handled by the conftest
   gate; the as-published certificate is permanently preserved inside the
   frozen `v49_d6_final/bundle/`.
3. The VDepth(3,7) manuscript phrasing issue ("depth-4 UNSAT" vs the
   actual depth-5 UNSAT evidence) and the analytic (Nakano) closure of the
   V(2,7)/V(2,9) sub-ladders, both already logged during the inventory,
   are stated explicitly in `PAPER_RESULTS.md`.

## Final state

- About 4,200 files, 196 MB; largest file 8.61 MB; nothing near GitHub
  limits.
- License: MIT (`LICENSE`), added at publication time.
- Published to
  `https://github.com/ono-work/selection-networks-artifact-202610`
  (tag `candar2026-v1.0`); the publication commit, push, and tag details
  are recorded in the repository history itself.
