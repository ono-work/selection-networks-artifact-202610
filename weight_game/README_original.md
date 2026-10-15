# Additive weight-game evaluation, n <= 17

Reproduces the finite-state evaluation of the additive certificate-weight
game (`src/weight_game.py`) reported in the paper's "An Additive
Weight-Game Lower Bound" section, Theorem "A_U(t,n) <= UDepth(t,n),
A_V(t,n) <= VDepth(t,n)".

## Contents

- `results_n11_17.json`: one entry per `{kind}_{t}_{n}` with the computed
  game value `A`, the number of rounds the search recorded (`A + 1` unless
  the search was cut off), the largest dominance-pruned frontier size seen
  at any round (`max_frontier_size`), wall-clock time, and whether the
  search reached the target within the round budget (`complete`).
- `sweep_log.txt`: the run's console output, in order, for an
  independently readable audit trail alongside the JSON.
- `run_sweep.py`: the driver. Re-running it with `results_n11_17.json`
  present resumes from what is already stored and only computes missing
  cells.

## Scope and completeness

U-type: every cell for `1 <= t <= n`, `11 <= n <= 17` is covered, either
directly (`t <= floor(n/2)`) or via the paper's Corollary
"`UDepth(t,n) >= max{A_U(t,n), A_U(n-t,n)}`" applied to the direct value at
the dual `t' = n - t <= floor(n/2)`; state spaces up to `T = t+1 = 9` were
evaluated.

V-type has no such duality, so cost grows with `t` directly. Every
non-exact cell with `n <= 16` is covered (the `t >= 13` columns at these
`n` are already exact via padding and sorting-network inheritance, so the
run stopped before reaching them without leaving a gap), and at `n = 17`
every `t <= 11` (state spaces up to `T = 12`). The four cells at `n = 17`,
`12 <= t <= 15` (state spaces `T >= 13`, still unresolved intervals in
the table) were not evaluated within the wall-clock budget used for this
run and are reported in the paper as not checked, not as bounded below
the target.

## Regression tests

`tests/test_weight_game.py` checks, independently of this sweep: no
violation of `A_U <= UDepth`, `A_V <= VDepth` across every exact value for
`n <= 10`; the eight cells the paper reports as newly theory-derived
match exactly; `UDepth(4,6) = 4` is *not* reachable by the game (`A_U(4,6)
= 3`, confirming this cell's provenance stays computational); the `t = 1`
boundary matches `ceil(log2 n)`; dominance-pruned search matches
unpruned breadth-first search on every case with `n <= 8`; and the O(T)
domination-check formulas match a generic sorted-tail-count
characterization on 2,000 random states.

## Rerunning

```sh
python3 -m experiments.weight_game.run_sweep
```
