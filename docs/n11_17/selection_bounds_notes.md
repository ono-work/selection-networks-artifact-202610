# Selection bounds notes for n=11..17

## Values inherited from n=10

The seed exact values are read from `experiments/baseline_n10/n10_depth_summary.json` and checked against the expected V/U rows.

## Values derived by monotonicity in n

Only lower bounds propagate from smaller n to larger n. This is used for V(2), V(3), V(t>=4), and U lower bounds inherited from n<=10.

## Values derived by V t-monotonicity

V upper bounds propagate from larger t to smaller t. V lower bounds propagate from smaller t to larger t. The tests assert that the opposite directions are not applied.

## Values derived by U-duality

U-duality fills mirrored U entries only. It is not applied to V. It is used to avoid duplicate frontier experiments for t and n-t.

## Values using sorting upper bounds

Sorting upper bounds use the planning table supplied for n=1..17. Local notes cite Dobbelaere/Bundala-Zavodny support through n<=16; n=17 remains `TODO_SORTING_DEPTH_CITATION`/planning assumption until a local citation is added.

## Implementation assumptions

- Bounds are integer comparator-layer depths.
- Missing lower or upper sources are represented as gaps, not exact values.
- Runtime is not used as evidence.
- The plan does not create solver instances or launch clingo.

## Next concrete Codex commands

After this planning step, choose one milestone and ask Codex to run only the listed experiment(s), for example:

```text
Run the Milestone 1 U-side frontier experiments for n=11,12 in order, using the existing ASP pipeline, saving artifacts separately, and stop on TIMEOUT.
```
