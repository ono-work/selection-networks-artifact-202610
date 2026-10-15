# Weight Game (curated view)

Curated copy of the additive weight-game implementation and results. The
canonical, importable locations inside this artifact are:

- implementation: `../src/weight_game.py` (tests: `../tests/test_weight_game.py`)
- sweep runner and results at their original repository-relative home:
  `../experiments/weight_game/` (so
  `python3 -m experiments.weight_game.run_sweep` works from the artifact
  root exactly as in the original repository)

Files here:

- `source/weight_game.py`, `source/run_sweep.py`, `source/test_weight_game.py`
  — byte-identical copies for inspection.
- `results/results_n11_17.json` — A_U / A_V values for 11 <= n <= 17
  (130 cells, all `complete: true`), the file consumed by
  `../scripts/reconstruct_final_tables.py`.
- `results/sweep_log.txt` — one-line-per-cell audit trail of the sweep.
- `results/game_values_n_le_10.json` — the n <= 10 game values consumed by
  the strict closure (`../experiments/provenance_closure/closure.py`),
  containing the paper's five direct inputs
  `A_V(2,5)=4, A_U(3,5)=3, A_U(2,9)=A_U(3,9)=A_U(4,9)=5`.
- `README_original.md` — the original experiment README.

See `../PAPER_RESULTS.md` sections E and F for the claim mapping, including
the 44 improved lower endpoints
(`../generated/weight_game_improvements.csv`).
