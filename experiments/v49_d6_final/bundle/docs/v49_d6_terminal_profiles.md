# V(4,9), Depth-6 Terminal Profiles

This document records proved terminal conditions for the six remaining leaves.
It does not infer any layer-5 prohibition by itself.

Let `y` be the binary state after layer 5 and let `z` be the total number of
zeros in `y`. After the fixed final layer is applied, V(4,9) requires output
wire `k` to be zero exactly when `z >= k`, for `k=1,2,3,4`.

## Proved Conditions

For final comparator `(2,3)`:

- `z <= 1`: `y_2 = y_3 = 1`
- `z = 2`: exactly one of `y_2,y_3` is zero
- `z >= 3`: `y_2 = y_3 = 0`

For final comparator `(4,q)`, `q in {5,6}`:

- `z <= 3`: `y_4 = y_q = 1`
- `z >= 4`: at least one of `y_4,y_q` is zero

For A5 and A6, wire 1 is untouched:

- `z = 0`: `y_1 = 1`
- `z >= 1`: `y_1 = 0`

For final comparator `(1,s)`, `s in {6,7,8,9}`:

- `z = 0`: `y_1 = y_s = 1`
- `z >= 1`: at least one of `y_1,y_s` is zero

## Leaf Tables

| leaf | final layer | terminal predicate |
| --- | --- | --- |
| A5 | `{(2,3),(4,5)}` | `(2,3)` profile and `(4,5)` profile and untouched-wire-1 profile |
| A6 | `{(2,3),(4,6)}` | `(2,3)` profile and `(4,6)` profile and untouched-wire-1 profile |
| B6 | `{(1,6),(2,3),(4,5)}` | `(1,6)` profile and `(2,3)` profile and `(4,5)` profile |
| B7 | `{(1,7),(2,3),(4,5)}` | `(1,7)` profile and `(2,3)` profile and `(4,5)` profile |
| B8 | `{(1,8),(2,3),(4,5)}` | `(1,8)` profile and `(2,3)` profile and `(4,5)` profile |
| B9 | `{(1,9),(2,3),(4,5)}` | `(1,9)` profile and `(2,3)` profile and `(4,5)` profile |

## Verification

`src/analyze_v49_d6_terminal_profiles.py` exhaustively checks all `2^9`
binary states. For each leaf, it compares the terminal predicate above with
directly applying the fixed final layer and checking the V(4,9) output
condition on wires 1..4.

These are rigorously proved terminal conditions by exhaustive finite
verification. Any additional observations about layer 5 are heuristic unless
separately proved.
