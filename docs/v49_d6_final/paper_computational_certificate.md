## Computational certificate for VDepth(4,9)=7

### Statement

For V-type 4-selection networks on 9 wires,

\[
\mathrm{VDepth}(4,9)=7 .
\]

Here depth means the number of comparator layers. Each layer is a matching of
disjoint comparators.

### Model and verification convention

A comparator network on \(n\) wires is a sequence of layers, where each layer
contains pairwise-disjoint comparators. A V-type \(t\)-selection network is
required to place the \(t\) selected outputs in the prescribed V-prefix positions
for every input. By the 0--1 principle, the network conditions are checked on
binary inputs. For the upper bound below, the stored SAT witness was checked by
an independent Python verifier on all \(2^9\) binary inputs.

### Upper bound

The certificate includes an explicit depth-7 witness for the V-type
4-selection problem on 9 wires. The witness is stored at
`experiments/baseline_n9/decisions/V_t4_n9/depth_07/network.json`. The verifier
artifact
`experiments/baseline_n9/decisions/V_t4_n9/depth_07/verifier.json` records
`ok=true`, `kind=V`, `t=4`, and `n=9`, with the message "verified all binary
inputs". Thus the upper bound \(\mathrm{VDepth}(4,9) \le 7\) is certified by an
explicit network and exhaustive binary simulation.

### Lower bound strategy

The lower bound is organized as a dependency graph whose machine-readable form
is `experiments/v49_d6_final/proof_dependency_graph.json`. The graph separates
mathematical lemmas, artifact audits, solver UNSAT artifacts, and derived
conclusions.

First, the raw solver artifact
`experiments/baseline_n9/decisions/V_t3_n9/depth_05/solver.json` records
`UNSATISFIABLE` for \(V(3,9)\) at depth 5; this is a `SOLVER_UNSAT` premise.
Second, the prefix observation that every V-type 4-selection network is also a
V-type 3-selection network is recorded as a `MATHEMATICAL_LEMMA`. Together with
the empty-layer elimination lemma, this implies that a depth-6 V(4,9) candidate
with an empty layer would yield a depth-at-most-5 V(3,9) candidate. Hence the
depth-6 search may be restricted to all layers nonempty; this is a
`DERIVED_CONCLUSION`.

The remaining depth-6 search is then reduced by the closure audit and
terminal-profile reduction, recorded as `ARTIFACT_AUDIT` nodes. These audits
leave three residual parent families. The L5 tail census exhaustively partitions
these residual parents into 75 tail categories. Finally, for each of the 75
leaves, the certificate records a raw clingo JSON artifact with
`Result=UNSATISFIABLE`; these leaf closures are `SOLVER_UNSAT` evidence for the
corresponding constrained ASP instances. Combining the audited coverage with
the 75 raw UNSAT leaf artifacts gives the derived depth-6 conclusion that no
V-type 4-selection network on 9 wires exists at depth 6.

### Tail partition summary

The following table is read from
`experiments/v49_d6_final/tail_leaf_table.csv` and
`experiments/v49_d6_final/tail_family_summary.csv`.

| residual parent | tail categories | compatible L5 matchings | closed in screening | closed overnight | total UNSAT leaves |
| --- | ---: | ---: | ---: | ---: | ---: |
| `A5_residual_L5eq3` | 9 | 1060 | 2 | 7 | 9 |
| `B6_residual_L5eq3` | 57 | 974 | 43 | 14 | 57 |
| `B6_residual_L5eq4` | 9 | 672 | 4 | 5 | 9 |
| total | 75 | 2706 | 49 | 26 | 75 |

The table is a structural and operational summary of the recorded partition.
The screening/overnight distinction records when the raw UNSAT artifact was
obtained; it is not used as a mathematical explanation of UNSAT.

### Reproducibility and certificate

- Final certificate: `experiments/v49_d6_final/final_certificate.json`.
- Evidence manifest: `experiments/v49_d6_final/evidence_manifest.json`.
- Dependency graph: `experiments/v49_d6_final/proof_dependency_graph.json`.
- Evidence index: `experiments/v49_d6_final/evidence_index.md`.
- Audit and bundling script: `scripts/audit_v49_d6_final_bundle.py`.
- Tail-leaf analysis script: `src/analyze_v49_d6_tail_leaves.py`.
- Raw solver outputs are included through the manifest.
- Source snapshots and SHA-256 hashes are recorded in the evidence manifest.

### Limitations of the certificate

The solver UNSAT outputs are not converted here into human-readable proofs, and
no UNSAT cores are presented. The current certificate also does not include an
independent second encoding of the depth-6 lower-bound search. Timing data are
operational observations only. Changing solver version or hardware may affect
runtime, but not the recorded branch definitions or the manifest checksums. A
future clean replay and an independent CNF/SAT encoding would strengthen the
certificate.

### Suggested citation in the paper

1. By the computational certificate described in Appendix X, no depth-six
   V-type 4-selection network on nine wires exists, while a depth-seven network
   is verified by exhaustive binary simulation. Hence
   \(\mathrm{VDepth}(4,9)=7\).
2. The case \(V(4,9)\) is settled by a computational certificate: the depth-six
   search is reduced to 75 certified UNSAT tail leaves, and a depth-seven
   witness is independently verified on all binary inputs.
3. Appendix X records the computational certificate for \(V(4,9)\), separating
   the mathematical reductions, artifact audits, raw solver UNSAT leaves, and
   the verified depth-seven witness.

