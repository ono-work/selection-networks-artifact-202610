# V(4,9) Depth-6 L5 Tail Partition

The unresolved parent branch definitions are recovered from
`src.run_v49_d6_l5_partitioned.branch_definitions()`, not reconstructed from
prose.

## A5_residual_L5eq3

The census enumerates every size-3 L5 matching satisfying the recovered A5
residual no-repeat restrictions. Each matching has exactly one status for wire
1: unused, or paired with a unique partner in `{2,...,9}`. These categories are
pairwise disjoint because a matching gives wire 1 at most one partner, and they
cover all compatible matchings because wire 1 is either used or unused.

## B6_residual_L5eq3

The census records the exact partner signature `(p1,p6)`, where `0` means the
wire is unused. A matching gives each wire at most one partner, so two distinct
signatures cannot contain the same matching. Every compatible matching has one
such signature. The coarse status for wires 1 and 6 is reported only as summary
metadata; the exact signature is the partition key.

## B6_residual_L5eq4

A size-4 matching on 9 wires touches 8 wires and leaves exactly one wire unused.
The unused-wire categories are therefore disjoint and exhaustive.

The machine-readable certificate is
`experiments/v49_d6_l5_tail_census/coverage_certificate.json`.
