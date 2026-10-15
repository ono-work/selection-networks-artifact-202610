# U-side depth-8 upper-bound preflight for n=13,14

- pyclingo/libclingo version: `pyclingo version 5.8.0`.
- Previous depth-7 TIMEOUT check errors: `0`.
- Existing `solver/common.lp` and `solver/target_u.lp` are used.
- Existing instance generator, parser, and independent verifier are used.
- Exhaustive verification sizes: `2^13 = 8192`, `2^14 = 16384` binary inputs.
- Only previous depth-7 TIMEOUT rows are raised to depth 8: `U(4..6,13)` and `U(3..7,14)`.
- GPU use: none.
- Sorting-depth citation status: `local note candidate: docs/n11_17/u_upper_bounds_n13_n14_depth7.md`.
- Source report exists: `True` at `experiments/baseline_n10/n10_depth_summary.json`.
- Source report exists: `True` at `docs/n11_17/u_milestone1_depth6_upper_bounds.md`.
- Source report exists: `True` at `docs/n11_17/u_n12_central_depth7_upper_bounds.md`.
- Source report exists: `True` at `docs/n11_17/residual_reuse_n11_u_depth5_depth6.md`.
- Source report exists: `True` at `docs/n11_17/u_upper_bounds_n13_n14_depth7.md`.
