# U(2,10), depth-5 preflight

- pyclingo/libclingo version: `5.8.0`.
- Existing `target_u.lp`, instance generator, parser, and independent verifier are used.
- The verifier accepts `n=10`, `t=2`, `kind=U` parameters.
- Exhaustive verification covers `2^10 = 1024` binary inputs.
- Lightweight U encoding, parser, and verifier regressions: `17 passed`.
- GPU use: none.
- Previous `U(2,10)` depth-4 UNSAT artifact: confirmed.
- The verified `V(3,10)` depth-6 network was independently accepted as both `V(2,10)` and `U(2,10)` on all 1024 binary inputs.
- This V-type implication is not inferred from the separate `U(3,10)` witness.
