# U_t5_n12_depth7

- Problem: U(5,12) at depth 7
- Previous depth-6 status: `TIMEOUT`
- Status: `VERIFIED_SAT`
- Solver status: `SATISFIABLE`
- Runtime seconds: `922.913407`
- Conclusion: `5 <= UDepth(5,12) <= 7`
- Command: `command.txt`
- Solver input: `instance.lp`
- Raw solver JSON: `solver_raw.json`
- Parsed solver result: `result.json`
- Solver metadata: `solver_metadata.json`
- Network: `network.json`
- Verifier result: `verifier.json`
- Verifier trace summary: `verifier_trace_summary.json`

This depth-7 run is upper-bound scouting. It does not rerun depth 5 or depth 6 and does not create a depth-5/6 UNSAT certificate.
A SAT witness is accepted only after independent exhaustive binary verification.
