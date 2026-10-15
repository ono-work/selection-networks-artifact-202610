# Reproducibility Guide

## Setup

Python >= 3.10 (original: 3.12.3). For the solver-free checks nothing else
is needed. For solver reruns and the test extras:

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install clingo==5.8.0 pytest
```

clingo is used **as a Python module** (`python -m clingo`), matching the
original runs; no standalone clingo binary is required. Original machine:
aarch64; nothing in the code is architecture-specific, but solver running
times will differ on other hardware. Solver search is deterministic for a
fixed clingo version and single thread (`-n 1`); UNSAT/SAT outcomes are
machine-independent, the specific SAT model found may vary with version.

## Tier 0 — integrity (seconds)

```sh
sha256sum -c CHECKSUMS.sha256            # every file in this artifact
python3 scripts/check_v49_references.py  # V(4,9) manifests, bundle, graph
```

`provenance/original_file_checksums.sha256` additionally records the
SHA-256 of every copied file at its original path on the experiment
machine.

## Tier 1 — solver-free verification (minutes)

```sh
python3 scripts/verify_all_witnesses.py
    # re-verifies every stored SAT witness (103) by exhaustive simulation
    # on all 2^n binary inputs, n up to 17; compares with stored verdicts

python3 generated/closure_rerun/closure.py
    # strict n <= 10 provenance closure from the 19 irredundant inputs;
    # writes its closure_report.json next to itself (a scratch copy).
    # Running experiments/provenance_closure/closure.py instead rewrites
    # the preserved report in place; the rerun output was verified
    # JSON-equal to the preserved report (byte order of JSON keys can
    # vary with Python hash randomization)

python3 scripts/reconstruct_final_tables.py
    # rebuilds the final n = 11..17 tables and the 44-cell improvement
    # list from stored inputs; fails loudly on any disagreement with the
    # manuscript transcription

python3 -m pytest -q
    # 186 tests: simulator/verifier semantics, weight game, bound
    # propagation, V(4,9) census/screening/pruning logic, reconstruction
```

Note: two tests are skipped by default because they regenerate
`experiments/v49_d6_closure_audit/coverage_certificate.json` in place;
set `ARTIFACT_ALLOW_CERT_REBUILD=1` to run them (see `tests/conftest.py`).
The as-published certificate is always preserved in
`experiments/v49_d6_final/bundle/`.

## Tier 2 — cheap/moderate solver reruns (clingo required)

Each depth decision can be reproduced individually; the exact original
command is stored in each run directory (`decision.json` `command` field,
`command.txt`, or `command.json`). Representative examples:

```sh
# UDepth(4,6) >= 4: depth-3 UNSAT in under a second
python -m clingo --outf=2 --time-limit=60 -n 1 \
  solver/common.lp solver/target_u.lp \
  experiments/milestone_3b_smoke/U_t4_n6/depth_03/instance.lp

# VDepth(3,7) >= 6: depth-5 UNSAT, a few seconds
python -m clingo --outf=2 --time-limit=1200 -n 1 \
  solver/common.lp solver/target_v.lp \
  experiments/baseline_n7/decisions/V_t3_n7/depth_05/instance.lp

# U(2,17) depth-6 witness search (~90 s originally)
python -m clingo --outf=2 --stats=2 -n 1 --time-limit=900 \
  solver/common.lp solver/target_u.lp \
  experiments/u2_n17_d6_witness_search/20260808_030007Z/instance.lp
```

Instance files are stored for every run, so no regeneration step is
needed; `src/generate_instance.py` regenerates them if desired.

Weight game (solver-free but with a wall-clock budget):

```sh
python3 -m experiments.weight_game.run_sweep
# resumable; consumes/extends experiments/weight_game/results_n11_17.json.
# To reproduce the sweep from scratch, run it in a fresh working copy of
# this artifact; do not overwrite the preserved results bundled here
# (V-type cells are bounded by a 55-minute wall-clock budget, as in the
# paper).
```

Moderate single runs (minutes to ~30 min each): VDepth(2,9) depth-5 UNSAT
(1008 s originally), U(3,11)/U(4,11)/U(5,11) depth-6 witness searches
(252--1696 s), U(4,10)/U(5,10) depth-5 witnesses.

## Tier 3 — EXPENSIVE: the V(4,9) depth-6 campaign (do not casually rerun)

The partitioned nonexistence campaign ran for many hours to days in total
(the 75 tail children alone include 26 overnight reruns at a 3600 s limit
each; screening used 900 s limits). The original stage runners are kept:

```sh
scripts/run_v49_d6_support_partitioned.sh     # EXPENSIVE
scripts/run_v49_d6_refined_partitioned.sh     # EXPENSIVE
scripts/run_v49_d6_partner_partitioned.sh     # EXPENSIVE
scripts/run_v49_d6_bp5_final_layer_partitioned.sh  # EXPENSIVE
scripts/run_v49_d6_six_leaf_reduced.sh        # EXPENSIVE
scripts/run_v49_d6_l5_partitioned.sh          # EXPENSIVE
scripts/run_v49_d6_l5_longrun.sh              # EXPENSIVE
scripts/run_v49_d6_tail_partitioned.sh        # EXPENSIVE (overnight)
```

They write into `experiments/v49_d6_*` relative to the working directory;
run them in a scratch copy if you rerun them at all. The recommended way to
scrutinize this result is **not** a rerun but:

```sh
python3 scripts/check_v49_references.py       # minutes: all hashes/refs
python3 scripts/audit_v49_d6.py               # run from the artifact root:
                                              # rebuilds the branch ledger
                                              # (writes v49_d6_branch_ledger.csv
                                              # next to the script; compare with
                                              # generated/v49_d6_branch_ledger.csv)
python3 -m pytest tests/test_v49_d6_closure_audit.py \
       tests/test_v49_d6_l5_tail_census.py \
       tests/test_v49_d6_tail_screening.py \
       tests/test_v49_d6_topology_pruning.py -q
```

A single tail child can be re-solved individually from its stored
`instance.lp` under
`experiments/v49_d6_tail_partitioned/{screening,overnight/*/}raw/<branch>/`
with the generic clingo command (900--3600 s time limits).

## What was NOT rerun while packaging

- the V(4,9) depth-6 solver campaign (stored evidence verified instead);
- the full n = 11..17 weight-game sweep (stored complete results consumed;
  the implementation is exercised by its test suite on small cells);
- the n = 11..17 witness searches and the n <= 10 baseline searches
  (stored solver outputs and witnesses verified instead).

See `VERIFICATION_REPORT.md` for exactly what was run and its results.
