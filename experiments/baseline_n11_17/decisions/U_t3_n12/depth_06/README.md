# U_t3_n12_depth6

- Problem: U(3,12) at depth 6
- Previous depth-5 status: `TIMEOUT`
- Status: `VERIFIED_SAT`
- Solver status: `SATISFIABLE`
- Runtime seconds: `1003.172956`
- Conclusion: `5 <= UDepth(3,12) <= 6`
- Command: `command.txt`
- Solver input: `instance.lp`
- Raw solver JSON: `solver_raw.json`
- Parsed solver result: `result.json`
- Solver metadata: `solver_metadata.json`
- Network: `network.json`
- Verifier result: `verifier.json`
- Verifier trace summary: `verifier_trace_summary.json`

This depth-6 run is upper-bound scouting. It does not rerun depth 5 and does not create a depth-5 UNSAT certificate.
A SAT witness is accepted only after independent exhaustive binary verification.
