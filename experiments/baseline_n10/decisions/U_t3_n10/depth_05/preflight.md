# U(3,10), depth-5 preflight

- pyclingo/libclingo version: `5.8.0`.
- Existing `target_u.lp`, instance generator, parser, and independent verifier are used.
- The verifier accepts `n=10`, `t=3`, `kind=U` parameters.
- Exhaustive verification covers `2^10 = 1024` binary inputs.
- Lightweight U encoding, parser, and verifier regressions: `17 passed`.
- GPU use: none.
