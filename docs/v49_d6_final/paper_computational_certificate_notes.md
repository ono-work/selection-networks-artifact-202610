# Notes for the V(4,9) Computational Certificate Subsection

## Artifact sources

- Final result and caveat: `experiments/v49_d6_final/final_certificate.json`.
  It records `status=AFFIRMATIVE`, `result=VDepth(4,9)=7`, and no problems.
- Dependency classifications and lower-bound chain:
  `experiments/v49_d6_final/proof_dependency_graph.json` and
  `docs/v49_d6_final/proof_dependency_graph.md`.
- Evidence manifest, source snapshots, and SHA-256 hashes:
  `experiments/v49_d6_final/evidence_manifest.json`.
- Human-readable evidence index:
  `experiments/v49_d6_final/evidence_index.md`.
- Tail partition counts and phase split:
  `experiments/v49_d6_final/tail_leaf_table.csv` and
  `experiments/v49_d6_final/tail_family_summary.csv`.
- Closure hierarchy:
  `experiments/v49_d6_final/tail_closure_ledger.csv`.
- Tail analysis text and proof tree:
  `docs/v49_d6_final/tail_leaf_analysis.md`,
  `docs/v49_d6_final/tail_partition_tree.md`, and
  `docs/v49_d6_final/tail_partition_tree.tex`.
- Depth-7 witness and verifier:
  `experiments/baseline_n9/decisions/V_t4_n9/depth_07/network.json` and
  `experiments/baseline_n9/decisions/V_t4_n9/depth_07/verifier.json`.
- V(3,9) depth-5 premise:
  `experiments/baseline_n9/decisions/V_t3_n9/depth_05/solver.json`.

## Numerical values used

From `tail_leaf_table.csv`:

| residual parent | categories / UNSAT leaves | compatible L5 matchings | screening | overnight |
| --- | ---: | ---: | ---: | ---: |
| `A5_residual_L5eq3` | 9 | 1060 | 2 | 7 |
| `B6_residual_L5eq3` | 57 | 974 | 43 | 14 |
| `B6_residual_L5eq4` | 9 | 672 | 4 | 5 |
| total | 75 | 2706 | 49 | 26 |

From `verifier.json`: `ok=true`, `kind=V`, `t=4`, `n=9`, with all binary
inputs verified.

From the V(3,9) depth-5 solver artifact: `Result=UNSATISFIABLE`.

## Minimal version for the paper body

Use the statement, one paragraph for the model, one paragraph for the depth-7
witness, one paragraph for the depth-6 certificate structure, and the tail
partition table. The limitations paragraph may be shortened to a sentence
saying that the 75 UNSAT leaves are raw solver artifacts, not human-readable
UNSAT proofs.

## Details better placed in an appendix

- Full dependency graph and node classifications.
- The 75-row tail leaf table.
- The closure ledger.
- Manifest and SHA-256 details.
- The proof-tree diagram from `tail_partition_tree.tex`.
- Exact artifact paths for every raw solver output.

## Remaining weak points

- No independent second encoding is included yet.
- A clean worktree replay is still desirable.
- The certificate does not include solver UNSAT proof objects.

## Next steps if strengthening the result

- Run a clean replay from the frozen manifest.
- Build an independent CNF/SAT encoding for the depth-6 lower-bound leaves.
- Extend the workflow toward `n=10`.
- Try to extract human-readable lemmas from recurring UNSAT structure without
  treating runtime or solver statistics as mathematical explanations.

