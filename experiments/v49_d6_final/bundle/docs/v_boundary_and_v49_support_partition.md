# V-boundary inputs and V(4,9) support partition

This note records implementation-local justifications only. It is not a novelty or exactness claim.

## V-type boundary inputs

For V-type `t`-selection on binary inputs, output wire `r` for `1 <= r <= t` is required to be `0` exactly when the input contains at least `r` zeros. Equivalently, for each fixed output wire `r`, the required Boolean target changes only between the Hamming layers with `r - 1` zeros and `r` zeros.

Every output wire of a comparator network is a monotone Boolean function of the input bits: replacing an input `1` by `0` cannot make any later wire value larger in the `0 < 1` order, because each comparator computes a local min/max pair and min/max are monotone in both arguments. Therefore, if the V-type specification is satisfied on the two boundary layers for every `r <= t`, it is satisfied on all lower-zero and higher-zero layers by monotonicity of both the network output and the target threshold.

The union of these boundary layers for ranks `1..t` is exactly the set of binary inputs with `0,1,...,t` zeros. The optional `v_boundary` input mode generates only those inputs. The ordinary `full` mode remains the default and still generates all `2^n` inputs.

## V(4,9), depth-6 last-layer normal form

In the special hard instance `V(4,9)` at depth `6`, all six layers are required to be nonempty. This relies on the already confirmed fact `V(3,9) = 6`: if a depth-6 `V(4,9)` network had an empty layer, its effective depth would be at most `5`, and the first three output wires would also form a depth-at-most-5 `V(3,9)` network, contradicting that confirmed result.

A comparator in the final layer whose endpoints both lie in wires `{5,6,7,8,9}` changes only non-output wires for `V(4,9)`, whose observed outputs are wires `{1,2,3,4}`. Such a comparator can be deleted without changing the final values on wires `1..4`.

If deleting all suffix-only final comparators made the final layer empty, the resulting network would again have effective depth at most `5` while preserving the first three V-type outputs, contradicting `V(3,9) = 6`. Therefore the special hard mode may forbid suffix-only final-layer comparators without excluding any depth-6 `V(4,9)` solution. This restriction is not applied to baseline experiments.

## Support partition

For final layer `L6`, define `T(L6)` as the subset of output wires `{1,2,3,4}` touched by final-layer comparators. Under the special hard-mode constraints, `T(L6)` is nonempty. The 15 nonempty subsets of `{1,2,3,4}` are pairwise disjoint by equality of touched output-wire support, and they cover every valid final layer satisfying the normal form.
