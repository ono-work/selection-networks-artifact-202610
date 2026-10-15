# Frontier experiments for n=11..17

No solver command is run by this planning step. The list below is derived from current bounds only.

## Recommended order

1. U side first: U-duality halves the targets, and the n=10 U cases closed at depth 5.
2. V small-t second: V(2,n) and V(3,n) are isolated from the t>=4 sorting frontier.
3. V sorting-frontier third: test S(n)-1 to find where V-depth reaches full sorting depth.

## First 10 experiments

1. `U(2,11) at depth 5` (Milestone 1: n=11,12, A_U_FIRST)
2. `U(3,11) at depth 5` (Milestone 1: n=11,12, A_U_FIRST)
3. `U(4,11) at depth 5` (Milestone 1: n=11,12, A_U_FIRST)
4. `U(5,11) at depth 5` (Milestone 1: n=11,12, A_U_FIRST)
5. `U(2,12) at depth 5` (Milestone 1: n=11,12, A_U_FIRST)
6. `U(3,12) at depth 5` (Milestone 1: n=11,12, A_U_FIRST)
7. `U(4,12) at depth 5` (Milestone 1: n=11,12, A_U_FIRST)
8. `U(5,12) at depth 5` (Milestone 1: n=11,12, A_U_FIRST)
9. `U(6,12) at depth 5` (Milestone 1: n=11,12, A_U_FIRST)
10. `V(2,11) at depth 6` (Milestone 1: n=11,12, B_V_SMALL_T)

## Milestones

### Milestone 1: n=11,12

- `U(2,11) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(3,11) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(4,11) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(5,11) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(2,12) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(3,12) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(4,12) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(5,12) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(6,12) at depth 5`: U-side first; U-duality removes the mirrored target.
- `V(2,11) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(3,11) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(2,12) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(3,12) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(4,11) at depth 7`: Find the smallest t whose V-depth reaches SortDepth(n); UNSAT at S-1 propagates to all larger t.
- `V(4,12) at depth 7`: Find the smallest t whose V-depth reaches SortDepth(n); UNSAT at S-1 propagates to all larger t.

### Milestone 2: n=13,14

- `U(2,13) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(3,13) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(4,13) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(5,13) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(6,13) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(2,14) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(3,14) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(4,14) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(5,14) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(6,14) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(7,14) at depth 5`: U-side first; U-duality removes the mirrored target.
- `V(2,13) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(3,13) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(2,14) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(3,14) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(4,13) at depth 8`: Find the smallest t whose V-depth reaches SortDepth(n); UNSAT at S-1 propagates to all larger t.
- `V(4,14) at depth 8`: Find the smallest t whose V-depth reaches SortDepth(n); UNSAT at S-1 propagates to all larger t.

### Milestone 3: n=15,16,17

- `U(2,15) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(3,15) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(4,15) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(5,15) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(6,15) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(7,15) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(2,16) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(3,16) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(4,16) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(5,16) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(6,16) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(7,16) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(8,16) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(2,17) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(3,17) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(4,17) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(5,17) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(6,17) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(7,17) at depth 5`: U-side first; U-duality removes the mirrored target.
- `U(8,17) at depth 5`: U-side first; U-duality removes the mirrored target.
- `V(2,15) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(3,15) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(2,16) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(3,16) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(2,17) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(3,17) at depth 6`: Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.
- `V(4,15) at depth 8`: Find the smallest t whose V-depth reaches SortDepth(n); UNSAT at S-1 propagates to all larger t.
- `V(4,16) at depth 8`: Find the smallest t whose V-depth reaches SortDepth(n); UNSAT at S-1 propagates to all larger t.
- `V(4,17) at depth 9`: Find the smallest t whose V-depth reaches SortDepth(n); UNSAT at S-1 propagates to all larger t.

## Expected conclusion patterns

- SAT at the current lower-bound depth closes the upper side for that entry.
- UNSAT at the current lower-bound depth raises the lower bound by one.
- For V sorting-frontier tests at S(n)-1, UNSAT closes that target and all larger V targets at S(n) by V lower-bound monotonicity plus sorting upper bound.
- TIMEOUT must be recorded honestly and must not be treated as UNSAT; only then consider partition or certificate strategies.
