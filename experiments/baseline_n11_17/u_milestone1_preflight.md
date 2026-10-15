# U-side Milestone 1 preflight for n=11,12

- pyclingo/libclingo version: `pyclingo version 5.8.0`.
- Existing `solver/common.lp` and `solver/target_u.lp` are used.
- Existing instance generator, parser, and independent verifier are used.
- Exhaustive verification sizes: `2^11 = 2048`, `2^12 = 4096` binary inputs.
- n=10 integrated summary exists: `True` at `experiments/baseline_n10/n10_depth_summary.json`.
- selection bounds table exists: `True` at `experiments/selection_bounds_n11_17/bounds_table.csv`.
- U-duality is used only for report consequences, not as a solver shortcut.
- GPU use: none.
