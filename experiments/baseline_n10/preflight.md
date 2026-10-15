# n=10 V-selection preflight

- clingo command: `.venv/bin/python -m clingo`
- clingo version: `pyclingo version 5.8.0`
- existing verifier accepts `n=10`, `t=2,3`, `kind=V` parameters.
- exhaustive binary verification size: `2^10 = 1024` inputs.
- existing decision components used: `generate_instance`, `target_v.lp`, `parse_selected_network`, `verify_binary`.
- GPU use: none.
