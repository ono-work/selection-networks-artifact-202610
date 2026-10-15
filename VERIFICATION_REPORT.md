# Verification Report (packaging stage)

Checks run while assembling this artifact, on the original experiment
machine (`thor`, aarch64, Python 3.12.3), 2026-10-15/16. Only cheap and
moderate checks were run; no expensive ASP search was repeated. Solver-free
checks used the system Python 3.12.3; the test suite ran under the original
project virtualenv (pytest 9.1.1). Machine-readable outputs live in
`generated/`.

## 1. Unit and integration tests

`python -m pytest -q` at the artifact root (with bytecode writing and
pytest cache disabled):

```
186 passed, 2 skipped
```

Coverage of concern: comparator-network simulator and binary verifier
semantics (`test_network.py`, `test_verifier.py`, `test_u_mirror_duality.py`,
`test_render_network.py`), weight game (`test_weight_game.py`, including the
A_U(4,6)=3 guard), bound propagation (`test_selection_bounds.py`,
`test_constructive_upper_bounds.py`, `test_network_composition.py`),
V(4,9) logic (`test_v49_d6_closure_audit.py` pure parts,
`test_v49_d6_l5_tail_census.py`, `test_v49_d6_tail_screening.py`,
`test_v49_d6_topology_pruning.py`), the n <= 10 completion record
(`test_n10_selection_depth_completion.py`), and the new reconstruction
(`test_reconstruct_final_tables.py`).

The 2 skipped tests regenerate the live V(4,9) closure certificate in
place and are opt-in (`ARTIFACT_ALLOW_CERT_REBUILD=1`, see
`tests/conftest.py`).

## 2. Independent re-verification of all stored SAT witnesses

`python3 scripts/verify_all_witnesses.py` →
`generated/witness_verification_report.json`:

```
witnesses checked : 103
all ok            : true   (fresh exhaustive verification on all 2^n inputs,
                            n up to 17; every verdict agrees with the stored
                            verifier report where one exists)
```

This covers all eight n <= 10 input witnesses, the V(4,9) depth-7 witness,
the U(2,17) witness, the three U(t,11) depth-6 witnesses, and every other
witness shipped under `experiments/`.

## 3. n <= 10 closure rerun

`experiments/provenance_closure/closure.py` was rerun in the scratch
directory `generated/closure_rerun/`. The regenerated
`closure_report.json` is **JSON-equal** to the preserved
`experiments/provenance_closure/closure_report.json` (byte order of JSON
keys can vary between runs with Python hash randomization). Irredundant input
set confirmed: 6 UNSAT (`L_U4_6, L_V2_7, L_V2_9, L_V3_5, L_V3_7, L_V4_9`)
+ 8 witnesses (`W_V2_6, W_V3_10, W_U3_6, W_U3_8, W_U4_8, W_U3_10,
W_U4_10, W_U5_10`) + 5 game values (`G_V2_5, G_U3_5, G_U2_9, G_U3_9,
G_U4_9`) — exactly the sets claimed in the paper.

## 4. Mechanical reconstruction of the final n = 11..17 tables

`python3 scripts/reconstruct_final_tables.py`:

```
RECONSTRUCTION OK
  cells reconstructed     : 196 (69 exact, 127 intervals)
  weight-game improvements: 44 (42 U-type, 2 V-type at (17,8), (17,9))
  upper-bound overlays    : U(2,17) 7 -> 6 and U(15,17) 7 -> 6
                            (verified depth-6 witness + mirror duality)
  manuscript agreement    : every cell matches the transcription of the
                            final manuscript tables
  U(2,17), U(15,17)       : reconstructed exact depth 6
```

All verification gates passed: recomputed pre-game lower bounds agree with
the stored `lower_bound_if_known` column for every cell; exactly 44 cells
improve, each by exactly one layer; lower <= upper everywhere.

Finding worth noting: at U(5,14) and U(9,14) the raw game values are 5;
their published lower bound 6 follows from the game-improved cell
U(4,13) = U(9,13) via n-monotonicity and mirror duality. The published
values are correct and unchanged; the paper's one-line description of the
44 cells ("a directly computed game value at that cell, its dual, or
both") is imprecise for exactly these two cells. Recorded in the
`mechanism` column of `generated/weight_game_improvements.csv`.

## 5. V(4,9) manifests, checksums, and references

`python3 scripts/check_v49_references.py`:

```
evidence_manifest: 588/588 bundle files verified (SHA-256)
bundle.sha256    : 588 entries verified
dependency graph : 179 evidence files present, 193 hash records match
closure cert     : 37/37 absolute-path branch artifacts resolved
known divergences observed (expected): coverage_certificate.json
                   (path-prefix rewrite), src/experiment.py (post-bundle
                   extension) -- both documented, bundle preserves originals
V49 REFERENCE CHECK OK
```

The depth-6 solver campaign itself was NOT rerun.

## 6. V(4,9) branch-genealogy ledger (newly generated)

`experiments/provenance_closure/audit_v49_d6.py` (read-only over the
evidence; copied to `scripts/audit_v49_d6.py`) was run from the artifact
root on 2026-10-16, producing `generated/v49_d6_branch_ledger.csv` — this
output was missing from the original repository. Summary of its findings:

```
branches total                : 20
  closed by direct solver UNSAT : 17
  timed out, handed to tail     : 3
tail parents: 3   total leaves: 75   (9 + 57 + 9), all UNSAT
re-run instance identity      : SAME (every re-run solved a byte-identical
                                instance, checked by hash)
leaf candidate sums           : 1060 + 974 + 672 match parent census counts
UNRESOLVED: none
```

## 7. Copy integrity

- All 4,178 copied files hash-logged at copy time
  (`provenance/copy_log.json`); 307-file spot check after all packaging
  steps: every hash unchanged.
- 144/144 applicable pre-packaging inventory hashes match
  (`provenance/COPY_AUDIT.md`).
- `CHECKSUMS.sha256` covers every file in the finished artifact.

## Not verified at this stage (by design)

- UNSAT solver outcomes were not re-solved (cheap single instances can be
  re-run per `REPRODUCIBILITY.md` Tier 2; the V(4,9) campaign is Tier 3).
- The full n = 11..17 weight-game sweep was not recomputed; the stored
  complete results were consumed, with the implementation exercised by its
  test suite.
