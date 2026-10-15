# V(4,9) Depth Evidence Dependency Graph

Overall audit status: `VERIFIED`.

This graph separates human mathematical lemmas from exhaustive Python checks, solver-produced UNSAT/SAT artifacts, artifact-integrity checks, and derived conclusions. A clingo UNSAT result is treated as computational evidence, not as a human-readable mathematical proof.

## Proof Chain

The lower-bound side starts from the raw clingo UNSAT result for `V_t3_n9` at depth 5. The mathematical prefix lemma says a V-type 4-selection network also satisfies the first three V outputs, so an empty layer in a hypothetical depth-6 `V(4,9)` network would collapse to a depth-at-most-5 `V(3,9)` network. This justifies the all-nonempty depth-6 search normal form.

The computer-assisted reduction then begins: terminal-profile and closure artifacts reduce the all-nonempty depth-6 search to three residual parent families. The tail census certificate partitions those parents into 75 disjoint exhaustive children. Topology pruning is included only through recorded necessary-condition validation. The 75 children are closed by raw clingo JSON: 49 in screening, 26 in the overnight run.

The upper-bound side is separate: an explicit depth-7 witness is stored as JSON and is checked by the independent Python verifier over all binary inputs. The final exact-depth conclusion depends on both the depth-6 UNSAT chain and the depth-7 verified witness.

## Nodes

### V3_9_DEPTH5_UNSAT

- Claim: No V-type 3-selection network on 9 wires exists at depth 5.
- Classification: `SOLVER_UNSAT`
- Status: `VERIFIED`
- Prerequisites: none
- Audit method: parsed clingo JSON Result=UNSATISFIABLE

### V4_IMPLIES_V3

- Claim: Every V-type 4-selection network is also a V-type 3-selection network by restricting the required output prefix.
- Classification: `MATHEMATICAL_LEMMA`
- Status: `VERIFIED`
- Prerequisites: none
- Audit method: human lemma recorded in documentation

### EMPTY_LAYER_ELIMINATION

- Claim: A depth-6 V(4,9) network with an empty layer has effective depth at most 5.
- Classification: `MATHEMATICAL_LEMMA`
- Status: `VERIFIED`
- Prerequisites: V3_9_DEPTH5_UNSAT, V4_IMPLIES_V3
- Audit method: human lemma plus lower-bound premise

### ALL_LAYERS_NONEMPTY_IN_DEPTH6_SEARCH

- Claim: The depth-6 search may restrict to all layers nonempty for V(4,9).
- Classification: `DERIVED_CONCLUSION`
- Status: `VERIFIED`
- Prerequisites: EMPTY_LAYER_ELIMINATION
- Audit method: derivation from empty-layer lemma

### TERMINAL_PROFILE_COVERAGE

- Claim: Terminal-profile closure audit covers the stated residual depth-6 cases.
- Classification: `ARTIFACT_AUDIT`
- Status: `VERIFIED`
- Prerequisites: ALL_LAYERS_NONEMPTY_IN_DEPTH6_SEARCH
- Audit method: parsed closure coverage_certificate.json recognized pass token

### NO_REPEAT_REDUCTION

- Claim: The no-repeat final-layer reduction used by closure is audited for covered cases.
- Classification: `ARTIFACT_AUDIT`
- Status: `VERIFIED`
- Prerequisites: EMPTY_LAYER_ELIMINATION
- Audit method: closure certificate and reduction docs inspected

### THREE_RESIDUAL_PARENT_COVERAGE

- Claim: The closure audit leaves exactly the three residual parent families used by the tail census.
- Classification: `ARTIFACT_AUDIT`
- Status: `VERIFIED`
- Prerequisites: TERMINAL_PROFILE_COVERAGE, NO_REPEAT_REDUCTION
- Audit method: cross-checked residual parent identifiers

### TAIL_CENSUS_75_WAY_PARTITION

- Claim: The three residual parents are partitioned into exactly 75 pairwise-disjoint exhaustive tail child branches.
- Classification: `ARTIFACT_AUDIT`
- Status: `VERIFIED`
- Prerequisites: THREE_RESIDUAL_PARENT_COVERAGE
- Audit method: parsed tail census certificate and counted branch definitions

### TOPOLOGY_PRUNING_UNIQUE_MIN_SOUND

- Claim: Unique-min trajectory pruning is a necessary condition for V-type networks, not a heuristic restriction.
- Classification: `EXHAUSTIVE_VERIFIER_CHECK`
- Status: `VERIFIED`
- Prerequisites: none
- Audit method: validation artifact status=PASSED and regression tests referenced

### TOPOLOGY_PRUNING_DEPENDENCY_CONE_SOUND

- Claim: Backward dependency-cone pruning is a necessary condition for V-type networks, not a heuristic restriction.
- Classification: `EXHAUSTIVE_VERIFIER_CHECK`
- Status: `VERIFIED`
- Prerequisites: none
- Audit method: validation artifact status=PASSED and regression tests referenced

### TAIL_CHILDREN_75_UNSAT

- Claim: All 75 tail children have raw clingo JSON certifying UNSAT.
- Classification: `SOLVER_UNSAT`
- Status: `VERIFIED`
- Prerequisites: TAIL_CENSUS_75_WAY_PARTITION, TOPOLOGY_PRUNING_UNIQUE_MIN_SOUND, TOPOLOGY_PRUNING_DEPENDENCY_CONE_SOUND
- Audit method: parsed 49 screening and 26 overnight raw solver JSON files for Result=UNSATISFIABLE

### V4_9_DEPTH6_UNSAT

- Claim: No V-type 4-selection network on 9 wires exists at depth 6.
- Classification: `DERIVED_CONCLUSION`
- Status: `VERIFIED`
- Prerequisites: TAIL_CHILDREN_75_UNSAT, TERMINAL_PROFILE_COVERAGE
- Audit method: derived from audited residual coverage and all tail UNSAT leaves

### V4_9_DEPTH7_WITNESS_VERIFIED

- Claim: An explicit V-type 4-selection network on 9 wires at depth 7 exists and passes the independent verifier on all binary inputs.
- Classification: `EXHAUSTIVE_VERIFIER_CHECK`
- Status: `VERIFIED`
- Prerequisites: none
- Audit method: parsed SAT raw solver output and replayed Python verifier

### V4_9_EXACT_DEPTH_7

- Claim: Combining depth-6 UNSAT with a verified depth-7 witness gives exact depth 7 for V(4,9).
- Classification: `DERIVED_CONCLUSION`
- Status: `VERIFIED`
- Prerequisites: V4_9_DEPTH6_UNSAT, V4_9_DEPTH7_WITNESS_VERIFIED
- Audit method: logical combination of lower and upper bounds; not a standalone solver proof

## Edges

- `V3_9_DEPTH5_UNSAT` -> `EMPTY_LAYER_ELIMINATION`
- `V4_IMPLIES_V3` -> `EMPTY_LAYER_ELIMINATION`
- `EMPTY_LAYER_ELIMINATION` -> `ALL_LAYERS_NONEMPTY_IN_DEPTH6_SEARCH`
- `ALL_LAYERS_NONEMPTY_IN_DEPTH6_SEARCH` -> `TERMINAL_PROFILE_COVERAGE`
- `EMPTY_LAYER_ELIMINATION` -> `NO_REPEAT_REDUCTION`
- `TERMINAL_PROFILE_COVERAGE` -> `THREE_RESIDUAL_PARENT_COVERAGE`
- `NO_REPEAT_REDUCTION` -> `THREE_RESIDUAL_PARENT_COVERAGE`
- `THREE_RESIDUAL_PARENT_COVERAGE` -> `TAIL_CENSUS_75_WAY_PARTITION`
- `TAIL_CENSUS_75_WAY_PARTITION` -> `TAIL_CHILDREN_75_UNSAT`
- `TOPOLOGY_PRUNING_UNIQUE_MIN_SOUND` -> `TAIL_CHILDREN_75_UNSAT`
- `TOPOLOGY_PRUNING_DEPENDENCY_CONE_SOUND` -> `TAIL_CHILDREN_75_UNSAT`
- `TAIL_CHILDREN_75_UNSAT` -> `V4_9_DEPTH6_UNSAT`
- `TERMINAL_PROFILE_COVERAGE` -> `V4_9_DEPTH6_UNSAT`
- `V4_9_DEPTH6_UNSAT` -> `V4_9_EXACT_DEPTH_7`
- `V4_9_DEPTH7_WITNESS_VERIFIED` -> `V4_9_EXACT_DEPTH_7`
