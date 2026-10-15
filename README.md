# Computational Artifact: Exact Depths and Bounds for Small Selection Networks

This repository is the public computational artifact accompanying the paper

> **Exact Depths and Bounds for Small Selection Networks**, CANDAR 2026.

The paper determines the exact minimum depth of V-type (ordered) and U-type
(unordered) t-selection comparator networks for all `1 <= t <= n <= 10`, and
lower/upper bounds for `11 <= n <= 17`. This artifact contains the solver
inputs and outputs, verified witnesses, audits, and programs needed to
inspect and (where computationally reasonable) reproduce every computational
claim of the paper. It is a packaging of the original experiment records; it
adds no new scientific claims.

Start here, then see:

- **`PAPER_RESULTS.md`** — every computational claim of the paper mapped to
  its evidence files, method, and verification status.
- **`REPRODUCIBILITY.md`** — quick checks (minutes) and full reproduction
  instructions, with expensive searches clearly marked.
- **`VERIFICATION_REPORT.md`** — the checks run while assembling this
  artifact, with results.
- **`provenance/`** — the pre-packaging inventory of the original experiment
  repository, the copy audit, and per-file checksums.

## Four kinds of evidence

The paper's results rest on evidence of different strengths. Keep these
distinct when interpreting any file in this artifact:

1. **Analytic and structural results** — lemmas proved in the paper
   (monotonicity, mirror duality, padding, sorting-network inheritance,
   Nakano's t=2 bounds). No computation involved.
2. **Finite-state weight-game computations** — exhaustive breadth-first
   evaluations of the additive weight game (`weight_game/`,
   `experiments/weight_game/`). These are deterministic, solver-free
   computations; the paper proves the game value lower-bounds the network
   depth.
3. **ASP SAT witness searches** — clingo searches that found explicit
   networks. Every SAT model was extracted to a `network.json` witness and
   is **independently checked by exhaustive simulation on all 2^n binary
   inputs** (`src/verify.py`, which shares no code with the ASP encoding).
   A verified witness is a self-contained, independently checkable proof of
   an upper bound.
4. **ASP UNSAT nonexistence results** — clingo runs that exhausted a search
   space without finding a network. These are **solver-based computational
   evidence**: the raw solver output (`solver.json`, `Result:
   UNSATISFIABLE`) is stored for every such run, but UNSAT results are
   *not* independently checkable proof certificates. The paper words the
   corresponding claims accordingly.

Two consequences stated explicitly:

- **A TIMEOUT never establishes a lower bound.** Several stored runs ended
  in TIMEOUT (for example the monolithic V(4,9) depth-6 attempt, and the
  U(3,11)/U(4,11)/U(5,11) depth-5 attempts). Such runs are kept for the
  record only; no claim in the paper rests on a timeout.
- Solver UNSAT evidence is strengthened where possible by audited search
  space partitions and coverage certificates (see the V(4,9) section
  below), but it remains computational evidence.

## Repository layout

The `experiments/`, `docs/`, `solver/`, `src/`, `tests/` trees preserve the
original repository-relative layout, so every path recorded inside stored
certificates, manifests, and logs resolves against the root of this
artifact.

```
solver/                 ASP encodings: common.lp + target_v.lp / target_u.lp
src/                    generators, solver driver, independent verifier,
                        bound-propagation and audit code (original sources)
scripts/                audit/reproduction entry points (see below)
tests/                  pytest suite (186 tests; runs without clingo)
experiments/            original experiment records, byte-for-byte:
  milestone_3b_smoke/     n <= 6 full UNSAT ladders + witnesses
  baseline_n7|n8|n9|n10/  n = 7..10 decisions, witnesses, reports
  n10_selection_depth_completion/  audited n <= 10 completion (3 jobs,
                          evidence audit, exact tables)
  provenance_closure/     strict provenance closure for n <= 10
  weight_game/            additive weight-game sweep (code + results)
  baseline_n11_17/        n = 11..17 witness runs, constructive and
                          paper-ready upper bounds
  selection_bounds_n11_17/ pre-game bound propagation record
  u2_n17_d6_witness_search/ the doubly verified U(2,17) depth-6 witness
  u_calibration/, milestone_3b_calibration/  calibration cells
  v49_d6_*/               the V(4,9) depth-6 nonexistence campaign (below)
docs/                   original experiment documentation
weight_game/            curated copy of the weight-game code and results
generated/              outputs produced while assembling this artifact
                        (reconstructed tables, verification reports, ledger)
environment/            original machine/environment record
provenance/             pre-packaging inventory, copy audit, checksums
```

## Result highlights and where to find them

| Paper result | Where |
| --- | --- |
| Exact tables, n <= 10 | `experiments/n10_selection_depth_completion/exact_tables.tex`, audited by `evidence_audit.json`; irredundant input set in `experiments/provenance_closure/closure_report.json` |
| Six ASP UNSAT lower bounds | see `PAPER_RESULTS.md` section A |
| Eight verified witness upper bounds (n <= 10 inputs) | `PAPER_RESULTS.md` section B |
| VDepth(4,9) = 7 | `experiments/v49_d6_final/` (certificate, manifest, dependency graph) plus the partition campaign directories |
| UDepth(2,17) = UDepth(15,17) = 6 — weight-game lower bound A_U(2,17)=6 + doubly verified depth-6 witness (+ mirror duality for t=15); see `PAPER_RESULTS.md` sections C and F | lower bound: `weight_game/results/`; upper bound: `experiments/u2_n17_d6_witness_search/20260808_030007Z/` |
| U(3,11), U(4,11), U(5,11) <= 6 | `experiments/baseline_n11_17/decisions/U_t{3,4,5}_n11/depth_06/` |
| Weight-game inputs and 44 improved lower endpoints | `weight_game/`, `generated/weight_game_improvements.csv` |
| Final n = 11..17 tables, mechanically rebuilt | `generated/final_bounds_n11_17.{csv,json}`, `generated/final_tables_n11_17.tex` |

## The V(4,9) depth-6 nonexistence evidence

`VDepth(4,9) >= 7` is the most involved computational result. Its structure
(all files under `experiments/`):

1. seed: `baseline_n9/decisions/V_t3_n9/depth_05/` (V(3,9) depth-5 UNSAT);
2. lemmas (`docs/v_boundary_and_v49_support_partition.md`) restrict the
   depth-6 search to all-layers-nonempty form;
3. parent partitions with direct UNSAT branches:
   `v49_d6_support_partitioned/`, `v49_d6_refined_partitioned/`,
   `v49_d6_partner_partitioned/`, `v49_d6_bp5_final_layer_partitioned/`,
   `v49_d6_six_leaf_reduced/`;
4. closure audit over 15,720 leaf classifications:
   `v49_d6_closure_audit/coverage_certificate.json`
   (`COVERAGE_AUDIT_PASSED`, 0 uncovered);
5. tail census: 3 residual parents split into 75 pairwise-disjoint
   children: `v49_d6_l5_tail_census/`;
6. 75/75 tail children UNSAT: `v49_d6_tail_partitioned/` (49 at screening,
   26 in the overnight rerun; raw clingo JSON per child);
7. pruning soundness: `v49_d6_topology_pruning/validation.json`;
8. the depth-7 upper bound witness, exhaustively verified:
   `baseline_n9/decisions/V_t4_n9/depth_07/`;
9. the frozen final certificate: `v49_d6_final/` —
   `final_certificate.json` (AFFIRMATIVE), `evidence_manifest.json`
   (588 files, hash-pinned), `proof_dependency_graph.json`,
   `bundle/` + `bundle.sha256` (sealed snapshot), plus a later re-audit
   `v49_d6_l5eq1_reaudit/`.

`python3 scripts/check_v49_references.py` verifies all of this in place
(manifest, bundle checksums, dependency graph, and the 37 branch artifacts
the closure certificate cites). `generated/v49_d6_branch_ledger.csv` is a
post-hoc genealogy ledger regenerated for this artifact (see
`VERIFICATION_REPORT.md`).

Note: running the optional certificate-rebuild tests (see
`tests/conftest.py`) regenerates `v49_d6_closure_audit/coverage_certificate.json`
in place; the as-published certificate always remains available inside the
frozen `v49_d6_final/bundle/`.

## Quick checks (no solver needed, minutes total)

```sh
python3 scripts/verify_all_witnesses.py      # re-verify all 103 stored SAT
                                             # witnesses on all 2^n inputs
python3 scripts/check_v49_references.py      # V(4,9) manifests + checksums
python3 scripts/reconstruct_final_tables.py  # rebuild the n=11..17 tables
                                             # and the 44-cell improvement list
python3 generated/closure_rerun/closure.py           # n<=10 strict closure
    # (writes its report next to itself in generated/closure_rerun/;
    #  running experiments/provenance_closure/closure.py instead rewrites
    #  the preserved report in place -- the output is JSON-equal but not
    #  necessarily byte-identical, since JSON key order varies with
    #  Python hash randomization)
python3 -m pytest -q                         # 186 unit/integration tests
```

`pytest` needs `pip install pytest`; everything above runs without clingo.
Full reproduction, including solver runs, is described in
`REPRODUCIBILITY.md`.

## Environment

Original machine: `thor`, aarch64, Linux (Ubuntu), **Python 3.12.3**,
**clingo 5.8.0 (pyclingo)**. clingo was invoked as

```sh
python -m clingo --outf=2 --time-limit=<T> -n 1 solver/common.lp solver/target_{v|u}.lp <instance.lp>
```

via the Python package — **not** through a standalone `clingo` binary. See
`environment/environment.md`.

**Historical path note.** The original repository lived at
`/home/ono/Codex` and was later moved to `/home/ono/Agent`. Historical
logs, `command.txt` files, and certificates in `experiments/` may contain
either absolute prefix; both refer to the same repository, whose
`experiments/...`-relative layout this artifact preserves. Evidence files
were copied byte-for-byte and deliberately not rewritten.

## Excluded: the U(3,11) depth-5 campaign

The original repository also contains a large experimental campaign on
U(3,11) at depth 5 (terminal-profile enumeration and closure). **That
campaign is not used by the paper and is intentionally excluded from this
artifact.** Its retained depth-2 representative family was later found to be
semantically incomplete, so no conclusion about `UDepth(3,11)` beyond the
published interval `[5,6]` is claimed here or in the paper. Do not read the
exclusion as a hidden result in either direction.

## License

This artifact is released under the MIT License; see `LICENSE`.
