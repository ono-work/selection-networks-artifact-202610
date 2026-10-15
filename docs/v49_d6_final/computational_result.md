# V(4,9) Computational Result

Status: `VERIFIED`

Final computational certificate: `VDepth(4,9)=7`.

This is a computational-evidence result. The raw clingo UNSAT artifacts are
treated as machine-checkable solver evidence, not as human-readable mathematical
proofs of each UNSAT claim.

## Result Summary

- Lower bound: no V-type 4-selection network on 9 wires exists at depth 6.
- Upper bound: an explicit V-type 4-selection network on 9 wires exists at depth 7.
- Exact conclusion: `VDepth(4,9)=7`.

## Lower-Bound Evidence

The depth-6 exclusion is assembled from the audited dependency graph:

- `V(3,9)` depth-5 raw solver result is `UNSATISFIABLE`.
- The prefix lemma gives that every V-type 4-selection network is also V-type
  3-selection when restricted to the required prefix.
- The empty-layer elimination lemma reduces any depth-6 candidate with an empty
  layer to a depth-at-most-5 `V(3,9)` candidate.
- Terminal-profile and closure artifacts reduce the all-nonempty depth-6 search
  to three residual parent families.
- The tail census partitions those residual parents into 75 disjoint exhaustive
  tail children.
- All 75 tail children have raw clingo JSON with `Result=UNSATISFIABLE`: 49 from
  screening and 26 from the overnight run.
- Topology pruning is included only through recorded necessary-condition
  validation, not as a heuristic restriction.

## Upper-Bound Evidence

The depth-7 upper bound is an explicit stored witness:

- The `V(4,9)` depth-7 solver output is `SATISFIABLE`.
- The witness network is stored as JSON.
- The independent Python binary-input verifier replayed the witness for
  `kind=V`, `t=4`, `n=9` and returned `ok=true`.

## Primary Artifacts

- Final certificate: `experiments/v49_d6_final/final_certificate.json`
- Dependency graph: `docs/v49_d6_final/proof_dependency_graph.md`
- Machine graph: `experiments/v49_d6_final/proof_dependency_graph.json`
- Evidence manifest: `experiments/v49_d6_final/evidence_manifest.json`
- Evidence index: `experiments/v49_d6_final/evidence_index.md`
- Bundle hashes: `experiments/v49_d6_final/bundle.sha256`

