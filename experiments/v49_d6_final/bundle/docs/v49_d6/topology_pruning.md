# V(4,9) Depth-6 Topology Pruning

This document covers optional special-hard-mode pruning only. It is not part of
the ordinary baseline ASP model.

## Unique-Min Trajectory

For the input with a single zero at source wire `s` and ones elsewhere, a
compare-exchange layer moves that zero only when the zero is on the higher
endpoint of a selected comparator. Since every layer is a matching, there is a
unique deterministic successor wire after each layer.

A V-type selection network with `t >= 1` must put the smallest input value on
output wire 1. Therefore each single-zero input must finish with the zero on
wire 1. The pruning rule enforces this necessary condition for every source.
It is only pruning; the full V target constraints and Python verifier remain
authoritative.

## Backward Dependency Cones

For an output wire `r`, initialize its cone at the final layer to `{r}`. Moving
backward through a comparator `(i,j)`, dependency on either output endpoint
implies dependency on both inputs `i` and `j`; untouched wires propagate
unchanged.

Each V output rank `r in {1,2,3,4}` depends essentially on every input variable:
if input `i` were absent, changing only `i` could not change output `r`. But
fix all other inputs with exactly `r-1` zeros among them. Changing `i` from 1 to
0 changes whether the `r`-th output is 1 or 0. Thus every input must be in every
rank-output cone.

## Regression Gate

The pruning fragment is enabled only by explicit command-line flag in the tail
partition runner, and only when the regression report status is `PASSED`.
UNSAT baseline decisions are preserved by monotonicity under added constraints.
SAT baseline decisions are checked by existing verified witnesses and the full
Python verifier.
