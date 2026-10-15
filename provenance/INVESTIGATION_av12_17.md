# Investigation Note: the stored A_V(12,17) = 8 record

Date: 2026-10-16. Investigation only; no file was modified, no experiment
was rerun. Conclusions are based entirely on the preserved artifact
records listed below.

Question investigated: the documentation states that, for the V-type
weight game at n = 17, the four cells 12 <= t <= 15 were not evaluated,
yet the preserved data contains A_V(12,17) = 8. Which is right, and does
anything depend on it?

## 1. All occurrences of the record

| File | Content |
| --- | --- |
| `weight_game/results/results_n11_17.json` (key `V_12_17`) | `{"A": 8, "complete": true, "max_frontier_size": 1474, "rounds_recorded": 9, "time_seconds": 1501.37}` |
| `experiments/weight_game/results_n11_17.json` | byte-identical copy (verified) |
| `weight_game/results/sweep_log.txt` line 130 (and the identical copy under `experiments/weight_game/`) | `V t=12 n=17: A=8 time=1501.37s frontier<= 1474` — the final line of the log |
| `PAPER_RESULTS.md` section F | parenthetical disclosure added during packaging cleanup |
| `generated/final_bounds_n11_17.{csv,json}` | cell row `V, n=17, t=12: lower 9, upper 10, base_lower_pre_game 9, weight_game_bound 8, improved_by_weight_game false` |
| `generated/weight_game_improvements.csv` | absent (correct: the only V-type improvements are (n,t) = (17,8), (17,9)) |
| `provenance/ARTIFACT_INVENTORY.md`, `provenance/artifact_inventory_details_20261015.md` | the "15 V-type cells unevaluated" framing; the enumerated missing set is t >= 13, consistent with the data |

No other reference exists: no code filter excluding the cell, no
exclusion note, no invalidation record. `tests/test_weight_game.py` does
not recompute this specific cell.

## 2. Status of the record: COMPLETE

- `complete: true` under the recorded semantics of
  `experiments/weight_game/run_sweep.py` (`complete = (A is not None)`),
  where `src/weight_game.py:compute_A` returns the exact minimum
  dominating round count from the same exhaustive BFS with Pareto
  pruning used for every published weight-game value.
- Produced by the same final implementation, in the same single sweep
  run as all published values (the log contains no duplicate cell lines,
  so the resumable runner was never resumed).
- Full runtime/frontier/round records exist: 1501.37 s, frontier <= 1474,
  target first dominated at round 8.
- It is not partial, stale, aborted, exploratory, or imported, and
  nothing in the record suggests later invalidation or deliberate
  exclusion.

## 3. How the discrepancy arose (code-level reconstruction)

`run_sweep.py` processes V-type cells sorted by `(t, n)` under a
**global** 55-minute wall-clock budget for the whole V section, checked
**before starting each cell**. The preserved timings sum to about
54.4 minutes of V-section time up to and including `V_12_17`, i.e. the
entire t = 12 column (n = 12..17) ran legitimately inside the budget.

Decisively, the preserved log contains **neither** the
`"V sweep: wall-clock budget exhausted ..."` line **nor** the
`"SWEEP DONE"` marker, both of which the code prints unconditionally on
any normal termination path. Therefore the sweep process was interrupted
or killed while computing the first t = 13 cell (state space T = 14),
after `V_12_17` had already been saved. The docstring/README description
of the V-type domain ("state spaces with T = t+1 >= 13 were not
evaluated for n = 17") reflects the planned cutoff; the paper text was
evidently written from that plan, while the preserved run in fact
completed all of t = 12 (T = 13) before dying.

In the requested vocabulary: the t = 12 cells were *attempted*,
*completed*, and *retained* in the results file; they are *loaded* by
the table reconstruction but *not used* (dominated); and they were
*wrongly declared unevaluated* in the prose.

## 4. Effect on the published table: none

Published value: VDepth(12,17) = [9,10]. The lower endpoint 9 is
structural: VDepth(12,17) >= VDepth(12,13) = SDepth(13) = 9
(n-monotonicity to the exact sorting cell; visible as
`base_lower_pre_game = 9` in `generated/final_bounds_n11_17.csv`).
`scripts/reconstruct_final_tables.py` loads A_V(12,17) = 8 as a game
seed; it is dominated (8 < 9) and changes nothing
(`improved_by_weight_game = false`). A game lower bound weaker than a
structural one is expected and is not a contradiction. No published
bound depends on this record.

## 5. Verdict

Interpretation **A** of the briefing, with one nuance: A_V(12,17) = 8 is
a **valid, completed exhaustive game evaluation** by the final
implementation, so the statement "the four cells n = 17, 12 <= t <= 15
were not evaluated" is **factually too broad** — only the **three**
cells 13 <= t <= 15 were not evaluated. The omission appears accidental
(prose written from the planned domain; run interrupted during t = 13
without reaching its end-of-run marker), not a documented deliberate
exclusion. The paper's companion claims survive unchanged: "every
non-exact cell at n <= 16" remains true (the t = 12 cells at n <= 16 are
exact cells and were evaluated anyway), and no numerical value anywhere
is affected.

## 6. Minimal proposed correction (NOT yet applied)

1. Paper (camera-ready, if editable): state that the V-type game was
   evaluated at every t <= 12 for n = 17 (state spaces up to T = 13) and
   that the three remaining cells 13 <= t <= 15 were not evaluated;
   optionally note A_V(12,17) = 8 improves no bound.
2. `PAPER_RESULTS.md` section F: replace the current "four cells ...
   not evaluated" sentence plus parenthetical with the three-cell
   statement matching the preserved data (noting the paper's four-cell
   phrasing as a known discrepancy if the camera-ready cannot change).
3. Leave untouched as historical records: `weight_game/README*.md`,
   `experiments/weight_game/run_sweep.py` docstring, the sweep log, and
   the results JSON. The discrepancy is documented about them, not by
   rewriting them.

## 7. Blocker assessment

Not a blocker for making the repository public: all data is preserved
and internally consistent, and `PAPER_RESULTS.md` already discloses the
stored t = 12 record. Recommended nonetheless: apply correction (2)
(one sentence) before flipping visibility, since the current sentence
contradicts both the adjacent parenthetical and the bundled data.
