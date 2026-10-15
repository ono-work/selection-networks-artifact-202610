# U(5,10), depth-5 preflight

- pyclingo/libclingo version: `5.8.0`.
- Existing `target_u.lp`, instance generator, parser, and independent verifier are used.
- The verifier accepts `n=10`, `t=5`, `kind=U` parameters.
- Exhaustive verification covers `2^10 = 1024` binary inputs.
- Lightweight U encoding, parser, and verifier regressions: `17 passed`.
- No direct `experiments/baseline_n9/decisions/U_t5_n9/` directory was present.
- Existing `U(5,9)` lower bound was confirmed by U-duality from `UDepth(4,9)=5`: depth 4 is `UNSAT`, and depth 5 has an independently verified SAT witness.
  - `experiments/baseline_n9/decisions/U_t4_n9/depth_04/decision.json`
  - `experiments/baseline_n9/decisions/U_t4_n9/depth_04/solver.json`
  - `experiments/baseline_n9/decisions/U_t4_n9/depth_05/network.json`
  - `experiments/baseline_n9/decisions/U_t4_n9/depth_05/verifier.json`
- Existing `U(4,10)` depth-5 artifacts were found and are used only for n=10 table consistency, not for the `U(5,10)` decision.
  - `experiments/baseline_n10/decisions/U_t4_n10/depth_05/result.json`
  - `experiments/baseline_n10/decisions/U_t4_n10/depth_05/network.json`
  - `experiments/baseline_n10/decisions/U_t4_n10/depth_05/verifier.json`
- GPU use: none.
