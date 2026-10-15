#!/usr/bin/env python3
"""Mechanically reconstruct the final n = 11..17 bound tables of the paper.

This script rebuilds every lower and upper bound shown in Tables
``tab:v-depth``, ``tab:v-depth-b``, ``tab:u-depth``, ``tab:u-depth-b`` of
the CANDAR 2026 paper "Exact Depths and Bounds for Small Selection
Networks", including the forty-four lower-endpoint improvements obtained
from the additive weight game, from stored computational and structural
inputs only.

INPUTS (all are pre-existing artifacts in this repository; the manuscript
tables are NEVER read as inputs):

  1. exact n <= 10 depth table
       experiments/n10_selection_depth_completion/bounds_table.csv
     (output of the audited n <= 10 closure; every row is EXACT)
  2. audited upper bounds for 11 <= n <= 17
       experiments/baseline_n11_17/paper_ready_upper_bounds/
         paper_ready_upper_bounds_{U,V}.csv
     (solver-free re-derivation over verified witnesses, two-block
     composition, padding, duality, and the sorting fallback; 2026-07-17)
  3. additive weight-game values
       weight_game/results/results_n11_17.json
     (A_U(t,n) for every t <= floor(n/2), 11 <= n <= 17, and A_V(t,n)
     where evaluated; all entries complete: true)
  4. the independently verified U(2,17) depth-6 witness
       experiments/u2_n17_d6_witness_search/20260808_030007Z/
     (network.json depth 6; two exhaustive verifiers over all 2^17 inputs)
  5. structural facts with literature provenance (constants below):
     optimal sorting-network depths for 11 <= n <= 17 and the Nakano t=2
     lower bound, as cited in the paper.

DERIVATION:

  base lower bounds   = fixpoint of {n-monotonicity from the exact n <= 10
                        table, ceil(log2 n) at t=1, U-type mirror duality,
                        UDepth(n,n)=0, VDepth(n-1,n)=VDepth(n,n)=SDepth(n),
                        Nakano t=2 V-type lower bound}
                        (cross-checked cell-by-cell against the stored
                        lower_bound_if_known column of input 2)
  final lower bounds  = the same fixpoint with the weight-game bounds added
                        as seeds, where the weight-game bound of a U cell is
                        max{A_U(t,n), A_U(n-t,n)} over the evaluated side(s)
                        (Corollary game-duality) and of a V cell is A_V(t,n)
                        when evaluated (no V-type duality).
                        Re-running the fixpoint matters for exactly two
                        cells: U(5,14) and U(9,14) have raw game value 5,
                        and their final lower bound 6 is obtained as
                        UDepth(9,14) >= UDepth(9,13) = UDepth(4,13) >=
                        A_U(4,13) = 6 (n-monotonicity on a game-improved
                        cell) followed by mirror duality to U(5,14).
  final upper bounds  = input 2, improved only by the verified U(2,17)
                        depth-6 witness (input 4) and its mirror dual
                        U(15,17)

VERIFICATION (the script FAILS, exit code 1, on any mismatch):

  - recomputed base lower bounds agree with the stored
    lower_bound_if_known column for every cell;
  - exactly 44 cells improve, all by exactly one layer;
  - 42 improvements are U-type and 2 are V-type;
  - the two V-type improvements are (n, t) = (17, 8) and (17, 9);
  - U(2,17) and U(15,17) are reconstructed as exact depth 6;
  - lower <= upper for every cell;
  - the reconstructed tables agree exactly with
    scripts/expected_paper_tables_n11_17.json, a hand transcription of the
    final manuscript tables used ONLY as a verification target.

OUTPUTS:

  generated/final_bounds_n11_17.csv
  generated/final_bounds_n11_17.json
  generated/final_tables_n11_17.tex
  generated/weight_game_improvements.csv

Usage:
  python3 scripts/reconstruct_final_tables.py
"""
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

N10_TABLE = (ROOT / "experiments/n10_selection_depth_completion/"
             "bounds_table.csv")
PAPER_READY = (ROOT / "experiments/baseline_n11_17/"
               "paper_ready_upper_bounds")
GAME_RESULTS = ROOT / "weight_game/results/results_n11_17.json"
U2N17_RUN = (ROOT / "experiments/u2_n17_d6_witness_search/"
             "20260808_030007Z")
EXPECTED = Path(__file__).resolve().parent / "expected_paper_tables_n11_17.json"
OUT = ROOT / "generated"

NS = range(11, 18)

# Optimal sorting-network depths, 11 <= n <= 17 (literature values cited in
# the paper: Bundala and Zavodny for n <= 16; Ehlers and Mueller for n = 17).
SDEPTH = {11: 8, 12: 8, 13: 9, 14: 9, 15: 9, 16: 9, 17: 10}


def ceil_log2(x: int) -> int:
    return math.ceil(math.log2(x)) if x > 1 else 0


def floor_log2(x: int) -> int:
    return math.floor(math.log2(x)) if x > 1 else 0


def nakano_v2_lower(n: int) -> int:
    """Nakano general t=2 lower bound: floor(log2 n) + ceil(log2 floor(log2 n))."""
    fl = floor_log2(n)
    return fl + (ceil_log2(fl) if fl >= 1 else 0)


def fail(msg: str):
    print(f"RECONSTRUCTION FAILED: {msg}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Input 1: exact n <= 10 table
# ---------------------------------------------------------------------------
def load_exact_n10():
    exact = {}
    with open(N10_TABLE) as f:
        for r in csv.DictReader(f):
            kind, n, t = r["kind"], int(r["n"]), int(r["t"])
            if r["status"] != "EXACT":
                fail(f"n<=10 table cell ({kind},{t},{n}) is not EXACT")
            lo, up = int(r["lower"]), int(r["upper"])
            if lo != up:
                fail(f"n<=10 EXACT cell ({kind},{t},{n}) has lower != upper")
            exact[(kind, t, n)] = lo
    if len(exact) != 110:  # 55 cells per kind, V and U
        fail(f"expected 110 exact n<=10 cells, found {len(exact)}")
    return exact


# ---------------------------------------------------------------------------
# Input 2: audited upper bounds and stored lower bounds, 11 <= n <= 17
# ---------------------------------------------------------------------------
def load_paper_ready():
    upper, stored_lower = {}, {}
    for kind in ("U", "V"):
        with open(PAPER_READY / f"paper_ready_upper_bounds_{kind}.csv") as f:
            for r in csv.DictReader(f):
                n, t = int(r["n"]), int(r["t"])
                if not (11 <= n <= 17 and 1 <= t <= n):
                    continue
                upper[(kind, t, n)] = int(r["best_upper_bound"])
                if r["lower_bound_if_known"].strip():
                    stored_lower[(kind, t, n)] = int(r["lower_bound_if_known"])
    return upper, stored_lower


# ---------------------------------------------------------------------------
# Input 3: weight-game values
# ---------------------------------------------------------------------------
def load_game():
    with open(GAME_RESULTS) as f:
        raw = json.load(f)
    A = {}
    for key, rec in raw.items():
        kind, t, n = key.split("_")
        if not rec.get("complete", False):
            fail(f"weight-game entry {key} is not marked complete")
        A[(kind, int(t), int(n))] = int(rec["A"])
    return A


def game_bound(A, kind, t, n):
    """Best available weight-game lower bound for one cell.

    U-type: max over the evaluated side(s) of {A_U(t,n), A_U(n-t,n)}
    (Corollary game-duality). V-type: A_V(t,n) when evaluated; V-type has
    no mirror duality.
    """
    cands = []
    if (kind, t, n) in A:
        cands.append(A[(kind, t, n)])
    if kind == "U" and 1 <= n - t <= n and (kind, n - t, n) in A:
        cands.append(A[(kind, n - t, n)])
    return max(cands) if cands else None


# ---------------------------------------------------------------------------
# Input 4: the verified U(2,17) depth-6 witness
# ---------------------------------------------------------------------------
def load_u2n17_witness():
    net = json.load(open(U2N17_RUN / "network.json"))
    vp = json.load(open(U2N17_RUN / "verifier_primary.json"))
    vi = json.load(open(U2N17_RUN / "verifier_independent.json"))
    if not (net.get("kind") == "U" and net.get("n") == 17 and net.get("t") == 2):
        fail("u2_n17 witness network.json is not a U(2,17) network")
    depth = net.get("depth", len(net.get("layers", [])))
    if depth != 6:
        fail(f"u2_n17 witness depth is {depth}, expected 6")
    if not vp.get("ok"):
        fail("u2_n17 primary verifier did not pass")
    if not (vi.get("ok") and vi.get("checked") == 2 ** 17 and vi.get("failures") == []):
        fail("u2_n17 independent verifier did not pass on all 2^17 inputs")
    return depth


# ---------------------------------------------------------------------------
# Base lower bounds: fixpoint of the structural rules over 11 <= n <= 17
# ---------------------------------------------------------------------------
def compute_lower_fixpoint(exact10, extra_seeds=None):
    """Fixpoint of the structural lower-bound rules over 11 <= n <= 17.

    extra_seeds, when given, maps (kind, t, n) -> additional lower bound
    (used to add the weight-game bounds for the final table).
    """
    lb = {}

    def cells():
        for n in NS:
            for t in range(1, n + 1):
                yield t, n

    # seeds
    for t, n in cells():
        for kind in ("U", "V"):
            v = 0
            if t == 1:
                v = max(v, ceil_log2(n))          # Depth(1,n) = ceil(log2 n)
            if kind == "V":
                if t == 2:
                    v = max(v, nakano_v2_lower(n))  # Nakano t=2 lower bound
                if t in (n - 1, n):
                    v = max(v, SDEPTH[n])          # VDepth(n-1,n)=VDepth(n,n)=SDepth(n)
            # n-monotonicity from the exact n <= 10 base (largest m <= 10 with t <= m)
            for m in range(min(10, n - 1), t - 1, -1):
                if (kind, t, m) in exact10:
                    v = max(v, exact10[(kind, t, m)])
                    break
            if extra_seeds:
                g = extra_seeds.get((kind, t, n))
                if g is not None:
                    v = max(v, g)
            lb[(kind, t, n)] = v

    # fixpoint: n-monotonicity within 11..17 and U-type mirror duality
    changed = True
    while changed:
        changed = False
        for t, n in cells():
            for kind in ("U", "V"):
                v = lb[(kind, t, n)]
                if n - 1 >= 11 and t <= n - 1:
                    v = max(v, lb[(kind, t, n - 1)])
                if kind == "U" and 1 <= n - t <= n:
                    v = max(v, lb[(kind, n - t, n)])
                if v > lb[(kind, t, n)]:
                    lb[(kind, t, n)] = v
                    changed = True
    for n in NS:
        if lb[("U", n, n)] != 0:
            fail(f"UDepth({n},{n}) lower bound is not 0")
    return lb


# ---------------------------------------------------------------------------
def main():
    exact10 = load_exact_n10()
    upper, stored_lower = load_paper_ready()
    A = load_game()
    load_u2n17_witness()

    # ---- base lower bounds and cross-check against the stored column
    base_lower = compute_lower_fixpoint(exact10)
    mismatches = []
    for key, v in stored_lower.items():
        if base_lower.get(key) != v:
            mismatches.append((key, base_lower.get(key), v))
    if mismatches:
        for key, got, want in mismatches[:20]:
            print(f"  base-lower mismatch {key}: recomputed {got}, stored {want}",
                  file=sys.stderr)
        fail(f"{len(mismatches)} recomputed base lower bounds disagree with the "
             f"stored lower_bound_if_known column")

    # ---- upper bounds: audited table + the verified U(2,17) witness overlay
    final_upper = dict(upper)
    overlays = []
    for (t, n) in ((2, 17), (15, 17)):
        old = final_upper[("U", t, n)]
        if 6 < old:
            final_upper[("U", t, n)] = 6
            overlays.append(("U", t, n, old, 6,
                             "verified U(2,17) depth-6 witness"
                             + ("" if t == 2 else " via mirror duality")))

    # ---- final lower bounds: structural fixpoint with weight-game seeds.
    # Rerunning the fixpoint lets a game-improved cell propagate through
    # n-monotonicity and mirror duality; this is what raises U(9,14) and its
    # mirror dual U(5,14) (raw game value 5) to 6 via the game-improved cell
    # U(4,13) = U(9,13).
    game_seeds = {}
    for (kind, t, n) in base_lower:
        g = game_bound(A, kind, t, n)
        if g is not None:
            game_seeds[(kind, t, n)] = g
    final_lower = compute_lower_fixpoint(exact10, extra_seeds=game_seeds)

    improvements = []
    for (kind, t, n), base in base_lower.items():
        v = final_lower[(kind, t, n)]
        if v > base:
            g = game_bound(A, kind, t, n)
            improvements.append({
                "kind": kind, "n": n, "t": t,
                "before_lower": base, "game_bound": g, "after_lower": v,
                "upper": final_upper[(kind, t, n)],
                "mechanism": ("game value at the cell or its mirror dual"
                              if g == v else
                              "propagation of game-improved cells "
                              "(n-monotonicity and mirror duality)"),
            })

    # ---- verification gates -------------------------------------------------
    if len(improvements) != 44:
        fail(f"expected exactly 44 weight-game improvements, got {len(improvements)}")
    n_u = sum(1 for r in improvements if r["kind"] == "U")
    n_v = sum(1 for r in improvements if r["kind"] == "V")
    if (n_u, n_v) != (42, 2):
        fail(f"expected 42 U-type and 2 V-type improvements, got {n_u} U, {n_v} V")
    v_cells = sorted((r["n"], r["t"]) for r in improvements if r["kind"] == "V")
    if v_cells != [(17, 8), (17, 9)]:
        fail(f"V-type improvements expected at n=17, t=8 and t=9, got {v_cells}")
    for r in improvements:
        if r["after_lower"] - r["before_lower"] != 1:
            fail(f"improvement at {r} is not exactly one layer")

    for (kind, t, n), lo in final_lower.items():
        if lo > final_upper[(kind, t, n)]:
            fail(f"lower > upper at ({kind},{t},{n}): {lo} > {final_upper[(kind, t, n)]}")

    for (t, n) in ((2, 17), (15, 17)):
        if not (final_lower[("U", t, n)] == final_upper[("U", t, n)] == 6):
            fail(f"U({t},{n}) not reconstructed as exact depth 6: "
                 f"[{final_lower[('U', t, n)]},{final_upper[('U', t, n)]}]")

    expected = json.load(open(EXPECTED))
    diff = []
    for kind in ("U", "V"):
        for n in NS:
            row = expected[kind][str(n)]
            if len(row) != n:
                fail(f"expected-table row {kind} n={n} has {len(row)} cells")
            for t in range(1, n + 1):
                want = tuple(row[t - 1])
                got = (final_lower[(kind, t, n)], final_upper[(kind, t, n)])
                if got != want:
                    diff.append((kind, n, t, got, want))
    if diff:
        for kind, n, t, got, want in diff[:30]:
            print(f"  table mismatch ({kind},t={t},n={n}): reconstructed {got}, "
                  f"manuscript {want}", file=sys.stderr)
        fail(f"{len(diff)} cells disagree with the manuscript tables; "
             f"NOT modifying the expected tables -- stopping as required")

    # ---- outputs ------------------------------------------------------------
    OUT.mkdir(exist_ok=True)

    rows = []
    for kind in ("U", "V"):
        for n in NS:
            for t in range(1, n + 1):
                lo, up = final_lower[(kind, t, n)], final_upper[(kind, t, n)]
                g = game_bound(A, kind, t, n)
                rows.append({
                    "kind": kind, "n": n, "t": t,
                    "lower": lo, "upper": up,
                    "exact": lo == up,
                    "base_lower_pre_game": base_lower[(kind, t, n)],
                    "weight_game_bound": "" if g is None else g,
                    "improved_by_weight_game": lo > base_lower[(kind, t, n)],
                })
    with open(OUT / "final_bounds_n11_17.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    with open(OUT / "final_bounds_n11_17.json", "w") as f:
        json.dump({
            "description": "Mechanically reconstructed final bounds, 11<=n<=17, "
                           "verified cell-by-cell against the manuscript tables.",
            "inputs": {
                "exact_n10_table": str(N10_TABLE.relative_to(ROOT)),
                "audited_upper_bounds": str(PAPER_READY.relative_to(ROOT)),
                "weight_game_results": str(GAME_RESULTS.relative_to(ROOT)),
                "u2_n17_witness_run": str(U2N17_RUN.relative_to(ROOT)),
                "sorting_depths_11_17": SDEPTH,
            },
            "upper_bound_overlays": [
                {"kind": k, "t": t, "n": n, "before": b, "after": a, "reason": r}
                for (k, t, n, b, a, r) in overlays],
            "improvement_count": len(improvements),
            "bounds": rows,
        }, f, indent=1)

    with open(OUT / "weight_game_improvements.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["kind", "n", "t", "before_lower",
                                          "game_bound", "after_lower", "upper",
                                          "mechanism"])
        w.writeheader()
        w.writerows(sorted(improvements,
                           key=lambda r: (r["kind"], r["n"], r["t"])))

    # LaTeX tables in the manuscript's format
    def cell(kind, t, n):
        if t > n:
            return "--"
        lo, up = final_lower[(kind, t, n)], final_upper[(kind, t, n)]
        return str(lo) if lo == up else f"[{lo},{up}]"

    tex = ["% Generated by scripts/reconstruct_final_tables.py -- do not edit.",
           "% Verified cell-by-cell against the final manuscript tables."]
    specs = [("V", range(1, 10), "V-type $t$-selection depth bounds, $11 \\le n \\le 17$, $t=1,\\dots,9$."),
             ("V", range(10, 18), "V-type $t$-selection depth bounds, $11 \\le n \\le 17$, $t=10,\\dots,17$."),
             ("U", range(1, 10), "U-type $t$-selection depth bounds, $11 \\le n \\le 17$, $t=1,\\dots,9$."),
             ("U", range(10, 18), "U-type $t$-selection depth bounds, $11 \\le n \\le 17$, $t=10,\\dots,17$.")]
    for kind, ts, caption in specs:
        ts = list(ts)
        tex += [r"\begin{table*}[htbp]",
                f"\\caption{{{caption} A single value is exact; $[a,b]$ gives "
                "the current lower and upper bounds; a dash indicates $t>n$.}",
                r"\begin{center}",
                f"\\begin{{tabular}}{{c|{'c' * len(ts)}}}",
                r"\hline",
                "$n \\backslash t$ & " + " & ".join(str(t) for t in ts) + r" \\",
                r"\hline"]
        for n in NS:
            tex.append(f"{n} & " + " & ".join(cell(kind, t, n) for t in ts) + r" \\")
        tex += [r"\hline", r"\end{tabular}", r"\end{center}", r"\end{table*}", ""]
    (OUT / "final_tables_n11_17.tex").write_text("\n".join(tex) + "\n")

    print("RECONSTRUCTION OK")
    print(f"  cells reconstructed : {len(rows)} "
          f"({sum(1 for r in rows if r['exact'])} exact, "
          f"{sum(1 for r in rows if not r['exact'])} intervals)")
    print(f"  weight-game improvements: {len(improvements)} "
          f"({n_u} U-type, {n_v} V-type at {v_cells})")
    print(f"  upper-bound overlays: {overlays}")
    print(f"  manuscript agreement: all cells match "
          f"{EXPECTED.relative_to(ROOT)}")
    for name in ("final_bounds_n11_17.csv", "final_bounds_n11_17.json",
                 "final_tables_n11_17.tex", "weight_game_improvements.csv"):
        print(f"  wrote generated/{name}")


if __name__ == "__main__":
    main()
