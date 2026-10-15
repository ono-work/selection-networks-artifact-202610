#!/usr/bin/env python3
"""Re-verify every stored SAT witness in this artifact by exhaustive
simulation on all binary inputs.

For each ``network.json`` found under the evidence directories, the network
is re-simulated with ``src.network.simulate`` on every input in {0,1}^n and
checked against the binary selection target with ``src.verify.verify_binary``
(an implementation independent of the ASP encoding). Where a stored verifier
report exists next to the witness, the fresh verdict is compared against it.

This is the cheap, solver-free check a reader should run first. The whole
sweep covers n <= 17 (the largest witness costs 2^17 simulations).

Usage:
  python3 scripts/verify_all_witnesses.py [--report OUT.json]

Exit code 0 iff every witness verifies and no stored report disagrees.
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.verify import verify_binary  # noqa: E402

SEARCH_ROOTS = [
    "experiments",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default=str(ROOT / "generated" /
                                            "witness_verification_report.json"))
    args = ap.parse_args()

    results = []
    failures = []
    t0 = time.time()
    for root in SEARCH_ROOTS:
        for net_path in sorted((ROOT / root).rglob("network.json")):
            # Skip copies inside the frozen V(4,9) bundle: the bundle is a
            # sealed snapshot whose integrity is checked by bundle.sha256;
            # its witness is the same file as the live baseline_n9 copy.
            if "v49_d6_final/bundle/" in str(net_path):
                continue
            try:
                net = json.load(open(net_path))
                kind, n, t = net["kind"], net["n"], net["t"]
                layers = [[tuple(c) for c in layer] for layer in net["layers"]]
            except Exception as e:  # malformed witness is a failure
                failures.append({"network": str(net_path.relative_to(ROOT)),
                                 "error": f"unreadable: {e}"})
                continue
            res = verify_binary(layers, n=n, t=t, kind=kind)
            rec = {
                "network": str(net_path.relative_to(ROOT)),
                "kind": kind, "n": n, "t": t,
                "depth": net.get("depth", len(layers)),
                "checked_binary_inputs": 2 ** n,
                "fresh_ok": bool(res.ok),
            }
            stored = net_path.parent / "verifier.json"
            if stored.exists():
                srep = json.load(open(stored))
                rec["stored_ok"] = bool(srep.get("ok"))
                rec["agrees_with_stored"] = rec["fresh_ok"] == rec["stored_ok"]
                if not rec["agrees_with_stored"]:
                    failures.append(rec)
            if not res.ok:
                rec["counterexample"] = getattr(res, "counterexample", None)
                failures.append(rec)
            results.append(rec)

    report = {
        "witnesses_checked": len(results),
        "all_ok": not failures,
        "failures": failures,
        "wall_seconds": round(time.time() - t0, 2),
        "results": results,
    }
    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(report, open(out, "w"), indent=1)
    print(f"witnesses checked : {len(results)}")
    print(f"all ok            : {report['all_ok']}")
    print(f"wall seconds      : {report['wall_seconds']}")
    print(f"report            : {out}")
    if failures:
        for f in failures[:10]:
            print("FAILURE:", f, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
