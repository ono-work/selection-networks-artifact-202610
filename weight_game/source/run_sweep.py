"""Reproduce the n<=17 additive weight-game evaluation reported in the paper.

Usage:
    python3 -m experiments.weight_game.run_sweep

Computes A_U(t,n) for every 1 <= t <= floor(n/2), n = 11..17 (U-type; the
dual t = n-t is covered for free by Corollary "UDepth(t,n) >=
max{A_U(t,n), A_U(n-t,n)}", so this is complete coverage for every U-type
cell in that range), and A_V(t,n) for V-type up to a wall-clock budget
(V-type has no duality shortcut, so larger t means a larger, more
expensive state space; state spaces with T = t+1 >= 13 were not evaluated
for n=17 in the run reported in the paper).

Results are written incrementally to results_n11_17.json, keyed
"{kind}_{t}_{n}", so the script can be interrupted and resumed. The
version of this file used for the paper is checked in alongside this
script; deleting it before rerunning reproduces it from scratch (subject
to the same wall-clock budget below).
"""
import json
import time
from pathlib import Path

from src.weight_game import compute_A

OUT = Path(__file__).parent / "results_n11_17.json"
LOG = Path(__file__).parent / "sweep_log.txt"

MAX_ROUNDS = 11
V_WALLCLOCK_BUDGET_SECONDS = 60 * 55


def _load():
    if OUT.exists():
        return json.loads(OUT.read_text())
    return {}


def _save(results):
    OUT.write_text(json.dumps(results, indent=1, sort_keys=True))


def _log(handle, *parts):
    line = " ".join(str(p) for p in parts)
    print(line)
    print(line, file=handle, flush=True)


def main():
    results = _load()
    with LOG.open("a") as handle:
        # U-type: t = 1..floor(n/2) suffices for every n via duality.
        for n in range(11, 18):
            for t in range(1, n // 2 + 1):
                key = f"U_{t}_{n}"
                if key in results:
                    continue
                t0 = time.time()
                a, trace = compute_A("U", t, n, max_rounds=MAX_ROUNDS)
                dt = time.time() - t0
                results[key] = {
                    "A": a,
                    "time_seconds": dt,
                    "rounds_recorded": len(trace),
                    "max_frontier_size": max(x[1] for x in trace),
                    "complete": a is not None,
                }
                _log(handle, f"U t={t} n={n} (dual t={n - t}):",
                     f"A={a} time={dt:.2f}s frontier<={results[key]['max_frontier_size']}")
                _save(results)

        # V-type: no duality; increasing t is markedly more expensive, so
        # cheapest (smallest-t) cells across every n are computed first.
        todo = sorted(
            ((t, n) for n in range(11, 18) for t in range(1, n + 1)),
            key=lambda tn: (tn[0], tn[1]),
        )
        deadline = time.time() + V_WALLCLOCK_BUDGET_SECONDS
        for t, n in todo:
            key = f"V_{t}_{n}"
            if key in results:
                continue
            if time.time() > deadline:
                _log(handle, f"V sweep: wall-clock budget exhausted before t={t} n={n}; stopping")
                break
            t0 = time.time()
            a, trace = compute_A("V", t, n, max_rounds=MAX_ROUNDS)
            dt = time.time() - t0
            results[key] = {
                "A": a,
                "time_seconds": dt,
                "rounds_recorded": len(trace),
                "max_frontier_size": max(x[1] for x in trace),
                "complete": a is not None,
            }
            _log(handle, f"V t={t} n={n}: A={a} time={dt:.2f}s frontier<={results[key]['max_frontier_size']}")
            _save(results)
        _log(handle, "SWEEP DONE")


if __name__ == "__main__":
    main()
