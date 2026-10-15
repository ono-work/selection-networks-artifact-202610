# V(4,9) Finalization Report

Finalization status: `AFFIRMATIVE`

The final audit completed with status `VERIFIED`; no blocking problems were
reported by `experiments/v49_d6_final/final_certificate.json`.

## Finalized Claim

`VDepth(4,9)=7`.

This conclusion combines:

- a depth-6 lower-bound chain certified by audited reductions and raw solver
  UNSAT artifacts; and
- a depth-7 upper-bound witness certified by independent verifier replay.

## What Was Frozen

The final bundle under `experiments/v49_d6_final/bundle/` archives the source,
documentation, test, solver, branch-definition, log, and certificate artifacts
needed to replay the evidence audit.

The bundle is indexed by:

- `experiments/v49_d6_final/evidence_manifest.json`
- `experiments/v49_d6_final/evidence_index.md`
- `experiments/v49_d6_final/bundle.sha256`

## Audit Outputs

- `docs/v49_d6_final/proof_dependency_graph.md` records the human-readable
  dependency graph.
- `experiments/v49_d6_final/proof_dependency_graph.json` records the
  machine-readable dependency graph.
- `experiments/v49_d6_final/final_certificate.json` records the final
  certificate status and result.
- `experiments/v49_d6_final/BLOCKED.md` is a sentinel file; its content says
  `Not Blocked` because the final audit completed successfully.

## Final Caveat

This finalization records a computational-evidence certificate, not a fully
expanded human-readable proof of every solver UNSAT result. The dependency graph
therefore separates mathematical lemmas, exhaustive Python verifier checks,
artifact audits, raw clingo results, and derived conclusions.

