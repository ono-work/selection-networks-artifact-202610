# Strict provenance closure for the n<=10 tables

Reconstructs, mechanically, which directly computed results the `n <= 10`
depth tables actually rest on, and which are implied by the rest.

## Strict mode

`closure.py` runs in strict mode only. Nothing is seeded from a finished
depth table, from a previous run's summary JSON, or from the manuscript.
Every fact entering the closure carries an explicit provenance type:

| type | meaning |
| ---: | --- |
| 1 | structural boundary value (Corollary 1, Theorem 1(f), definitions) |
| 2 | sorting-network inheritance from literature `SDepth(n)` |
| 3 | direct network UNSAT / exhaustive-search lower bound |
| 4 | verified SAT witness upper bound |
| 5 | finite-state additive weight-game evaluation (Theorem 3) |
| 6 | Nakano-derived bound |
| 7 | DERIVED by the closure (never an input) |

The published tables appear only as `VERIFY_V` / `VERIFY_U`, used solely
as the target the closure output is checked against. They are never added
to the closure state. An earlier version of this script injected them as
"background truth" for non-candidate cells, which made the sufficiency
check vacuous; that behaviour is gone.

## What the run reports

1. Closure from the full evidence pool (159 inputs) reproduces all 110
   cells.
2. The previously claimed 9-input set does **not** close the table. It
   fails at exactly `V(2,5)`, `U(2,5)`, `U(3,5)`, `U(3,6)`.
3. A greedy irredundant set (removing the most expensive provenance
   first, so UNSAT results are dropped in preference to game
   evaluations): **6 UNSAT lower bounds, 5 game lower bounds, 8 verified
   witnesses = 19 direct inputs**.
4. One-at-a-time recheck: every retained input is individually
   load-bearing.
5. Raw game value vs exact depth: **66** matches over all 110 cells,
   **24** once `t in {1, n-1, n}` is set aside (per `n=4..10`:
   2,3,2,4,5,3,5).

## Scope of the irredundancy claim

Irredundancy is relative to the implemented rules and the candidate pool.
We do not claim minimality or uniqueness. The set is visibly non-unique:
`A_U(3,5)` and `A_U(2,5)` are interchangeable, since Theorem 1(d) makes
each imply the other at `n=5`.

## Rerunning

```sh
python3 experiments/provenance_closure/closure.py     # writes closure_report.json
```

`game_values_n_le_10.json` is regenerated from `src/weight_game.py`; see
`experiments/weight_game/` for the `11 <= n <= 17` evaluation.
