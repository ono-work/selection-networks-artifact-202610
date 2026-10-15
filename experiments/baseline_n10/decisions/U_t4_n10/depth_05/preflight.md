# U(4,10), depth-5 preflight

- pyclingo/libclingo version: `5.8.0`.
- Existing `target_u.lp`, instance generator, parser, and independent verifier are used.
- The verifier accepts `n=10`, `t=4`, `kind=U` parameters.
- Exhaustive verification covers `2^10 = 1024` binary inputs.
- Lightweight U encoding, parser, and verifier regressions: `17 passed`.
- Existing `U(4,9)` lower-bound artifacts were found: depth 4 is `UNSAT`, and depth 5 has an independently verified SAT witness.
  - `experiments/baseline_n9/decisions/U_t4_n9/depth_04/decision.json`
  - `experiments/baseline_n9/decisions/U_t4_n9/depth_04/solver.json`
  - `experiments/baseline_n9/decisions/U_t4_n9/depth_05/network.json`
  - `experiments/baseline_n9/decisions/U_t4_n9/depth_05/verifier.json`
- GPU use: none.
