# Copy Audit

This artifact was assembled on 2026-10-15/16 on the original experiment
machine (`thor`) by copying files from the read-only source repository
`/home/ono/Agent` (git HEAD `7c06ad41aa6b9037ce471cebc143dae24897f5f5`,
dirty tree; see `../environment/original_git_status.txt`). The source
repository was not modified in any way.

## Method

- Every file was copied with `shutil.copy2` (byte-for-byte, mtime
  preserved) by a staging script; no copy overwrote an existing file.
- `copy_log.json` in this directory records, for each of the **4,178**
  copied files: source path (relative to `/home/ono/Agent`), destination
  path (relative to this artifact root), SHA-256, and size.
- `original_file_checksums.sha256` lists the same SHA-256 values keyed by
  the original absolute path, in `sha256sum -c` format against the original
  machine.
- Evidence trees under `experiments/` and `docs/` keep their original
  repository-relative paths, so source path = destination path for them.
  Curated duplicates exist only in `weight_game/` (4 small files copied a
  second time from `src/` and `experiments/weight_game/`).

## Verification against the pre-packaging inventory

`artifact_inventory.json` (in this directory) is the read-only inventory of
the original repository taken on 2026-10-15, including SHA-256 hashes of
148 key files. Cross-check of the copies against it:

- **144 of 148 inventory-hashed files are present in this artifact and
  every one matches its inventory SHA-256 exactly (0 mismatches).**
- The remaining 4 inventory-hashed files are intentionally not part of the
  artifact:
  - `manuscript/main.tex`, `manuscript/selection.bib` — the paper itself,
    not artifact material (its tables appear here only as the hand
    transcription `scripts/expected_paper_tables_n11_17.json`, used as a
    verification target);
  - `u3_n11_d5_full_terminal_profile_audit_bundle.tar.gz` and
    `experiments/provenance_closure/depth2_family_verification.json` —
    the excluded U(3,11) depth-5 campaign (see README).

## Newly generated files (not copies)

Written during packaging; never overwriting a copied file:

| File | Origin |
| --- | --- |
| `README.md`, `PAPER_RESULTS.md`, `REPRODUCIBILITY.md`, `VERIFICATION_REPORT.md` | written for this artifact |
| `pyproject.toml` | written for this artifact (minimal packaging/test config) |
| `environment/environment.md`, `environment/original_git_status.txt` | written/captured for this artifact |
| `scripts/reconstruct_final_tables.py`, `scripts/expected_paper_tables_n11_17.json`, `scripts/verify_all_witnesses.py`, `scripts/check_v49_references.py` | written for this artifact |
| `tests/test_reconstruct_final_tables.py`, `tests/conftest.py` | written for this artifact |
| `weight_game/README.md` | written for this artifact |
| `generated/final_bounds_n11_17.{csv,json}`, `generated/final_tables_n11_17.tex`, `generated/weight_game_improvements.csv` | output of `scripts/reconstruct_final_tables.py` |
| `generated/witness_verification_report.json` | output of `scripts/verify_all_witnesses.py` |
| `generated/v49_d6_branch_ledger.csv` | output of `scripts/audit_v49_d6.py` (a copy of `experiments/provenance_closure/audit_v49_d6.py`), run from the artifact root against the copied evidence on 2026-10-16; this file was missing from the original repository (the script existed, its output did not) |
| `generated/closure_rerun/` | scratch rerun of `closure.py`; its `closure_report.json` is identical to the preserved `experiments/provenance_closure/closure_report.json` |
| `provenance/copy_log.json`, `provenance/original_file_checksums.sha256`, this file | packaging records |
| `CHECKSUMS.sha256` | SHA-256 manifest of the finished artifact |

## Intentional differences and non-copies

1. **No evidence file was rewritten.** Historical absolute paths
   (`/home/ono/Codex`, `/home/ono/Agent`) inside JSON/CSV/log evidence are
   preserved verbatim; the mapping is documented in the README.
2. **Historical checksums were not overwritten.** The frozen
   `experiments/v49_d6_final/bundle.sha256`, `evidence_manifest.json`, and
   every stored `artifact_manifest.sha256` are untouched; the new
   `CHECKSUMS.sha256` is a separate, additional manifest.
3. Two known divergences between the live tree and the frozen V(4,9)
   bundle are inherited from the original repository and documented in
   `ARTIFACT_INVENTORY.md` (coverage certificate path-prefix rewrite;
   post-bundle extension of `src/experiment.py`). This artifact copies the
   live versions; the bundle preserves the as-frozen versions.
4. Excluded from the copy (see README and `ARTIFACT_INVENTORY.md`): the
   U(3,11) depth-5 campaign (`experiments/u3_n11_d5_*`,
   `experiments/baseline_n11_17/decisions/unsat_u3_n11_d5/`, the preserved
   tarball, `residual_reuse_*`, `u3_n11_d5_prefix_filters_pilot/`), the
   unused `experiments/baseline_n11_17/decisions/unsat_v4_n11_d7/` attempt,
   superseded scratch outputs not referenced by any final certificate
   (`experiments/v49_d6_partitioned/`, `v49_d6_solver_config_benchmark/`),
   prompt files, manuscript build products, and empty directories.
   `experiments/v49_d6_l5_partitioned/` IS included although superseded,
   because the final audit (`audit_v49_d6.py`) and the
   `v49_d6_l5eq1_reaudit` input hashes reference it.
