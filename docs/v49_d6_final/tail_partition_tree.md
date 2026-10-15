# V(4,9) Depth-6 Tail Partition Tree

This tree shows the audited partition path without drawing all 75 leaves individually.

```text
depth-6 candidate
  -> closure audit / terminal-profile reduction
      -> A5_residual_L5eq3 (9 categories; experiments/v49_d6_l5_tail_census/coverage_certificate.json)
      -> B6_residual_L5eq3 (57 categories; experiments/v49_d6_l5_tail_census/coverage_certificate.json)
      -> B6_residual_L5eq4 (9 categories; experiments/v49_d6_l5_tail_census/coverage_certificate.json)
          -> 75 raw UNSAT leaves (screening raw + overnight raw)
              -> depth-6 UNSAT (experiments/v49_d6_final/proof_dependency_graph.json)
```

The raw UNSAT leaves are computational solver artifacts for constrained ASP instances. This diagram does not assert human-readable UNSAT causes.
