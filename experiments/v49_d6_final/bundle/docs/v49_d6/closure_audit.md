# V(4,9), Depth-6 Closure Audit

This audit is generated and checked by `src/v49_d6_closure_audit.py` and
`tests/test_v49_d6_closure_audit.py`.

Scope: V-type selection with `n=9`, `t=4`, `depth=6` in the current special
hard-instance mode: all six layers nonempty, no final-layer comparator wholly
inside wires `{5,6,7,8,9}`, and validated `v_boundary` inputs. This audit does
not alter baseline ASP semantics, verifier semantics, or input-mode semantics.

## Reduction Chain

1. The special hard-instance universe is split by final-prefix support.
   Thirteen support classes have direct prior `UNSAT` artifacts.
2. The two unresolved support classes were refined by final-layer size.
   Three refined size children have direct prior `UNSAT` artifacts.
3. The remaining partner/fixed-terminal leaves were refined further. Direct
   `UNSAT` artifacts close all but the six terminal-profile residual leaves.
4. For the six leaves, a repeated comparator in adjacent `L5,L6` is handled by
   the consecutive-comparator redundancy lemma.

No prior `TIMEOUT` branch is treated as UNSAT evidence.

## Repeated-Comparator Lemma

If comparator `e=(i,j)` occurs in both `L5` and `L6`, then the occurrence in
`L6` is redundant. Both layers are matchings, so no other comparator in either
layer touches `i` or `j`. Comparators on disjoint wires commute, and
compare-exchange on `e` is idempotent. Therefore deleting the repeated final
copy preserves feasibility.

If deleting the repeated comparator makes `L6` empty, the network has effective
depth at most 5. In this hard-instance setting that would contradict the
already confirmed `V(3,9)=6` depth requirement used by the prior normal-form
argument.

## Certificate

Machine-readable certificate:

`experiments/v49_d6_closure_audit/coverage_certificate.json`

The certificate records every enumerated layer-5 matching for each of the six
terminal leaves, its classification, the destination branch, provenance for
any invoked prior `UNSAT`, and an acyclic dependency graph.

The expected pass condition is:

`COVERAGE_AUDIT_PASSED`

with open residuals exactly:

- `A5_residual`
- `B6_residual`
- `B7_residual`
- `B8_residual`
- `B9_residual`
